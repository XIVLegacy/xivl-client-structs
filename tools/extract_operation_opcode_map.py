#!/usr/bin/env python3
"""Build the outbound Operation -> opcode map for the Lua-name to opcode bridge.

Companion to extract_receiver_opcode_map.py. The outbound (serverbound)
direction is sparser than inbound. The vendored opcode catalog has a small
class-annotated set and a larger set without `retail_class_name`; there is no
client-side Operation-class catalog analogous to
`data/vendor/opcodes/client_receivers.json` for the outbound direction.

This tool produces a *scaffolding* manifest. It inventories the class-annotated
Operation entries and records every serverbound opcode without a class.

Curated enrichment layers added by one-shot follow-on passes
live in manifests/operation_opcode_map_overlay.json
and are merged on top of the generated base map. This script does not mine
them from prior output.

Output: manifests/operation_opcode_map_outbound.json.

Run:
    python tools\\extract_operation_opcode_map.py
    python tools\\extract_operation_opcode_map.py --check
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _symbols_io import load_symbols  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SYMBOLS_JSON = REPO_ROOT / "manifests" / "symbols.json"
OPCODES_JSON = REPO_ROOT / "data" / "vendor" / "opcodes" / "opcodes.json"
OVERLAY_JSON = REPO_ROOT / "manifests" / "operation_opcode_map_overlay.json"
OUT_JSON = REPO_ROOT / "manifests" / "operation_opcode_map_outbound.json"


def _implementation_anchor(op: dict) -> object:
    """Translate the pinned sibling vocabulary at the import boundary."""
    return op.get("implementationAnchor")


def _implementation_confidence(op: dict) -> object:
    """Translate the pinned sibling status at the import boundary."""
    value = op.get("confidence")
    return "implemented" if value == "implemented" else value


def _load_opcodes() -> dict:
    with OPCODES_JSON.open(encoding="utf-8-sig") as f:
        data = json.load(f)
    if isinstance(data, list):
        # The vendored opcodes file may be wrapped in a single-element list.
        data = data[0]
    return data


def _flatten_opcodes(catalog: dict) -> list[dict]:
    """Yield every opcode entry with bucket/list metadata attached."""
    out = []
    for bucket, ops in catalog["lists"].items():
        for op in ops:
            out.append({**op, "bucket": bucket})
    return out


def _index_bcs_by_class_token(symbols: list[dict]) -> dict[str, list[dict]]:
    """Map class-name substring -> [BCS-Y entries that mention it]."""
    index: dict[str, list[dict]] = defaultdict(list)
    for sym in symbols:
        name = sym["name"]
        for chunk in name.replace("::", " ").split():
            if chunk.endswith(("Operation", "Receiver", "Sender", "Builder",
                               "Channel", "Callback", "Dispatcher", "Backend")):
                index[chunk].append({
                    "bcsId": sym["id"],
                    "symbolName": sym["name"],
                    "kind": sym["kind"],
                    "address": sym["address"],
                })
    return index


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="verify the committed output matches a fresh build")
    args = ap.parse_args()

    if not SYMBOLS_JSON.is_file():
        print(f"error: {SYMBOLS_JSON} missing", file=sys.stderr)
        return 1
    if not OPCODES_JSON.is_file():
        print(f"error: {OPCODES_JSON} missing - run tools/refresh_vendor.py to refresh it",
              file=sys.stderr)
        return 1

    symbols_manifest = load_symbols(SYMBOLS_JSON)
    catalog = _load_opcodes()

    opcodes = _flatten_opcodes(catalog)
    print(f"loaded {len(opcodes)} opcodes from {OPCODES_JSON.name}")

    bcs_index = _index_bcs_by_class_token(symbols_manifest["symbols"])

    by_dir: dict[str, list[dict]] = defaultdict(list)
    for op in opcodes:
        by_dir[op.get("direction") or "unknown"].append(op)

    serverbound = by_dir.get("serverbound", [])
    print(f"  serverbound:  {len(serverbound)}")
    print(f"  clientbound:  {len(by_dir.get('clientbound', []))}")
    print(f"  backend:      {len(by_dir.get('backend', []))}")

    classed: dict[str, list[dict]] = defaultdict(list)
    unclassed: list[dict] = []
    for op in serverbound:
        rc = op.get("retail_class_name")
        if rc:
            classed[rc].append(op)
        else:
            unclassed.append(op)

    operations = []
    for cls, ops in sorted(classed.items()):
        tail = cls.split("::")[-1]
        ops_summary = [
            {
                "opcode": op.get("opcode"),
                "opcodeHex": op.get("opcodeHex"),
                "name": op.get("name"),
                "direction": op.get("direction"),
                "bucket": op["bucket"],
                "implementationAnchor": _implementation_anchor(op),
                "decompAnchor": op.get("decompAnchor"),
                "confidence": _implementation_confidence(op),
            }
            for op in ops
        ]
        operations.append({
            "retailClass": cls,
            "tail": tail,
            "opcodeCount": len(ops),
            "opcodes": ops_summary,
            "bcsRefs": bcs_index.get(tail, []),
        })

    gap_serverbound = [
        {
            "opcode": op.get("opcode"),
            "opcodeHex": op.get("opcodeHex"),
            "name": op.get("name"),
            "bucket": op["bucket"],
            "implementationAnchor": _implementation_anchor(op),
            "decompAnchor": op.get("decompAnchor"),
            "confidence": _implementation_confidence(op),
        }
        for op in unclassed
    ]
    gap_serverbound.sort(key=lambda o: (o.get("opcode") or 0))

    if not OVERLAY_JSON.is_file():
        print(f"error: {OVERLAY_JSON} missing - the curated overlay is a "
              "committed input, not optional", file=sys.stderr)
        return 1
    with OVERLAY_JSON.open(encoding="utf-8") as fov:
        overlay = json.load(fov)

    for op in operations:
        slot_data = overlay.get("operationClassSlots", {}).get(op["retailClass"])
        if slot_data:
            op.update(slot_data)

    gap_extras = overlay.get("serverboundGapExtras", {})
    for e in gap_serverbound:
        extras = gap_extras.get(str(e.get("opcode")))
        if extras:
            e.update(extras)

    out = {
        "version": "1",
        "gameVersion": catalog.get("version", "1.23b"),
        "source": (
            "data\\vendor\\opcodes\\opcodes.json (retail_class_name + serverbound) + "
            "manifests\\symbols.json (BCS-Y class-token cross-ref)"
        ),
        "notes": (
            "Outbound scaffolding manifest. Operation classes are the only "
            "retail_class_name-annotated outbound classes in opcodes.json; "
            f"the gap is {len(unclassed)} serverbound opcodes with no class annotation - "
            "filling those requires a Ghidra opcode-emission scan "
            "or class-driven decomp. Aux enrichments come from "
            "manifests/operation_opcode_map_overlay.json: per-class "
            "vtable/confirmedEmissions/confirmedReceives blocks, per-opcode "
            "gap extras, top-level enrichment sections, and notes appendices."
        ),
        "totals": {
            "serverbound": len(serverbound),
            "serverboundClassed": sum(len(ops) for ops in classed.values()),
            "serverboundGap": len(unclassed),
            "operationClasses": len(operations),
        },
        "operationClasses": operations,
        "serverboundGap": gap_serverbound,
    }

    appendices = overlay.get("notesAppendices") or []
    if appendices:
        out["notes"] = " | ".join([out["notes"], *appendices])
    for k, v in (overlay.get("totalsExtras") or {}).items():
        out["totals"].setdefault(k, v)
    for k, v in (overlay.get("topLevelSections") or {}).items():
        if k in out:
            print(f"error: overlay topLevelSections key {k!r} collides with a "
                  "generated key", file=sys.stderr)
            return 1
        out[k] = v

    rendered = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUT_JSON.is_file() or OUT_JSON.read_text(encoding="utf-8") != rendered:
            print(f"error: {OUT_JSON.name} does not match a fresh build",
                  file=sys.stderr)
            return 1
        print(f"OK: {OUT_JSON.name} matches a fresh build")
        return 0

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(rendered, encoding="utf-8", newline="")

    print(f"wrote {OUT_JSON}")
    print(f"  operationClasses:     {len(operations)}")
    print(f"  classed serverbound:  {sum(len(ops) for ops in classed.values())}")
    print(f"  serverbound gap:      {len(unclassed)}")
    for o in operations:
        bcs = ",".join(r["bcsId"] for r in o["bcsRefs"][:4])
        print(f"    {o['tail']:30} {o['opcodeCount']:>2} opcodes  "
              f"bcsRefs: {bcs or '(none)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
