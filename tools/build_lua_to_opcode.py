#!/usr/bin/env python3
"""Compose the Lua-name -> opcode bridge.

Joins four manifests into one queryable index:
    - manifests/lua_api_index.json              (Step 3 output)
    - manifests/receiver_opcode_map_inbound.json (Step 4a output)
    - manifests/operation_opcode_map_outbound.json (Step 4b scaffolding)

Join keys:
    luaName -> [bcsRef.slot] -> receiver(luaActorImplSlot) -> opcodes

Output: manifests/lua_to_opcode.json.

Schema:
    {
      version, gameVersion, sources,
      counts: { luaNames, withOpcodes, ... },
      bindings: {
        <luaName>: {
          opcodes: [{opcodeInt, opcodeHex, direction, receiverClass}],
          slots: [N],
          bcsRefs: [...]
        }
      },
      coverage: { gapLuaNamesNoOpcode, gapOpcodesNoLuaName }
    }

Run:
    python tools\\build_lua_to_opcode.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

SLOT_IN_SYMNAME_RE = re.compile(r"_slot(\d+)_", re.IGNORECASE)
SLOT_IN_NOTES_RE = re.compile(
    r"LuaActorImpl::vftable(?:\[(\d+)\]|\s+slot\s+(\d+))", re.IGNORECASE
)

REPO_ROOT = Path(__file__).resolve().parent.parent
LUA_INDEX_JSON = REPO_ROOT / "manifests" / "lua_api_index.json"
RECEIVER_JSON = REPO_ROOT / "manifests" / "receiver_opcode_map_inbound.json"
OPERATION_JSON = REPO_ROOT / "manifests" / "operation_opcode_map_outbound.json"
DATA_DEP_CATALOG_JSON = REPO_ROOT / "manifests" / "data_dependency_catalog.json"
APPLY_CHAIN_FIRERS_JSON = REPO_ROOT / "manifests" / "lua_apply_chain_firers.json"
OUT_JSON = REPO_ROOT / "manifests" / "lua_to_opcode.json"


def _load_json(p: Path, required: bool = True) -> dict | None:
    if not p.is_file():
        if required:
            print(f"error: {p} missing - run the prerequisite bridge step first", file=sys.stderr)
            sys.exit(1)
        return None
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def _infer_slot(receiver: dict, symbols_index: dict[str, dict]) -> int | None:
    """Infer the LuaActorImpl::vftable slot for a receiver.

    Tries in priority order:
      1. receiver.luaActorImplSlot (from client_receivers.json structured field)
      2. _slotN_ in any cross-referenced BCS-Y symbol NAME
      3. "LuaActorImpl::vftable slot N" in any cross-referenced BCS-Y NOTES
    """
    if receiver.get("luaActorImplSlot") is not None:
        return receiver["luaActorImplSlot"]
    bcs_refs = receiver.get("bcsRefs") or {}
    for role_entries in bcs_refs.values():
        for ref in role_entries:
            m = SLOT_IN_SYMNAME_RE.search(ref.get("symbolName", ""))
            if m:
                return int(m.group(1))
    for role_entries in bcs_refs.values():
        for ref in role_entries:
            sym = symbols_index.get(ref["bcsId"])
            if not sym:
                continue
            m = SLOT_IN_NOTES_RE.search(sym.get("notes", "") or "")
            if m:
                return int(m.group(1) or m.group(2))
    return None


def _build_slot_to_receiver(
    receiver_manifest: dict,
    symbols_index: dict[str, dict],
) -> dict[int, list[dict]]:
    """slot N -> [receiver entries with that LuaActorImpl slot]."""
    out: dict[int, list[dict]] = defaultdict(list)
    for r in receiver_manifest.get("inboundReceivers", []):
        slot = _infer_slot(r, symbols_index)
        if slot is not None:
            out[slot].append({
                "receiverClass": r["name"],
                "namespace": r.get("namespace"),
                "opcodes": r.get("opcodes", []),
                "luaCallback": r.get("luaCallback"),
                "confidence": r.get("confidence"),
                "inferredSlot": slot,
            })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="verify the committed output matches a fresh build")
    args = ap.parse_args()

    lua_index = _load_json(LUA_INDEX_JSON)
    receiver_map = _load_json(RECEIVER_JSON)
    operation_map = _load_json(OPERATION_JSON)
    symbols_manifest = _load_json(REPO_ROOT / "manifests" / "symbols.json")
    symbols_index = {s["id"]: s for s in symbols_manifest["symbols"]}

    slot_to_receiver = _build_slot_to_receiver(receiver_map, symbols_index)

    # Only LuaActorImpl refs contribute slots; other vftables use unrelated numbering.
    # Exclude BCS-Y-0238's paired slot 63: `_onUpdateDisplayName` fires from
    # slot 62's SetDisplayName 0x013d apply helper, not the native SendLog range.
    bindings: dict[str, dict] = {}
    for lua_name, refs in lua_index["apis"].items():
        observed_slots: set[int] = set()
        for ref in refs:
            slot = ref.get("slot")
            if slot is None:
                continue
            # Older indexes without source default to LuaActorImpl for compatibility.
            if ref.get("source", "name-luaactorimpl") != "name-luaactorimpl":
                continue
            sym = ref.get("symbolName", "") or ""
            if "_paired" in sym or "_secondary" in sym:
                continue
            observed_slots.add(slot)

        opcodes_bound: list[dict] = []
        receivers_bound: list[dict] = []
        for slot in sorted(observed_slots):
            for r in slot_to_receiver.get(slot, []):
                receivers_bound.append({
                    "receiverClass": r["receiverClass"],
                    "namespace": r["namespace"],
                    "slot": slot,
                    "confidence": r["confidence"],
                })
                for op in r["opcodes"]:
                    opcodes_bound.append({
                        "opcodeInt": op.get("opcodeInt"),
                        "opcodeHex": op.get("opcodeHex"),
                        "direction": "inbound",
                        "receiverClass": r["receiverClass"],
                        "slot": slot,
                    })

        bindings[lua_name] = {
            "luaName": lua_name,
            "bcsRefs": refs,
            "observedSlots": sorted(observed_slots),
            "opcodes": opcodes_bound,
            "receivers": receivers_bound,
            "applyChainBindings": [],
            "indirectBindings": [],
        }

    # Merge apply-chain firers and retain mechanism=apply_chain for consumers.
    apply_chain_firers_added = 0
    apply_chain_opcodes_set: set[int] = set()
    if APPLY_CHAIN_FIRERS_JSON.is_file():
        with APPLY_CHAIN_FIRERS_JSON.open(encoding="utf-8") as f:
            acf = json.load(f)
        for fr in acf.get("firers", []):
            lua = fr.get("luaName")
            if not lua:
                continue
            if lua not in bindings:
                bindings[lua] = {
                    "luaName": lua,
                    "bcsRefs": lua_index["apis"].get(lua, []),
                    "observedSlots": [],
                    "opcodes": [],
                    "receivers": [],
                    "applyChainBindings": [],
                    "indirectBindings": [],
                }
            entry = {
                "mechanism": "apply_chain",
                "bindingFlavor": fr.get("bindingFlavor", "direct"),
                "opcodeInt": fr.get("opcodeInt"),
                "opcodeHex": fr.get("opcodeHex"),
                "direction": "inbound",
                "receiverClass": fr.get("receiverClass"),
                "applyHelperVa": fr.get("applyHelperVa"),
                "fireSite": fr.get("fireSite"),
                "evidenceBcsy": fr.get("evidenceBcsy"),
                "evidenceFile": fr.get("evidenceFile"),
            }
            bindings[lua]["applyChainBindings"].append(entry)
            # Include apply-chain firers in opcodes while retaining the mechanism flag.
            already_in_opcodes = any(
                op.get("opcodeInt") == entry["opcodeInt"]
                and op.get("receiverClass") == entry["receiverClass"]
                for op in bindings[lua]["opcodes"]
            )
            if not already_in_opcodes:
                bindings[lua]["opcodes"].append({
                    "opcodeInt": entry["opcodeInt"],
                    "opcodeHex": entry["opcodeHex"],
                    "direction": "inbound",
                    "receiverClass": entry["receiverClass"],
                    "mechanism": "apply_chain",
                    "bindingFlavor": entry["bindingFlavor"],
                })
            apply_chain_firers_added += 1
            if entry["opcodeInt"] is not None:
                apply_chain_opcodes_set.add(entry["opcodeInt"])

    # Indirect bindings pair Lua readers with inbound writers through shared actor state.
    # BCS-Y-0338/0341/0342/0343 record the evidence.
    indirect_bindings_added = 0
    indirect_opcodes_set: set[int] = set()
    if DATA_DEP_CATALOG_JSON.is_file():
        with DATA_DEP_CATALOG_JSON.open(encoding="utf-8") as f:
            dd = json.load(f)
        for ib in dd.get("confirmedIndirectBindings", []):
            lua = ib.get("luaName")
            if not lua or lua not in bindings:
                continue
            receivers = ib.get("writingReceivers") or [ib.get("writingReceiver")]
            opcodes = ib.get("writingOpcodes") or [ib.get("writingOpcode")]
            receivers = [r for r in receivers if r]
            opcodes = [o for o in opcodes if o]
            for i, (recv, op_hex) in enumerate(zip(receivers, opcodes)):
                try:
                    op_int = int(op_hex, 16)
                except (ValueError, TypeError):
                    op_int = None
                bindings[lua]["indirectBindings"].append({
                    "mechanism": ib.get("mechanism", "data_dependency"),
                    "opcodeInt": op_int,
                    "opcodeHex": op_hex.lower() if isinstance(op_hex, str) else None,
                    "direction": "inbound",
                    "receiverClass": recv,
                    "sharedField": {
                        "actorClass": ib.get("readActorClass"),
                        "offsets": ib.get("readsOffsets", []),
                    },
                    "writerBcsy": ib.get("writingReceiverBcsy"),
                    "luaApiBcsy": ib.get("luaApiBcsy"),
                    "luaApiImplVa": ib.get("luaApiImplVa"),
                    "confidence": ib.get("confidence", "confirmed"),
                    "evidence": ib.get("evidence"),
                })
                indirect_bindings_added += 1
                if op_int is not None:
                    indirect_opcodes_set.add(op_int)

    lua_with_opcode = sum(1 for b in bindings.values() if b["opcodes"])
    lua_with_slot_based = sum(
        1 for b in bindings.values()
        if any(op.get("mechanism") != "apply_chain" for op in b["opcodes"])
    )
    lua_with_apply_chain = sum(
        1 for b in bindings.values() if b.get("applyChainBindings")
    )
    lua_with_deferred_apply_chain = sum(
        1 for b in bindings.values()
        if any(e.get("bindingFlavor") == "deferred_via_event_condition"
               for e in b.get("applyChainBindings", []))
    )
    lua_with_indirect = sum(
        1 for b in bindings.values() if b.get("indirectBindings")
    )
    lua_with_slot_but_no_receiver = sum(
        1 for b in bindings.values()
        if b["observedSlots"] and not b["receivers"]
    )

    # Track inbound opcodes with no direct or indirect Lua binding.
    opcoded_lua: set[tuple[str, int]] = set()
    for b in bindings.values():
        for op in b["opcodes"]:
            if op["opcodeHex"]:
                opcoded_lua.add(("inbound", op["opcodeInt"]))
    all_inbound_opcodes: set[int] = set()
    for r in receiver_map.get("inboundReceivers", []):
        for op in r.get("opcodes", []):
            if op.get("opcodeInt") is not None:
                all_inbound_opcodes.add(op["opcodeInt"])
    bound_inbound_opcodes = {oi for d, oi in opcoded_lua if d == "inbound"}
    gap_direct = sorted(all_inbound_opcodes - bound_inbound_opcodes)
    indirect_resolved_gap = sorted(
        op for op in gap_direct if op in indirect_opcodes_set
    )
    gap_inbound_opcodes = sorted(
        all_inbound_opcodes - bound_inbound_opcodes - indirect_opcodes_set
    )

    out = {
        "version": "1",
        "gameVersion": lua_index.get("gameVersion", "1.23b"),
        "sources": [
            "manifests/lua_api_index.json",
            "manifests/receiver_opcode_map_inbound.json",
            "manifests/operation_opcode_map_outbound.json",
            "manifests/lua_apply_chain_firers.json (apply-chain firers)",
            "manifests/data_dependency_catalog.json (indirect bindings)",
        ],
        "counts": {
            "luaNamesIndexed": len(bindings),
            "luaNamesWithOpcode": lua_with_opcode,
            "luaNamesWithSlotBasedBinding": lua_with_slot_based,
            "luaNamesWithApplyChainBinding": lua_with_apply_chain,
            "luaNamesWithDeferredApplyChainBinding": lua_with_deferred_apply_chain,
            "luaNamesWithIndirectBinding": lua_with_indirect,
            "luaNamesWithSlotButNoReceiver": lua_with_slot_but_no_receiver,
            "inboundOpcodesTotal": len(all_inbound_opcodes),
            "inboundOpcodesWithLuaName": len(bound_inbound_opcodes),
            "inboundOpcodesIndirectlyResolved": len(indirect_resolved_gap),
            "inboundOpcodesGap": len(gap_inbound_opcodes),
            "serverboundGap": operation_map.get("totals", {}).get("serverboundGap"),
            "applyChainFirersAdded": apply_chain_firers_added,
            "indirectBindingsAdded": indirect_bindings_added,
        },
        "bindings": dict(sorted(bindings.items())),
        "gaps": {
            "inboundOpcodesNoLuaName": [f"0x{op:04x}" for op in gap_inbound_opcodes],
            "inboundOpcodesIndirectlyResolved": [
                f"0x{op:04x}" for op in indirect_resolved_gap
            ],
        },
    }

    rendered = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUT_JSON.is_file() or OUT_JSON.read_text(encoding="utf-8") != rendered:
            print(f"error: {OUT_JSON.name} does not match a fresh build", file=sys.stderr)
            return 1
        print(f"OK: {OUT_JSON.name} matches a fresh build")
        return 0

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(rendered, encoding="utf-8", newline="")

    print(f"wrote {OUT_JSON}")
    print(f"  luaNamesIndexed:                {out['counts']['luaNamesIndexed']}")
    print(f"  luaNamesWithOpcode:             {out['counts']['luaNamesWithOpcode']}")
    print(f"  luaNamesWithSlotBasedBinding:   {out['counts']['luaNamesWithSlotBasedBinding']}")
    print(f"  luaNamesWithApplyChainBinding:  {out['counts']['luaNamesWithApplyChainBinding']}")
    print(f"  luaNamesWithDeferredApplyChain: {out['counts']['luaNamesWithDeferredApplyChainBinding']}")
    print(f"  luaNamesWithIndirectBinding:    {out['counts']['luaNamesWithIndirectBinding']}")
    print(f"  luaNamesWithSlotNoReceiver:     {out['counts']['luaNamesWithSlotButNoReceiver']}")
    print(f"  inboundOpcodesTotal:            {out['counts']['inboundOpcodesTotal']}")
    print(f"  inboundOpcodesWithLuaName:      {out['counts']['inboundOpcodesWithLuaName']}")
    print(f"  inboundOpcodesIndirRez:         {out['counts']['inboundOpcodesIndirectlyResolved']}")
    print(f"  inboundOpcodesGap:              {out['counts']['inboundOpcodesGap']}")
    print(f"  applyChainFirersAdded:          {out['counts']['applyChainFirersAdded']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
