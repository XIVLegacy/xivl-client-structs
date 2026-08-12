"""PE import table walker.

Reads the PE optional-header import directory, walks each
IMAGE_IMPORT_DESCRIPTOR (20 bytes), resolves each Import Lookup
Table to hint/name entries, and outputs DLL -> [function names].
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ImportEntry:
    dll_name: str
    functions: list[str] = field(default_factory=list)


def extract(exe_path: str | Path) -> list[ImportEntry]:
    data = Path(exe_path).read_bytes()
    pe_off = struct.unpack_from("<i", data, 0x3C)[0]
    opt_off = pe_off + 24

    num_sections = struct.unpack_from("<H", data, pe_off + 6)[0]
    opt_header_size = struct.unpack_from("<H", data, pe_off + 20)[0]
    section_table_off = pe_off + 24 + opt_header_size

    import_dir_rva = struct.unpack_from("<I", data, opt_off + 104)[0]
    if import_dir_rva == 0:
        return []

    import_file_off = rva_to_file_offset(data, import_dir_rva, section_table_off, num_sections)
    if import_file_off < 0:
        return []

    results: list[ImportEntry] = []

    i = 0
    while True:
        entry_off = import_file_off + i * 20
        name_rva = struct.unpack_from("<I", data, entry_off + 12)[0]
        if name_rva == 0:
            break

        name_off = rva_to_file_offset(data, name_rva, section_table_off, num_sections)
        if name_off < 0:
            i += 1
            continue

        dll_name = read_cstring(data, name_off)
        functions: list[str] = []

        ilt_rva = struct.unpack_from("<I", data, entry_off)[0]
        if ilt_rva == 0:
            ilt_rva = struct.unpack_from("<I", data, entry_off + 16)[0]
        if ilt_rva == 0:
            results.append(ImportEntry(dll_name, functions))
            i += 1
            continue

        ilt_off = rva_to_file_offset(data, ilt_rva, section_table_off, num_sections)
        if ilt_off < 0:
            results.append(ImportEntry(dll_name, functions))
            i += 1
            continue

        j = 0
        while True:
            thunk = struct.unpack_from("<I", data, ilt_off + j * 4)[0]
            if thunk == 0:
                break
            if thunk & 0x80000000:
                functions.append(f"Ordinal #{thunk & 0xFFFF}")
            else:
                hint_name_off = rva_to_file_offset(data, thunk, section_table_off, num_sections)
                if hint_name_off >= 0:
                    fname = read_cstring(data, hint_name_off + 2)
                    functions.append(fname)
            j += 1

        results.append(ImportEntry(dll_name, functions))
        i += 1

    return results


def dump_to_file(exe_path: str | Path, output_path: str | Path) -> None:
    imports = extract(exe_path)
    output_path = Path(output_path)
    with output_path.open("w", encoding="utf-8") as f:
        f.write("// FFXIV 1.0 (1.23b) Import Table\n")
        f.write(f"// Generated from: {Path(exe_path).name}\n\n")
        for dll in imports:
            f.write(f"[{dll.dll_name}] ({len(dll.functions)} imports)\n")
            for func in dll.functions:
                f.write(f"  {func}\n")
            f.write("\n")


def rva_to_file_offset(pe: bytes, rva: int, section_table_off: int, num_sections: int) -> int:
    for i in range(num_sections):
        sec_off = section_table_off + i * 40
        va = struct.unpack_from("<I", pe, sec_off + 12)[0]
        raw_size = struct.unpack_from("<I", pe, sec_off + 16)[0]
        raw_ptr = struct.unpack_from("<I", pe, sec_off + 20)[0]
        v_size = struct.unpack_from("<I", pe, sec_off + 8)[0]
        if va <= rva < va + max(v_size, raw_size):
            return raw_ptr + (rva - va)
    return -1


def read_cstring(data: bytes, offset: int) -> str:
    end = offset
    while end < len(data) and data[end] != 0:
        end += 1
    return data[offset:end].decode("ascii", errors="replace")
