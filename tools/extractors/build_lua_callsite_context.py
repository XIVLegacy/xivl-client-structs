#!/usr/bin/env python3
"""Build callsite context for the deferred Lua binding names.

The input corpus is supplied explicitly because the decoded Lua bodies are
local-only.  This extractor records metadata and source locations only; it
never copies a script body into the tracked manifest.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "manifests" / "lua_callsite_context.json"
DEFAULT_API_CONTRACT = REPO / "manifests" / "lua_api_contract.json"

TARGETS = (
    "AbandonGuildleve",
    "CreateGuildleveDirector",
    "EndDirector",
    "EndGuildleve",
    "StartGuildleve",
    "SyncAllInfo",
    "UpdateAimNumNow",
    "UpdateMarkers",
    "CanTarget",
    "GetHPP",
    "GetStatusEffect",
    "GetTargetFind",
    "HasHateForTarget",
    "SetCombos",
    "SetProc",
    "RequestWorldLinkshellCreate",
    "SendUpdatePackets",
    "SetMaxHP",
    "StartChocoboRental",
)

IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
SUBSYSTEMS = {
    "chara": "chara/player",
    "director": "director",
    "quest": "quest",
    "command": "command",
    "commanddebugger": "command",
    "widget": "widget",
    "status": "status",
    "group": "group",
}


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    start: int
    end: int
    line: int
    column: int


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _json_sha256(value: object) -> str:
    rendered = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return _sha256_bytes(rendered.encode("utf-8"))


def _commit(repo: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _line_column(line_starts: list[int], offset: int) -> tuple[int, int]:
    line_index = bisect.bisect_right(line_starts, offset) - 1
    return line_index + 1, offset - line_starts[line_index] + 1


def _long_bracket_end(source: str, start: int) -> int | None:
    if source[start:start + 1] != "[":
        return None
    match = re.match(r"\[(=*)\[", source[start:])
    if not match:
        return None
    marker = "]" + match.group(1) + "]"
    end = source.find(marker, start + len(match.group(0)))
    return len(source) if end < 0 else end + len(marker)


def _lex(source: str) -> list[Token]:
    """Lex enough Lua syntax to exclude comments/strings and balance calls."""
    tokens: list[Token] = []
    line_starts = [0]
    line_starts.extend(index + 1 for index, char in enumerate(source) if char == "\n")
    i = 0
    n = len(source)
    while i < n:
        ch = source[i]
        if ch.isspace():
            i += 1
            continue
        if source.startswith("--", i):
            long_end = _long_bracket_end(source, i + 2)
            if long_end is not None:
                i = long_end
                continue
            newline = source.find("\n", i + 2)
            i = n if newline < 0 else newline + 1
            continue
        if ch in "'\"":
            quote = ch
            start = i
            i += 1
            while i < n:
                if source[i] == "\\":
                    i += 2
                elif source[i] == quote:
                    i += 1
                    break
                else:
                    i += 1
            line, column = _line_column(line_starts, start)
            tokens.append(Token("string", source[start:i], start, i, line, column))
            continue
        long_end = _long_bracket_end(source, i)
        if long_end is not None:
            line, column = _line_column(line_starts, i)
            tokens.append(Token("string", source[i:long_end], i, long_end, line, column))
            i = long_end
            continue
        if ch.isalpha() or ch == "_":
            match = IDENTIFIER_RE.match(source, i)
            assert match is not None
            end = match.end()
            line, column = _line_column(line_starts, i)
            tokens.append(Token("identifier", source[i:end], i, end, line, column))
            i = end
            continue
        if ch.isdigit():
            match = re.match(r"(?:0[xX][0-9A-Fa-f]+|[0-9]+(?:\.[0-9]*)?)", source[i:])
            assert match is not None
            end = i + len(match.group(0))
            line, column = _line_column(line_starts, i)
            tokens.append(Token("number", source[i:end], i, end, line, column))
            i = end
            continue
        matched = next((op for op in ("...", "..", "::", "<=", ">=", "==", "~=", "->")
                        if source.startswith(op, i)), None)
        value = matched or ch
        line, column = _line_column(line_starts, i)
        tokens.append(Token("punctuation", value, i, i + len(value), line, column))
        i += len(value)
    return tokens


def _token_text(source: str, tokens: list[Token], first: int, last: int) -> str:
    if first > last:
        return ""
    return source[tokens[first].start:tokens[last].end]


def _previous_boundary(tokens: list[Token], index: int) -> int:
    boundaries = {";", "=", "return", "local", "then", "do", "else", "elseif", "function"}
    cursor = index - 1
    while cursor >= 0:
        token = tokens[cursor]
        if token.value in boundaries or token.value in {"(", "[", "{", ","}:
            return cursor + 1
        cursor -= 1
    return 0


def _receiver(source: str, tokens: list[Token], index: int) -> str | None:
    """Return the written receiver expression for dot/colon member calls."""
    if index < 1 or tokens[index - 1].value not in {".", ":"}:
        return None
    member = index - 2
    if member < 0:
        return None
    first = member
    # Decompiled output places member calls on one line.  Do not cross a
    # line boundary (or an expression delimiter) while recovering the written
    # receiver; otherwise an earlier function declaration can be mistaken for
    # the receiver of a later call.
    while first > 0:
        previous = tokens[first - 1]
        if previous.line != tokens[member].line:
            break
        if previous.value in {"=", ",", ";", "return", "local", "then", "do", "else", "elseif", "function", "("}:
            break
        if previous.kind == "identifier" or previous.value in {".", "]", "}"}:
            first -= 1
            continue
        break
    return _token_text(source, tokens, first, member).strip() or None


def _matching_close(tokens: list[Token], open_index: int) -> int | None:
    opens = {"(": ")", "[": "]", "{": "}"}
    closes = {")", "]", "}"}
    stack: list[str] = []
    for index in range(open_index, len(tokens)):
        value = tokens[index].value
        if value in opens:
            stack.append(opens[value])
        elif value in closes:
            if not stack or stack.pop() != value:
                return None
            if not stack:
                return index
    return None


def _arguments(source: str, tokens: list[Token], open_index: int, close_index: int) -> list[str]:
    if close_index == open_index + 1:
        return []
    parts: list[str] = []
    start_offset = tokens[open_index].end
    depth = {"(": 0, "[": 0, "{": 0}
    for index in range(open_index + 1, close_index):
        value = tokens[index].value
        if value in depth:
            depth[value] += 1
        elif value == ")":
            depth["("] -= 1
        elif value == "]":
            depth["["] -= 1
        elif value == "}":
            depth["{"] -= 1
        elif value == "," and not any(depth.values()):
            parts.append(source[start_offset:tokens[index].start].strip())
            start_offset = tokens[index].end
    parts.append(source[start_offset:tokens[close_index].start].strip())
    return [part for part in parts if part]


def _subsystem(script: str) -> str:
    top = script.split("/", 1)[0]
    return SUBSYSTEMS.get(top, "other")


def _string_value(raw: str) -> str | None:
    if len(raw) >= 2 and raw[0] in "'\"" and raw[-1] == raw[0]:
        # The target names are ASCII and contain no escape sequences. Treat an
        # escaped literal as non-equal rather than applying semantic decoding.
        value = raw[1:-1]
        return value if "\\" not in value else None
    long_match = re.fullmatch(r"\[(=*)\[(.*)\]\1\]", raw, re.DOTALL)
    return long_match.group(2) if long_match else None


def _occurrences(source: str, target_set: set[str]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    tokens = _lex(source)
    result = {name: {"declarations": [], "references": [], "invocations": []}
              for name in target_set}
    for index, token in enumerate(tokens):
        name = token.value if token.kind == "identifier" else _string_value(token.value)
        if name not in target_set:
            continue
        if token.kind == "string":
            result[name]["references"].append({
                "line": token.line,
                "column": token.column,
                "written": token.value,
                "referenceKind": "string_literal",
            })
            continue
        previous = tokens[index - 1].value if index else None
        following = tokens[index + 1].value if index + 1 < len(tokens) else None
        is_function_declaration = previous == "function" or (
            index >= 3 and tokens[index - 3].value == "function" and previous in {".", ":"}
        )
        is_assignment = following == "="
        if is_function_declaration or is_assignment:
            declaration = {
                "line": token.line,
                "column": token.column,
                "written": token.value,
                "declarationKind": "function" if is_function_declaration else "assignment",
                "receiver": _receiver(source, tokens, index),
            }
            if is_function_declaration and index + 1 < len(tokens) and tokens[index + 1].value == "(":
                close = _matching_close(tokens, index + 1)
                if close is not None:
                    args = _arguments(source, tokens, index + 1, close)
                    declaration["parameters"] = args
                    declaration["arity"] = len(args)
            result[name]["declarations"].append(declaration)
            continue
        if following == "(":
            close = _matching_close(tokens, index + 1)
            if close is not None:
                args = _arguments(source, tokens, index + 1, close)
                result[name]["invocations"].append({
                    "line": token.line,
                    "column": token.column,
                    "written": token.value,
                    "receiver": _receiver(source, tokens, index),
                    "callKind": "member" if previous in {".", ":"} else "direct",
                    "arguments": args,
                    "arity": len(args),
                })
                continue
        result[name]["references"].append({
            "line": token.line,
            "column": token.column,
            "written": token.value,
            "referenceKind": "identifier",
        })
    return result


def _source_snapshot(scripts_repo: Path, api_contract: Path, registry_path: Path,
                     napi_path: Path, script_manifest_path: Path) -> dict[str, Any]:
    return {
        "scripts": {
            "repository": "XIVLegacy/xivl-client-scripts",
            "commit": _commit(scripts_repo),
            "registry": {"path": "lua/registry.json", "sha256": _sha256(registry_path)},
            "napiIndex": {"path": "lua/napi_index.json", "sha256": _sha256(napi_path)},
            "scriptManifest": {"path": "manifests/scripts.json", "sha256": _sha256(script_manifest_path)},
            "localBodies": "lua/scripts/**/*.lua; required to regenerate, gitignored, and not copied",
        },
        "apiContract": {
            "path": "manifests/lua_api_contract.json",
            "sha256": _sha256(api_contract),
        },
    }


def build(scripts_repo: Path, api_contract_path: Path = DEFAULT_API_CONTRACT) -> dict[str, Any]:
    registry_path = scripts_repo / "lua" / "registry.json"
    napi_path = scripts_repo / "lua" / "napi_index.json"
    script_manifest_path = scripts_repo / "manifests" / "scripts.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    napi = json.loads(napi_path.read_text(encoding="utf-8"))
    script_manifest = json.loads(script_manifest_path.read_text(encoding="utf-8"))
    api_contract = json.loads(api_contract_path.read_text(encoding="utf-8"))
    manifest_rows = {row["relativePath"]: row for row in script_manifest["scripts"]}
    target_set = set(TARGETS)
    if len(target_set) != len(TARGETS):
        raise ValueError("target list contains duplicate names")

    rows: dict[str, dict[str, Any]] = {
        name: {
            "name": name,
            "baseContract": {
                "present": any(surface.get("name") == name for surface in api_contract.get("napiSurfaces", [])),
                "napiReferenceLineCount": next(
                    (surface.get("referenceLineCount") for surface in api_contract.get("napiSurfaces", [])
                     if surface.get("name") == name), 0),
            },
            "registryDeclarations": [],
            "sidecarReferences": [],
            "scriptOccurrences": [],
            "declarations": [],
            "references": [],
            "invocations": [],
        }
        for name in TARGETS
    }
    scripts_scanned = sidecars_scanned = 0
    for decoded, metadata in sorted(registry["scripts"].items()):
        relative = f"lua/scripts/{decoded}.lua"
        source_path = scripts_repo / relative
        sidecar_path = scripts_repo / "lua" / "scripts" / f"{decoded}.calls.json"
        source = source_path.read_bytes()
        contract_row = manifest_rows.get(relative)
        if contract_row is None:
            raise ValueError(f"{relative}: missing scripts manifest row")
        if (len(source), _sha256_bytes(source)) != (contract_row["bytes"], contract_row["sha256"]):
            raise ValueError(f"{relative}: local source does not match reproduction manifest")
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        if sidecar.get("decoded") != decoded:
            raise ValueError(f"{relative}: sidecar decoded identity drifted")
        scripts_scanned += 1
        sidecars_scanned += 1
        classes = metadata.get("classes", [])
        context = {
            "script": decoded,
            "subsystem": _subsystem(decoded),
            "class": classes[0] if len(classes) == 1 else None,
            "receiverReason": "registry_unique_class" if len(classes) == 1 else "no_class_signal",
            "scriptSha256": contract_row["sha256"],
        }
        body_hits = _occurrences(source.decode("utf-8"), target_set)
        for name in TARGETS:
            row = rows[name]
            if name in metadata.get("methods", []):
                row["registryDeclarations"].append({**context, "kind": "registry_method"})
            for line in sidecar.get("apis", {}).get(name, []):
                row["sidecarReferences"].append({**context, "line": line, "kind": "sidecar_api"})
            hits = body_hits[name]
            for kind in ("declarations", "references", "invocations"):
                for hit in hits[kind]:
                    enriched = {**context, **hit}
                    row["scriptOccurrences"].append(enriched)
                    row[kind].append(enriched)

    for row in rows.values():
        arities = [hit["arity"] for hit in row["declarations"] if isinstance(hit.get("arity"), int)]
        arities += [hit["arity"] for hit in row["invocations"] if isinstance(hit.get("arity"), int)]
        row["arityRange"] = {
            "min": min(arities) if arities else None,
            "max": max(arities) if arities else None,
        }
        row["occurrenceVerdict"] = (
            "occurrences_present"
            if row["registryDeclarations"] or row["sidecarReferences"] or row["scriptOccurrences"]
            else "no_occurrence_in_preserved_corpus"
        )

    target_rows = [rows[name] for name in TARGETS]
    totals = {
        "targetCount": len(target_rows),
        "scriptsScanned": scripts_scanned,
        "sidecarsScanned": sidecars_scanned,
        "targetsWithOccurrences": sum(row["occurrenceVerdict"] == "occurrences_present" for row in target_rows),
        "registryDeclarationCount": sum(len(row["registryDeclarations"]) for row in target_rows),
        "sidecarReferenceCount": sum(len(row["sidecarReferences"]) for row in target_rows),
        "declarationCount": sum(len(row["declarations"]) for row in target_rows),
        "referenceCount": sum(len(row["references"]) for row in target_rows),
        "invocationCount": sum(len(row["invocations"]) for row in target_rows),
    }
    document: dict[str, Any] = {
        "version": 1,
        "generated": "2026-08-14",
        "gameVersion": "1.23b",
        "extraction": "2012.09.19.0001",
        "scope": "Preserved-corpus declaration, reference, and bounded syntactic invocation context for exactly 19 deferred Lua binding names. The invocation parser covers an identifier followed by a balanced parenthesized argument list; written expressions are source text and receive no semantic promotion.",
        "sourceSnapshots": _source_snapshot(
            scripts_repo, api_contract_path, registry_path, napi_path, script_manifest_path),
        "baseContract": {
            "path": "manifests/lua_api_contract.json",
            "sha256": _sha256(api_contract_path),
            "napiSurfaceCount": len(api_contract.get("napiSurfaces", [])),
            "deferredNamesPresent": sum(row["baseContract"]["present"] for row in target_rows),
        },
        "targets": target_rows,
        "totals": totals,
        "boundaries": [
            "The local Lua bodies are regeneration inputs and remain gitignored; no body text is copied into this manifest.",
            "Registry method rows and sidecar API rows are preserved as separate evidence classes from lexical body occurrences.",
            "Identifier and string-literal references are not treated as invocations unless a balanced call expression is syntactically present.",
            "Written argument expressions are source text only; this manifest does not assign semantic types, values, or server behavior.",
            "Invocation extraction is deliberately bounded to an identifier followed immediately by parentheses; Lua sugar, parenthesized callee, and bracket-index call forms remain lexical references.",
            "Receiver extraction covers simple same-line dot or colon expressions. Argument splitting balances parentheses, brackets, and braces but does not model nested Lua function/end blocks.",
            "A no_occurrence_in_preserved_corpus verdict is bounded to the explicit registry, sidecars, and local body snapshot.",
        ],
        "sourceRefs": [
            "xivl-client-scripts:lua/registry.json",
            "xivl-client-scripts:lua/napi_index.json",
            "xivl-client-scripts:lua/scripts/**/*.calls.json",
            "xivl-client-scripts:lua/scripts/**/*.lua",
            "xivl-client-scripts:manifests/scripts.json",
            "manifests/lua_api_contract.json",
            "tools/extractors/build_lua_callsite_context.py",
        ],
    }
    document["contractSha256"] = _json_sha256({"targets": target_rows, "totals": totals})
    # Keep the explicit target order stable while guarding against accidental
    # additions to the output table.
    if [row["name"] for row in target_rows] != list(TARGETS):
        raise ValueError("target order drifted")
    if len(target_rows) != 19 or len({row["name"] for row in target_rows}) != 19:
        raise ValueError("callsite context must contain exactly 19 unique targets")
    return document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scripts-repo", type=Path, required=True,
                        help="Explicit xivl-client-scripts checkout containing the local corpus.")
    parser.add_argument("--api-contract", type=Path, default=DEFAULT_API_CONTRACT,
                        help="Base lua_api_contract.json to extend (default: this checkout).")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        document = build(args.scripts_repo.resolve(), args.api_contract.resolve())
        rendered = json.dumps(document, indent=2, ensure_ascii=True) + "\n"
        if args.check:
            if not args.out.is_file() or args.out.read_text(encoding="utf-8") != rendered:
                print(f"error: {args.out} does not match a fresh extraction", file=sys.stderr)
                return 1
            print(f"OK: {args.out} matches the preserved Lua corpus")
            return 0
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {document['totals']['targetCount']} targets to {args.out}")
        return 0
    except (OSError, UnicodeError, ValueError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
