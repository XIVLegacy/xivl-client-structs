#!/usr/bin/env python3
"""Query the offline static call graph: who calls FUN_xxxx, and what it calls.

Resolves a raw or mid-function VA to its owning function via [entryVA, maxVA],
then prints the function, its direct callees, and its callers -- every VA
annotated with its curated name + BCS-Y id from manifests/symbols.json
(uncataloged -> the Ghidra FUN_<va> name).

Reads build/callgraph.json (produce it with tools/build_callgraph.py). Static
direct calls only; indirect / virtual (vtable) dispatch is not represented.

Stdlib only.

Usage:
    python tools/callers.py FUN_004d9910
    python tools/callers.py 0x004d9910
    python tools/callers.py 004d9988        # mid-function VA resolves to owner
    python tools/callers.py FUN_004d9910 --json
"""
from __future__ import annotations

import argparse
import bisect
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _symbols_io  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
DEFAULT_GRAPH = REPO / "build" / "callgraph.json"


def parse_va(token: str) -> int:
    t = token.strip()
    if t.lower().startswith("fun_"):
        t = t[4:]
    if t.lower().startswith("0x"):
        t = t[2:]
    return int(t, 16)


def va_str(va: int) -> str:
    return f"0x{va:08x}"


def load_symbol_index(data: dict) -> dict:
    """address(int) -> (id, name). On address collision, prefer function-kind."""
    idx: dict[int, tuple] = {}
    for s in data.get("symbols", []):
        addr = s.get("address")
        if not addr:
            continue
        try:
            a = int(str(addr), 16)
        except ValueError:
            continue
        if a not in idx or s.get("kind") == "function":
            idx[a] = (s.get("id", ""), s.get("name", ""))
    return idx


def annotate(va_hex: str, functions: dict, symidx: dict) -> str:
    va = int(va_hex, 16)
    sym = symidx.get(va)
    if sym:
        sid, name = sym
        return f"{va_hex} {name}" + (f" [{sid}]" if sid else "")
    node = functions.get(va_hex)
    name = node["name"] if node else f"FUN_{va_hex[2:]}"
    return f"{va_hex} {name}"


def resolve(va: int, functions: dict, entries_sorted: list):
    """Return the entry-VA key of the function whose body contains va, or None."""
    key = va_str(va)
    if key in functions:
        return key
    i = bisect.bisect_right(entries_sorted, va) - 1
    if i < 0:
        return None
    cand_key = va_str(entries_sorted[i])
    node = functions.get(cand_key)
    if node and int(node["maxVA"], 16) >= va:
        return cand_key
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Who calls FUN_xxxx (offline static call graph).")
    ap.add_argument("target", help="FUN_xxxxxxxx, 0xVA, or bare hex VA")
    ap.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    if not args.graph.exists():
        print(f"ERROR: call graph not found: {args.graph}")
        print("Build it first:  python tools/build_callgraph.py")
        return 1

    with args.graph.open(encoding="utf-8") as f:
        doc = json.load(f)
    functions = doc["functions"]
    entries_sorted = sorted(int(k, 16) for k in functions)

    try:
        va = parse_va(args.target)
    except ValueError:
        print(f"ERROR: could not parse a hex VA from {args.target!r}")
        return 2

    owner = resolve(va, functions, entries_sorted)
    if owner is None:
        print(f"No function contains {va_str(va)} in {args.graph.name}.")
        return 3

    symidx = load_symbol_index(_symbols_io.load_symbols())
    node = functions[owner]
    callees = node["callees"]
    callers = node["callers"]

    if args.json:
        out = {
            "query": args.target,
            "resolvedEntry": owner,
            "name": node["name"],
            "maxVA": node["maxVA"],
            "callees": [{"va": c, "label": annotate(c, functions, symidx)} for c in callees],
            "callers": [{"va": c, "label": annotate(c, functions, symidx)} for c in callers],
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    print(annotate(owner, functions, symidx))
    if va != int(owner, 16):
        print(f"  (query {va_str(va)} resolved to owning function {owner})")
    print(f"  callees: {len(callees)}   callers: {len(callers)}")
    print()
    print(f"Callees ({len(callees)}):")
    for c in callees:
        print("  -> " + annotate(c, functions, symidx))
    print()
    print(f"Callers ({len(callers)}):")
    for c in callers:
        print("  <- " + annotate(c, functions, symidx))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
