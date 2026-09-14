"""Promote the closed RaptureCharacterProxy retained-Y path."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import _symbols_io  # noqa: E402


SOURCE_REFS = [
    "tools/ghidra/logs/c567_player-proxy-retained-y.txt",
    "tools/ghidra/logs/c567_player-proxy-retained-y-listing.txt",
    "manifests/player_render_boundary.json",
]

REFINEMENTS = {
    "0x007CD360": (
        "[Tier C564/C567 2026-09-14] CharaActor vtable slot 68. Constructs a "
        "RaptureCharacterProxy and RaptureCharacterController, then stores the "
        "controller at Actor+0x18. The bounded controller capture confirmed the "
        "live Actor+0x18 vtable as 0x00FEE17C and its +0x04 proxy vtable as "
        "0x00FEE210."
    ),
    "0x007D8080": (
        "[Tier C564/C567 2026-09-14] Confirmed live RaptureCharacterProxy "
        "vtable slot 1. With +0x40 bit 8 set, it subtracts current "
        "RigidBody position from its absolute input and sends the resulting "
        "[dX,dY,dZ,0] through [[BCS-Y-2286]]. The bounded controller capture "
        "proved that the input had the new Y on every held frame while a "
        "nested [[BCS-Y-2287]] writer published the preceding RigidBody Y."
    ),
    "0x00A68000": (
        "[Tier C564/C567 2026-09-14] CharacterController slot 10. Dispatches "
        "+0x0C state 1, 2, or 3 through slots 32, 33, or 34 with +0x10, then "
        "clears +0x0C. The live RaptureCharacterController used state 1 on all "
        "900 captured frames, including every held-Y frame."
    ),
    "0x00AFA160": (
        "[Tier C564/C567 2026-09-14] Writes input lanes 0..2 and the canonical "
        "fourth lane to the active indexed RigidBody record and clears "
        "record+0x64. On every held-Y frame the call returning to 0x007D77B7 "
        "received and wrote the preceding RigidBody Y exactly."
    ),
    "0x00A61130": (
        "[Tier C562/C564/C567 2026-09-14] Fallback transform-source reader. "
        "The bounded controller capture proves that its live input is the "
        "RaptureCharacterProxy returned by controller slot 29 and +0x2C is "
        "the live RigidBody. It copies [X,Y,Z,1] through [[BCS-Y-2268]] and "
        "returns immediately before ModelObject slot 13."
    ),
}

NEW_SYMBOLS = [
    {
        "name": "Application_Scene_RaptureCharacterProxy_dispatch_segmented_displacement_FUN_007D77E0",
        "kind": "function",
        "address": "0x007D77E0",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": (
            "[Tier C567 2026-09-14] __thiscall proxy helper with four stack "
            "arguments and RET 0x10. It normalizes and segments [dX,dY,dZ,0], "
            "then passes each segment to [[BCS-Y-2287]]. Called from live "
            "RaptureCharacterProxy slot 1 at 0x007D8118. No timer or frame "
            "divider is present."
        ),
    },
    {
        "name": "Application_Scene_RaptureCharacterProxy_resolve_vector_displacement_FUN_007D70D0",
        "kind": "function",
        "address": "0x007D70D0",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": (
            "[Tier C567 2026-09-14] __thiscall recursive proxy helper with "
            "three stack arguments and RET 0x0C. It evaluates displacement "
            "against opaque record vectors, removes a negative projection "
            "component, can add a thresholded vector correction, and recurses "
            "with adjusted displacement. Its terminal 0x007D77B2 call writes "
            "current RigidBody position plus that invocation's displacement; "
            "0x007D77B7 is the return address. Runtime proved terminal dY was "
            "zero on all 160 held-Y writes."
        ),
    },
]


def main() -> None:
    with _symbols_io.symbols_transaction() as data:
        by_address = {entry.get("address"): entry for entry in data["symbols"]}

        for address, notes in REFINEMENTS.items():
            entry = by_address.get(address)
            if entry is None:
                raise RuntimeError(f"missing refinement target {address}")
            refs = list(entry.get("sourceRefs", []))
            for source_ref in SOURCE_REFS:
                if source_ref not in refs:
                    refs.append(source_ref)
            entry["notes"] = notes
            entry["sourceRefs"] = refs

        for new_entry in NEW_SYMBOLS:
            address = new_entry["address"]
            if address in by_address:
                entry = by_address[address]
                if not entry.get("name", "").endswith(f"FUN_{address[2:]}"):
                    raise RuntimeError(f"promotion target already exists at {address}")
                refs = list(entry.get("sourceRefs", []))
                for source_ref in SOURCE_REFS:
                    if source_ref not in refs:
                        refs.append(source_ref)
                entry["kind"] = new_entry["kind"]
                entry["name"] = new_entry["name"]
                entry["confidence"] = new_entry["confidence"]
                entry["notes"] = new_entry["notes"]
                entry["sourceRefs"] = refs
                continue
            allocated = _symbols_io.append_symbol(data, dict(new_entry))
            by_address[address] = data["symbols"][-1]
            print(f"{allocated} {address}")


if __name__ == "__main__":
    main()
