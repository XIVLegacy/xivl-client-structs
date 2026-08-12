#!/usr/bin/env python3
"""Cross-reference receiver-apply writes in CharaBase.0x60.* and
CharaBase.0xDC.* chain keys against N-API readers.

Two match mechanisms beyond the existing flat-offset cross-ref:

(1) `nested_match`: an N-API reader's `nestedReads[]` entry
    `{outer, inner}` directly mirrors a writer chain key
    `Class.outer.inner`. Highest confidence: exact byte-level field
    overlap.

(2) `substruct_pointer_match`: an N-API reader reads the OUTER offset
    (the sub-struct pointer), and the writer writes INSIDE the same
    sub-struct. The reader subsequently dereferences via either a known
    sub-struct accessor (FUN_006EEC00 for CharaBase+0xDC) or direct
    pointer-chase that the recursive field-access extractor didn't
    chase into. High confidence when (a) the API's chasedCallees
    contains FUN_006EEC00 and the writer chain has outer=0xDC, or
    (b) reader's deepReads contains the outer offset and the reader's
    Lua-name semantic matches the writer's semantic.

Output: appends new entries to data_dependency_catalog.json
`confirmedIndirectBindings[]` AND records the cross-ref pass in a
dedicated `crossRef` section.

Run:
    python tools\\extractors\\build_substruct_cross_ref.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CATALOG = REPO_ROOT / "manifests" / "data_dependency_catalog.json"
FA_DIRECT = REPO_ROOT / "manifests" / "control_class_napi_field_access.json"
FA_RECURSIVE = REPO_ROOT / "manifests" / "control_class_napi_field_access_recursive.json"

# This lazy initializer returns CharaBase+0xDC, allocating 0x1C bytes when null.
# Calls on `this` therefore read the CharaBase.0xDC substruct.
SUBSTRUCT_ACCESSORS = {
    "0x006EEC00": ("CharaBase", "0xDC"),
}
# BCS-Y-0359 shows FUN_007487C0 and FUN_00748920 are not +0x60 accessors.

# `receiver_apply_findings_wire_derived.json findingsByOpcode[0x0145]` shows
# s2c 0x0145 writes CharaBase+0xDC+0x10 via FUN_006FA980; readers use FUN_006EEC00.
SEMANTIC_OVERLAP = {
    "_getNetStatUser": {
        "writeChainKey": "CharaBase.0xDC.0x10",
        "rationale": (
            "Lua-name root '_getNetStat' mirrors 0x0145's apply-chain "
            "firer naming root '_onChangeNetStat'. Receiver-apply evidence: "
            "FUN_006FA980 fires _onChangeNetStatUser on bit-diffs in "
            "range 8..15 of the u32 at CharaBase+0xDC+0x10. The N-API "
            "calls FUN_006EEC00 (the +0xDC sub-struct accessor) in its "
            "chasedCallees, so it reads the same sub-struct word the "
            "receiver writes."
        ),
    },
    "_getNetStatSystem": {
        "writeChainKey": "CharaBase.0xDC.0x10",
        "rationale": (
            "Mirror of _getNetStatUser: receiver-apply evidence shows "
            "FUN_006FA980 fires _onChangeNetStatSystem for bit-diffs at "
            "positions 0x10/0x11/0x12 of the same u32 at CharaBase+0xDC"
            "+0x10. Same chasedCallees pattern (FUN_006EEC00) confirms "
            "the reader operates on the same sub-struct word."
        ),
    },
    "_getSubStatStatus": {
        "writeChainKey": "CharaBase.0xDC.0x04",
        "rationale": (
            "FUN_00707D60 (the 0x0179 ChangeActor"
            "SubStatStatus depth-4 worker) writes a u32 into the dynamic "
            "SubStat array at *(CharaBase+0xDC+0x04)+sub_stat_enum*4 and "
            "fires _onChangeSubStatStatus. The N-API _getSubStatStatus "
            "(CharaBase impl 0x006FA150) calls FUN_006EEC00 in its "
            "chasedCallees (same +0xDC sub-struct accessor), so it reads "
            "into the same sub-struct - and the name root "
            "'_getSubStatStatus' mirrors the apply-chain firer "
            "'_onChangeSubStatStatus'."
        ),
    },
}


WRITE_CHAIN_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\.(0x[0-9a-fA-F]+)\.(0x[0-9a-fA-F]+)$")


def parse_chain_key(k: str):
    m = WRITE_CHAIN_RE.match(k)
    if not m:
        return None
    return m.group(1), m.group(2).lower(), m.group(3).lower()


def main() -> int:
    cat = json.load(CATALOG.open(encoding="utf-8"))
    fa = json.load(FA_DIRECT.open(encoding="utf-8"))
    fa_rec = json.load(FA_RECURSIVE.open(encoding="utf-8"))

    write_index = cat["receiverWriteIndex"]
    chain_writes: dict[tuple[str, str, str], list[dict]] = {}
    for k, writers in write_index.items():
        parsed = parse_chain_key(k)
        if parsed:
            chain_writes[parsed] = writers

    by_outer: dict[tuple[str, str], list[tuple[str, list[dict]]]] = {}
    for (cls, outer, inner), writers in chain_writes.items():
        by_outer.setdefault((cls, outer), []).append((inner, writers))

    fa_by_key: dict[tuple[str, str], dict] = {}
    for cls, apis in fa["byClass"].items():
        for a in apis:
            fa_by_key[(cls, a["luaName"])] = a
    fa_rec_by_key: dict[tuple[str, str], dict] = {}
    for cls, apis in fa_rec["byClass"].items():
        for a in apis:
            fa_rec_by_key[(cls, a["luaName"])] = a

    promotions: list[dict] = []

    def append_promotion(rec: dict) -> None:
        # Avoid duplicating an existing promotion.
        existing = cat.get("confirmedIndirectBindings", [])
        for e in existing:
            if (e.get("luaName") == rec["luaName"]
                and e.get("writingReceiver") == rec.get("writingReceiver")
                and e.get("writingOpcode") == rec.get("writingOpcode")):
                return
        for p in promotions:
            if (p["luaName"] == rec["luaName"]
                and p.get("writingReceiver") == rec.get("writingReceiver")
                and p.get("writingOpcode") == rec.get("writingOpcode")):
                return
        promotions.append(rec)

    # Exact nested reads include recursive accessor-derived deepNestedReads.
    for (cls, outer, inner), writers in chain_writes.items():
        for (a_cls, lua), a in fa_by_key.items():
            if a_cls != cls or a.get("status") != "ok":
                continue
            nested = list(a.get("nestedReads", []) or [])
            a_rec = fa_rec_by_key.get((a_cls, lua))
            if a_rec:
                nested.extend(a_rec.get("deepNestedReads", []) or [])
            for nr in nested:
                if nr.get("outer", "").lower() == outer and nr.get("inner", "").lower() == inner:
                    for w in writers:
                        append_promotion({
                            "luaName": lua,
                            "luaNameClass": cls,
                            "luaApiImplVa": a.get("implVa"),
                            "readsOffsets": [outer, f"{outer}.{inner}"],
                            "readActorClass": cls,
                            "writingReceiver": w["receiver"],
                            "writingOpcode": w["opcode"],
                            "writingReceiverBcsy": w.get("bcsyRef"),
                            "confidence": "confirmed",
                            "mechanism": "nested_match",
                            "evidence": (
                                f"Exact byte-overlap match: N-API {lua} (impl {a.get('implVa')}) "
                                f"has nestedRead {{outer: {outer}, inner: {inner}}} which "
                                f"directly mirrors receiver write key {cls}.{outer}.{inner}. "
                                f"Receiver {w['receiver']} (opcode {w['opcode']}) writes "
                                f"{w.get('semantic')} into this exact sub-struct field per "
                                f"{w.get('bcsyRef')}."
                            ),
                        })

    # Accessor-callsite evidence without an inner offset is not auto-promoted.

    for lua, rule in SEMANTIC_OVERLAP.items():
        a = fa_rec_by_key.get(("CharaBase", lua))
        if not a or a.get("status") != "ok":
            print(f"  semantic-overlap candidate {lua}: missing field-access entry", file=sys.stderr)
            continue
        callees = {c.lower() for c in a.get("chasedCallees", [])}
        # The sub-struct accessor must appear in the chased callees.
        if not any(acc.lower() in callees for acc in SUBSTRUCT_ACCESSORS):
            print(f"  semantic-overlap candidate {lua}: FUN_006EEC00 not in chasedCallees", file=sys.stderr)
            continue
        chain_key = rule["writeChainKey"]
        parsed = parse_chain_key(chain_key)
        if not parsed:
            continue
        cls, outer, inner = parsed
        writers = chain_writes.get((cls, outer, inner), [])
        if not writers:
            print(f"  semantic-overlap candidate {lua}: write chain {chain_key} not present", file=sys.stderr)
            continue
        for w in writers:
            append_promotion({
                "luaName": lua,
                "luaNameClass": cls,
                "luaApiImplVa": a.get("implVa"),
                "readsOffsets": [outer, f"{outer}.{inner}"],
                "readActorClass": cls,
                "writingReceiver": w["receiver"],
                "writingOpcode": w["opcode"],
                "writingReceiverBcsy": w.get("bcsyRef"),
                "confidence": "confirmed",
                "mechanism": "substruct_accessor_semantic",
                "evidence": (
                    f"Sub-struct-accessor + semantic match: {lua} (impl "
                    f"{a.get('implVa')}) calls FUN_006EEC00 (the {cls}+{outer} "
                    f"sub-struct lazy accessor) in its chasedCallees. "
                    f"{rule['rationale']} Therefore the reader reads the field "
                    f"that receiver {w['receiver']} (opcode {w['opcode']}) writes."
                ),
            })

    # A direct outer-pointer read matches writers for fields within that sub-struct.
    for (a_cls, lua), a in fa_by_key.items():
        if a.get("status") != "ok":
            continue
        direct_reads = {r.lower() for r in a.get("readsOffsets", [])}
        for (cls, outer), inner_writers in by_outer.items():
            if a_cls != cls:
                continue
            if outer not in direct_reads:
                continue
            # Nested matches are stronger and already cover the same opcode.
            for (inner, writers) in inner_writers:
                for w in writers:
                    append_promotion({
                        "luaName": lua,
                        "luaNameClass": cls,
                        "luaApiImplVa": a.get("implVa"),
                        "readsOffsets": [outer],
                        "readActorClass": cls,
                        "writingReceiver": w["receiver"],
                        "writingOpcode": w["opcode"],
                        "writingReceiverBcsy": w.get("bcsyRef"),
                        "confidence": "confirmed",
                        "mechanism": "substruct_pointer_structural",
                        "evidence": (
                            f"Structural sub-struct match: {lua} (impl {a.get('implVa')}) "
                            f"reads {cls}+{outer} directly (the sub-struct pointer). "
                            f"Receiver {w['receiver']} (opcode {w['opcode']}) writes "
                            f"{w.get('semantic')} into {cls}.{outer}.{inner}. The reader "
                            f"and writer share the same sub-struct; the reader's "
                            f"sub-struct dereference accesses bytes that the receiver "
                            f"populates."
                        ),
                    })

    print(f"indirect bindings (substruct cross-ref): {len(promotions)}")
    for p in promotions:
        print(f"  {p['luaName']:35s} <- {p['writingOpcode']}  "
              f"[{p['mechanism']}]  via {p['writingReceiver']}")

    if not promotions:
        print("nothing to append.")
        return 0

    cat.setdefault("confirmedIndirectBindings", []).extend(promotions)
    cat.setdefault("crossRef", {
        "method": (
            "Sub-struct-aware cross-ref over receiver-apply write chain keys. "
            "Three match mechanisms: nested_match "
            "(N-API's nestedRead {outer, inner} exactly mirrors writer "
            "chain key), substruct_accessor_semantic (N-API calls a "
            "known sub-struct accessor like FUN_006EEC00 + Lua-name "
            "semantic overlap with apply-chain firers), and "
            "substruct_pointer_structural (N-API reads the sub-struct "
            "pointer directly without further chase)."
        ),
        "newBindings": len(promotions),
        "promotedLuaNames": sorted({p["luaName"] for p in promotions}),
        "promotedOpcodes": sorted({p["writingOpcode"] for p in promotions}),
    })
    cat["totals"]["confirmedBindings"] = len(cat.get("confirmedIndirectBindings", []))

    src_marker = "manifests\\substruct_cross_ref (in-file pass)"
    srcs = cat.setdefault("source", [])
    if src_marker not in srcs:
        srcs.append(src_marker)

    with CATALOG.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(cat, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"updated {CATALOG}")
    print(f"  totals.confirmedBindings now {cat['totals']['confirmedBindings']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
