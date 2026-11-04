#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decode FFXIV 1.x client script files (.le.lpb) to Lua 5.1 bytecode.

The client ships compiled scripts as <cipher>.le.lpb under
<install_root>/client/script/, where <cipher> is a character-substitution
encoding of the script's source name. Each file starts with one of two
wrappers, identified by its first four bytes:

  72 6C 75 0B   plain: the bytecode is everything from offset 8 onward.
  72 6C 65 0C   obfuscated: the bytecode is every byte from offset 13
                onward, XORed with 0x73.

The result begins with the Lua signature (1B 4C 75 61 51) and can be fed to a
Lua 5.1 decompiler. Files with any other leading bytes are not decodable.

Usage:
  decode_lpb.py INSTALL_ROOT [SOURCE_NAME] [--out DIR] [--show-cipher]

With SOURCE_NAME, only the matching script is decoded to DIR/SOURCE_NAME.luac.
Without it, every .le.lpb file under the script directory is decoded into DIR,
preserving the directory layout. --show-cipher prints the filename cipher table.
"""

import argparse
import sys
from pathlib import Path

PLAIN_MAGIC = bytes.fromhex("726C750B")
OBFUSCATED_MAGIC = bytes.fromhex("726C650C")
LUA51_SIGNATURE = bytes.fromhex("1B4C756151")
XOR_KEY = 0x73
SUFFIX = ".le.lpb"


def decode_lpb(data: bytes) -> bytes | None:
    """Return the Lua bytecode inside an LPB file, or None if unrecognized."""
    magic = data[:4]
    if magic == PLAIN_MAGIC:
        return data[8:]
    if magic == OBFUSCATED_MAGIC:
        return bytes(b ^ XOR_KEY for b in data[13:])
    return None


def _build_cipher() -> dict[int, str]:
    table: dict[int, str] = {}
    for i in range(10):
        table[ord("a") + i] = chr(ord("9") - i)
        table[ord("0") + i] = chr(ord("j") - i)
    for i in range(ord("z") - ord("k") + 1):
        table[ord("k") + i] = chr(ord("z") - i)
    return table


_CIPHER = _build_cipher()


def encode_filename(name: str) -> str:
    """Apply the filename cipher; it is its own inverse."""
    return name.lower().translate(_CIPHER)


def decode_filename(s: str) -> str:
    return encode_filename(s)


def find_lpb(install_root: Path, source_name: str) -> Path | None:
    """Locate the shipped .lpb for a source name, or None if absent."""
    target = encode_filename(source_name) + SUFFIX
    script_dir = install_root / "client" / "script"
    # Compare literally: a source name is not a glob pattern or a relative path.
    for path in sorted(script_dir.rglob("*" + SUFFIX)):
        if path.name.lower() == target and path.is_file():
            return path
    return None


def decode_tree(
    install_root: Path,
    out_dir: Path,
    source_name: str | None = None,
    *,
    standalone_report: bool = False,
) -> int:
    """Decode one script, or all of them, into out_dir. Returns an exit code."""
    if source_name is not None:
        return _decode_one(
            install_root, out_dir, source_name, standalone_report=standalone_report
        )

    script_dir = install_root / "client" / "script"
    if not script_dir.is_dir():
        print(
            f"error: {script_dir} missing - is this the install root?",
            file=sys.stderr,
        )
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    decoded = 0
    failed = 0
    for path in sorted(script_dir.rglob("*" + SUFFIX)):
        if not path.is_file():
            continue
        bytecode = decode_lpb(path.read_bytes())
        if bytecode is None:
            failed += 1
            continue
        rel_dir = path.relative_to(script_dir).parent
        out_path = out_dir / rel_dir / (path.name[: -len(SUFFIX)] + ".luac")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(bytecode)
        decoded += 1

    verb = "Decoded" if standalone_report else "decoded"
    print(f"{verb} {decoded} .lpb files to {out_dir}/ ({failed} failed)")
    return 0


def _decode_one(
    install_root: Path,
    out_dir: Path,
    source_name: str,
    *,
    standalone_report: bool,
) -> int:
    path = find_lpb(install_root, source_name)
    if path is None:
        cipher = encode_filename(source_name)
        print(
            f"error: no shipped .lpb matches source '{source_name}' "
            f"(ciphered: '{cipher}{SUFFIX}')",
            file=sys.stderr,
        )
        return 1

    bytecode = decode_lpb(path.read_bytes())
    if bytecode is None:
        print(f"error: unrecognized .lpb wrapper magic in {path}", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (source_name + ".luac")
    out_path.write_bytes(bytecode)

    if standalone_report:
        print(f"  {source_name}: {path}")
        print(f"  -> {out_path} ({len(bytecode)} B)")
        if bytecode.startswith(LUA51_SIGNATURE):
            print("  valid Lua 5.1 bytecode (run unluac to decompile)")
    else:
        print(f"decoded {source_name}: {path} -> {out_path} ({len(bytecode)} B)")
    return 0


def _show_cipher() -> None:
    print("FFXIV 1.x script tree filename cipher:")
    for c in "abcdefghijklmnopqrstuvwxyz0123456789":
        print(f"  {c} <-> {encode_filename(c)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("install_root", type=Path, help="game install root")
    parser.add_argument(
        "source_name", nargs="?", help="decode only this script (uncoded name)"
    )
    parser.add_argument(
        "--out", type=Path, default=Path("build/lpb"), help="output directory"
    )
    parser.add_argument(
        "--show-cipher", action="store_true", help="print the filename cipher table"
    )
    args = parser.parse_args()

    if args.show_cipher:
        _show_cipher()
        return 0
    return decode_tree(
        args.install_root, args.out, args.source_name, standalone_report=True
    )


if __name__ == "__main__":
    sys.exit(main())
