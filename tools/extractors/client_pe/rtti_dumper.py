"""RTTI extraction from a client PE image.

Scans the PE for `.?AV` markers, walks each to its TypeDescriptor,
locates the COL (CompleteObjectLocator), then finds the vtable via
the COL pointer at vtable[-1]. Also extracts base-class chains via
the ClassHierarchyDescriptor.

Output: list of RttiEntry tuples (mangled, demangled, td_va, col_va,
vtable_va, vtable_count, base_classes).
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

from . import IMAGE_BASE, RDATA_FILE_END, RDATA_FILE_START, TEXT_VA_END, TEXT_VA_START


@dataclass
class RttiEntry:
    mangled_name: str
    demangled_name: str
    type_descriptor_va: int
    complete_object_locator_va: int | None = None
    vtable_va: int | None = None
    vtable_entry_count: int | None = None
    base_classes: list[str] = field(default_factory=list)


def extract_all(exe_path: str | Path) -> list[RttiEntry]:
    data = Path(exe_path).read_bytes()
    results: list[RttiEntry] = []

    idx = 0
    while True:
        idx = data.find(b".?AV", idx)
        if idx < 0:
            break

        end = data.find(b"@@", idx)
        if end < 0:
            idx += 1
            continue
        end += 2
        if end < len(data) and data[end:end + 1] == b"@":
            end += 1

        mangled = data[idx:end].decode("ascii", errors="replace")
        td_file_off = idx - 8
        td_va = td_file_off + IMAGE_BASE

        demangled = demangle(mangled)

        col_va: int | None = None
        vtable_va: int | None = None
        vtable_count: int | None = None

        td_bytes = struct.pack("<I", td_va)
        i = RDATA_FILE_START
        while i < RDATA_FILE_END - 20:
            if data[i + 12:i + 16] == td_bytes:
                sig = struct.unpack_from("<I", data, i)[0]
                if sig == 0:
                    col_va = i + IMAGE_BASE

                    col_bytes = struct.pack("<I", col_va)
                    j = RDATA_FILE_START
                    while j < RDATA_FILE_END - 4:
                        if data[j:j + 4] == col_bytes:
                            candidate_vt = j + 4 + IMAGE_BASE
                            first = struct.unpack_from("<I", data, j + 4)[0]
                            if TEXT_VA_START <= first < TEXT_VA_END:
                                vtable_va = candidate_vt
                                count = 0
                                for k in range(500):
                                    entry = struct.unpack_from("<I", data, j + 4 + k * 4)[0]
                                    if entry < TEXT_VA_START or entry >= TEXT_VA_END:
                                        break
                                    count += 1
                                vtable_count = count
                                break
                        j += 4
                    break
            i += 4

        base_classes: list[str] = []
        if col_va is not None:
            col_off = col_va - IMAGE_BASE
            chd_va = struct.unpack_from("<I", data, col_off + 16)[0]
            if IMAGE_BASE <= chd_va < IMAGE_BASE + len(data):
                chd_off = chd_va - IMAGE_BASE
                num_bases = struct.unpack_from("<i", data, chd_off + 8)[0]
                bca_va = struct.unpack_from("<I", data, chd_off + 12)[0]

                if 0 < num_bases < 100 and IMAGE_BASE <= bca_va < IMAGE_BASE + len(data):
                    bca_off = bca_va - IMAGE_BASE
                    for b in range(1, num_bases):
                        bcd_va = struct.unpack_from("<I", data, bca_off + b * 4)[0]
                        if bcd_va < IMAGE_BASE or bcd_va >= IMAGE_BASE + len(data):
                            continue
                        bcd_off = bcd_va - IMAGE_BASE
                        base_td_va = struct.unpack_from("<I", data, bcd_off)[0]
                        if base_td_va < IMAGE_BASE or base_td_va >= IMAGE_BASE + len(data):
                            continue
                        base_td_off = base_td_va - IMAGE_BASE
                        name_off = base_td_off + 8
                        if name_off < len(data):
                            name_end = name_off
                            while name_end < len(data) and data[name_end] != 0:
                                name_end += 1
                            base_name = data[name_off:name_end].decode("ascii", errors="replace")
                            if base_name.startswith(".?AV"):
                                base_classes.append(demangle(base_name))

        results.append(RttiEntry(
            mangled_name=mangled,
            demangled_name=demangled,
            type_descriptor_va=td_va,
            complete_object_locator_va=col_va,
            vtable_va=vtable_va,
            vtable_entry_count=vtable_count,
            base_classes=base_classes,
        ))
        idx = end

    return results


def demangle(mangled: str) -> str:
    name = mangled
    if name.startswith(".?AV"):
        name = name[4:]
    elif name.startswith(".?AU"):
        name = name[4:]
    if name.endswith("@@"):
        name = name[:-2]

    if name.startswith("?$"):
        name = name[2:]
        at_idx = name.find("@")
        if at_idx > 0:
            template_name = name[:at_idx]
            rest = name[at_idx + 1:]
            template_params: list[str] = []
            outer_parts: list[str] = []
            depth = 0
            current: list[str] = []

            for c in rest:
                if c == "@":
                    if current:
                        token = "".join(current)
                        if token.startswith(("V", "U")):
                            if depth == 0:
                                template_params.append(token[1:])
                            else:
                                outer_parts.append(token)
                        else:
                            outer_parts.append(token)
                        current = []
                else:
                    current.append(c)

            outer_parts.reverse()
            ns = "::".join(outer_parts) + "::" if outer_parts else ""
            tparams = f"<{', '.join(template_params)}>" if template_params else ""
            return f"{ns}{template_name}{tparams}"

    parts = [p for p in name.split("@") if p]
    parts.reverse()
    return "::".join(parts)


def dump_to_file(exe_path: str | Path, output_path: str | Path) -> int:
    entries = extract_all(exe_path)
    output_path = Path(output_path)
    with output_path.open("w", encoding="utf-8") as f:
        from datetime import datetime
        f.write(f"// FFXIV 1.0 (1.23b) RTTI Database - {len(entries)} classes\n")
        f.write(f"// Generated from: {Path(exe_path).name}\n")
        f.write(f"// Date: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n")
        f.write("// Format: Demangled | VTable VA | VFunc Count | TypeDescriptor VA | Mangled\n")
        f.write("// -------------------------------------------------------------------------\n")
        for e in sorted(entries, key=lambda x: x.demangled_name):
            vt = f"0x{e.vtable_va:08X}" if e.vtable_va is not None else "          "
            count = f"{e.vtable_entry_count:>3}" if e.vtable_entry_count is not None else "   "
            f.write(f"{e.demangled_name:<90} | {vt} | {count} | 0x{e.type_descriptor_va:08X} | {e.mangled_name}\n")
    return len(entries)


def search_classes(exe_path: str | Path, pattern: str) -> list[RttiEntry]:
    pattern_low = pattern.lower()
    return sorted(
        (e for e in extract_all(exe_path)
         if pattern_low in e.demangled_name.lower() or pattern_low in e.mangled_name.lower()),
        key=lambda x: x.demangled_name,
    )


def dump_hierarchy(exe_path: str | Path, class_name: str, writer) -> None:
    entries = extract_all(exe_path)
    target = next((e for e in entries if class_name.lower() in e.demangled_name.lower()), None)
    if target is None:
        raise ValueError(f"Class '{class_name}' not found in RTTI")

    writer.write(f"// Inheritance hierarchy for: {target.demangled_name}\n\n")
    if target.base_classes:
        writer.write("// Direct + transitive bases:\n")
        for bc in target.base_classes:
            base_entry = next((e for e in entries if e.demangled_name == bc), None)
            vt_info = f"vt=0x{base_entry.vtable_va:08X}" if base_entry and base_entry.vtable_va else "no vtable"
            writer.write(f"//   <- {bc} ({vt_info})\n")
    else:
        writer.write("// No base classes (root type)\n")

    writer.write("\n// Derived classes:\n")
    derived = sorted(
        (e for e in entries if target.demangled_name in e.base_classes),
        key=lambda x: x.demangled_name,
    )
    if derived:
        for d in derived:
            writer.write(f"//   -> {d.demangled_name}\n")
    else:
        writer.write("//   (none found)\n")


def dump_vtable(exe_path: str | Path, class_name: str, output_path: str | Path) -> None:
    entries = extract_all(exe_path)
    target = next((e for e in entries if class_name.lower() in e.demangled_name.lower()), None)
    if target is None or target.vtable_va is None:
        raise ValueError(f"Class '{class_name}' not found or has no vtable")

    data = Path(exe_path).read_bytes()
    file_off = target.vtable_va - IMAGE_BASE
    output_path = Path(output_path)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(f"// {target.demangled_name}\n")
        f.write(f"// VTable: 0x{target.vtable_va:08X} ({target.vtable_entry_count} entries)\n\n")
        for i in range(target.vtable_entry_count or 0):
            addr = struct.unpack_from("<I", data, file_off + i * 4)[0]
            f.write(f"vt[{i:>3}] = 0x{addr:08X}\n")
