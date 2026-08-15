#!/usr/bin/env python3
"""Build the frozen static Group-family wire-identity evidence manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "manifests" / "director_group_wire_identity.json"

ROWS = [
    ("0x017A", "BCS-Y-0563", "0x005763B0", ["BCS-Y-0873", "BCS-Y-1795"], "0x006C9910 -> 0x006C96B0", 0x90),
    ("0x017C", "BCS-Y-0564", "0x00576250", ["BCS-Y-0874"], "0x006CC620", 0x78),
    ("0x017D", "BCS-Y-0565", "0x005762C0", ["BCS-Y-0875"], "0x006C2F30", 0x20),
    ("0x017E", "BCS-Y-0566", "0x005762D0", ["BCS-Y-0876"], "0x006C4180", 0x18),
    ("0x017F", "BCS-Y-0567", "0x005762E0", ["BCS-Y-0877"], "0x006C2F70", 0x198),
    ("0x0183", "BCS-Y-0571", "0x00576320", [], "0x006C3100", 0x78),
    ("0x0187", "BCS-Y-0575", "0x00576390", ["BCS-Y-0885"], "0x006C8340 -> 0x006C6B20 / 0x006C5460", 0x40),
    ("0x018B", "BCS-Y-0579", "0x005763A0", ["BCS-Y-0889"], "0x006C5DF0 -> 0x006C5240", 0x38),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(decomp: Path) -> dict:
    required = {
        "group_header": decomp / "asm" / "ffxivgame" / "002cc620_FUN_006cc620.s",
        "group_members_x08": decomp / "asm" / "ffxivgame" / "002c2f70_FUN_006c2f70.s",
        "occupancy": decomp / "asm" / "ffxivgame" / "002c8340_FUN_006c8340.s",
        "layout": decomp / "asm" / "ffxivgame" / "002c5240_FUN_006c5240.s",
        "member_self_compare": decomp / "asm" / "ffxivgame" / "002c1040_FUN_006c1040.s",
        "actor_self_compare": decomp / "asm" / "ffxivgame" / "0035bbf0_FUN_0075bbf0.s",
        "zone_self_actor": decomp / "asm" / "ffxivgame" / "000d7490_FUN_004d7490.s",
    }
    for path in required.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    header_text = required["group_header"].read_text(encoding="utf-8", errors="replace").lower()
    if "cmp dword ptr [ebp + 0x30],0x2711" not in header_text:
        raise ValueError("0x017C handler no longer compares packet +0x30 with 0x2711")
    members_text = required["group_members_x08"].read_text(encoding="utf-8", errors="replace").lower()
    for expected in ("movsx eax,byte ptr [esi + 0x190]", "lea edx,[esi + 0x10]", "call 0x006c1040"):
        if expected not in members_text:
            raise ValueError(f"0x017F handler no longer contains: {expected}")
    party = ROOT / "manifests" / "party_subsystem.json"
    return {
        "schemaVersion": 1,
        "generatedBy": "tools/extractors/build_director_group_wire_identity.py",
        "scope": "retail 1.23b client-side Group-family routing and packet reads",
        "inputs": {
            "party_subsystem": {"path": "manifests/party_subsystem.json", "sha256": digest(party)},
            **{key: {"path": f"xivl-decomp:asm/ffxivgame/{path.name}", "sha256": digest(path)}
               for key, path in required.items()},
        },
        "opcodes": [
            {"opcodeHex": op, "primaryBcsId": bcs, "primaryVa": va,
             "calleeBcsIds": ids, "clientChain": chain,
             "applicationPayloadSize": size,
             "sourceRefs": ["manifests/party_subsystem.json"]}
            for op, bcs, va, ids, chain, size in ROWS
        ],
        "layouts": {
            "0x017C": {"groupTypeCandidate": {"offset": 0x30, "width": 4},
                       "memberCount": {"offset": 0x74, "width": 4},
                       "condition": {"va": "0x006CC620", "offset": 0x30,
                                     "comparedValue": 10001,
                                     "boundary": "comparison selects a client path; it does not enumerate valid server values"}},
            "0x017F": {"recordsOffset": 0x10, "recordCount": 8,
                       "recordStride": 0x30, "actorIdOffset": 0,
                       "unresolvedFieldOffset": 8, "memberCountOffset": 0x190},
            "0x0183": {"recordsOffset": 0x10, "recordCount": 8,
                       "recordStride": 0x0C, "actorIdOffset": 0,
                       "memberCountOffset": 0x70},
        },
        "claimCeilings": {
            "directorActorKind": "No Group handler masks or compares the actor-ID high nibble.",
            "directorSelfMembership": "A downstream member path compares member IDs with the local/self actor ID; no static chain labels either operand as a content director.",
            "groupType": "The client compares 10001 at 0x017C +0x30; other wire values are capture-side evidence.",
            "layout": "The 0x017F and 0x0183 member records are distinct shapes.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decomp-repo", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = (json.dumps(build(args.decomp_repo.resolve()), indent=2) + "\n").encode("ascii")
    if args.check:
        if not OUT.is_file() or OUT.read_bytes() != data:
            print(f"stale: {OUT}")
            return 1
        print(f"verified {OUT.relative_to(ROOT)}")
        return 0
    OUT.write_bytes(data)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
