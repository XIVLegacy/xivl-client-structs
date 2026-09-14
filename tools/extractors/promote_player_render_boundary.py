"""Promote the closed player render-transform boundary facts."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import _symbols_io  # noqa: E402


SOURCE_REFS = [
    "tools/ghidra/logs/c560_player-render-boundary.txt",
    "manifests/player_render_boundary.json",
]
GETTER_SOURCE_REFS = [
    "tools/ghidra/logs/c561_player-model-position-getter.txt",
    *SOURCE_REFS,
]

REFINEMENTS = {
    "0x0058DF90": {
        "notes": "[battle-effect-queue-consumer; Tier C560 2026-09-14] 299-byte per-actor frame tick orchestrator for CharaElement. Calls the combat-status snapshot, action-state machine, status-effect timer, and battle-effect queue drain, then invokes slots 19 and 13 on the inline NamePlate subobject at CharaElement+0xBA0. Slot 13 receives the CharaElement pointer. It has no instruction-level callers and is reached virtually; runtime cadence relative to Present remains unresolved.",
        "sourceRefs": [
            "manifests/battle_effect_queue_consumer.json",
            *SOURCE_REFS,
        ],
    }
}


NEW_SYMBOLS = [
    {
        "name": "Application_Scene_SceneObject_Actor_constructor_FUN_00A60B80",
        "kind": "function",
        "address": "0x00A60B80",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C560 2026-09-14] SceneObject::Actor constructor. It stores the ModelObject at Actor+0x0C and registers the UPDATE_MODEL_TRANSFORM callback thunk at 0x00A61180.",
    },
    {
        "name": "Application_Scene_SceneObject_Actor_get_model_position_record_FUN_00A5F8A0",
        "kind": "function",
        "address": "0x00A5F8A0",
        "confidence": "confirmed",
        "sourceRefs": GETTER_SOURCE_REFS,
        "notes": "[Tier C561 2026-09-14] CharaActor vtable slot 34 inherited from SceneObject::Actor. It returns the four-dword record at ModelObject+0x30 through ModelObject slot 17. Exact coordinate semantics remain runtime-unverified.",
    },
    {
        "name": "Application_Scene_SceneObject_Actor_update_model_transform_FUN_00A5FF60",
        "kind": "function",
        "address": "0x00A5FF60",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C560 2026-09-14] UPDATE_MODEL_TRANSFORM virtual target. On the attached-source path it builds a 0x40-byte record and publishes it through ModelObject slot 26 at 0x00A600EF or 0x00A60183. It invokes ModelObject slot 7 afterward only when Actor+0x0C is non-null. Cadence and local-player specificity require runtime proof.",
    },
    {
        "name": "Graphics_Scene_ModelObject_get_position_record_FUN_008DDAF0",
        "kind": "function",
        "address": "0x008DDAF0",
        "confidence": "confirmed",
        "sourceRefs": GETTER_SOURCE_REFS,
        "notes": "[Tier C561 2026-09-14] ModelObject vtable slot 17. Returns ModelObject+0x30, a four-dword record consumed by CharaActor slot 34 and the cached-transform builder.",
    },
    {
        "name": "Graphics_Scene_ModelObject_set_transform_record_FUN_008DEC70",
        "kind": "function",
        "address": "0x008DEC70",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C560 2026-09-14] ModelObject vtable slot 26. Copies a 0x40-byte input into ModelObject+0x50..+0x8C, sets bits 0x10, 0x01, and 0x02 at +0x29C, and can substitute fallback globals for invalid input. World-matrix convention and render cadence remain runtime-unverified.",
    },
    {
        "name": "Graphics_Scene_ModelObject_get_cached_transform_FUN_008DE790",
        "kind": "function",
        "address": "0x008DE790",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C560 2026-09-14] ModelObject vtable slot 25. Returns ModelObject+0x50 after conditionally rebuilding that 0x40-byte record from ModelObject+0x30 and other ModelObject fields.",
    },
    {
        "name": "Graphics_Scene_ModelObject_publish_transform_to_drawable_FUN_00A61620",
        "kind": "function",
        "address": "0x00A61620",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C560 2026-09-14] ModelObject vtable slot 7. When the attached-drawable and dirty-bit guards pass, reads the cached 0x40-byte record through slot 25, optionally transforms it under bit 0x10, forwards the result through FUN_00BB7550, and clears bit 0x02.",
    },
    {
        "name": "Graphics_Render_Drawable_set_transform_record_FUN_00BB7550",
        "kind": "function",
        "address": "0x00BB7550",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C560 2026-09-14] Copies a 0x40-byte transform record into drawable+0x30..+0x6C, updates a flag at +0xA0, and invokes FUN_00C579A0. The final player shader register remains unresolved.",
    },
    {
        "name": "Application_NamePlate_sync_cached_presentation_FUN_006A3560",
        "kind": "function",
        "address": "0x006A3560",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C560 2026-09-14] NamePlate vtable slot 13, called from the per-actor frame path. It compares NamePlate+0x78..+0x84 with +0x98..+0xA4 and publishes changes through FUN_00938020. Static evidence does not identify the source writer or equate this cache with ModelObject state.",
    },
]


def main() -> None:
    with _symbols_io.symbols_transaction() as data:
        by_address = {entry.get("address"): entry for entry in data["symbols"]}
        for address, refinement in REFINEMENTS.items():
            entry = by_address.get(address)
            if entry is None:
                raise RuntimeError(f"missing refinement target {address}")
            refs = list(entry.get("sourceRefs", []))
            for source_ref in refinement["sourceRefs"]:
                if source_ref not in refs:
                    refs.append(source_ref)
            entry["notes"] = refinement["notes"]
            entry["sourceRefs"] = refs

        for new_entry in NEW_SYMBOLS:
            address = new_entry["address"]
            if address in by_address:
                if by_address[address].get("name") != new_entry["name"]:
                    raise RuntimeError(f"promotion target already exists at {address}")
                refs = list(by_address[address].get("sourceRefs", []))
                for source_ref in new_entry["sourceRefs"]:
                    if source_ref not in refs:
                        refs.append(source_ref)
                by_address[address]["kind"] = new_entry["kind"]
                by_address[address]["confidence"] = new_entry["confidence"]
                by_address[address]["notes"] = new_entry["notes"]
                by_address[address]["sourceRefs"] = refs
                continue
            allocated = _symbols_io.append_symbol(data, dict(new_entry))
            by_address[address] = data["symbols"][-1]
            print(f"{allocated} {address}")


if __name__ == "__main__":
    main()
