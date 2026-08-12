#!/usr/bin/env python3
"""Build the inbound receiver -> opcode map for the Lua-name to opcode bridge.

Combines two sources:
    1. data/vendor/opcodes/client_receivers.json - a vendored copy of the
       receiver catalog with per-receiver opcode bindings and
       confidence tiers (prior receiver-catalog work). The fields we care about:
            name, namespace, rtti_rva, slots, slot1_fn,
            lua_actor_impl_slot, mapping{opcode, confidence,
            catalog_entry, evidence, lua_callback, body_shape,
            dispatch_shape, opcodeHex}, cast_target
    2. manifests/symbols.json - BCS-Y entries for the same receivers,
       reached by string-matching the receiver name into the symbol
       name. Gives us bcsId pointers for class/ctor/dtor/apply/slot1.

The MDI-019 saturation pass classified all 43 receivers; we partition
into:
    - inboundReceivers      : mapping.confidence == 'confirmed'
                              (15 receivers; the resolved opcode set)
    - clientInternalReceivers: mapping.confidence == 'client_internal'
                              (5 receivers, slots 7/19/20/21/22)
    - strongCandidates      : mapping.confidence in {'strong','candidate'}
                              (23 receivers, retained for follow-on work)

Curated enrichment (e.g. the pcap wire-confirmation pass) lives
in manifests/receiver_opcode_map_overlay.json and is merged on top of the
generated base map. This script does not mine prior output.

Output: manifests/receiver_opcode_map_inbound.json.

Run:
    python tools\\extract_receiver_opcode_map.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _symbols_io import load_symbols  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SYMBOLS_JSON = REPO_ROOT / "manifests" / "symbols.json"
CLIENT_RECV_JSON = REPO_ROOT / "data" / "vendor" / "opcodes" / "client_receivers.json"
OVERLAY_JSON = REPO_ROOT / "manifests" / "receiver_opcode_map_overlay.json"
OUT_JSON = REPO_ROOT / "manifests" / "receiver_opcode_map_inbound.json"
WORKLOG_DATE_RE = re.compile(r"_(?:19|20)\d{2}-\d{2}-\d{2}(?=:)")

ROLE_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("ctor", re.compile(r"::ctor\b|::ctor_|_ctor_", re.IGNORECASE)),
    ("dtor", re.compile(r"::dtor\b|::dtor_|::nondelete_dtor|::deleting_dtor", re.IGNORECASE)),
    ("apply", re.compile(r"::apply\b|::apply_|::Receive\b|::Receive_", re.IGNORECASE)),
    ("slot1", re.compile(r"::slot1\b|::slot1_", re.IGNORECASE)),
    ("dispatchWrapper", re.compile(r"::dispatch_wrapper|ApplyWrapper", re.IGNORECASE)),
    ("factory", re.compile(r"_factory|_client_side_factory", re.IGNORECASE)),
]


def _classify_bcs(name: str) -> str:
    for role, pat in ROLE_PATTERNS:
        if pat.search(name):
            return role
    return "other"


def _index_bcs_by_receiver(symbols: list[dict]) -> dict[str, dict[str, list[dict]]]:
    """Map receiver class name -> { role -> [bcs_entry] }."""
    by_recv: dict[str, dict[str, list[dict]]] = {}

    for sym in symbols:
        if "Receiver" not in sym["name"]:
            continue
        m = re.search(r"\b([A-Z][A-Za-z0-9_]*Receiver)\b", sym["name"])
        if not m:
            continue
        recv_name = m.group(1)
        role = "class" if sym["kind"] == "rtti" else _classify_bcs(sym["name"])
        entry = {
            "bcsId": sym["id"],
            "symbolName": sym["name"],
            "kind": sym["kind"],
            "address": sym["address"],
            "confidence": sym.get("confidence", "unknown"),
        }
        by_recv.setdefault(recv_name, {}).setdefault(role, []).append(entry)
    return by_recv


def _opcode_field_to_list(op) -> list[dict]:
    """Normalize mapping.opcode (int or list-of-int) into a [{int, hex}] list."""
    if op is None:
        return []
    if isinstance(op, int):
        return [{"opcodeInt": op, "opcodeHex": f"0x{op:04x}"}]
    if isinstance(op, str):
        try:
            i = int(op, 16) if op.lower().startswith("0x") else int(op)
            return [{"opcodeInt": i, "opcodeHex": f"0x{i:04x}"}]
        except ValueError:
            return [{"opcodeRaw": op}]
    if isinstance(op, list):
        out = []
        for v in op:
            if isinstance(v, int):
                out.append({"opcodeInt": v, "opcodeHex": f"0x{v:04x}"})
            else:
                out.append({"opcodeRaw": str(v)})
        return out
    return [{"opcodeRaw": str(op)}]


def _emit_receiver(r: dict, bcs_index: dict[str, dict[str, list[dict]]]) -> dict:
    mapping = r.get("mapping") or {}
    opcodes = _opcode_field_to_list(mapping.get("opcode"))
    refs = bcs_index.get(r["name"], {})
    evidence = WORKLOG_DATE_RE.sub("", mapping.get("evidence") or "")
    evidence = evidence.replace(
        "Reproducible by a FindAllReferences pass",
        "Reproducible by a Ghidra FindAllReferences pass",
    )
    return {
        "name": r["name"],
        "namespace": r.get("namespace"),
        "rttiRva": r.get("rtti_rva"),
        "slot1Fn": r.get("slot1_fn"),
        "luaActorImplSlot": r.get("lua_actor_impl_slot"),
        "confidence": mapping.get("confidence"),
        "opcodes": opcodes,
        "catalogEntry": mapping.get("catalog_entry"),
        "luaCallback": mapping.get("lua_callback"),
        "bodyShape": mapping.get("body_shape"),
        "dispatchShape": mapping.get("dispatch_shape"),
        "castTarget": r.get("cast_target"),
        "evidence": evidence or None,
        "bcsRefs": refs,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="verify the committed output matches a fresh build")
    args = ap.parse_args()

    if not SYMBOLS_JSON.is_file():
        print(f"error: {SYMBOLS_JSON} missing", file=sys.stderr)
        return 1
    if not CLIENT_RECV_JSON.is_file():
        print(f"error: {CLIENT_RECV_JSON} missing - run tools/refresh_vendor.py to refresh it",
              file=sys.stderr)
        return 1

    symbols_manifest = load_symbols(SYMBOLS_JSON)
    with CLIENT_RECV_JSON.open(encoding="utf-8") as f:
        recv_manifest = json.load(f)

    bcs_index = _index_bcs_by_receiver(symbols_manifest["symbols"])

    receivers = recv_manifest["receivers"]
    inbound: list[dict] = []
    client_internal: list[dict] = []
    strong: list[dict] = []
    candidate: list[dict] = []

    for r in receivers:
        conf = ((r.get("mapping") or {}).get("confidence")) or "no-mapping"
        rec = _emit_receiver(r, bcs_index)
        if conf == "confirmed":
            inbound.append(rec)
        elif conf == "client_internal":
            client_internal.append(rec)
        elif conf == "strong":
            strong.append(rec)
        elif conf == "candidate":
            candidate.append(rec)

    out = {
        "version": "1",
        "gameVersion": recv_manifest.get("version", "1.23b"),
        "source": (
            "data\\vendor\\opcodes\\client_receivers.json + "
            "manifests\\symbols.json (BCS-Y cross-ref by receiver class name)"
        ),
        "totalReceiversInCatalog": len(receivers),
        "inboundConfirmedCount": len(inbound),
        "clientInternalCount": len(client_internal),
        "strongCount": len(strong),
        "candidateCount": len(candidate),
        "inboundReceivers": inbound,
        "clientInternalReceivers": client_internal,
        "strongCandidates": strong,
        "candidates": candidate,
    }

    if not OVERLAY_JSON.is_file():
        print(f"error: {OVERLAY_JSON} missing - the curated overlay is a "
              "committed input, not optional", file=sys.stderr)
        return 1
    with OVERLAY_JSON.open(encoding="utf-8") as fov:
        overlay = json.load(fov)
    for k, v in overlay.items():
        if k == "_comment":
            continue
        if k in out:
            print(f"error: overlay key {k!r} collides with a generated key",
                  file=sys.stderr)
            return 1
        out[k] = v

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
    print(f"  inboundConfirmed:    {len(inbound)}")
    print(f"  clientInternal:      {len(client_internal)}")
    print(f"  strongCandidates:    {len(strong)}")
    print(f"  candidates:          {len(candidate)}")
    print(f"  total:               {len(receivers)}")

    unmatched = [r["name"] for r in inbound + client_internal
                 if r["name"] not in bcs_index]
    if unmatched:
        print(f"warn: {len(unmatched)} confirmed/client-internal receivers "
              f"have no BCS-Y cross-ref: {unmatched}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
