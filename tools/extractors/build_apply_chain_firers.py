#!/usr/bin/env python3
"""Extract apply-chain Lua firers from
manifests/receiver_apply_findings_wire_derived.json into a dedicated bridge
ingest file at manifests/lua_apply_chain_firers.json.

An 'apply-chain firer' is a Lua-name fired from the apply helper of an
inbound receiver (depth >= 2 of the receiver's apply chain), NOT from a
LuaActorImpl::vftable slot dispatcher. The Lua-name to opcode bridge's slot-based
source filter cannot capture these because there is no LuaActorImpl slot
that names the Lua-callback as its own dispatcher; instead, the helper
calls the Lua-dispatcher pattern FUN_00447260(name, ...) + FUN_00CC7A90
explicitly with the firer name.

Examples from the receiver-apply findings:
  0x013D SetDisplayNameReceiver -> _onUpdateDisplayName via FUN_006FAFF0
  0x0145 ChangeActorExtraStatReceiver -> _onChangeNetStatUser via FUN_006FA980
  0x0145 ChangeActorExtraStatReceiver -> _onChangeNetStatSystem via FUN_006FA980

Output schema:
  {
    version, gameVersion, source,
    firers: [
      { luaName, opcodeHex, opcodeInt, receiverClass, applyHelperVa,
        fireSite, evidenceBcsy, evidenceFile }
    ]
  }

Run:
    python tools\\extractors\\build_apply_chain_firers.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RECEIVER_MAP = REPO_ROOT / "manifests" / "receiver_opcode_map_inbound.json"
OUT = REPO_ROOT / "manifests" / "lua_apply_chain_firers.json"

# Add each findings manifest as (path, source tag).
FINDINGS_SOURCES = [
    (REPO_ROOT / "manifests" / "receiver_apply_findings_wire_derived.json",
     "BCS-Y-wire-derived", "manifests\\receiver_apply_findings_wire_derived.json"),
    (REPO_ROOT / "manifests" / "receiver_apply_findings_remaining.json",
     "BCS-Y-remaining", "manifests\\receiver_apply_findings_remaining.json"),
    (REPO_ROOT / "manifests" / "event_condition_consumer_findings.json",
     "event_condition_consumer_findings", "manifests\\event_condition_consumer_findings.json"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="verify the committed output matches a fresh build")
    args = ap.parse_args()

    rmap = json.load(RECEIVER_MAP.open(encoding="utf-8"))
    receiver_by_name = {r["name"]: r for r in rmap["inboundReceivers"]}

    firers = []
    seen_keys: set[tuple[str, str]] = set()
    for findings_path, bcsy_tag, file_ref in FINDINGS_SOURCES:
        if not findings_path.is_file():
            print(f"  skipping {findings_path.name}: not present", file=sys.stderr)
            continue
        findings = json.load(findings_path.open(encoding="utf-8"))
        for op_hex, entry in findings.get("findingsByOpcode", {}).items():
            # Skip synthetic multi-opcode keys; only canonical hex keys are emitted.
            if not (op_hex.startswith("0x") and len(op_hex) <= 6):
                continue
            receiver_name = entry.get("receiverName")
            helper_va = entry.get("applyHelperVa")
            for cb in entry.get("luaCallbacksFired", []) or []:
                key = (cb["luaName"], op_hex.lower())
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                r_meta = receiver_by_name.get(receiver_name, {})
                firers.append({
                    "luaName": cb["luaName"],
                    "opcodeHex": op_hex.lower(),
                    "opcodeInt": int(op_hex, 16),
                    "receiverClass": receiver_name,
                    "receiverNamespace": r_meta.get("namespace"),
                    "luaActorImplSlot": r_meta.get("luaActorImplSlot"),
                    "applyHelperVa": helper_va,
                    "fireSite": cb.get("fireSite"),
                    "bridgeStatus": cb.get("bridgeStatus"),
                    "bindingFlavor": cb.get("bindingFlavor", "direct"),
                    "evidenceBcsy": bcsy_tag,
                    "evidenceFile": file_ref,
                })

    out = {
        "version": "1",
        "gameVersion": "1.23b",
        "source": [src for _, _, src in FINDINGS_SOURCES] + [
            "manifests\\receiver_opcode_map_inbound.json",
        ],
        "description": (
            "Apply-chain Lua firers: Lua-names fired from receiver apply "
            "helpers (depth >= 2) rather than from LuaActorImpl::vftable "
            "slot dispatchers. The Lua-name to opcode bridge merges this manifest "
            "as a third binding mechanism (alongside slot-based direct "
            "bindings and data-dependency indirect bindings)."
        ),
        "firers": firers,
        "totals": {
            "firerCount": len(firers),
            "distinctLuaNames": len({f["luaName"] for f in firers}),
            "distinctOpcodes": len({f["opcodeHex"] for f in firers}),
        },
    }

    rendered = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != rendered:
            print(f"error: {OUT.name} does not match a fresh build", file=sys.stderr)
            return 1
        print(f"OK: {OUT.name} matches a fresh build")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(rendered, encoding="utf-8", newline="")
    print(f"wrote {OUT}")
    print(f"  firerCount:        {out['totals']['firerCount']}")
    print(f"  distinctLuaNames:  {out['totals']['distinctLuaNames']}")
    print(f"  distinctOpcodes:   {out['totals']['distinctOpcodes']}")
    for f in firers:
        print(f"    {f['luaName']:28s} <- {f['opcodeHex']} ({f['receiverClass']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
