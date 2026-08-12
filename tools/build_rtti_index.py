"""Reduce the raw RTTI extraction to the vftable VA index the IR needs.

`manifests/rtti_extraction_OUR.txt` is near-verbatim binary metadata read
out of ffxivgame.exe (vftable VA, COL VA, mangled name, and demangled name)
and stays out of the public tree. The IR only ever asks it
one question: is a given VA a known vftable VA? This reduces the dump to
that column alone, so `addressCorroboration` stays derivable - and
`build_ir.py --check` stays meaningful - in a checkout that has no dump.

Addresses are already the repo's published product; the mangled-name table
is what the reduction drops.

Run this whenever the dump is regenerated. `--check` proves the committed
index still matches the dump, and build_ir.py runs the same comparison
whenever the dump happens to be present.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DUMP_PATH = REPO / "manifests" / "rtti_extraction_OUR.txt"
INDEX_PATH = REPO / "manifests" / "rtti_vftable_index.json"

GAME_VERSION = "1.23b"


def read_dump(path: Path) -> list[str]:
    """Return the sorted, deduplicated vftable VA column of the dump."""
    vas: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            continue
        parts = line.split("\t")
        if parts and parts[0].strip():
            vas.add(parts[0].strip().lower())
    return sorted(vas)


def build_index(path: Path = DUMP_PATH) -> dict:
    vas = read_dump(path)
    return {
        "version": "1.0",
        "gameVersion": GAME_VERSION,
        "generator": {"tool": "tools/build_rtti_index.py"},
        "source": "manifests/rtti_extraction_OUR.txt",
        "vftableCount": len(vas),
        "vftableVAs": vas,
    }


def render(doc: dict) -> str:
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="verify the committed index matches the dump; write nothing")
    args = ap.parse_args()

    if not DUMP_PATH.exists():
        print(f"FATAL: {DUMP_PATH.name} is not in this checkout. It is local "
              "evidence: regenerate it with tools/extractors/client_pe against your "
              "own client install.", file=sys.stderr)
        return 2

    doc = build_index()

    if args.check:
        if not INDEX_PATH.exists():
            print(f"FAIL: {INDEX_PATH.name} is missing", file=sys.stderr)
            return 1
        with INDEX_PATH.open(encoding="utf-8", newline="") as f:
            committed = f.read()
        if committed != render(doc):
            print(f"FAIL: {INDEX_PATH.name} is not what this tool produces "
                  "from the current dump; rerun without --check", file=sys.stderr)
            return 1
        print(f"OK: {INDEX_PATH.name} matches the dump "
              f"({doc['vftableCount']} vftable VAs)")
        return 0

    # newline="" keeps the LF the repo commits (.gitattributes eol=lf). The
    # IR records this file's sha256, so a CRLF working copy would hash
    # differently from the checkout every other reader gets.
    with INDEX_PATH.open("w", encoding="utf-8", newline="") as f:
        f.write(render(doc))
    print(f"wrote {INDEX_PATH.name} ({doc['vftableCount']} vftable VAs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
