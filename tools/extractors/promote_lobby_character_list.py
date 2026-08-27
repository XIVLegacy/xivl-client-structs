#!/usr/bin/env python3
"""Promote the canonical lobby character-list projection into BCS catalogs."""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from _structs_io import load_structs, structs_transaction  # noqa: E402
from _symbols_io import load_symbols, symbols_transaction  # noqa: E402

SOURCE_REF = "manifests/lobby_character_list_projection.json"


STRUCT_UPDATES = {
    "BCS-S-0008": {
        "name": "CharaListPerCharacterRecord",
        "namespace": "FFXIV.Client.Network",
        "size": "0x1D0",
        "confidence": "confirmed",
        "sourceRefs": [SOURCE_REF, "mdi-014"],
        "fields": [
            {
                "offset": "0x00",
                "size": "0x04",
                "name": "logged_u32",
                "type": "uint32_t",
                "notes": "Record 0 only. BCS-Y-0017 reads this value and sends it to a numeric logger before calling FUN_00DA76B0; its semantic role remains opaque.",
            },
            {
                "offset": "0x04",
                "size": "0x04",
                "name": "opaque_04",
                "type": "byte[4]",
                "notes": "Not read by the bounded opcode-0x000D route.",
            },
            {
                "offset": "0x08",
                "size": "0x01",
                "name": "control_flags",
                "type": "uint8_t",
                "notes": "Record 0 only. When bits 1..7 are all clear, FUN_00DA76B0 clears the existing slot vector before processing. The parser returns the inverse of bit 0; a set bit makes the outer ServiceLoginOperation handler call FUN_00DA5030 and return 0.",
            },
            {
                "offset": "0x09",
                "size": "0x01",
                "name": "record_count",
                "type": "uint8_t",
                "notes": "Record 0 only. Read as a byte by the outer numeric logger and as FUN_00DA76B0's loop bound. The parser receives no payload length and does not validate count against the available bytes.",
            },
            {
                "offset": "0x0A",
                "size": "0x0A",
                "name": "opaque_0A",
                "type": "byte[10]",
                "notes": "Not read by the bounded opcode-0x000D route.",
            },
            {
                "offset": "0x14",
                "size": "0x04",
                "name": "equality_key",
                "type": "uint32_t",
                "notes": "Bulk-copied to destination+0x04. FUN_00DA9550 compares it with +0x04 of each 0x30-stride operation record; no domain noun is established.",
            },
            {
                "offset": "0x18",
                "size": "0x01",
                "name": "slot_key_and_flags",
                "type": "uint8_t",
                "notes": "FUN_00DA76B0 uses bits 0..5 as the lookup key. On insertion, nonzero upper bits cause every destination slot byte at +0x08 to be masked with 0x3F.",
            },
            {
                "offset": "0x19",
                "size": "0x37",
                "name": "opaque_19",
                "type": "byte[55]",
                "notes": "Bulk-copied from record+0x19 to destination+0x09 but not otherwise interpreted by the bounded route.",
            },
            {
                "offset": "0x50",
                "size": "variable",
                "name": "append_c_string",
                "type": "char[]",
                "notes": "On an existing low-six-bit key match, FUN_00DA76B0 scans from this byte to the first NUL and copies the string including its terminator to the first NUL at destination slot+0x40. Neither scan nor the append has a parser-side bound. Bytes after the terminator through record+0x1CF remain opaque.",
            },
        ],
        "notes": "Opcode-0x000D parser window at body + index*0x1D0. New keys project record+0x10 for 0x1D0 bytes into BCS-S-0009; that source reaches record+0x1DF, 0x10 bytes beyond this nominal window. Repeated low-six-bit keys append the NUL-terminated string beginning at record+0x50. The restricted retail fixture confirms one type-0x000D occurrence in one of two deterministically labeled lobby sessions, a client-read count of one in a body with two-entry capacity, an all-zero unused entry, and string termination inside the copied source. It cannot classify type-0x000D fields invariant or dynamic across sessions because the other session has no such opcode. Unnamed spans remain opaque; former server-lineage field names were removed because this client route does not consume them.",
    },
    "BCS-S-0009": {
        "name": "CharaMakeSlotEntry",
        "namespace": "FFXIV.Client.Lobby",
        "size": "0x2E0",
        "confidence": "probable",
        "sourceRefs": [SOURCE_REF, "mdi-025"],
        "fields": [
            {
                "offset": "0x000",
                "size": "0x1D0",
                "name": "wire_projection",
                "type": "byte[464]",
                "notes": "Plain copy of record+0x10..record+0x1DF for opcode 0x000D. The projection is source-relative and does not assign semantics to opaque wire bytes.",
            },
            {
                "offset": "0x004",
                "size": "0x04",
                "name": "equality_key",
                "type": "uint32_t",
                "notes": "FUN_00DA9550 compares this dword with +0x04 of each 0x30-stride operation record before calling FUN_00DA94C0. The bounded route proves equality-key use, not a domain noun.",
            },
            {
                "offset": "0x008",
                "size": "0x01",
                "name": "slot_key_and_flags",
                "type": "uint8_t",
                "notes": "Lookup byte used by FUN_00DA76B0. Bits 0..5 are the key; the insertion normalization path clears bits 6..7 across all slots.",
            },
            {
                "offset": "0x040",
                "size": "variable",
                "name": "append_c_string",
                "type": "char[]",
                "notes": "Destination C string scanned from +0x40 and extended for repeated low-six-bit keys. The parser provides no destination bound or capacity check.",
            },
            {
                "offset": "0x1D0",
                "size": "0x100",
                "name": "zero_initialized_opaque_state",
                "type": "byte[256]",
                "notes": "Zeroed in the temporary slot buffer before push, then copied as 0x40 dwords by FUN_00891360. No semantic consumer is established in the bounded chain.",
            },
            {
                "offset": "0x2D0",
                "size": "0x10",
                "name": "embedded_0x30_stride_vector",
                "type": "std::vector<opaque_0x30_byte_element>",
                "notes": "FUN_00890EE0 copy-constructs this embedded container. The control word at +0x00 remains opaque; begin/end/capacity at +0x04/+0x08/+0x0C are initialized to zero and populated only when the source has elements. Element stride 0x30 is proven, but the generic helper does not uniquely establish an element domain type.",
            },
        ],
        "notes": "0x2E0-byte destination used by the slot vector at CharaMakeOperation+0x1D0. FUN_00DA76B0 prepares 0x1D0 copied bytes, 0x100 zero bytes, and an empty embedded vector; FUN_00891F00 pushes it. The construction chain FUN_00891900 -> FUN_008916F0 -> FUN_008913E0 -> FUN_00891360 copies the two plain regions and delegates the final 0x10 bytes to FUN_00890EE0. This corrects the former 0x110 zero-region claim and removes unsupported source-specific names from the wire projection.",
    },
}


SYMBOL_UPDATES = {
    "BCS-Y-0017": {
        "notes": "Lobby operation receive dispatcher. Case 0x000D reads packet body+0x00 as a u32 for a numeric logger and body+0x09 as a u8 for the count logger, then calls FUN_00DA76B0 with packet+0x10. If that parser returns 0, it calls FUN_00DA5030 on this+0x34 and returns 0. Cases 0x0015, 0x0016, and 0x0017 route the other list records. See manifests/lobby_character_list_projection.json. [apply-log fix] Address shifted from 0x009AA9F0 to 0x00DAA9F0 (+0x00400000) per the catalog-validation-report pass TYPO_RVA_NOT_VA finding: catalog originally stored the RVA instead of the PE-image-base VA; shifted address matches the FUN_<hex> function entry Ghidra resolves at the corrected VA."
    },
    "BCS-Y-0019": {
        "notes": "Direct s2c opcode-0x000D parser reached only from BCS-Y-0017 with packet+0x10. It clears the slot vector when body+0x08 bits 1..7 are zero, loops over the u8 count at body+0x09 with 0x1D0 record-window stride, and looks up each record+0x18 low-six-bit key in the 0x2E0-stride vector at this+0x1D0. Existing keys append the unbounded NUL-terminated record+0x50 string to the first NUL at slot+0x40. New keys copy record+0x10 for 0x1D0 bytes, zero 0x100 bytes, initialize an empty embedded vector, and push through BCS-Y-0023; upper key bits request a 0x3F mask over every destination key byte. The parser returns the inverse of control-flags bit 0. It has vector-state checks through FUN_009D22B4 but no payload-length, count-to-length, string-scan, or append-capacity validation. See manifests/lobby_character_list_projection.json and its sanitized restricted-capture fixture. | [hygiene systematic-rva-not-va-address-shift] Address shifted from 0x009A76B0 to 0x00DA76B0 (+0x00400000) per the matrix-s2c-wire-name-backfill pass audit. The catalog-validation-report pass's PASS_DATA classification let this entry escape the apply-log pass's bulk fix; the entry's own metadata self-described the VA. Evidence: unambiguous_shift; evidence=name_fun_token; count=1."
    },
    "BCS-Y-0023": {
        "notes": "std::vector::push_back specialization for 0x2E0-byte BCS-S-0009 entries. With spare capacity it copy-constructs one element at end through FUN_00891900 and advances end by 0x2E0. Otherwise it validates end >= begin and delegates growth/insertion to FUN_00891E50. It does not parse wire fields. See manifests/lobby_character_list_projection.json. [apply-log fix] Address shifted from 0x00491F00 to 0x00891F00 (+0x00400000) per the catalog-validation-report pass TYPO_RVA_NOT_VA finding: catalog originally stored the RVA instead of the PE-image-base VA; shifted address matches the FUN_<hex> function entry Ghidra resolves at the corrected VA."
    },
    "BCS-Y-0079": {
        "notes": "BCS-S-0009 copy-constructor. It copies 0x74 dwords (0x1D0 bytes) from source+0x000, then 0x40 dwords (0x100 bytes) from source+0x1D0, and delegates the embedded 0x10-byte container at +0x2D0 to FUN_00890EE0. The two plain ranges plus the container close the exact 0x2E0 destination layout. See manifests/lobby_character_list_projection.json. [apply-log fix] Address shifted from 0x00491360 to 0x00891360 (+0x00400000) per the catalog-validation-report pass TYPO_RVA_NOT_VA finding: catalog originally stored the RVA instead of the PE-image-base VA; shifted address matches the FUN_<hex> function entry Ghidra resolves at the corrected VA."
    },
    "BCS-Y-0080": {
        "name": "SlotEmbeddedVectorCopyConstructor_FUN_00890EE0",
        "confidence": "confirmed",
        "notes": "Copy-constructor for the embedded container at BCS-S-0009+0x2D0. It derives source count from begin/end at +0x04/+0x08 with element stride 0x30, zeroes destination begin/end/capacity at +0x04/+0x08/+0x0C, rejects counts above 0x05555555 through FUN_006D20B0, allocates count*0x30 bytes for a nonempty source, and copy-constructs the range. The control word at +0x00 is not interpreted here, and the generic 0x30 stride does not uniquely prove an element domain type. See manifests/lobby_character_list_projection.json. [apply-log fix] Address shifted from 0x00490EE0 to 0x00890EE0 (+0x00400000) per the catalog-validation-report pass TYPO_RVA_NOT_VA finding: catalog originally stored the RVA instead of the PE-image-base VA; shifted address matches the FUN_<hex> function entry Ghidra resolves at the corrected VA."
    },
    "BCS-Y-0091": {
        "notes": "Walks the operation-level vector at param_2 in 0x30-byte steps. For each element whose +0x04 dword equals the newly inserted BCS-S-0009 slot's +0x04 join key, it calls FUN_00DA94C0 with the slot retained as this. Every begin/end and per-element access is guarded through FUN_009D22B4. This proves equality-key use and the 0x30 stride, but not a unique domain noun for the generic record type. Called only from FUN_00DA76B0 after a new slot push. See manifests/lobby_character_list_projection.json. [apply-log fix] Address shifted from 0x009A9550 to 0x00DA9550 (+0x00400000) per the catalog-validation-report pass TYPO_RVA_NOT_VA finding: catalog originally stored the RVA instead of the PE-image-base VA; shifted address matches the FUN_<hex> function entry Ghidra resolves at the corrected VA."
    },
}


def _updated(data: dict, updates: dict, key: str) -> dict:
    result = copy.deepcopy(data)
    index = {entry["id"]: entry for entry in result[key]}
    missing = sorted(set(updates) - set(index))
    if missing:
        raise ValueError(f"missing catalog ids: {', '.join(missing)}")
    for entry_id, fields in updates.items():
        entry = index[entry_id]
        entry.update(copy.deepcopy(fields))
        refs = entry.setdefault("sourceRefs", [])
        if SOURCE_REF not in refs:
            refs.append(SOURCE_REF)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if catalog promotion drifted")
    args = parser.parse_args()

    structs = load_structs()
    symbols = load_symbols()
    expected_structs = _updated(structs, STRUCT_UPDATES, "structs")
    expected_symbols = _updated(symbols, SYMBOL_UPDATES, "symbols")
    if args.check:
        drift = structs != expected_structs or symbols != expected_symbols
        print("lobby character-list promotion: " + ("drift" if drift else "current"))
        return 1 if drift else 0

    with structs_transaction() as current:
        updated = _updated(current, STRUCT_UPDATES, "structs")
        current.clear()
        current.update(updated)
    with symbols_transaction() as current:
        updated = _updated(current, SYMBOL_UPDATES, "symbols")
        current.clear()
        current.update(updated)
    print("lobby character-list promotion: updated BCS-S-0008/0009 and related symbols")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
