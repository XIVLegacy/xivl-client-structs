#!/usr/bin/env python3
"""Build the frozen client-visible Lua callback contract from a local corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


FUNCTION_RE = re.compile(r"^function\s+(L\d+_\d+)\(([^)]*)\)\s*$")
ASSIGN_RE = re.compile(
    r"^L\d+_\d+\.(?P<name>_on[A-Za-z0-9_]*|onJobQuestComplete(?:First|Second|Third))"
    r"\s*=\s*(?P<rhs>L\d+_\d+)\s*$"
)
SCRIPT_EVENT_NAMES = {
    "onJobQuestCompleteFirst",
    "onJobQuestCompleteSecond",
    "onJobQuestCompleteThird",
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_sha256(value: object) -> str:
    rendered = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return _sha256(rendered.encode("utf-8"))


def _source_commit(repo: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _parse_contracts(source: bytes, allowed: set[str]) -> tuple[list[dict], list[dict]]:
    lines = source.decode("utf-8").splitlines()
    definitions: dict[str, tuple[int, list[str]]] = {}
    callbacks: list[dict] = []
    script_handlers: list[dict] = []
    for line_number, raw in enumerate(lines, 1):
        line = raw.strip()
        function_match = FUNCTION_RE.match(line)
        if function_match:
            params = [part.strip() for part in function_match.group(2).split(",") if part.strip()]
            definitions[function_match.group(1)] = (line_number, params)
            continue
        assign_match = ASSIGN_RE.match(line)
        if not assign_match or assign_match.group("name") not in allowed:
            continue
        name = assign_match.group("name")
        target = assign_match.group("rhs")
        if target not in definitions:
            raise ValueError(f"line {line_number}: {name} assignment lacks preceding {target} definition")
        function_line, params = definitions[target]
        row = {
            "name": name,
            "params": params,
            "arity": sum(param != "..." for param in params),
            "variadic": "..." in params,
            "functionLine": function_line,
            "sourceLine": line_number,
        }
        (script_handlers if name in SCRIPT_EVENT_NAMES else callbacks).append(row)
    return callbacks, script_handlers


def build(scripts_repo: Path) -> dict:
    registry_path = scripts_repo / "lua" / "registry.json"
    manifest_path = scripts_repo / "manifests" / "scripts.json"
    registry_bytes = registry_path.read_bytes()
    manifest_bytes = manifest_path.read_bytes()
    registry = json.loads(registry_bytes)
    script_manifest = json.loads(manifest_bytes)
    manifest_rows = {row["relativePath"]: row for row in script_manifest["scripts"]}

    output_scripts: dict[str, dict] = {}
    callback_names: set[str] = set()
    callback_count = fixed_count = variadic_count = parsed_count = 0
    event_count = 0
    for decoded, metadata in sorted(registry["scripts"].items()):
        allowed = {
            name for name in metadata.get("methods", [])
            if name.startswith("_on") or name in SCRIPT_EVENT_NAMES
        }
        if not allowed:
            continue
        relative_path = f"lua/scripts/{decoded}.lua"
        source_path = scripts_repo / relative_path
        source = source_path.read_bytes()
        manifest_row = manifest_rows[relative_path]
        if (len(source), _sha256(source)) != (manifest_row["bytes"], manifest_row["sha256"]):
            raise ValueError(f"{relative_path}: local source does not match reproduction manifest")
        callbacks, script_handlers = _parse_contracts(source, allowed)
        found = {row["name"] for row in callbacks + script_handlers}
        missing = sorted(allowed - found)
        if missing:
            raise ValueError(f"{relative_path}: missing assignments for {missing}")
        if not callbacks and not script_handlers:
            continue
        classes = metadata.get("classes", [])
        if len(classes) != 1:
            raise ValueError(f"{relative_path}: expected one class, found {classes!r}")
        output_scripts[decoded] = {
            "ciphered": metadata["ciphered"],
            "class": classes[0],
            "scriptSha256": manifest_row["sha256"],
            "lineCount": manifest_row["lineCount"],
            "callbacks": callbacks,
            "scriptEventHandlers": script_handlers,
        }
        callback_names.update(row["name"] for row in callbacks)
        callback_count += len(callbacks)
        fixed_count += sum(not row["variadic"] for row in callbacks)
        variadic_count += sum(row["variadic"] for row in callbacks)
        parsed_count += len(callbacks)
        event_count += len(script_handlers)

    callback_script_count = sum(bool(row["callbacks"]) for row in output_scripts.values())
    event_script_count = sum(bool(row["scriptEventHandlers"]) for row in output_scripts.values())
    return {
        "version": 1,
        "generated": "2026-08-14",
        "gameVersion": "1.23b",
        "extraction": "2012.09.19.0001",
        "scope": "Decoded script-declared client callback and script-event contracts. Parameter names are decompiler slots, not semantic types. No native registrar, xref, packet, or server behavior is claimed.",
        "sourceSnapshot": {
            "repository": "XIVLegacy/xivl-client-scripts",
            "commit": _source_commit(scripts_repo),
            "registry": {"path": "lua/registry.json", "sha256": _sha256(registry_bytes)},
            "scriptManifest": {"path": "manifests/scripts.json", "sha256": _sha256(manifest_bytes)},
            "localBodies": "lua/scripts/**/*.lua; required to regenerate, gitignored, and not copied",
        },
        "totals": {
            "corpusScripts": registry["scriptCount"],
            "contractScriptCount": len(output_scripts),
            "callbackScriptCount": callback_script_count,
            "callbackAssignments": callback_count,
            "distinctCallbacks": len(callback_names),
            "parsedParameterLists": parsed_count,
            "fixedCallbacks": fixed_count,
            "variadicCallbacks": variadic_count,
            "scriptEventHandlerScripts": event_script_count,
            "scriptEventHandlerAssignments": event_count,
        },
        "contractSha256": _json_sha256(output_scripts),
        "relationshipToCompleteContract": {
            "status": "narrower_earlier_pass",
            "supersededBy": "manifests/lua_api_contract.json",
            "retainedPurpose": "Compact callback-only view with per-script positional shapes.",
        },
        "nativeTraceBoundary": {
            "status": "bounded_sample_succeeded_complete_attribution_blocked",
            "functionalEquivalents": ["DumpStrings.java", "FindCallers.java", "exported asm corpus"],
            "missingCapability": "A reproducible string-name -> string-address -> all data/code references -> registrar/implementation mapping for every callback name.",
            "effect": "The bounded native sample is recorded in lua_api_contract.json. This callback-only manifest does not infer native callback targets."
        },
        "scripts": output_scripts,
        "sourceRefs": [
            "xivl-client-scripts:lua/registry.json",
            "xivl-client-scripts:lua/scripts/**/*.lua",
            "xivl-client-scripts:manifests/scripts.json",
            "manifests/lua_api_contract.json",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scripts-repo", type=Path, required=True,
                        help="Explicit xivl-client-scripts checkout containing the local corpus.")
    parser.add_argument("--out", type=Path,
                        default=Path("manifests/lua_callback_contract.json"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        document = build(args.scripts_repo.resolve())
        rendered = json.dumps(document, indent=2, ensure_ascii=True) + "\n"
        if args.check:
            if not args.out.is_file() or args.out.read_text(encoding="utf-8") != rendered:
                print(f"error: {args.out} does not match a fresh extraction", file=sys.stderr)
                return 1
            print(f"OK: {args.out} matches the local corpus")
            return 0
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {document['totals']['callbackAssignments']} callbacks to {args.out}")
        return 0
    except (OSError, UnicodeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
