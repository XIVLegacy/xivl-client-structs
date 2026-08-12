"""Catalog cross-reference audit.

Read-only. Scans symbols.json notes (and sourceRefs) for two classes of
BCS-Y cross-reference bugs:

    ORPHAN     A BCS-Y-NNNN token cites an ID that does not exist in
               the catalog (deleted, renumbered, or typo).

    MISMATCH   A paired citation of the form `FUN_XXXXXXXX (BCS-Y-NNNN)`
               (or close variants) names a FUN_VA AND a BCS-Y entry, but
               the cited entry's address is not that FUN_VA. The author
               meant to cite the entry AT the FUN_VA but typed the wrong
               id.

Motivating case: BCS-Y-0672/0673/0674/0675 (case
handlers) all cite "FUN_0081f090 (BCS-Y-0539)". BCS-Y-0539 is
RaptureElement_Ctor_FUN_004dab50 at 0x004dab50; the entry actually at
0x0081f090 is BCS-Y-0671 (PendingOpVector_AppendPair_FUN_0081f090). Four known
instances motivated this audit; the tool scans the current full catalog for
any others.

Distinct from tools/audit_matrix.py drift mode:
    audit_matrix.py: matrix bcsYIds vs cataloged downstream helpers
    this tool:       in-notes BCS-Y citation strings vs catalog reality

Bare BCS-Y mentions in prose (e.g. "BCS-Y-0539 chain note" with no
paired FUN_VA) are NOT mismatches - they are contextual references to
the entry by its established role, and the entry exists. Only the
explicit `FUN_VA (BCS-Y-ID)` pairing is verified.

CLI:
    python tools/audit_catalog_xref.py
    python tools/audit_catalog_xref.py --json
    python tools/audit_catalog_xref.py --mismatch-only

Pure stdlib (json, pathlib, re, sys, argparse).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

REPO = pathlib.Path(__file__).resolve().parents[1]
SYMBOLS_PATH = REPO / "manifests" / "symbols.json"

_include_uncataloged = False

BCS_Y_ID_RE = re.compile(r"\bBCS-Y-(\d{4})\b")
# Forward form: "FUN_XXXXXXXX (BCS-Y-NNNN)" with optional whitespace.
FORWARD_PAIR_RE = re.compile(
    r"\bFUN_([0-9a-fA-F]{8})\b\s*\(\s*(BCS-Y-\d{4})\s*\)"
)
# Require "at" in reverse pairs. `BCS-Y-0273 FUN_0057ABB0` is contextual.
REVERSE_PAIR_RE = re.compile(
    r"\b(BCS-Y-\d{4})\b\s*\)?\s+at\s+FUN_([0-9a-fA-F]{8})\b"
)


def _load_json(path: pathlib.Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build_address_index(symbols: list[dict]) -> dict[str, dict]:
    """Map canonical lowercase 0xXXXXXXXX address -> BCS-Y entry."""
    idx: dict[str, dict] = {}
    for s in symbols:
        addr = s.get("address")
        if not isinstance(addr, str):
            continue
        addr_lower = addr.lower()
        if addr_lower in ("0x00000000", "0x0", ""):
            continue
        # Skip composite forms (cluster, range) for this paired-citation check.
        if ";" in addr or ".." in addr:
            continue
        idx[addr_lower] = s
    return idx


def build_id_index(symbols: list[dict]) -> dict[str, dict]:
    """Map BCS-Y-NNNN id -> entry."""
    return {s["id"]: s for s in symbols if isinstance(s.get("id"), str)}


def _notes_text(sym: dict) -> str:
    notes = sym.get("notes", "")
    return notes if isinstance(notes, str) else ""


def audit_entry(sym: dict, addr_idx: dict, id_idx: dict) -> list[dict]:
    findings: list[dict] = []
    notes = _notes_text(sym)
    if not notes:
        return findings
    sym_id = sym.get("id", "<?>")

    seen_orphans: set[str] = set()
    for m in BCS_Y_ID_RE.finditer(notes):
        bid = f"BCS-Y-{m.group(1)}"
        if bid in seen_orphans:
            continue
        seen_orphans.add(bid)
        if bid == sym_id:
            continue
        if bid not in id_idx:
            findings.append({
                "kind": "ORPHAN",
                "inEntry": sym_id,
                "inEntryName": sym.get("name", ""),
                "citedId": bid,
                "context": _context_snippet(notes, m.start(), m.end()),
            })

    seen_pairs: set[tuple[str, str]] = set()
    for pat, va_grp, id_grp in (
        (FORWARD_PAIR_RE, 1, 2),
        (REVERSE_PAIR_RE, 2, 1),
    ):
        for m in pat.finditer(notes):
            va = "0x" + m.group(va_grp).lower()
            bid = m.group(id_grp)
            key = (va, bid)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            cited = id_idx.get(bid)
            if not cited:
                # The ORPHAN bucket already reports this ID.
                continue
            cited_addr = cited.get("address", "").lower()
            if cited_addr == va:
                continue
            real = addr_idx.get(va)
            # An uncataloged FUN_VA has no alternative ID to propose.
            if real is None and not _include_uncataloged:
                continue
            findings.append({
                "kind": "MISMATCH",
                "inEntry": sym_id,
                "inEntryName": sym.get("name", ""),
                "citedFunVa": va,
                "citedId": bid,
                "citedActualAddr": cited_addr,
                "citedName": cited.get("name", ""),
                "expectedId": real.get("id") if real else None,
                "expectedName": real.get("name") if real else None,
                "context": _context_snippet(notes, m.start(), m.end()),
            })
    return findings


def _context_snippet(text: str, start: int, end: int, pad: int = 40) -> str:
    lo = max(0, start - pad)
    hi = min(len(text), end + pad)
    snippet = text[lo:hi]
    if lo > 0:
        snippet = "..." + snippet
    if hi < len(text):
        snippet = snippet + "..."
    return snippet


def audit_catalog(symbols: list[dict]) -> list[dict]:
    addr_idx = build_address_index(symbols)
    id_idx = build_id_index(symbols)
    all_findings: list[dict] = []
    for sym in symbols:
        all_findings.extend(audit_entry(sym, addr_idx, id_idx))
    return all_findings


def _render_text(findings: list[dict], mismatch_only: bool) -> str:
    out: list[str] = []
    out.append("=" * 72)
    out.append("CATALOG CROSS-REFERENCE AUDIT")
    out.append("=" * 72)
    by_kind: dict[str, list[dict]] = {"MISMATCH": [], "ORPHAN": []}
    for f in findings:
        by_kind[f["kind"]].append(f)

    kinds = ("MISMATCH",) if mismatch_only else ("MISMATCH", "ORPHAN")
    for kind in kinds:
        bucket = by_kind[kind]
        if not bucket:
            out.append(f"\n--- {kind}: 0 findings ---")
            continue
        bucket.sort(key=lambda f: (f["inEntry"], f.get("citedId", "")))
        out.append(f"\n--- {kind}: {len(bucket)} findings ---")
        if kind == "MISMATCH":
            out.append("    (paired FUN_VA + BCS-Y citation where the cited"
                       " entry's address != that FUN_VA)")
        else:
            out.append("    (BCS-Y-NNNN token references an ID not in catalog)")
        for f in bucket:
            out.append(f"\n  in {f['inEntry']} ({f['inEntryName']}):")
            if kind == "MISMATCH":
                out.append(
                    f"    cited      : {f['citedId']} -> {f['citedName']}"
                )
                out.append(
                    f"                 (actually at {f['citedActualAddr']})"
                )
                out.append(
                    f"    paired w/  : {f['citedFunVa']}"
                )
                if f["expectedId"]:
                    out.append(
                        f"    should be  : {f['expectedId']}"
                        f" -> {f['expectedName']}"
                    )
                else:
                    out.append(
                        f"    should be  : (no catalog entry at"
                        f" {f['citedFunVa']})"
                    )
            else:
                out.append(f"    orphan id  : {f['citedId']}")
            out.append(f"    context    : {f['context']}")

    out.append("\n" + "=" * 72)
    out.append(f"SUMMARY: {len(by_kind['MISMATCH'])} MISMATCH"
               f" + {len(by_kind['ORPHAN'])} ORPHAN"
               f" = {len(findings)} total findings")
    out.append("=" * 72)
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--json", action="store_true",
                   help="emit machine-readable JSON instead of text report")
    p.add_argument("--mismatch-only", action="store_true",
                   help="suppress ORPHAN findings in text report")
    p.add_argument("--include-uncataloged", action="store_true",
                   help="also flag MISMATCH where no entry exists at the"
                        " paired FUN_VA (typically vtable / finding-doc"
                        " cross-refs; default-suppressed as non-actionable)")
    args = p.parse_args()

    global _include_uncataloged
    _include_uncataloged = args.include_uncataloged

    try:
        symbols_doc = _load_json(SYMBOLS_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2

    symbols = symbols_doc.get("symbols", [])
    findings = audit_catalog(symbols)

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        print(_render_text(findings, args.mismatch_only))

    has_errors = any(f["kind"] in ("MISMATCH", "ORPHAN") for f in findings)
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
