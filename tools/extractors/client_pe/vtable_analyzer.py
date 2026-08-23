"""Vtable function analysis for a client PE image.

For each vtable slot:
- estimate function size by scanning for RET (C3) or RET imm16 (C2 xx xx)
- detect pure-virtual thunks (JMP [addr])
- count stack parameters from RET imm16 cleanup bytes
- detect short stubs (size <= 6)

Uses byte-pattern matching only (no disassembly library).
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

from . import IMAGE_BASE, TEXT_VA_END, TEXT_VA_START
from .rtti_dumper import RttiEntry


@dataclass
class VtableFunction:
    index: int
    address: int
    stack_param_bytes: int
    is_pure_virtual: bool
    is_stub: bool
    signature: str | None


def analyze_vtable(exe_bytes: bytes, vtable_va: int, entry_count: int) -> list[VtableFunction]:
    results: list[VtableFunction] = []
    vt_off = vtable_va - IMAGE_BASE

    for i in range(entry_count):
        func_va = struct.unpack_from("<I", exe_bytes, vt_off + i * 4)[0]
        if func_va < TEXT_VA_START or func_va >= TEXT_VA_END:
            results.append(VtableFunction(i, func_va, 0, False, False, None))
            continue

        func_off = func_va - IMAGE_BASE
        size = estimate_function_size(exe_bytes, func_off)
        is_pure = is_pure_virtual_thunk(exe_bytes, func_off)
        is_stub = size <= 6 and not is_pure
        stack_params = count_stack_parameters(exe_bytes, func_off)
        sig = build_signature(exe_bytes, func_off, func_va, stack_params)
        results.append(VtableFunction(i, func_va, stack_params, is_pure, is_stub, sig))

    return results


def estimate_function_size(exe_bytes: bytes, func_off: int) -> int:
    if func_off < 0 or func_off >= len(exe_bytes) - 5:
        return 0

    for i in range(0x10000):
        off = func_off + i
        if off >= len(exe_bytes) - 3:
            break
        b = exe_bytes[off]
        if b == 0xC3:
            return i + 1
        if b == 0xC2:
            return i + 3
        if i > 0 and b == 0xCC and exe_bytes[off - 1] == 0xC3:
            return i
    return 0


def is_pure_virtual_thunk(exe_bytes: bytes, func_off: int) -> bool:
    if func_off < 0 or func_off + 10 >= len(exe_bytes):
        return False
    if exe_bytes[func_off] == 0xFF and exe_bytes[func_off + 1] == 0x25:
        return True
    if exe_bytes[func_off] == 0xE8 and func_off + 5 < len(exe_bytes):
        if exe_bytes[func_off + 5] in (0xCC, 0xC3):
            return True
    return False


def count_stack_parameters(exe_bytes: bytes, func_off: int) -> int:
    if func_off < 0 or func_off >= len(exe_bytes) - 5:
        return 0
    if exe_bytes[func_off] != 0x55 or exe_bytes[func_off + 1] != 0x8B or exe_bytes[func_off + 2] != 0xEC:
        return 0
    for i in range(3, 0x5000):
        off = func_off + i
        if off >= len(exe_bytes) - 3:
            break
        if exe_bytes[off] == 0xC2:
            cleanup = struct.unpack_from("<H", exe_bytes, off + 1)[0]
            if 0 < cleanup <= 0x80:
                return cleanup
        if exe_bytes[off] == 0xC3:
            return 0
    return 0


def build_signature(exe_bytes: bytes, func_off: int, func_va: int, stack_param_bytes: int) -> str:
    parts = [f"0x{func_va:08X}"]
    size = estimate_function_size(exe_bytes, func_off)
    if size > 0:
        parts.append(f"({size}B)")
    param_count = stack_param_bytes // 4
    args = ", ".join(["this"] + [f"arg{p + 1}" for p in range(param_count)])
    parts.append(f"thiscall({args})")
    return " ".join(parts)


def dump_vtable_analysis(exe_bytes: bytes, entry: RttiEntry, writer) -> None:
    if entry.vtable_va is None or entry.vtable_entry_count is None:
        return
    funcs = analyze_vtable(exe_bytes, entry.vtable_va, entry.vtable_entry_count)
    writer.write(f"// {entry.demangled_name}\n")
    writer.write(f"// VTable: 0x{entry.vtable_va:08X} ({entry.vtable_entry_count} entries)\n\n")
    pure_count = sum(1 for f in funcs if f.is_pure_virtual)
    stub_count = sum(1 for f in funcs if f.is_stub)
    writer.write(f"// Summary: {len(funcs)} total, {pure_count} pure virtual, {stub_count} stubs\n\n")
    for f in funcs:
        flags = []
        if f.is_pure_virtual:
            flags.append("PURE")
        if f.is_stub:
            flags.append("STUB")
        flag_str = f" [{','.join(flags)}]" if flags else ""
        sig_or_addr = f.signature if f.signature else f"0x{f.address:08X}"
        writer.write(f"vt[{f.index:>3}] {sig_or_addr}{flag_str}\n")
