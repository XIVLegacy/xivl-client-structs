"""String reference extraction from a client PE image.

extract_from_function(exe, func_va, max_scan)
    Scan a function body for instructions that load a pointer into
    .rdata - PUSH imm32 (0x68), MOV reg, imm32 (0xB8-0xBF),
    or MOV [reg+disp], imm32 (0xC7). Filter the targets to those
    pointing inside .rdata and decode as ASCII C-strings.

find_string_xrefs(exe, literal)
    Locate the literal in .rdata, then scan .text for PUSH imm32
    instructions whose immediate matches the .rdata VA.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

from . import (
    IMAGE_BASE,
    RDATA_FILE_END,
    RDATA_FILE_START,
    TEXT_FILE_END,
    TEXT_FILE_START,
)


@dataclass
class StringRef:
    instruction_va: int
    string_va: int
    value: str


def extract_from_function(exe_bytes: bytes, func_va: int, max_scan_bytes: int = 4096) -> list[StringRef]:
    results: list[StringRef] = []
    func_off = func_va - IMAGE_BASE
    if func_off < 0 or func_off >= len(exe_bytes):
        return results

    seen: set[int] = set()
    i = 0
    while i < max_scan_bytes and func_off + i < len(exe_bytes) - 5:
        off = func_off + i
        va = func_va + i
        str_va = 0

        b = exe_bytes[off]
        if b == 0x68:
            str_va = struct.unpack_from("<I", exe_bytes, off + 1)[0]
        elif 0xB8 <= b <= 0xBF:
            str_va = struct.unpack_from("<I", exe_bytes, off + 1)[0]
        elif b == 0xC7:
            modrm = exe_bytes[off + 1]
            mod = (modrm >> 6) & 3
            reg = (modrm >> 3) & 7
            rm = modrm & 7
            if reg == 0 and rm not in (4, 5):
                if mod == 2 and off + 10 <= len(exe_bytes):
                    str_va = struct.unpack_from("<I", exe_bytes, off + 6)[0]
                elif mod == 1 and off + 7 <= len(exe_bytes):
                    str_va = struct.unpack_from("<I", exe_bytes, off + 3)[0]

        i += 1
        if str_va == 0:
            continue
        str_file_off = str_va - IMAGE_BASE
        if str_file_off < RDATA_FILE_START or str_file_off >= RDATA_FILE_END:
            continue
        if str_va in seen:
            continue
        s = _read_cstring(exe_bytes, str_file_off, 256)
        if s is None or len(s) < 2 or not _is_printable(s):
            continue
        seen.add(str_va)
        results.append(StringRef(va, str_va, s))

    return results


def find_string_xrefs(exe_bytes: bytes, search_string: str) -> list[StringRef]:
    results: list[StringRef] = []
    search_bytes = search_string.encode("ascii")
    str_vas: list[int] = []

    i = RDATA_FILE_START
    while i < RDATA_FILE_END - len(search_bytes):
        if exe_bytes[i:i + len(search_bytes)] == search_bytes:
            term_off = i + len(search_bytes)
            if term_off >= len(exe_bytes) or exe_bytes[term_off] == 0:
                str_vas.append(i + IMAGE_BASE)
        i += 1

    for str_va in str_vas:
        str_bytes = struct.pack("<I", str_va)
        value = _read_cstring(exe_bytes, str_va - IMAGE_BASE, 256) or search_string

        i = TEXT_FILE_START
        while i < TEXT_FILE_END - 5:
            if exe_bytes[i] == 0x68 and exe_bytes[i + 1:i + 5] == str_bytes:
                results.append(StringRef(i + IMAGE_BASE, str_va, value))
            i += 1

    return results


def _read_cstring(data: bytes, offset: int, max_len: int) -> str | None:
    if offset < 0 or offset >= len(data):
        return None
    end = offset
    while end < len(data) and end - offset < max_len and data[end] != 0:
        end += 1
    if end == offset:
        return None
    return data[offset:end].decode("ascii", errors="replace")


def _is_printable(s: str) -> bool:
    return all(0x20 <= ord(c) <= 0x7E for c in s)
