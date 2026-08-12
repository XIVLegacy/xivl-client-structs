#!/usr/bin/env python3
"""Cross-ref: build the data-dependency catalog from existing
BCS-Y receiver field-write evidence + control_class_napi_field_access.json's
field-read evidence. Each match (opcode X writes field Y) x (Lua API Z reads
field Y) = one indirect opcode binding.

For the pilot pass, we seed the catalog from BCS-Y-0278 (which documents the
11 PURE-NATIVE inbound receiver apply VAs and the specific actor-state field
offsets each writes). Cross-ref against the 206 N-API map.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from _regen_guard import add_force_arg, check_regen_safe  # noqa: E402
NAPI_MAP = REPO_ROOT / "manifests" / "control_class_napi_map.json"
NAPI_FIELD_ACCESS = REPO_ROOT / "manifests" / "control_class_napi_field_access.json"
NAPI_FIELD_ACCESS_RECURSIVE = REPO_ROOT / "manifests" / "control_class_napi_field_access_recursive.json"
VTABLE_RESOLVED_EVIDENCE = REPO_ROOT / "manifests" / "vtable_resolved_evidence.json"
RECEIVER_FIELD_WRITES = REPO_ROOT / "manifests" / "receiver_field_writes.json"
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


# BCS-Y-0278 is hand-curated because its offsets/types are documented in prose; other writes are extracted from receiver_field_writes.json.
PURE_NATIVE_RECEIVER_WRITES = [
    {
        "receiver": "HateStatusReceiver",
        "opcode": "0x0195",
        "bcsyRef": "BCS-Y-0278",
        "writes": [
            {"actorClass": "NpcBase", "offset": "0x154", "type": "u32",
             "semantic": "enmity amount"},
            {"actorClass": "NpcBase", "offset": "0x158", "type": "u16",
             "semantic": "enmity kind"},
        ],
        "applyVa": "0x0089D030",
    },
    {
        "receiver": "ChangeShadowActorFlagReceiver",
        "opcode": "0x017B",
        "bcsyRef": "BCS-Y-0278",
        "writes": [
            {"actorClass": "CharaBase", "offset": "0x5D", "type": "u8",
             "semantic": "shadow-actor flag"},
        ],
        "applyVa": "0x0089CC70",
    },
    {
        "receiver": "KickClientOrderEventReceiver",
        "opcode": "0x012F",
        "bcsyRef": "BCS-Y-0278",
        "writes": [
            {"actorClass": "param_2", "offset": "0x0", "type": "u8",
             "semantic": "kick result byte (not actor field)"},
        ],
        "applyVa": "0x0089E450",
        "note": "writes to packet result buffer, not actor state",
    },
]


def build_receiver_writes() -> list[dict]:
    """Merge BCS-Y-0278's curated PURE-NATIVE writes with the auto-extracted
    writes for the other 26 receivers."""
    out = list(PURE_NATIVE_RECEIVER_WRITES)
    receiver_classification = json.load(RECEIVER_FIELD_WRITES.open(encoding="utf-8"))
    for r in receiver_classification["perReceiver"]:
        if not r["unifiedWrites"]:
            continue
        if not r.get("castTarget"):
            continue
        out.append({
            "receiver": r["receiverName"],
            "opcode": r["opcodeHex"],
            "bcsyRef": "receiver_classification",
            "writes": [
                {"actorClass": r["castTarget"], "offset": o, "type": "?",
                 "semantic": f"auto-extracted from {r['slot1Va']}+workers"}
                for o in r["unifiedWrites"]
            ],
            "applyVa": r["slot1Va"],
            "kind": r["kind"],
            "workers": r["workers"],
        })
    # GrandCompanyReceiver resolves through PlayerBase::vftable[0xA4] to FUN_006DEB00, which writes PlayerBase+0xED-0xF0.
    out.append({
        "receiver": "GrandCompanyReceiver",
        "opcode": "0x0194",
        "bcsyRef": "src-12f",
        "writes": [
            {"actorClass": "PlayerBase", "offset": "0xed", "type": "u8",
             "semantic": "grand-company rank cluster byte 0 (vtable[0xa4]->FUN_006DEB00)"},
            {"actorClass": "PlayerBase", "offset": "0xee", "type": "u8",
             "semantic": "grand-company rank cluster byte 1"},
            {"actorClass": "PlayerBase", "offset": "0xef", "type": "u8",
             "semantic": "grand-company rank cluster byte 2"},
            {"actorClass": "PlayerBase", "offset": "0xf0", "type": "u8",
             "semantic": "grand-company rank cluster byte 3"},
        ],
        "applyVa": "0x0089CD60",
        "kind": "trivial_with_vtable_dispatch",
        "vtableTarget": "0x006DEB00",
    })
    return out


KNOWN_INDIRECT_BINDINGS = [
    {
        "luaName": "_isEnmity",
        "luaNameClass": "NpcBase",
        "luaApiBcsy": "BCS-Y-0212",
        "luaApiRegistrationVa": "0x00750A70",
        "readsOffsets": ["0x154", "0x158"],
        "readActorClass": "NpcBase",
        "writingReceiver": "HateStatusReceiver",
        "writingOpcode": "0x0195",
        "writingReceiverBcsy": "BCS-Y-0278",
        "confidence": "confirmed",
        "evidence": (
            "BCS-Y-0278 documents HateStatusReceiver's apply method FUN_0089D030 "
            "performs PURE-NATIVE memory writes of NpcBase+0x154 (enmity amount u32) "
            "and NpcBase+0x158 (enmity kind u16). BCS-Y-0212 catalogs _isEnmity as "
            "an NpcBase vftable[2] 8-API entry (registration at 0x00750A70). The "
            "_isEnmity impl reads the same NpcBase+0x154/+0x158 fields (per "
            "BCS-Y-0278's example narrative). This is the canonical indirect "
            "binding mechanism the data-dependency catalog tracks."
        ),
    },
    {
        "luaName": "_getBelongGrandCompany",
        "luaNameClass": "PlayerBase",
        "luaApiImplVa": "0x00706CC0",
        "readsOffsets": ["0xed"],
        "readActorClass": "PlayerBase",
        "writingReceiver": "GrandCompanyReceiver",
        "writingOpcode": "0x0194",
        "writingReceiverBcsy": "src-12f",
        "confidence": "confirmed",
        "evidence": (
            "Vtable resolution: GrandCompanyReceiver's slot1Fn "
            "FUN_0089CD60 performs a virtual call PlayerBase::vftable[0xA4] "
            "which resolves to FUN_006DEB00 (43B body) writing param_1+0xED..0xF0 "
            "(4 consecutive bytes). _getBelongGrandCompany (PlayerBase N-API "
            "impl 0x00706CC0) reads PlayerBase+0xED directly. Match was found "
            "by the auto cross-ref (pilot matches: direct/exact) after adding "
            "GrandCompany's vtable-resolved writes to receiver_field_writes."
        ),
    },
    {
        "luaName": "_getChocoboRidingGrade",
        "luaNameClass": "PlayerBase",
        "luaApiImplVa": "0x0071E4D0",
        "readsOffsets": ["0x15d"],
        "readActorClass": "PlayerBase",
        "writingReceivers": ["GoobbueReceiver", "ChocoboReceiver"],
        "writingOpcodes": ["0x01a0", "0x0198"],
        "writingReceiverBcsy": "receiver_classification",
        "confidence": "confirmed",
        "evidence": (
            "Vtable resolution: _getChocoboRidingGrade is an N-API "
            "impl (0x0071E4D0) that's also reached as a PlayerBase virtual "
            "method. Direct decomp shows it reads param_1+0x15D and writes "
            "param_1+0x15F. GoobbueReceiver (opcode 0x01a0) writes MyPlayer"
            "+0x15D and 0x15F (per the auto-extracted receiver writes); ChocoboReceiver (opcode 0x0198) "
            "writes MyPlayer+0x158/+0x15C/+0x15D/+0x15F. Match is hierarchy "
            "(PlayerBase API on MyPlayer-derived object via runtime dispatch)."
        ),
    },
    {
        "luaName": "_isEnabledGoobbue",
        "luaNameClass": "PlayerBase",
        "luaApiImplVa": "0x0071E4E0",
        "readsOffsets": ["0x160"],
        "readActorClass": "PlayerBase",
        "writingReceiver": "VehicleGradeReceiver",
        "writingOpcode": "0x01a1",
        "writingReceiverBcsy": "receiver_classification",
        "confidence": "confirmed",
        "evidence": (
            "Vtable resolution: _isEnabledGoobbue (PlayerBase N-API "
            "impl 0x0071E4E0) reads param_1+0x160. VehicleGradeReceiver (opcode "
            "0x01a1) writes MyPlayer+0x160 (per the auto-extracted receiver writes). Match is hierarchy "
            "(PlayerBase API on MyPlayer-derived object)."
        ),
    },
    {
        "luaName": "_getJob",
        "luaNameClass": "CharaBase",
        "luaApiImplVa": "0x0071E020",
        "readsOffsets": ["0xf1"],
        "readActorClass": "PlayerBase",
        "writingReceiver": "JobChangeReceiver",
        "writingOpcode": "0x01a4",
        "writingReceiverBcsy": "receiver_classification",
        "confidence": "confirmed",
        "evidence": (
            "Vtable resolution + hierarchy preference fix: _getJob "
            "is a CharaBase N-API (impl 0x0071E020) that calls "
            "CharaBase::vftable[0x9c]. CharaBase's slot is FUN_00776340 (small), "
            "but PlayerBase override at the same slot is FUN_00706D90 (37B, "
            "reads param_1+0xF1). JobChangeReceiver (opcode 0x01A4) writes "
            "PlayerBase+0xF1 (per the auto-extracted receiver writes). Found by widening the "
            "hierarchy preference to include PlayerBase override for CharaBase "
            "casts (originally only MyPlayer was preferred)."
        ),
    },
    {
        "luaName": "_getLookAtCharacter",
        "luaNameClass": "CharaBase",
        "luaApiImplVa": "0x006FA690",
        "readsOffsets": ["0x154"],
        "readActorClass": "NpcBase",
        "writingReceiver": "HateStatusReceiver",
        "writingOpcode": "0x0195",
        "writingReceiverBcsy": "BCS-Y-0278",
        "confidence": "confirmed",
        "evidence": (
            "Vtable resolution: _getLookAtCharacter (CharaBase N-API "
            "impl 0x006FA690) calls CharaBase::vftable[0xA0]. CharaBase's slot "
            "is FUN_0071E030 (1-liner, returns constant); NpcBase override is "
            "FUN_0072D000 (4-line copy-out reading param_1+0x154). "
            "HateStatusReceiver (opcode 0x0195) writes NpcBase+0x154 per "
            "BCS-Y-0278. When the runtime actor is an NPC, _getLookAtCharacter "
            "returns the NPC's hate-target slot - this is a 2nd reader of "
            "NpcBase+0x154 alongside _isEnmity (BCS-Y-0338). Semantic "
            "interpretation: NPCs reuse the look-at-character slot for "
            "current-hate-target tracking."
        ),
    },
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_force_arg(ap)
    ap.add_argument(
        "--normalize-citations", action="store_true",
        help="update moved sibling citation paths while preserving accumulated blocks",
    )
    args = ap.parse_args()

    if args.normalize_citations:
        existing = json.load(OUT_JSON.open(encoding="utf-8"))
        updated, changes = normalize_citations(existing)
        with OUT_JSON.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(updated, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"updated {changes} citation strings in {OUT_JSON}")
        return 0

    fa = json.load(NAPI_FIELD_ACCESS.open(encoding="utf-8"))
    fa_recursive = json.load(NAPI_FIELD_ACCESS_RECURSIVE.open(encoding="utf-8"))
    receiver_writes = build_receiver_writes()

    write_offset_to_receivers: dict[str, list[dict]] = {}
    for r in receiver_writes:
        for w in r["writes"]:
            key = (w["actorClass"], w["offset"].lower())
            write_offset_to_receivers.setdefault(key, []).append({
                "receiver": r["receiver"],
                "opcode": r["opcode"],
                "bcsyRef": r["bcsyRef"],
                "semantic": w["semantic"],
                "type": w["type"],
            })

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
                out.append({
                    "offset": off,
                    "matchKind": "exact",
                    "receivers": exact,
                })
                continue
            relaxed = offset_only_to_writers.get(off, [])
            compatible = []
            for w in relaxed:
                if w.get("writerActorClass") in HIERARCHY.get(cls_name, set()) or \
                   cls_name in HIERARCHY.get(w.get("writerActorClass", ""), set()):
                    compatible.append(w)
            if compatible:
                out.append({
                    "offset": off,
                    "matchKind": "hierarchy",
                    "receivers": compatible,
                })
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
                pilot_matches.append({
                    "luaName": api["luaName"],
                    "luaClass": cls_name,
                    "implVa": api.get("implVa"),
                    "matches": api_matches,
                })
            else:
                pilot_no_match.append({
                    "luaName": api["luaName"],
                    "luaClass": cls_name,
                    "implVa": api.get("implVa"),
                    "readsOffsets": api.get("readsOffsets", []),
                    "writesOffsets": api.get("writesOffsets", []),
                })

    vtable_evidence: dict[str, dict] = {}
    if VTABLE_RESOLVED_EVIDENCE.exists():
        ve = json.load(VTABLE_RESOLVED_EVIDENCE.open(encoding="utf-8"))
        for e in ve.get("perImplEvidence", []):
            vtable_evidence[e["implVa"]] = {
                "reads": [o.lower() for o in e.get("derivedReads", [])],
                "writes": [o.lower() for o in e.get("derivedWrites", [])],
                "nested": [
                    {"inner": r["inner"].lower()}
                    for r in e.get("derivedNested", [])
                ],
            }

    recursive_matches: list[dict] = []
    for cls_name, apis in fa_recursive["byClass"].items():
        for api in apis:
            if api.get("status") != "ok":
                continue
            deep_reads = [o.lower() for o in api.get("deepReads", [])]
            deep_nested = [
                r["inner"].lower() for r in api.get("deepNestedReads", [])
            ]
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
                recursive_matches.append({
                    "luaName": api["luaName"],
                    "luaClass": cls_name,
                    "implVa": api.get("implVa"),
                    "chasedCallees": api.get("chasedCallees", []),
                    "matches": api_matches,
                })

    out = {
        "version": "1",
        "gameVersion": "1.23b",
        "source": [
            "manifests\\control_class_napi_map.json",
            "manifests\\control_class_napi_field_access.json",
            "manifests\\symbols.json (BCS-Y-0278, BCS-Y-0210/0211/0212/0208)",
        ],
        "description": (
            "Indirect opcode -> Lua API bindings via shared actor-state fields. "
            "For each known {receiver writes field, API reads field} pair, "
            "the receiver's opcode indirectly drives the API's data domain. "
            "Pilot scope: BCS-Y-0278's 11 PURE-NATIVE receivers + the 14 "
            "successfully-decomped N-API impls from the pilot cross-ref "
            "(DirectorBase + NpcBase). Next: scale "
            "receiver-write evidence to all 38 receivers (need apply-method "
            "decomp pass), scale N-API impl decomp to all 206 entries."
        ),
        "receiverWriteIndex": {
            f"{cls}.{off}": writers
            for (cls, off), writers in write_offset_to_receivers.items()
        },
        "confirmedIndirectBindings": KNOWN_INDIRECT_BINDINGS,
        "pilotCrossRef": {
            "matches": pilot_matches,
            "noMatch": pilot_no_match,
        },
        "recursiveCrossRef": {
            "matches": recursive_matches,
        },
        "totals": {
            "confirmedBindings": len(KNOWN_INDIRECT_BINDINGS),
            "receiverWritesIndexed": sum(
                len(w) for w in write_offset_to_receivers.values()
            ),
            "pilotApisChecked": len(pilot_matches) + len(pilot_no_match),
            "pilotMatches": len(pilot_matches),
            "pilotNoMatch": len(pilot_no_match),
        },
    }

    if not check_regen_safe(OUT_JSON, out, args.force):
        return 1

    with OUT_JSON.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {OUT_JSON}")
    print(f"  confirmed indirect bindings: {len(KNOWN_INDIRECT_BINDINGS)}")
    print(f"  pilot matches (direct only): {len(pilot_matches)}")
    print(f"  recursive matches (direct + 1-level chase): {len(recursive_matches)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
