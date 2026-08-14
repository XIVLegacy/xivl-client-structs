#!/usr/bin/env python3
"""Build the complete client-side Lua API contract from the local corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "manifests" / "lua_api_contract.json"
FUNCTION_RE = re.compile(r"^function\s+(L\d+_\d+)\(([^)]*)\)\s*$")
ASSIGN_RE = re.compile(
    r"^L\d+_\d+\.(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<rhs>L\d+_\d+)\s*$"
)
SCRIPT_EVENT_NAMES = {
    "onJobQuestCompleteFirst",
    "onJobQuestCompleteSecond",
    "onJobQuestCompleteThird",
}
SUBSYSTEM_PREFIXES = {
    "chara/player": {"chara"},
    "director": {"director"},
    "quest": {"quest"},
    "command": {"command", "commanddebugger"},
    "widget": {"widget"},
    "status": {"status"},
    "group": {"group"},
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _commit(repo: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _json_sha256(value: object) -> str:
    rendered = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest().upper()


def _subsystem(decoded: str) -> str:
    prefix = decoded.split("/", 1)[0] if "/" in decoded else "root"
    for subsystem, prefixes in SUBSYSTEM_PREFIXES.items():
        if prefix in prefixes:
            return subsystem
    return "other"


def _parse_methods(source: bytes, allowed: set[str]) -> list[dict[str, object]]:
    definitions: dict[str, tuple[int, list[str]]] = {}
    assignments: list[dict[str, object]] = []
    for line_number, raw in enumerate(source.decode("utf-8").splitlines(), 1):
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
            raise ValueError(f"line {line_number}: {name} lacks preceding {target} definition")
        function_line, params = definitions[target]
        assignments.append({
            "name": name,
            "params": params,
            "arity": sum(param != "..." for param in params),
            "variadic": "..." in params,
            "functionLine": function_line,
            "sourceLine": line_number,
            "callsiteCount": None,
        })
    found = {row["name"] for row in assignments}
    if found != allowed:
        raise ValueError(f"method assignment mismatch: missing={sorted(allowed - found)!r}")
    return assignments


def _native_retest(decomp_repo: Path) -> dict[str, object]:
    strings_path = decomp_repo / "config" / "ffxivgame.strings.json"
    dump_strings = decomp_repo / "tools" / "ghidra_scripts" / "DumpStrings.java"
    find_callers = decomp_repo / "tools" / "ghidra_scripts" / "FindCallers.java"
    direct = [
        ("_globalSave", "0xbd43f4", "asm/ffxivgame/002da450_FUN_006da450.s", "0xfd43f4"),
        ("_globalTemp", "0xbd4400", "asm/ffxivgame/002da4c0_FUN_006da4c0.s", "0xfd4400"),
        ("_memberSave", "0xbd440c", "asm/ffxivgame/002da530_FUN_006da530.s", "0xfd440c"),
    ]
    direct_rows: list[dict[str, object]] = []
    for name, string_rva, relative_asm, immediate in direct:
        text = (decomp_repo / relative_asm).read_text(encoding="utf-8").lower()
        if immediate not in text or "call 0x00447260" not in text:
            raise ValueError(f"{relative_asm}: direct registrar evidence drifted for {name}")
        direct_rows.append({
            "name": name,
            "status": "direct_string_immediate_to_name_helper",
            "stringRva": string_rva,
            "stringLocator": f"config/ffxivgame.strings.json:{7892 + len(direct_rows)}",
            "asmLocator": f"{relative_asm}:21-23",
            "derivation": "string VA = RVA + image base 0x00400000; asm pushes that VA before FUN_00447260",
        })

    assign_asm = decomp_repo / "asm" / "ffxivgame" / "009212a0_FUN_00d212a0.s"
    assign_text = assign_asm.read_text(encoding="utf-8").lower()
    if "0x0130d84c" not in assign_text or "call 0x00447260" not in assign_text:
        raise ValueError("_assignForChild bounded evidence drifted")

    return {
        "status": "bounded_sample_succeeded_complete_attribution_blocked",
        "sampleSize": 10,
        "directAttributions": direct_rows,
        "partialAttributions": [{
            "name": "_assignForChild",
            "status": "indirect_data_pointer_not_string_xref",
            "stringLocator": "config/ffxivgame.strings.json:21145",
            "stringRva": "0xd0f6bc",
            "asmLocator": "asm/ffxivgame/009212a0_FUN_00d212a0.s:8,15",
            "boundary": "The asm uses data pointer 0x0130d84c before FUN_00447260; no direct reference to the string VA is established.",
        }],
        "unattributedSampleNames": [
            "_defineClass", "_runCharaScheduler", "_wait", "_printLog", "_getMyPlayer", "_onInit",
        ],
        "existingExporterAssessment": {
            "DumpStrings.java": "Exports defined string values and RVAs but no references.",
            "FindCallers.java": "Requires supplied code addresses and does not discover string addresses or map all string references to registrars.",
            "missingCapability": "A reproducible string-name -> string-address -> all data/code references -> registrar/implementation mapping for every N-API name.",
        },
        "sourceSnapshot": {
            "repository": "XIVLegacy/xivl-decomp",
            "commit": _commit(decomp_repo),
            "strings": {"path": "config/ffxivgame.strings.json", "sha256": _sha256(strings_path)},
            "dumpStrings": {"path": "tools/ghidra_scripts/DumpStrings.java", "sha256": _sha256(dump_strings)},
            "findCallers": {"path": "tools/ghidra_scripts/FindCallers.java", "sha256": _sha256(find_callers)},
        },
    }


def build(scripts_repo: Path, decomp_repo: Path) -> dict[str, object]:
    registry_path = scripts_repo / "lua" / "registry.json"
    napi_path = scripts_repo / "lua" / "napi_index.json"
    scripts_manifest_path = scripts_repo / "manifests" / "scripts.json"
    api_catalog_path = REPO / "manifests" / "lua_api_index.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    napi = json.loads(napi_path.read_text(encoding="utf-8"))
    scripts_manifest = json.loads(scripts_manifest_path.read_text(encoding="utf-8"))
    api_catalog = json.loads(api_catalog_path.read_text(encoding="utf-8"))
    manifest_rows = {row["relativePath"]: row for row in scripts_manifest["scripts"]}

    script_contracts: list[dict[str, object]] = []
    method_count = callback_count = event_count = ordinary_count = 0
    subsystem_counts: dict[str, Counter] = {name: Counter() for name in [*SUBSYSTEM_PREFIXES, "other"]}

    for decoded, metadata in sorted(registry["scripts"].items()):
        subsystem = _subsystem(decoded)
        counts = subsystem_counts[subsystem]
        counts["scriptCount"] += 1
        classes = metadata.get("classes", [])
        if len(classes) > 1:
            raise ValueError(f"{decoded}: multiple registry classes are unsupported")
        if classes:
            counts["classBearingScripts"] += 1
        methods = set(metadata.get("methods", []))
        if not methods:
            continue
        relative_path = f"lua/scripts/{decoded}.lua"
        source_path = scripts_repo / relative_path
        source = source_path.read_bytes()
        manifest_row = manifest_rows[relative_path]
        if (len(source), _sha256(source_path)) != (manifest_row["bytes"], manifest_row["sha256"]):
            raise ValueError(f"{relative_path}: local body does not match scripts manifest")
        assignments = _parse_methods(source, methods)
        callbacks = [row for row in assignments if str(row["name"]).startswith("_on")]
        events = [row for row in assignments if row["name"] in SCRIPT_EVENT_NAMES]
        ordinary = [
            row for row in assignments
            if not str(row["name"]).startswith("_on") and row["name"] not in SCRIPT_EVENT_NAMES
        ]
        method_count += len(assignments)
        callback_count += len(callbacks)
        event_count += len(events)
        ordinary_count += len(ordinary)
        counts["methodAssignments"] += len(assignments)
        counts["callbackAssignments"] += len(callbacks)
        counts["scriptEventAssignments"] += len(events)
        counts["ordinaryMethodAssignments"] += len(ordinary)
        counts["scriptsWithMethods"] += 1
        script_contracts.append({
            "script": decoded,
            "subsystem": subsystem,
            "receiverClass": classes[0] if classes else None,
            "receiverReason": "registry_unique_class" if classes else "no_class_signal",
            "scriptSha256": manifest_row["sha256"],
            "lineCount": manifest_row["lineCount"],
            "callbacks": callbacks,
            "scriptEventHandlers": events,
            "ordinaryMethods": ordinary,
        })

    native_surfaces: list[dict[str, object]] = []
    scripts_with_napi: set[str] = set()
    api_names_by_subsystem: dict[str, set[str]] = defaultdict(set)
    for name, api in sorted(napi["apis"].items()):
        receiver_groups: dict[tuple[str, str | None, str], dict[str, object]] = {}
        for callsite in api["callsites"]:
            decoded = callsite["script"]
            metadata = registry["scripts"][decoded]
            classes = metadata.get("classes", [])
            subsystem = _subsystem(decoded)
            receiver = classes[0] if classes else None
            reason = "registry_unique_class" if classes else "no_class_signal"
            key = (subsystem, receiver, reason)
            group = receiver_groups.setdefault(key, {
                "subsystem": subsystem,
                "receiverClass": receiver,
                "receiverReason": reason,
                "referenceLineCount": 0,
                "scripts": Counter(),
            })
            group["referenceLineCount"] = int(group["referenceLineCount"]) + 1
            group["scripts"][decoded] += 1
            scripts_with_napi.add(decoded)
            subsystem_counts[subsystem]["napiReferenceLines"] += 1
            api_names_by_subsystem[subsystem].add(name)
        receivers: list[dict[str, object]] = []
        for group in receiver_groups.values():
            scripts = group.pop("scripts")
            receivers.append({
                **group,
                "scripts": [
                    {"script": script, "referenceLineCount": count}
                    for script, count in sorted(scripts.items())
                ],
                "arity": None,
                "variadic": None,
            })
        native_surfaces.append({
            "name": name,
            "referenceLineCount": api["callsiteCount"],
            "referenceSemantics": "one whitelist identifier hit per source line; not necessarily an invocation",
            "arity": None,
            "variadic": None,
            "catalogRefs": api_catalog["apis"].get(name, []),
            "receivers": sorted(receivers, key=lambda row: (
                str(row["subsystem"]), str(row["receiverClass"]), str(row["receiverReason"]))),
        })

    for decoded, metadata in registry["scripts"].items():
        subsystem = _subsystem(decoded)
        sidecar_path = scripts_repo / "lua" / "scripts" / f"{decoded}.calls.json"
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        subsystem_counts[subsystem]["napiApiScriptReferences"] += len(sidecar["apis"])
        if sidecar["apis"]:
            subsystem_counts[subsystem]["scriptsWithNapiReferences"] += 1

    subsystem_rows: list[dict[str, object]] = []
    for subsystem in [*SUBSYSTEM_PREFIXES, "other"]:
        counts = subsystem_counts[subsystem]
        subsystem_rows.append({
            "name": subsystem,
            "sourceTopLevels": sorted(SUBSYSTEM_PREFIXES.get(subsystem, {
                "area", "debug", "gamedata", "item", "judge", "root", "system", "world"})),
            "scriptCount": counts["scriptCount"],
            "classBearingScripts": counts["classBearingScripts"],
            "scriptsWithMethods": counts["scriptsWithMethods"],
            "methodAssignments": counts["methodAssignments"],
            "callbackAssignments": counts["callbackAssignments"],
            "scriptEventAssignments": counts["scriptEventAssignments"],
            "ordinaryMethodAssignments": counts["ordinaryMethodAssignments"],
            "scriptsWithNapiReferences": counts["scriptsWithNapiReferences"],
            "napiApiScriptReferences": counts["napiApiScriptReferences"],
            "distinctNapiNames": len(api_names_by_subsystem[subsystem]),
            "napiReferenceLines": counts["napiReferenceLines"],
        })

    if (method_count, callback_count, event_count, ordinary_count) != (13782, 209, 43, 13530):
        raise ValueError("script declaration totals drifted")
    if (len(native_surfaces), sum(row["referenceLineCount"] for row in native_surfaces)) != (433, 17049):
        raise ValueError("N-API surface totals drifted")

    tables = {"scriptDeclarations": script_contracts, "napiSurfaces": native_surfaces}
    return {
        "version": 1,
        "generated": "2026-08-14",
        "gameVersion": "1.23b",
        "extraction": "2012.09.19.0001",
        "scope": "Complete client-side Lua corpus API contract. Script bodies remain local-only. Decompiler parameter slots are positional evidence, not semantic types. N-API index callsites are one-per-line whitelist references and are not guaranteed invocations.",
        "sourceSnapshots": {
            "scripts": {
                "repository": "XIVLegacy/xivl-client-scripts",
                "commit": _commit(scripts_repo),
                "registry": {"path": "lua/registry.json", "sha256": _sha256(registry_path)},
                "napiIndex": {"path": "lua/napi_index.json", "sha256": _sha256(napi_path)},
                "scriptManifest": {"path": "manifests/scripts.json", "sha256": _sha256(scripts_manifest_path)},
                "localBodies": "lua/scripts/**/*.lua; required to regenerate, gitignored, and not copied",
            },
            "apiCatalog": {
                "path": "manifests/lua_api_index.json",
                "sha256": _sha256(api_catalog_path),
            },
        },
        "tierCriteria": [
            {"tier": "napi_surface", "criterion": "Name is present in lua/napi_index.json after whitelist annotation. Reference counts retain the source scanner's one-hit-per-line semantics; arity and variadic are unknown."},
            {"tier": "script_callback", "criterion": "Registry method starts with _on and a local function assignment supplies an exact positional parameter list."},
            {"tier": "script_event_handler", "criterion": "Registry method is one of the three onJobQuestComplete handlers and a local function assignment supplies its positional parameter list."},
            {"tier": "ordinary_script_method", "criterion": "Registry method is neither a callback nor a script-event handler; its local assignment supplies arity and variadic shape, but ordinary callsites are not indexed."},
        ],
        "totals": {
            "corpusScripts": registry["scriptCount"],
            "classBearingScripts": sum(bool(row.get("classes")) for row in registry["scripts"].values()),
            "scriptsWithoutClassSignal": sum(not row.get("classes") for row in registry["scripts"].values()),
            "scriptsWithMethods": len(script_contracts),
            "methodAssignments": method_count,
            "callbackAssignments": callback_count,
            "scriptEventAssignments": event_count,
            "ordinaryMethodAssignments": ordinary_count,
            "napiNames": len(native_surfaces),
            "scriptsWithNapiReferences": len(scripts_with_napi),
            "napiApiScriptReferences": sum(row["napiApiScriptReferences"] for row in subsystem_rows),
            "napiReferenceLines": sum(row["referenceLineCount"] for row in native_surfaces),
        },
        "subsystems": subsystem_rows,
        "nativeAttributionRetest": _native_retest(decomp_repo),
        "contractSha256": _json_sha256(tables),
        **tables,
        "boundaries": [
            "N-API arity and variadic shape remain null because the index includes member access, callback assignments, identifier references, and string literals as well as calls.",
            "Ordinary script-method callsite counts remain null because the corpus registry indexes declarations, not a receiver-resolved script call graph.",
            "Script bodies are local-only regeneration inputs and are not copied into this manifest.",
            "Decompiler parameter slots are positional labels, not semantic types.",
            "Client-side surfaces and callbacks do not establish packet or server behavior.",
        ],
        "sourceRefs": [
            "xivl-client-scripts:lua/registry.json",
            "xivl-client-scripts:lua/napi_index.json",
            "xivl-client-scripts:lua/scripts/**/*.calls.json",
            "xivl-client-scripts:manifests/scripts.json",
            "manifests/lua_api_index.json",
            "xivl-decomp:config/ffxivgame.strings.json:7892-7894",
            "xivl-decomp:asm/ffxivgame/002da450_FUN_006da450.s:21-23",
            "xivl-decomp:asm/ffxivgame/002da4c0_FUN_006da4c0.s:21-23",
            "xivl-decomp:asm/ffxivgame/002da530_FUN_006da530.s:21-23",
            "xivl-decomp:tools/ghidra_scripts/DumpStrings.java:53-72",
            "xivl-decomp:tools/ghidra_scripts/FindCallers.java:25-47",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scripts-repo", type=Path, required=True)
    parser.add_argument("--decomp-repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        document = build(args.scripts_repo.resolve(), args.decomp_repo.resolve())
        rendered = json.dumps(document, indent=2, ensure_ascii=True) + "\n"
        if args.check:
            if not args.out.is_file() or args.out.read_text(encoding="utf-8") != rendered:
                print(f"error: {args.out} does not match a fresh extraction", file=sys.stderr)
                return 1
            print(f"OK: {args.out} matches the complete local Lua corpus")
            return 0
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {document['totals']['methodAssignments']} methods to {args.out}")
        return 0
    except (OSError, UnicodeError, ValueError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
