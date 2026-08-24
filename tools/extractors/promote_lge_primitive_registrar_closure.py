#!/usr/bin/env python3
"""Promote the verified LGE primitive registrar closure into symbols.json."""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import _symbols_io  # noqa: E402


SOURCE = "manifests/lge_primitive_registrar_closure.json"

UPDATES = {
    "BCS-Y-0231": {
        "name": "Control::Global::vftable_slot2_lua_registrar_owner_FUN_007582E0",
        "notes": "Application::Lua::Script::Client::Control::Global has a 34-slot primary vftable at 0x00FD60AC (RTTI TypeDescriptor 0x012C27C0). Slot 2, stored at 0x00FD60B4, is FUN_007582E0. Its guarded direct-callee list includes the confirmed _defineClass registrar at 0x0073C270, _defineBaseClass registrar at 0x0073C3C0, and _isInstanceOf registrar at 0x00753470. Those registrars pass their handler addresses to FUN_00726E00; the handlers are invoked indirectly and are not callback fire sites.",
    },
    "BCS-Y-0484": {
        "name": "LuaNApiHandler__defineClass_FUN_006DCC30",
        "notes": "Registered handler wrapper for _defineClass. Global registrar owner FUN_007582E0 directly calls per-name registrar FUN_0073C270, whose exact string reference is 0x0073C359 -> 0x00FD7354 and whose binder argument is FUN_006DCC30. The handler has no recorded direct callers because Lua dispatch is indirect. It directly calls inner implementation FUN_0078C2A0, which reads child and parent from two 0x10-byte argument slots, links them through FUN_00CC7050, and follows FUN_00CC71F0 -> FUN_00CD9C10 to create/find the registry record and clear +0x7C. This is registration and invocation plumbing, not a callback fire site.",
    },
    "BCS-Y-0487": {
        "name": "LuaNApiHandler__defineBaseClass_FUN_006DCCA0",
        "notes": "Registered handler wrapper for _defineBaseClass. Global registrar owner FUN_007582E0 directly calls per-name registrar FUN_0073C3C0, whose exact string reference is 0x0073C4A9 -> 0x00FD7364 and whose binder argument is FUN_006DCCA0. The handler has no recorded direct callers because Lua dispatch is indirect. It directly calls inner implementation FUN_0078C330, which reads child and parent from two 0x10-byte argument slots, links them through FUN_00CC7050, and follows FUN_00CC71E0 -> FUN_00CD9BC0 to create/find the registry record and clear +0x7B. This is registration and invocation plumbing, not a callback fire site.",
    },
    "BCS-Y-0512": {
        "name": "LuaNApiInner__defineClass_FUN_0078C2A0_and__defineBaseClass_FUN_0078C330",
        "address": "0x0078C2A0;0x0078C330",
        "notes": "Paired inner implementations reached directly from the registered wrappers: FUN_006DCC30 -> FUN_0078C2A0 for _defineClass and FUN_006DCCA0 -> FUN_0078C330 for _defineBaseClass. Both read child and parent from two 0x10-byte argument slots and link them through FUN_00CC7050. FUN_0078C2A0 then uses the utility-class path FUN_00CC71F0 -> FUN_00CD9C10, which clears registry-record +0x7C; FUN_0078C330 uses the BaseClass path FUN_00CC71E0 -> FUN_00CD9BC0, which clears +0x7B.",
    },
    "BCS-Y-0521": {
        "name": "GroupSharedWork_GetName__globalSave_FUN_006DA450",
        "notes": "Application::Lua::Script::Client::Group::SharedWork vftable slot 5. The only recorded reference to FUN_006DA450 is the function pointer at 0x00FD4348, within the RTTI-confirmed 28-slot SharedWork vftable at 0x00FD4334. The function constructs _globalSave from string VA 0x00FD43F4 into the caller-supplied string result and returns it. It is a virtual name getter with no direct callers, not a static initializer, registrar, registered handler, or callback fire site.",
    },
    "BCS-Y-0522": {
        "name": "GroupSharedWork_GetName__globalTemp_FUN_006DA4C0",
        "notes": "Application::Lua::Script::Client::Group::SharedWork vftable slot 6. The only recorded reference to FUN_006DA4C0 is the function pointer at 0x00FD434C, within the RTTI-confirmed 28-slot SharedWork vftable at 0x00FD4334. The function constructs _globalTemp from string VA 0x00FD4400 into the caller-supplied string result and returns it. It is a virtual name getter with no direct callers, not a static initializer, registrar, registered handler, or callback fire site.",
    },
    "BCS-Y-0523": {
        "name": "GroupSharedWork_GetName__memberSave_FUN_006DA530",
        "notes": "Application::Lua::Script::Client::Group::SharedWork vftable slot 7. The only recorded reference to FUN_006DA530 is the function pointer at 0x00FD4350, within the RTTI-confirmed 28-slot SharedWork vftable at 0x00FD4334. The function constructs _memberSave from string VA 0x00FD440C into the caller-supplied string result and returns it. It is a virtual name getter with no direct callers, not a static initializer, registrar, registered handler, or callback fire site.",
    },
    "BCS-Y-0893": {
        "notes": "RTTI vftable for Application::Lua::Script::Client::Group::SharedWork at 0x00FD4334 (TypeDescriptor 0x012BFA88), with 28 slots. Slots 5, 6, and 7 are virtual name getters FUN_006DA450 (_globalSave), FUN_006DA4C0 (_globalTemp), and FUN_006DA530 (_memberSave); each function's only recorded reference is its vftable pointer. The work table is populated by the 0x017F..0x0186 GroupMembers/ContentMembers paths and carries the Group member, property, and WorkSync pipelines.",
    },
    "BCS-Y-0371": {
        "notesReplace": {
            "- Global @ FUN_007582E0 (BCS-Y-0231): 10 APIs, not 8.": "- Global @ FUN_007582E0 (BCS-Y-2145): 10 APIs in this map, not 8."
        },
    },
}

ADDITIONS = [
    {
        "name": "Control_Global_NApiRegistrarOwner_FUN_007582E0",
        "kind": "function",
        "address": "0x007582E0",
        "confidence": "confirmed",
        "sourceRefs": [SOURCE, "manifests/symbols.json#BCS-Y-0231"],
        "notes": "Control::Global vftable slot 2 and owner of the class's guarded registration sequence. It directly calls the confirmed _defineClass registrar at 0x0073C270, _defineBaseClass registrar at 0x0073C3C0, and _isInstanceOf registrar at 0x00753470. The function itself has no direct callers because its only recorded reference is the primary Global vftable entry at 0x00FD60B4.",
    },
    {
        "name": "LuaNApiRegistrar__defineClass_FUN_0073C270",
        "kind": "function",
        "address": "0x0073C270",
        "confidence": "confirmed",
        "sourceRefs": [SOURCE, "manifests/symbols.json#BCS-Y-0484"],
        "notes": "Per-name registrar for _defineClass. Its sole direct caller is Global registrar owner FUN_007582E0. It passes registered handler FUN_006DCC30 to FUN_00726E00 and associates exact string VA 0x00FD7354 before finalization.",
    },
    {
        "name": "LuaNApiRegistrar__defineBaseClass_FUN_0073C3C0",
        "kind": "function",
        "address": "0x0073C3C0",
        "confidence": "confirmed",
        "sourceRefs": [SOURCE, "manifests/symbols.json#BCS-Y-0487"],
        "notes": "Per-name registrar for _defineBaseClass. Its sole direct caller is Global registrar owner FUN_007582E0. It passes registered handler FUN_006DCCA0 to FUN_00726E00 and associates exact string VA 0x00FD7364 before finalization.",
    },
    {
        "name": "LuaNApiRegistrar__isInstanceOf_FUN_00753470",
        "kind": "function",
        "address": "0x00753470",
        "confidence": "confirmed",
        "sourceRefs": [SOURCE, "manifests/control_class_napi_field_access_recursive.json"],
        "notes": "Per-name registrar for _isInstanceOf. Its sole direct caller is Global registrar owner FUN_007582E0. It passes registered handler FUN_006FF210 to FUN_00726E00 and associates exact string VA 0x00FD8314 before finalization.",
    },
    {
        "name": "LuaNApiHandler__isInstanceOf_FUN_006FF210",
        "kind": "function",
        "address": "0x006FF210",
        "confidence": "confirmed",
        "sourceRefs": [SOURCE, "manifests/control_class_napi_field_access_recursive.json"],
        "notes": "Registered handler for Global _isInstanceOf, stored by registrar FUN_00753470 and therefore reached indirectly with no recorded direct callers. It rejects a first argument whose tag is not 4, extracts its LuaControl pointer plus a requested class name, returns true for ActorBaseClass, uses MSVC __RTDynamicCast for CharaBaseClass, PlayerBaseClass, NpcBaseClass, AreaBaseClass, DirectorBaseClass, and DesktopWidget, and otherwise checks the object's LGE class-registry chain by name through FUN_00CC7210. It packages the result as a Lua boolean and has no network-send or callback-fire path.",
    },
]


def apply_updates(data: dict) -> list[str]:
    by_id = {entry["id"]: entry for entry in data["symbols"]}
    for symbol_id, patch in UPDATES.items():
        if symbol_id not in by_id:
            raise ValueError(f"missing required symbol {symbol_id}")
        patch = copy.deepcopy(patch)
        replacements = patch.pop("notesReplace", {})
        for old, new in replacements.items():
            notes = by_id[symbol_id].get("notes", "")
            if old in notes:
                by_id[symbol_id]["notes"] = notes.replace(old, new)
            elif new not in notes:
                raise ValueError(f"{symbol_id}: expected note text is missing")
        by_id[symbol_id].update(patch)
        refs = list(by_id[symbol_id].get("sourceRefs", []))
        if SOURCE not in refs:
            refs.append(SOURCE)
        by_id[symbol_id]["sourceRefs"] = refs

    existing = {entry["name"]: entry for entry in data["symbols"]}
    allocated: list[str] = []
    for addition in ADDITIONS:
        if addition["name"] in existing:
            current = existing[addition["name"]]
            if current.get("address") != addition["address"]:
                raise ValueError(f"existing symbol address drifted: {addition['name']}")
            current.update(copy.deepcopy(addition))
            allocated.append(current["id"])
            continue
        symbol_id = _symbols_io.append_symbol(data, copy.deepcopy(addition))
        allocated.append(symbol_id)
    return allocated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        current = _symbols_io.load_symbols()
        expected = copy.deepcopy(current)
        ids = apply_updates(expected)
        if current != expected:
            print("error: LGE primitive registrar closure is not promoted", file=sys.stderr)
            return 1
        print(f"OK: LGE primitive registrar closure is current ({', '.join(ids)})")
        return 0

    with _symbols_io.symbols_transaction() as data:
        ids = apply_updates(data)
    print(f"Promoted LGE primitive registrar closure ({', '.join(ids)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
