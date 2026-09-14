"""Promote the closed player render-transform boundary facts."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import _symbols_io  # noqa: E402


SOURCE_REFS = [
    "tools/ghidra/logs/c560_player-render-boundary.txt",
    "tools/ghidra/logs/c562_player-render-fallback.txt",
    "tools/ghidra/logs/c564_player-transform-source.txt",
    "tools/ghidra/logs/c565_player-rigidbody-ownership.txt",
    "manifests/player_render_boundary.json",
]
GETTER_SOURCE_REFS = [
    "tools/ghidra/logs/c561_player-model-position-getter.txt",
    *SOURCE_REFS,
]
NAMEPLATE_SOURCE_REFS = [
    "tools/ghidra/logs/c563_nameplate-post-update.txt",
    *SOURCE_REFS,
]

REFINEMENTS = {
    "0x0058DF90": {
        "notes": "[battle-effect-queue-consumer; Tier C560/C562 2026-09-14] 299-byte per-actor frame tick orchestrator for CharaElement. Calls the combat-status snapshot, action-state machine, status-effect timer, and battle-effect queue drain, then invokes slots 19 and 13 on the inline NamePlate subobject at CharaElement+0xBA0. Slot 19 only updates NamePlate+0x190 bit 0x04. The sampled slot-13 color records are not moving position, but its indirect helper path remains unresolved.",
        "sourceRefs": [
            "manifests/battle_effect_queue_consumer.json",
            *NAMEPLATE_SOURCE_REFS,
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
        "notes": "[Tier C560/C562 2026-09-14] SceneObject::Actor constructor. It stores the ModelObject at Actor+0x0C, zeros Actor+0x18 and +0x48, and registers the UPDATE_MODEL_TRANSFORM callback thunk at 0x00A61180. The normal RaptureActor chain supplies RaptureModelObjectFactory.",
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
        "notes": "[Tier C560/C562/C564 2026-09-14] UPDATE_MODEL_TRANSFORM virtual target: __thiscall(Actor *this, uint32_t ignored_arg), ending in RET 4. The local bounded trace proved the Actor+0x18 fallback was active, resolved the live ModelObject slots, and observed slot 13 receiving the already-held position before slot 25 rebuilt the drawable cache.",
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
        "notes": "[Tier C560/C562/C564 2026-09-14] Base and live RaptureModelObject vtable slot 26. Copies a 0x40-byte input into ModelObject+0x50..+0x8C, updates +0x29C flags, and can substitute fallback globals for invalid input. The follow-up trace resolved this live target but observed zero local calls because the attached-source gate was inactive.",
    },
    {
        "name": "Graphics_Scene_ModelObject_get_cached_transform_FUN_008DE790",
        "kind": "function",
        "address": "0x008DE790",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C560/C564 2026-09-14] Live RaptureModelObject vtable slot 25. Returns ModelObject+0x50 after conditionally rebuilding that 0x40-byte record from ModelObject+0x30 and other fields. The follow-up trace proved it rebuilt and supplied the exact Drawable-setter record after slot 13, but did not introduce the held Y.",
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
        "sourceRefs": NAMEPLATE_SOURCE_REFS,
        "notes": "[Tier C560/C562 2026-09-14] NamePlate vtable slot 13. It compares the index-1 RGBA color at NamePlate+0x78..+0x84 with +0x98..+0xA4 and publishes changes through FUN_00938020. Both records remained constant during captured movement, ruling out those records as moving position; indirect helpers in this slot remain unresolved.",
    },
    {
        "name": "Application_Scene_Actor_read_transform_source_position_FUN_00A61130",
        "kind": "function",
        "address": "0x00A61130",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C562/C564 2026-09-14] Fallback transform-source reader. It reads +0x2C from the opaque Actor+0x18 slot-29 result. Normal static CharaActor construction identifies that result as a CharacterProxy and +0x2C as a RigidBody, but the bounded capture did not record the live controller or proxy vtables. It copies [X,Y,Z,1] through [[BCS-Y-2268]] or uses the default record, then returns immediately before ModelObject slot 13.",
    },
    {
        "name": "Graphics_Scene_ModelObject_set_position_record_FUN_008DE970",
        "kind": "function",
        "address": "0x008DE970",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C562/C564 2026-09-14] Confirmed live RaptureModelObject vtable slot 13. Copies [X,Y,Z,1] to ModelObject+0x30..+0x3C, updates +0x29C cache flags, and conditionally mirrors the four lanes at +0x80..+0x8C. The fallback calls it at 0x00A601CD; the live trace proved its input was already held and that it overwrote newer shared ModelObject state.",
    },
    {
        "name": "Application_NamePlate_set_indexed_color_FUN_006A3AD0",
        "kind": "function",
        "address": "0x006A3AD0",
        "confidence": "confirmed",
        "sourceRefs": NAMEPLATE_SOURCE_REFS,
        "notes": "[Tier C562 2026-09-14] NamePlate vtable slot 2. Writes four color lanes into the indexed 0x10-byte record beginning at NamePlate+0x68; index 1 is +0x78..+0x84. This record remained constant during captured movement and is not the moving position.",
    },
    {
        "name": "Application_NamePlate_set_flag_0x04_FUN_006A2A60",
        "kind": "function",
        "address": "0x006A2A60",
        "confidence": "confirmed",
        "sourceRefs": NAMEPLATE_SOURCE_REFS,
        "notes": "[Tier C562 2026-09-14] NamePlate vtable slot 19. Updates only bit 0x04 at NamePlate+0x190. Called immediately before slot 13 by the per-actor frame tick; it is not a position producer.",
    },
    {
        "name": "Application_Scene_CharaActor_create_rapture_character_controller_FUN_007CD360",
        "kind": "function",
        "address": "0x007CD360",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] CharaActor vtable slot 68. Constructs a RaptureCharacterProxy and RaptureCharacterController, then stores the controller at Actor+0x18. The bounded local trace proved Actor+0x18 was the active fallback source but did not record that object's vtable.",
    },
    {
        "name": "Application_Scene_RaptureCharacterProxy_constructor_FUN_007D4560",
        "kind": "function",
        "address": "0x007D4560",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] Calls the base CharacterProxy constructor and installs RaptureCharacterProxy vtable 0x00FEE210. CharaActor slot 68 supplies this proxy to the RaptureCharacterController constructor.",
    },
    {
        "name": "Application_Scene_RaptureCharacterController_constructor_FUN_007D49F0",
        "kind": "function",
        "address": "0x007D49F0",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] Calls [[BCS-Y-2265]] with the CharaActor and supplied RaptureCharacterProxy, then installs RaptureCharacterController vtable 0x00FEE17C.",
    },
    {
        "name": "Engine_SceneObject_CharacterController_constructor_FUN_00A68CB0",
        "kind": "function",
        "address": "0x00A68CB0",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] Base CharacterController constructor. Stores CharacterProxy at +0x04, Actor at +0x08, initializes queued-operation fields +0x0C/+0x10, and sets the proxy's controller backlink at +0x48.",
    },
    {
        "name": "Engine_SceneObject_CharacterController_slot10_consume_position_queue_FUN_00A68000",
        "kind": "function",
        "address": "0x00A68000",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] CharacterController slot 10. Dispatches +0x0C state 1, 2, or 3 through slots 32, 33, or 34 with +0x10, then clears +0x0C. State zero performs no CharacterProxy/RigidBody update. Both base and Rapture controller vtables use this target.",
    },
    {
        "name": "Engine_SceneObject_CharacterController_slot29_get_proxy_FUN_008D5570",
        "kind": "function",
        "address": "0x008D5570",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] CharacterController slot 29. Returns CharacterController+0x04, the CharacterProxy passed next to [[BCS-Y-2258]]. Both base and Rapture controller vtables use this target.",
    },
    {
        "name": "Engine_Phieg_RigidBody_read_indexed_position_FUN_00AFA220",
        "kind": "function",
        "address": "0x00AFA220",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] Copies four floats from **(RigidBody+0x14) + RigidBody+0x10*0x70. Runtime propagation through [[BCS-Y-2258]] establishes [X,Y,Z,1] lane order.",
    },
    {
        "name": "Engine_Phieg_RigidBody_constructor_FUN_00AFA070",
        "kind": "function",
        "address": "0x00AFA070",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] Constructs a 0x48-byte RigidBody with vtable 0x010A9878, obtains an index and pool owner for its 0x70-byte record, initializes record data, and stores the RigidBody backpointer at record+0x6C.",
    },
    {
        "name": "Engine_Phieg_RigidBody_write_indexed_position_FUN_00AFA160",
        "kind": "function",
        "address": "0x00AFA160",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] Writes input lanes 0..2 and the canonical fourth-lane constant to the active indexed 0x70-byte RigidBody record, then clears record+0x64. The function has no timer or frame-divider gate; cadence is caller-owned.",
    },
    {
        "name": "Engine_SceneObject_CharacterController_slot7_queue_absolute_position_FUN_00A67F80",
        "kind": "function",
        "address": "0x00A67F80",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] CharacterController slot 7. Sets pending selector +0x0C to 1 and copies the absolute four-float value to +0x10 while returning a copy to its caller.",
    },
    {
        "name": "Engine_SceneObject_CharacterController_slot8_queue_relative_position_FUN_00A67FB0",
        "kind": "function",
        "address": "0x00A67FB0",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] CharacterController slot 8. Sets pending selector +0x0C to 2 and copies the relative four-float value to +0x10.",
    },
    {
        "name": "Engine_SceneObject_CharacterController_slot9_queue_direct_position_FUN_00A67FD0",
        "kind": "function",
        "address": "0x00A67FD0",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] CharacterController slot 9. Sets pending selector +0x0C to 3, copies the direct four-float value to +0x10, and immediately invokes slot 10.",
    },
    {
        "name": "Application_Scene_RaptureCharacterProxy_slot1_update_position_FUN_007D8080",
        "kind": "function",
        "address": "0x007D8080",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] RaptureCharacterProxy vtable slot 1. It conditionally calls opaque helpers 0x007D77E0 and 0x007D79C0, writes CharacterProxy+0x2C RigidBody through [[BCS-Y-2270]], and snapshots the resulting position at RaptureCharacterProxy+0x70.",
    },
    {
        "name": "Engine_SceneObject_CharacterProxy_slot2_set_direct_position_FUN_007D8E90",
        "kind": "function",
        "address": "0x007D8E90",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] CharacterProxy vtable slot 2. If +0x2C is non-null, tail-calls [[BCS-Y-2270]] with the supplied four-float value; otherwise returns with RET 4.",
    },
    {
        "name": "Application_Scene_Actor_slot32_publish_position_FUN_00A5F810",
        "kind": "function",
        "address": "0x00A5F810",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] Actor slot 32. Queues an absolute position through Actor+0x18 slot 7, then sends the returned value to ModelObject slot 16. The local runtime caller and cadence remain unobserved.",
    },
    {
        "name": "Graphics_Scene_ModelObject_slot16_set_position_record_FUN_008DDAB0",
        "kind": "function",
        "address": "0x008DDAB0",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] ModelObject vtable slot 16. Copies four lanes to ModelObject+0x30..+0x3C and updates cache state at +0x29C. Actor slot 32 calls it after queueing the same position through the CharacterController.",
    },
    {
        "name": "Engine_SceneObject_CharacterController_slot32_dispatch_absolute_position_FUN_00A68060",
        "kind": "function",
        "address": "0x00A68060",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] CharacterController slot 32. Tail-dispatches the supplied four-float value to CharacterController+0x04 slot 1. Slot 10 selects it for pending state 1.",
    },
    {
        "name": "Engine_SceneObject_CharacterController_slot33_dispatch_relative_position_FUN_00A68070",
        "kind": "function",
        "address": "0x00A68070",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] CharacterController slot 33. Reads the current record through CharacterController+0x04+0x2C, adds the supplied four-float delta, and invokes CharacterController+0x04 slot 1. Slot 10 selects it for pending state 2.",
    },
    {
        "name": "Engine_SceneObject_CharacterController_slot34_dispatch_direct_position_FUN_00A680D0",
        "kind": "function",
        "address": "0x00A680D0",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C564 2026-09-14] CharacterController slot 34. Tail-dispatches the supplied four-float value to CharacterController+0x04 slot 2. Slot 10 selects it for pending state 3.",
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
