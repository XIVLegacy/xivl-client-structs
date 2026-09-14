"""Promote the local-player display-name access contract."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import _symbols_io  # noqa: E402


SOURCE_REFS = [
    "tools/ghidra/logs/c566_local-player-display-name.txt",
    "tools/ghidra/logs/c566_local-player-display-name-listing.txt",
    "tools/ghidra/logs/c566_local-player-helper-listing.txt",
    "manifests/local_player_display_name.json",
]


REFINEMENTS = {
    "0x00445CF0": {
        "notes": "[Tier C566 2026-09-14] Historical symbol name retained. This is the default constructor for the 0x54-byte SqexMiscUtf8StringLayout (BCS-S-0135): data points to this+0x12, capacity is 0x40, byte count including NUL is 1, +0x0C is zero, +0x10 and ownership_state +0x11 are one, and the first inline byte is NUL.",
    },
    "0x00447260": {
        "notes": "[Tier C566 2026-09-14] Sqex::Misc narrow-byte string constructor from a byte span. It default-constructs the 0x54-byte destination, derives strlen when the explicit length is 0xFFFFFFFF, reserves length+1 bytes through [[BCS-Y-2282]], copies exactly length bytes, and writes the trailing NUL. The destination +0x08 dword is therefore the current logical byte count including the terminator, not an unresolved state value. The helper performs no UTF-8 validation.",
    },
    "0x00CC7510": {
        "notes": "[Tier C566 2026-09-14] Historical symbol name retained. Exact body is MOV ECX,[ECX]; JMP 0x00CD7910. Given a pointer to a Component::Lua::GameEngine pointer, it returns the address of that GameEngine's +0x220 nil_holder field through BCS-Y-1675.",
    },
    "0x00CD7910": {
        "notes": "[Tier C566 2026-09-14] Historical symbol name retained. Exact body is LEA EAX,[ECX+0x220]; RET. With ECX equal to Component::Lua::GameEngine, it returns the address of the nil_holder field, not the holder pointer stored there.",
    },
}


NEW_SYMBOLS = [
    {
        "name": "Sqex_Misc_Utf8String_data_FUN_00445210",
        "kind": "function",
        "address": "0x00445210",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C566 2026-09-14] Leaf __thiscall accessor returning the char pointer at SqexMiscUtf8StringLayout+0x00. It supplies no length, validation, ownership, or synchronization and is not by itself a complete safe-copy API.",
    },
    {
        "name": "Sqex_Misc_Utf8String_reserve_bytes_FUN_00447010",
        "kind": "function",
        "address": "0x00447010",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C566 2026-09-14] __thiscall reserve helper with an explicit requested byte count and a mode byte that clears state +0x10 when nonzero. It stores the requested count at +0x08. Counts above +0x04 capacity allocate a 0x20-byte-rounded buffer, copy the old +0x08 bytes, release old storage only when ownership_state +0x11 is zero, set data/capacity, and clear +0x11; counts within capacity retain the existing data pointer. The count includes the trailing NUL on all witnessed string constructors and assignments.",
    },
    {
        "name": "Control_CharaBase_getDisplayName_NAPI_FUN_006FA4C0",
        "kind": "function",
        "address": "0x006FA4C0",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C566 2026-09-14] Control::CharaBase _getDisplayName N-API member. Signature is void __thiscall(CharaBase *this, ExecuteParameters *params), ending in RET 4. It reads this+0x60. When display_name_id is not -1 it marshals the identifier; when it is -1 it marshals the embedded string at state+0x04 and the kind byte at +0x58. This is a Lua result builder, not a native const-char getter, so external consumers should not call it outside an established Lua invocation.",
    },
    {
        "name": "Control_WorldMaster_getMyPlayer_NAPI_FUN_00707970",
        "kind": "function",
        "address": "0x00707970",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C566 2026-09-14] WorldMaster _getMyPlayer N-API implementation, a one-explicit-argument member-shaped function ending in RET 4; ECX is unused. From ExecuteParameters+0x04 it obtains a pointer to the Component::Lua::GameEngine pointer, follows GameEngine+0x220 -> [0] -> +0x04 -> +0x0C, and marshals the resulting Control::MyPlayer pointer through FUN_00748B30. The exact pointer chain supports read-only sampling from a RaptureElementContainer callback after the original update; the N-API function itself is not a native pointer getter, and C566 does not establish thread identity or a lock.",
    },
    {
        "name": "Control_CharaBase_setDisplayName_NAPI_FUN_00708200",
        "kind": "function",
        "address": "0x00708200",
        "confidence": "confirmed",
        "sourceRefs": SOURCE_REFS,
        "notes": "[Tier C566 2026-09-14] Control::CharaBase _setDisplayName N-API member. It parses a localized identifier or custom narrow-byte name and calls the same CharaBase+0x60 update helper used by SetDisplayNameReceiver. This proves the live display-name state is presentation data mutable by Lua and is not an immutable selected-character identity store; the client copy path does not validate UTF-8.",
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
            entry["notes"] = refinement["notes"]
            entry["sourceRefs"] = refs

        for new_entry in NEW_SYMBOLS:
            address = new_entry["address"]
            if address in by_address:
                if by_address[address].get("name") != new_entry["name"]:
                    raise RuntimeError(f"promotion target already exists at {address}")
                by_address[address].update(new_entry)
                continue
            allocated = _symbols_io.append_symbol(data, dict(new_entry))
            by_address[address] = data["symbols"][-1]
            print(f"{allocated} {address}")


if __name__ == "__main__":
    main()
