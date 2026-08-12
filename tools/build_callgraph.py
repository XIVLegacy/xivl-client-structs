#!/usr/bin/env python3
"""Fold the Ghidra call-graph TSV export into build/callgraph.json.

Input: a TSV from tools/ghidra/DumpCallGraph.java, one row per function:
    <entryVA>\t<maxBodyVA>\t<name>\t<comma-separated callee entry VAs>

Output: build/callgraph.json (gitignored, regenerable):
    {
      "meta": { "source", "functionCount", "edgeCount", "note" },
      "functions": {
        "0x004d9910": {
          "name": "FUN_004d9910",
          "maxVA": "0x004d996e",
          "callees": ["0x...", ...],   # static direct calls (sorted, unique)
          "callers": ["0x...", ...]    # inverted edges (sorted, unique)
        }, ...
      }
    }

This is a generated index, not a curated catalog manifest: it lives in build/,
not manifests/, and is not gated by validate_catalog.py. Indirect / virtual
(vtable) dispatch is NOT represented -- see tools/ghidra/DumpCallGraph.java.

Stdlib only.

Usage:
    python tools/build_callgraph.py [--tsv PATH] [--out PATH]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_TSV = REPO / "tools" / "ghidra" / "logs" / "callgraph_edges.tsv"
DEFAULT_OUT = REPO / "build" / "callgraph.json"


def _stub(va_hex: str) -> dict:
    return {"name": "FUN_" + va_hex[2:], "maxVA": va_hex, "callees": [], "callers": []}


def build(tsv_path: Path) -> dict:
    functions: dict[str, dict] = {}
    with tsv_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            entry, max_va, name = parts[0], parts[1], parts[2]
            callee_field = parts[3] if len(parts) > 3 else ""
            callees = sorted({c for c in callee_field.split(",") if c})
            node = functions.setdefault(entry, _stub(entry))
            node["name"] = name
            node["maxVA"] = max_va
            node["callees"] = callees

    # DumpCallGraph emits function-entry callees. setdefault covers an absent target node.
    for entry in list(functions.keys()):
        for callee in functions[entry]["callees"]:
            functions.setdefault(callee, _stub(callee))["callers"].append(entry)
    for node in functions.values():
        node["callers"] = sorted(set(node["callers"]))
    return functions


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Build build/callgraph.json from the Ghidra TSV export.")
    ap.add_argument("--tsv", type=Path, default=DEFAULT_TSV)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)

    if not args.tsv.exists():
        print(f"ERROR: TSV not found: {args.tsv}")
        print("Generate it with the headless dumper:")
        print("  analyzeHeadless <proj> ffxivgame -process ffxivgame.exe "
              "-noanalysis -readOnly \\")
        print("    -scriptPath tools/ghidra -postScript DumpCallGraph.java")
        print("  (set XIVL_CALLGRAPH_OUT to "
              "tools/ghidra/logs/callgraph_edges.tsv)")
        return 1

    functions = build(args.tsv)
    total_edges = sum(len(n["callees"]) for n in functions.values())
    try:
        source = str(args.tsv.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        source = str(args.tsv).replace("\\", "/")
    doc = {
        "meta": {
            "source": source,
            "functionCount": len(functions),
            "edgeCount": total_edges,
            "note": "Static direct-call graph from tools/ghidra/DumpCallGraph.java. "
                    "Indirect/virtual dispatch NOT captured. Generated; regenerable.",
        },
        "functions": functions,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as f:
        json.dump(doc, f, separators=(",", ":"), ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {args.out} ({len(functions)} functions, {total_edges} edges)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
