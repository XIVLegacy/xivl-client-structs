"""Promote the closed shader-camera boundary facts into symbols.json."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import _symbols_io  # noqa: E402


SOURCE_REFS = [
    "tools/ghidra/logs/c559_shader-camera-boundary.txt",
    "manifests/shader_camera_boundary.json",
]


REFINEMENTS = {
    "0x0061B5A0": {
        "name": "Application_Scene_Actor_System_CameraActor_constructor_FUN_0061B5A0",
        "confidence": "confirmed",
        "notes": "[Tier C559 2026-09-13] Exact 0x490-byte CameraActor constructor. It writes vftable 0x00FB906C and installs eleven camera-mode contexts. It also emits CameraElement async opcode 0x13; that side effect does not define the function's owner.",
    },
    "0x006195D0": {
        "name": "Application_Scene_Actor_System_CameraActor_update_FUN_006195D0",
        "confidence": "confirmed",
        "notes": "[Tier C559 2026-09-13] CameraActor update called by UPDATE_CAMERA_RAPTURE. It dispatches the active mode context, runs [[BCS-Y-0851]], and writes the sixteen-dword record at CameraActor+0x370. It also emits CameraElement async opcodes 0x13 and 0x2E. Render cadence and a shader consumer remain unresolved.",
    },
    "0x00617A80": {
        "name": "Application_Scene_Actor_System_CameraActor_build_derived_transforms_FUN_00617A80",
        "confidence": "confirmed",
        "notes": "[Tier C559 2026-09-13] CameraActor derived-transform builder. It reads the +0x310/+0x320 endpoint records and writes sixteen-float records at +0x210, +0x250, and +0x2D0 plus a scalar at +0x420 before calling through a singleton returned by FUN_00B8E7D0. The singleton owner is unresolved; no shader register or final render consumer is established. It also emits SqwtElement async opcode 0x2A.",
    },
    "0x00419020": {
        "name": "Shader_indexed_parameter_submit_FUN_00419020",
        "confidence": "confirmed",
        "notes": "[Tier C559 2026-09-13] Indexed shader-parameter submission primitive. It passes a pointer through FUN_00419B60 and submits it with count 4 through [[BCS-Y-2247]]. The pointed-to type, count unit, index meaning, matrix interpretation, and camera provenance remain unresolved.",
    },
    "0x00422F90": {
        "name": "Shader_parameter_conditional_submit_FUN_00422F90",
        "confidence": "confirmed",
        "notes": "[Tier C559 2026-09-13] Conditional shader-parameter submission wrapper. It invokes the selected parameter object's unresolved virtual setter only when unresolved FUN_00423A40 returns zero. C559 does not join that indirect target to the SetVertexShaderConstantF task family or identify a register or camera owner.",
    },
    "0x00419240": {
        "name": "Shader_submit_global_parameter_blocks_FUN_00419240",
        "confidence": "confirmed",
        "notes": "[Tier C559 2026-09-13] On an anonymous selection change, submits three globals at 0x01328FF4, 0x01329034, and 0x01329074 with count 4 through [[BCS-Y-2247]]. The owning shader class, count unit, value semantics, matrix interpretation, and camera provenance remain unresolved.",
    },
}


NEW_SYMBOLS = [
    {
        "name": "Application_Scene_Actor_System_CameraActor_vftable",
        "kind": "rtti",
        "address": "0x00FB906C",
        "confidence": "confirmed",
        "sourceRefs": ["tools/ghidra/logs/c314_async-queue-rtti.txt", *SOURCE_REFS],
        "notes": "[Tier C559 2026-09-13] RTTI-confirmed CameraActor vftable with 164 executable slots.",
    },
    {
        "name": "Application_Scene_UPDATE_CAMERA_RAPTURE_callback_FUN_004E8B50",
        "kind": "function",
        "address": "0x004E8B50",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C559 2026-09-13] Callback registered under UPDATE_CAMERA_RAPTURE by FUN_004EA870. It retrieves the shared scene object and conditionally calls [[BCS-Y-0832]]. Callback ordering and render-frame cadence remain unresolved.",
    },
    {
        "name": "Application_Scene_Actor_System_CameraActor_FPS_context_update_FUN_007F31A0",
        "kind": "function",
        "address": "0x007F31A0",
        "confidence": "confirmed",
        "sourceRefs": ["tools/ghidra/logs/c314_async-queue-rtti.txt", *SOURCE_REFS],
        "notes": "[Tier C559 2026-09-13] FPS camera-context vtable slot 1. This __thiscall-shaped update consumes a float delta and writes CameraActor+0x330..+0x34C.",
    },
    {
        "name": "Application_Scene_Actor_System_CameraActor_TPS_context_update_FUN_007F3BA0",
        "kind": "function",
        "address": "0x007F3BA0",
        "confidence": "confirmed",
        "sourceRefs": ["tools/ghidra/logs/c314_async-queue-rtti.txt", *SOURCE_REFS],
        "notes": "[Tier C559 2026-09-13] TPS camera-context vtable slot 1. This __thiscall-shaped update consumes a float delta, reads the followed actor, performs collision and smoothing work, and writes CameraActor+0x330..+0x34C.",
    },
    {
        "name": "Application_Scene_Actor_System_CameraActor_get_endpoint0_FUN_0060E7B0",
        "kind": "function",
        "address": "0x0060E7B0",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C559 2026-09-13] CameraActor vtable slot 34. Copies exactly four dwords from CameraActor+0x310..+0x31C to the caller output; this is a 0x10-byte endpoint record, not a 4x4 matrix.",
    },
    {
        "name": "Shader_indexed_parameter_submit_FUN_00419020",
        "kind": "function",
        "address": "0x00419020",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C559 2026-09-13] Indexed shader-parameter submission primitive. It passes a pointer through FUN_00419B60 and submits it with count 4 through [[BCS-Y-2247]]. The pointed-to type, count unit, index meaning, matrix interpretation, and camera provenance remain unresolved.",
    },
    {
        "name": "Shader_parameter_conditional_submit_FUN_00422F90",
        "kind": "function",
        "address": "0x00422F90",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C559 2026-09-13] Conditional shader-parameter submission wrapper. It invokes the selected parameter object's unresolved virtual setter only when unresolved FUN_00423A40 returns zero. C559 does not join that indirect target to the SetVertexShaderConstantF task family or identify a register or camera owner.",
    },
    {
        "name": "Shader_submit_global_parameter_blocks_FUN_00419240",
        "kind": "function",
        "address": "0x00419240",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C559 2026-09-13] On an anonymous selection change, submits three globals at 0x01328FF4, 0x01329034, and 0x01329074 with count 4 through [[BCS-Y-2247]]. The owning shader class, count unit, value semantics, matrix interpretation, and camera provenance remain unresolved.",
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
            for source_ref in SOURCE_REFS:
                if source_ref not in refs:
                    refs.append(source_ref)
            entry.update(refinement)
            entry["sourceRefs"] = refs

        for new_entry in NEW_SYMBOLS:
            address = new_entry["address"]
            if address in by_address:
                if by_address[address].get("name") != new_entry["name"]:
                    raise RuntimeError(f"promotion target already exists at {address}")
                continue
            allocated = _symbols_io.append_symbol(data, dict(new_entry))
            by_address[address] = data["symbols"][-1]
            print(f"{allocated} {address}")


if __name__ == "__main__":
    main()
