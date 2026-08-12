"""Struct layout extraction from constructor patterns.

Workflow:
- locate class via RTTI sweep
- find its constructor by scanning .text for `MOV [r/m], vtable_va`
- locate the allocation size from any caller that does `PUSH size; CALL ctor`
- scan the ctor body for field-init instructions (MOV imm/reg, MOVSS, MOVSD)
- scan for embedded sub-object init: `LEA ecx, [this+disp]; CALL sub_ctor`
- scan for base-class ctor calls: `MOV ecx, esi/edi/ebx; CALL base_ctor`

x86 opcode bytes used:
  C3              RET
  C2 imm16        RET imm16
  CC              INT3
  55 8B EC        push ebp; mov ebp, esp  (prologue)
  C6              MOV r/m8, imm8
  C7              MOV r/m32, imm32
  66 C7           MOV r/m16, imm16
  66 89           MOV r/m16, reg16
  89              MOV r/m32, reg32
  F3 0F 11        MOVSS r/m32, xmmN
  F2 0F 11        MOVSD r/m64, xmmN
  8D              LEA reg, r/m
  E8 rel32        CALL near
  8B C1/CB/CE/CF  MOV ecx, reg
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

from . import (
    IMAGE_BASE,
    TEXT_FILE_END,
    TEXT_FILE_START,
)
from .rtti_dumper import RttiEntry, extract_all


@dataclass
class FieldStore:
    va: int
    offset: int
    type: str
    value: str


@dataclass
class SubObject:
    offset: int
    ctor_va: int
    class_name: str | None
    vtable_va: int | None


@dataclass
class InheritanceInfo:
    class_name: str
    ctor_va: int
    vtable_va: int | None
    fields: list[FieldStore]


@dataclass
class StructLayout:
    class_name: str
    vtable_va: int | None
    vtable_entry_count: int
    ctor_va: int
    alloc_size: int | None
    fields: list[FieldStore]
    sub_objects: list[SubObject]
    base_ctors: list[InheritanceInfo] = field(default_factory=list)


def analyze(exe_bytes: bytes, class_name: str, exe_path: str | Path) -> StructLayout:
    entries = extract_all(exe_path)
    target = next((e for e in entries if class_name.lower() in e.demangled_name.lower()), None)
    if target is None:
        raise ValueError(f"Class '{class_name}' not found in RTTI")

    ctor_va = find_constructor(exe_bytes, target.vtable_va)
    if ctor_va == 0:
        raise ValueError(f"Constructor not found for '{class_name}'")

    alloc_size = find_alloc_size(exe_bytes, ctor_va)
    fields = extract_field_stores(exe_bytes, ctor_va)
    sub_objects = extract_sub_objects(exe_bytes, ctor_va, entries)
    base_ctors = extract_base_ctor_calls(exe_bytes, ctor_va, entries)

    return StructLayout(
        class_name=target.demangled_name,
        vtable_va=target.vtable_va,
        vtable_entry_count=target.vtable_entry_count or 0,
        ctor_va=ctor_va,
        alloc_size=alloc_size,
        fields=fields,
        sub_objects=sub_objects,
        base_ctors=base_ctors,
    )


def find_constructor(exe_bytes: bytes, vtable_va: int | None) -> int:
    if vtable_va is None:
        return 0
    vt_bytes = struct.pack("<I", vtable_va)

    i = TEXT_FILE_START
    while i < TEXT_FILE_END - 10:
        if exe_bytes[i] != 0xC7:
            i += 1
            continue
        modrm = exe_bytes[i + 1]
        mod = (modrm >> 6) & 3
        reg = (modrm >> 3) & 7
        rm = modrm & 7
        if reg != 0:
            i += 1
            continue

        if mod == 0 and rm not in (4, 5):
            imm_offset = 2
        elif mod == 1 and rm != 4:
            imm_offset = 3
        elif mod == 2 and rm != 4:
            imm_offset = 6
        else:
            i += 1
            continue

        if i + imm_offset + 4 > len(exe_bytes):
            i += 1
            continue

        if mod == 1 and exe_bytes[i + 2] > 8:
            i += 1
            continue
        if mod == 2:
            d = struct.unpack_from("<I", exe_bytes, i + 2)[0]
            if d > 8:
                i += 1
                continue

        if exe_bytes[i + imm_offset:i + imm_offset + 4] != vt_bytes:
            i += 1
            continue

        func_start = find_func_start(exe_bytes, i + IMAGE_BASE)
        if func_start:
            return func_start
        i += 1
    return 0


def find_func_start(exe_bytes: bytes, va: int) -> int:
    file_off = va - IMAGE_BASE
    lower_bound = max(1, file_off - 0x500)
    for i in range(file_off, lower_bound, -1):
        if i + 2 >= len(exe_bytes):
            continue
        if exe_bytes[i] == 0x55 and exe_bytes[i + 1] == 0x8B and exe_bytes[i + 2] == 0xEC:
            if i > 0 and exe_bytes[i - 1] in (0xC3, 0xCC, 0x90, 0xC2):
                return i + IMAGE_BASE
    return 0


def find_alloc_size(exe_bytes: bytes, ctor_va: int) -> int | None:
    i = TEXT_FILE_START
    while i < TEXT_FILE_END - 5:
        if exe_bytes[i] != 0xE8:
            i += 1
            continue
        rel = struct.unpack_from("<i", exe_bytes, i + 1)[0]
        dest = (i + 5 + IMAGE_BASE) + rel
        if (dest & 0xFFFFFFFF) != ctor_va:
            i += 1
            continue
        for j in range(1, 80):
            if i - j < 0:
                break
            if exe_bytes[i - j] == 0x68:
                size = struct.unpack_from("<I", exe_bytes, i - j + 1)[0]
                if 0x20 < size < 0x100000:
                    return size
        i += 1
    return None


def extract_field_stores(exe_bytes: bytes, ctor_va: int) -> list[FieldStore]:
    fields: list[FieldStore] = []
    file_off = ctor_va - IMAGE_BASE
    scan_len = 8192
    reg32_names = ("eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi")
    reg16_names = ("ax", "cx", "dx", "bx", "sp", "bp", "si", "di")

    for i in range(scan_len):
        off = file_off + i
        if off >= len(exe_bytes) - 10:
            break
        va = ctor_va + i
        b = exe_bytes[off]

        if b == 0xC7:
            modrm = exe_bytes[off + 1]
            mod = (modrm >> 6) & 3
            reg = (modrm >> 3) & 7
            rm = modrm & 7
            if reg == 0 and rm not in (4, 5):
                if mod == 2:
                    disp = struct.unpack_from("<I", exe_bytes, off + 2)[0]
                    imm = struct.unpack_from("<I", exe_bytes, off + 6)[0]
                    if 0 < disp < 0x10000:
                        fields.append(FieldStore(va, disp, "dword", f"0x{imm:08X}"))
                elif mod == 1:
                    disp = exe_bytes[off + 2]
                    imm = struct.unpack_from("<I", exe_bytes, off + 3)[0]
                    if disp > 0:
                        fields.append(FieldStore(va, disp, "dword", f"0x{imm:08X}"))
        elif b == 0xC6:
            modrm = exe_bytes[off + 1]
            mod = (modrm >> 6) & 3
            reg = (modrm >> 3) & 7
            rm = modrm & 7
            if reg == 0 and rm not in (4, 5):
                if mod == 2:
                    disp = struct.unpack_from("<I", exe_bytes, off + 2)[0]
                    imm = exe_bytes[off + 6]
                    if 0 < disp < 0x10000:
                        fields.append(FieldStore(va, disp, "byte", f"0x{imm:02X}"))
                elif mod == 1:
                    disp = exe_bytes[off + 2]
                    imm = exe_bytes[off + 3]
                    if disp > 0:
                        fields.append(FieldStore(va, disp, "byte", f"0x{imm:02X}"))

        elif b == 0x66 and off + 1 < len(exe_bytes) and exe_bytes[off + 1] == 0xC7:
            modrm = exe_bytes[off + 2]
            mod = (modrm >> 6) & 3
            reg = (modrm >> 3) & 7
            rm = modrm & 7
            if reg == 0 and rm not in (4, 5):
                if mod == 2:
                    disp = struct.unpack_from("<I", exe_bytes, off + 3)[0]
                    imm = struct.unpack_from("<H", exe_bytes, off + 7)[0]
                    if 0 < disp < 0x10000:
                        fields.append(FieldStore(va, disp, "word", f"0x{imm:04X}"))
                elif mod == 1:
                    disp = exe_bytes[off + 3]
                    imm = struct.unpack_from("<H", exe_bytes, off + 4)[0]
                    if disp > 0:
                        fields.append(FieldStore(va, disp, "word", f"0x{imm:04X}"))

        elif b == 0x66 and off + 1 < len(exe_bytes) and exe_bytes[off + 1] == 0x89:
            modrm = exe_bytes[off + 2]
            mod = (modrm >> 6) & 3
            src = (modrm >> 3) & 7
            rm = modrm & 7
            if rm not in (4, 5):
                if mod == 2:
                    disp = struct.unpack_from("<I", exe_bytes, off + 3)[0]
                    if 0 < disp < 0x10000:
                        fields.append(FieldStore(va, disp, "word", reg16_names[src]))
                elif mod == 1:
                    disp = exe_bytes[off + 3]
                    if disp > 0:
                        fields.append(FieldStore(va, disp, "word", reg16_names[src]))

        elif b == 0x89:
            modrm = exe_bytes[off + 1]
            mod = (modrm >> 6) & 3
            src = (modrm >> 3) & 7
            rm = modrm & 7
            if rm not in (4, 5) and src != rm:
                if mod == 2:
                    disp = struct.unpack_from("<I", exe_bytes, off + 2)[0]
                    if 0 < disp < 0x10000:
                        fields.append(FieldStore(va, disp, "dword", reg32_names[src]))
                elif mod == 1:
                    disp = exe_bytes[off + 2]
                    if disp > 0:
                        fields.append(FieldStore(va, disp, "dword", reg32_names[src]))

        elif b == 0xF3 and off + 2 < len(exe_bytes) and exe_bytes[off + 1] == 0x0F and exe_bytes[off + 2] == 0x11:
            modrm = exe_bytes[off + 3]
            mod = (modrm >> 6) & 3
            src = (modrm >> 3) & 7
            rm = modrm & 7
            if rm not in (4, 5):
                if mod == 2 and off + 8 <= len(exe_bytes):
                    disp = struct.unpack_from("<I", exe_bytes, off + 4)[0]
                    if 0 < disp < 0x10000:
                        fields.append(FieldStore(va, disp, "float", f"xmm{src}"))
                elif mod == 1 and off + 5 <= len(exe_bytes):
                    disp = exe_bytes[off + 4]
                    if disp > 0:
                        fields.append(FieldStore(va, disp, "float", f"xmm{src}"))

        elif b == 0xF2 and off + 2 < len(exe_bytes) and exe_bytes[off + 1] == 0x0F and exe_bytes[off + 2] == 0x11:
            modrm = exe_bytes[off + 3]
            mod = (modrm >> 6) & 3
            src = (modrm >> 3) & 7
            rm = modrm & 7
            if rm not in (4, 5):
                if mod == 2 and off + 8 <= len(exe_bytes):
                    disp = struct.unpack_from("<I", exe_bytes, off + 4)[0]
                    if 0 < disp < 0x10000:
                        fields.append(FieldStore(va, disp, "double", f"xmm{src}"))
                elif mod == 1 and off + 5 <= len(exe_bytes):
                    disp = exe_bytes[off + 4]
                    if disp > 0:
                        fields.append(FieldStore(va, disp, "double", f"xmm{src}"))

    seen: dict[int, FieldStore] = {}
    for f in fields:
        if f.offset not in seen:
            seen[f.offset] = f
    return sorted(seen.values(), key=lambda x: x.offset)


def extract_sub_objects(exe_bytes: bytes, ctor_va: int, rtti_entries: list[RttiEntry]) -> list[SubObject]:
    sub_objects: list[SubObject] = []
    file_off = ctor_va - IMAGE_BASE
    vtable_names = _build_vtable_name_map(rtti_entries)
    scan_len = 8192

    for i in range(scan_len):
        off = file_off + i
        if off >= len(exe_bytes) - 10:
            break
        if exe_bytes[off] != 0x8D:
            continue

        modrm = exe_bytes[off + 1]
        mod = (modrm >> 6) & 3
        rm = modrm & 7
        if rm in (4, 5):
            continue

        if mod == 2:
            disp = struct.unpack_from("<I", exe_bytes, off + 2)[0]
            lea_len = 6
        elif mod == 1:
            disp = exe_bytes[off + 2]
            lea_len = 3
        else:
            continue

        if disp == 0 or disp > 0x10000:
            continue

        dst_reg = (modrm >> 3) & 7
        if dst_reg != 1:
            continue

        ctor_target = 0
        for j in range(lea_len, 30):
            if off + j >= len(exe_bytes) - 5:
                break
            if exe_bytes[off + j] != 0xE8:
                continue
            rel = struct.unpack_from("<i", exe_bytes, off + j + 1)[0]
            ctor_target = (off + j + 5 + IMAGE_BASE + rel) & 0xFFFFFFFF
            break

        if ctor_target == 0:
            continue

        vtable, name = _find_vtable_in_function(exe_bytes, ctor_target, vtable_names)
        sub_objects.append(SubObject(disp, ctor_target, name, vtable))

    seen: dict[int, SubObject] = {}
    for s in sub_objects:
        if s.offset not in seen:
            seen[s.offset] = s
    return sorted(seen.values(), key=lambda x: x.offset)


def extract_base_ctor_calls(exe_bytes: bytes, ctor_va: int, rtti_entries: list[RttiEntry]) -> list[InheritanceInfo]:
    bases: list[InheritanceInfo] = []
    file_off = ctor_va - IMAGE_BASE
    vtable_names = _build_vtable_name_map(rtti_entries)

    for i in range(200):
        off = file_off + i
        if off >= len(exe_bytes) - 7:
            break

        if exe_bytes[off] != 0x8B:
            continue
        if exe_bytes[off + 1] not in (0xCE, 0xCF, 0xCB):
            continue

        for j in range(2, 10):
            if off + j >= len(exe_bytes) - 5:
                break
            if exe_bytes[off + j] != 0xE8:
                continue
            rel = struct.unpack_from("<i", exe_bytes, off + j + 1)[0]
            target = (off + j + 5 + IMAGE_BASE + rel) & 0xFFFFFFFF
            if target < IMAGE_BASE + TEXT_FILE_START or target >= IMAGE_BASE + TEXT_FILE_END:
                break
            vtable, name = _find_vtable_in_function(exe_bytes, target, vtable_names)
            if name is not None:
                base_fields = extract_field_stores(exe_bytes, target)
                bases.append(InheritanceInfo(name, target, vtable, base_fields))
            break

    return bases


def _build_vtable_name_map(rtti_entries: list[RttiEntry]) -> dict[int, str]:
    return {e.vtable_va: e.demangled_name for e in rtti_entries if e.vtable_va is not None}


def _find_vtable_in_function(exe_bytes: bytes, func_va: int, vtable_names: dict[int, str]) -> tuple[int | None, str | None]:
    func_off = func_va - IMAGE_BASE
    if func_off < 0 or func_off >= len(exe_bytes) - 10:
        return None, None

    for k in range(300):
        if func_off + k >= len(exe_bytes) - 6:
            break
        if exe_bytes[func_off + k] != 0xC7:
            continue
        modrm = exe_bytes[func_off + k + 1]
        mod = (modrm >> 6) & 3
        reg = (modrm >> 3) & 7
        rm = modrm & 7
        if reg != 0:
            continue

        if mod == 0 and rm not in (4, 5):
            imm_off = 2
        elif mod == 1 and rm != 4:
            imm_off = 3
        else:
            continue

        if func_off + k + imm_off + 4 > len(exe_bytes):
            continue

        vt = struct.unpack_from("<I", exe_bytes, func_off + k + imm_off)[0]
        if 0x00F40000 <= vt <= 0x01200000:
            return vt, vtable_names.get(vt)

    return None, None


def dump_analysis(layout: StructLayout, writer) -> None:
    writer.write(f"// {layout.class_name}\n")
    vt = f"0x{layout.vtable_va:08X}" if layout.vtable_va is not None else "none"
    writer.write(f"// VTable: {vt} ({layout.vtable_entry_count} vfuncs)\n")
    writer.write(f"// Ctor:   0x{layout.ctor_va:08X}\n")
    size = f"0x{layout.alloc_size:X} ({layout.alloc_size} bytes)" if layout.alloc_size else "unknown"
    writer.write(f"// Size:   {size}\n\n")

    if layout.base_ctors:
        writer.write("// === Base Class Constructors ===\n")
        for b in layout.base_ctors:
            vt = f"vt=0x{b.vtable_va:08X}" if b.vtable_va else "no vtable"
            writer.write(f"//   {b.class_name} (ctor=0x{b.ctor_va:08X}, {vt}, {len(b.fields)} fields)\n")
        writer.write("\n")

    writer.write(f"// === Fields (from constructor init) === [{len(layout.fields)} total]\n")
    for f in layout.fields:
        writer.write(f"// +0x{f.offset:04X} [{f.type:<6}] = {f.value}  (@ 0x{f.va:08X})\n")

    if layout.sub_objects:
        writer.write(f"\n// === Embedded Sub-Objects === [{len(layout.sub_objects)} total]\n")
        for s in layout.sub_objects:
            name = s.class_name or "unknown"
            vt = f"vt=0x{s.vtable_va:08X}" if s.vtable_va else "no vtable"
            writer.write(f"// +0x{s.offset:04X} {name} ({vt}, ctor=0x{s.ctor_va:08X})\n")
