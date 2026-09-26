#!/usr/bin/env python3
"""Build the data-dependency catalog from local observations and curated inputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from _catalog_lock import catalog_lock  # noqa: E402

NAPI_FIELD_ACCESS = REPO_ROOT / "manifests" / "control_class_napi_field_access.json"
NAPI_FIELD_ACCESS_RECURSIVE = (
    REPO_ROOT / "manifests" / "control_class_napi_field_access_recursive.json"
)
VTABLE_RESOLVED_EVIDENCE = REPO_ROOT / "manifests" / "vtable_resolved_evidence.json"
RECEIVER_FIELD_WRITES = REPO_ROOT / "manifests" / "receiver_field_writes.json"
CURATED_JSON = REPO_ROOT / "manifests" / "data_dependency_overlay.json"
C2S_CURATED_JSON = REPO_ROOT / "manifests" / "c2s_bridge_overlay.json"
OUT_JSON = REPO_ROOT / "manifests" / "data_dependency_catalog.json"

CITATION_RENAMES = {
    "xivl-opcodes:" + "data/opcodes.json": "xivl-opcodes:opcodes.json",
    "xivl-opcodes:" + "data/external_opcodes.json": "xivl-opcodes:opcodes.json",
}


def normalize_citations(value: object) -> tuple[object, int]:
    """Update moved sibling citations without rebuilding accumulated blocks."""
    if isinstance(value, str):
        updated = value
        for old, new in CITATION_RENAMES.items():
            updated = updated.replace(old, new)
        return updated, int(updated != value)
    if isinstance(value, list):
        result = []
        changes = 0
        for item in value:
            updated, count = normalize_citations(item)
            result.append(updated)
            changes += count
        return result, changes
    if isinstance(value, dict):
        result = {}
        changes = 0
        for key, item in value.items():
            updated, count = normalize_citations(item)
            result[key] = updated
            changes += count
        return result, changes
    return value, 0


def build_receiver_writes(curated: dict) -> list[dict]:
    """Combine curated native writes with extracted receiver writes."""
    out = list(curated["nativeReceiverWrites"])
    receiver_classification = json.loads(
        RECEIVER_FIELD_WRITES.read_text(encoding="utf-8")
    )
    for r in receiver_classification["perReceiver"]:
        if not r["unifiedWrites"]:
            continue
        if not r.get("castTarget"):
            continue
        out.append(
            {
                "receiver": r["receiverName"],
                "opcode": r["opcodeHex"],
                "bcsyRef": "receiver_classification",
                "writes": [
                    {
                        "actorClass": r["castTarget"],
                        "offset": o,
                        "type": "?",
                        "semantic": f"auto-extracted from {r['slot1Va']}+workers",
                    }
                    for o in r["unifiedWrites"]
                ],
                "applyVa": r["slot1Va"],
                "kind": r["kind"],
                "workers": r["workers"],
            }
        )
    out.extend(curated["virtualReceiverWrites"])
    return out


def build_cross_refs(curated: dict) -> tuple[dict, dict, dict]:
    fa = json.loads(NAPI_FIELD_ACCESS.read_text(encoding="utf-8"))
    fa_recursive = json.loads(NAPI_FIELD_ACCESS_RECURSIVE.read_text(encoding="utf-8"))
    receiver_writes = build_receiver_writes(curated)

    write_offset_to_receivers: dict[str, list[dict]] = {}
    for r in receiver_writes:
        for w in r["writes"]:
            key = (w["actorClass"], w["offset"].lower())
            write_offset_to_receivers.setdefault(key, []).append(
                {
                    "receiver": r["receiver"],
                    "opcode": r["opcode"],
                    "bcsyRef": r["bcsyRef"],
                    "semantic": w["semantic"],
                    "type": w["type"],
                }
            )

    # Cross-class offset matches are allowed only within the known inheritance hierarchy.
    HIERARCHY = {
        "MyPlayer": {"MyPlayer", "PlayerBase", "CharaBase", "ActorBase"},
        "PlayerBase": {"PlayerBase", "CharaBase", "ActorBase"},
        "NpcBase": {"NpcBase", "CharaBase", "ActorBase"},
        "CharaBase": {"CharaBase", "ActorBase"},
        "ActorBase": {"ActorBase"},
        "DirectorBase": {"DirectorBase"},
        "AreaBase": {"AreaBase"},
        "PrivateAreaBase": {"PrivateAreaBase", "AreaBase"},
        "ItemBase": {"ItemBase"},
    }

    offset_only_to_writers: dict[str, list[dict]] = {}
    for (cls, off), writers in write_offset_to_receivers.items():
        offset_only_to_writers.setdefault(off, []).extend(
            [{**w, "writerActorClass": cls} for w in writers]
        )

    def find_api_matches(read_offsets: list[str], cls_name: str) -> list[dict]:
        out = []
        for off in read_offsets:
            exact = write_offset_to_receivers.get((cls_name, off), [])
            if exact:
                out.append(
                    {
                        "offset": off,
                        "matchKind": "exact",
                        "receivers": exact,
                    }
                )
                continue
            relaxed = offset_only_to_writers.get(off, [])
            compatible = []
            for w in relaxed:
                if w.get("writerActorClass") in HIERARCHY.get(
                    cls_name, set()
                ) or cls_name in HIERARCHY.get(w.get("writerActorClass", ""), set()):
                    compatible.append(w)
            if compatible:
                out.append(
                    {
                        "offset": off,
                        "matchKind": "hierarchy",
                        "receivers": compatible,
                    }
                )
        return out

    pilot_matches: list[dict] = []
    pilot_no_match: list[dict] = []
    for cls_name, apis in fa["byClass"].items():
        for api in apis:
            if api.get("status") != "ok":
                continue
            reads = [o.lower() for o in api.get("readsOffsets", [])]
            nested = [r["inner"].lower() for r in api.get("nestedReads", [])]
            all_reads = sorted(set(reads + nested))
            api_matches = find_api_matches(all_reads, cls_name)
            if api_matches:
                pilot_matches.append(
                    {
                        "luaName": api["luaName"],
                        "luaClass": cls_name,
                        "implVa": api.get("implVa"),
                        "matches": api_matches,
                    }
                )
            else:
                pilot_no_match.append(
                    {
                        "luaName": api["luaName"],
                        "luaClass": cls_name,
                        "implVa": api.get("implVa"),
                        "readsOffsets": api.get("readsOffsets", []),
                        "writesOffsets": api.get("writesOffsets", []),
                    }
                )

    vtable_evidence: dict[str, dict] = {}
    if VTABLE_RESOLVED_EVIDENCE.exists():
        ve = json.loads(VTABLE_RESOLVED_EVIDENCE.read_text(encoding="utf-8"))
        for e in ve.get("perImplEvidence", []):
            vtable_evidence[e["implVa"]] = {
                "reads": [o.lower() for o in e.get("derivedReads", [])],
                "writes": [o.lower() for o in e.get("derivedWrites", [])],
                "nested": [
                    {"inner": r["inner"].lower()} for r in e.get("derivedNested", [])
                ],
            }

    recursive_matches: list[dict] = []
    for cls_name, apis in fa_recursive["byClass"].items():
        for api in apis:
            if api.get("status") != "ok":
                continue
            deep_reads = [o.lower() for o in api.get("deepReads", [])]
            deep_nested = [r["inner"].lower() for r in api.get("deepNestedReads", [])]
            vt = vtable_evidence.get(api.get("implVa"), {})
            vt_reads = vt.get("reads", [])
            vt_nested = [r["inner"] for r in vt.get("nested", [])]
            all_reads = sorted(set(deep_reads + deep_nested + vt_reads + vt_nested))
            api_matches = find_api_matches(all_reads, cls_name)
            if api_matches:
                direct_reads = set(o.lower() for o in api.get("directReads", []))
                direct_nested = set(
                    r["inner"].lower() for r in api.get("directNestedReads", [])
                )
                deep_set = set(deep_reads + deep_nested)
                vt_set = set(vt_reads + vt_nested)
                for m in api_matches:
                    if m["offset"] in (direct_reads | direct_nested):
                        m["source"] = "direct"
                    elif m["offset"] in deep_set:
                        m["source"] = "deep_chase"
                    elif m["offset"] in vt_set:
                        m["source"] = "vtable_resolved"
                    else:
                        m["source"] = "unknown"
                recursive_matches.append(
                    {
                        "luaName": api["luaName"],
                        "luaClass": cls_name,
                        "implVa": api.get("implVa"),
                        "chasedCallees": api.get("chasedCallees", []),
                        "matches": api_matches,
                    }
                )

    return (
        {
            f"{cls}.{off}": writers
            for (cls, off), writers in write_offset_to_receivers.items()
        },
        {"matches": pilot_matches, "noMatch": pilot_no_match},
        {"matches": recursive_matches},
    )


def add_sections(out: dict, sections: dict) -> None:
    if out.keys() & sections.keys():
        raise ValueError("curated sections collide with generated catalog fields")
    out.update(sections)


def build_catalog(curated: dict | None = None) -> dict:
    if curated is None:
        curated = json.loads(CURATED_JSON.read_text(encoding="utf-8"))
    if set(curated) != {
        "metadata",
        "nativeReceiverWrites",
        "virtualReceiverWrites",
        "additionalReceiverWriteIndex",
        "confirmedIndirectBindings",
        "recursiveMatchSources",
        "totalsExtras",
        "relationshipFindings",
        "directEmissionMining",
        "payloadFindings",
    }:
        raise ValueError(
            "data-dependency curated input has missing or unowned sections"
        )
    if set(curated["metadata"]) != {
        "version",
        "gameVersion",
        "generated",
        "source",
        "description",
    }:
        raise ValueError("data-dependency metadata has missing or unowned fields")
    write_index, pilot, recursive = build_cross_refs(curated)
    add_sections(write_index, curated["additionalReceiverWriteIndex"])

    # Preserve the recorded evidence tier when direct and resolved reads overlap.
    for assertion in curated["recursiveMatchSources"]:
        matches = [
            match
            for api in recursive["matches"]
            if all(
                api[key] == assertion[key] for key in ("luaName", "luaClass", "implVa")
            )
            for match in api["matches"]
            if match["offset"] == assertion["offset"]
        ]
        if len(matches) != 1 or matches[0]["source"] != assertion["expectedSource"]:
            raise ValueError(
                f"recursive evidence source changed: {assertion['luaName']} {assertion['offset']}"
            )
        matches[0]["source"] = assertion["source"]

    totals = {
        "confirmedBindings": len(curated["confirmedIndirectBindings"]),
        "receiverWritesIndexed": len(write_index),
        "pilotApisChecked": len(pilot["matches"]) + len(pilot["noMatch"]),
        "pilotMatches": len(pilot["matches"]),
        "pilotNoMatch": len(pilot["noMatch"]),
    }
    add_sections(totals, curated["totalsExtras"])
    out = {
        **curated["metadata"],
        "receiverWriteIndex": write_index,
        "confirmedIndirectBindings": curated["confirmedIndirectBindings"],
        "pilotCrossRef": pilot,
        "recursiveCrossRef": recursive,
        "totals": totals,
    }
    add_sections(out, curated["relationshipFindings"])
    shared = json.loads(C2S_CURATED_JSON.read_text(encoding="utf-8"))[
        "outboundFindings"
    ]
    if "directEmissionMining" not in shared:
        raise ValueError("outbound findings lack the direct-emission projection")
    shared["directEmissionMining"] = curated["directEmissionMining"]
    add_sections(out, shared)
    add_sections(out, curated["payloadFindings"])
    return out


def write_curated(curated: dict) -> None:
    """Atomically replace the curated input while its catalog lock is held."""
    temporary = CURATED_JSON.with_name(CURATED_JSON.name + ".tmp")
    temporary.write_text(
        json.dumps(curated, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(CURATED_JSON)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--check",
        action="store_true",
        help="check the committed catalog without writing",
    )
    modes.add_argument(
        "--normalize-citations",
        action="store_true",
        help="normalize curated citation paths, then rebuild the catalog",
    )
    args = parser.parse_args()
    try:
        if args.normalize_citations:
            with catalog_lock(CURATED_JSON):
                curated = json.loads(CURATED_JSON.read_text(encoding="utf-8"))
                curated, changes = normalize_citations(curated)
                document = build_catalog(curated)
                if changes:
                    write_curated(curated)
                print(f"normalized {changes} curated citation strings")
        else:
            document = build_catalog()
        rendered = (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode(
            "utf-8"
        )
        if args.check:
            if not OUT_JSON.is_file() or OUT_JSON.read_bytes() != rendered:
                print(f"out of date: {OUT_JSON.name}", file=sys.stderr)
                return 1
            print(f"up to date: {OUT_JSON.name}")
        else:
            OUT_JSON.write_bytes(rendered)
            print(f"wrote {OUT_JSON}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
