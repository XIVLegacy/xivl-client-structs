"""Promote retained __FUNCTION__ name candidates into the BCS-Y catalog.

Input: data/vendor/client_function_names/candidate_symbols.json, a vendored
harvest of scoped-name strings (A::B::C) that the 1.23b client pushes together
with __FILE__ and __LINE__ into its assert, log and tagged-allocation macros,
bound to the Ghidra function containing the push. The harvest and its
automated per-row checks are described in that file's PROVENANCE record.

Projection rules (deterministic, idempotent):
- One BCS-Y function entry per candidate whose address is not already in the
  catalog. Existing addresses are reported and left untouched, so curated rows
  keep their names.
- name is the retained string verbatim (scope plus leaf; no signature).
- confidence is "probable" for a source-file site that passed every automated
  check, else "candidate" (header-file site, or a flagged check).
- sourceRefs cite the vendored file and its PROVENANCE record.
- notes carry the locators: string VA, site VAs, file and lines, macro helper,
  Ghidra body size, check results and the script-derived boundary caveat.

--check writes nothing and exits non-zero if the catalog lacks any projected
row or holds one with different content.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import _symbols_io  # noqa: E402

REPO = TOOLS.parent
VENDOR_DIR = Path("data") / "vendor" / "client_function_names"
CANDIDATES = REPO / VENDOR_DIR / "candidate_symbols.json"
SOURCE_REFS = [
    (VENDOR_DIR / "candidate_symbols.json").as_posix(),
    (VENDOR_DIR / "PROVENANCE.json").as_posix(),
]
TAG = "[function-name-harvest 2026-10-02]"


def load_candidates() -> list[dict]:
    doc = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    return doc["candidates"]


def canonical_address(value: str) -> str:
    return "0x%08X" % int(value, 16)


def confidence_for(cand: dict) -> str:
    source = cand["evidence"]["file_kind"] == "source"
    if source and cand["auto_check"] == "pass":
        return "probable"
    return "candidate"


def flag_reasons(cand: dict) -> list[str]:
    checks = cand["evidence"]["checks"]
    reasons = []
    for key in ("entry_after_padding", "entry_prologue", "site_in_body"):
        if not checks.get(key, 1):
            reasons.append(key)
    for key in ("jcc_into_entry", "other_file_pushed", "other_name_pushed"):
        if checks.get(key, 0):
            reasons.append(key)
    return reasons


def notes_for(cand: dict) -> str:
    ev = cand["evidence"]
    lines = ",".join(str(n) for n in ev["lines"])
    sites = ",".join(ev["site_vas"])
    helpers = ",".join(ev["helpers"])
    parts = [
        TAG,
        f"Retained __FUNCTION__ string at {ev['string_va']} pushed with __FILE__"
        f" {ev['file']} line {lines} into macro helper {helpers} at site {sites};"
        f" the only scoped name pushed inside the Ghidra 12.1.3 body"
        f" ({cand['function_size']} bytes).",
    ]
    if ev["file_kind"] == "header":
        parts.append("Header-file site: the macro may belong to an inlined callee.")
    reasons = flag_reasons(cand)
    if reasons:
        parts.append("Automated checks flagged: " + ", ".join(reasons) + ".")
    else:
        parts.append(
            "Automated checks passed (site in body, padded entry, prologue, no jcc into entry, single file and name)."
        )
    parts.append(
        "The string and push site are direct client evidence; the binding to this"
        " address is script-derived from the auto-analysis boundary. __FUNCTION__"
        " carries no signature."
    )
    return " ".join(parts)


def project(cands: list[dict]) -> list[dict]:
    rows = []
    for cand in cands:
        rows.append(
            {
                "name": cand["name"],
                "kind": "function",
                "address": canonical_address(cand["va"]),
                "confidence": confidence_for(cand),
                "sourceRefs": list(SOURCE_REFS),
                "notes": notes_for(cand),
            }
        )
    rows.sort(key=lambda r: (r["address"], r["name"]))
    return rows


def existing_by_address(data: dict) -> dict[int, list[dict]]:
    index: dict[int, list[dict]] = {}
    for sym in data["symbols"]:
        for part in str(sym.get("address", "")).split(";"):
            part = part.strip()
            if part.startswith("0x"):
                try:
                    index.setdefault(int(part, 16), []).append(sym)
                except ValueError:
                    continue
    return index


def same_row(existing: dict, row: dict) -> bool:
    return all(
        existing.get(k) == row[k]
        for k in ("name", "kind", "address", "confidence", "sourceRefs", "notes")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check", action="store_true", help="verify the projection without writing"
    )
    args = parser.parse_args()

    rows = project(load_candidates())
    data = _symbols_io.load_symbols()
    by_addr = existing_by_address(data)
    harvest_rows = [
        s for s in data["symbols"] if str(s.get("notes", "")).startswith(TAG)
    ]
    harvest_keys = {(s["address"], s["name"]): s for s in harvest_rows}

    to_add, skipped, drift = [], [], []
    for row in rows:
        key = (row["address"], row["name"])
        if key in harvest_keys:
            if not same_row(harvest_keys[key], row):
                drift.append(key)
            continue
        addr = int(row["address"], 16)
        if addr in by_addr:
            skipped.append(
                (row["address"], row["name"], [s["id"] for s in by_addr[addr]])
            )
            continue
        to_add.append(row)

    print(
        f"candidates: {len(rows)}; already projected: {len(rows) - len(to_add) - len(skipped)}; new: {len(to_add)}; skipped (address already catalogued): {len(skipped)}; drift: {len(drift)}"
    )
    for address, name, ids in skipped:
        print(f"  skip {address} {name} -> existing {','.join(ids)}")

    if args.check:
        if to_add or drift:
            for key in drift:
                print(f"  drift {key[0]} {key[1]}")
            print("projection drift: run without --check to update symbols.json")
            return 1
        print("projection is current")
        return 0

    if not to_add and not drift:
        print("nothing to write")
        return 0

    with _symbols_io.symbols_transaction() as live:
        live_keys = {
            (s["address"], s["name"]): s
            for s in live["symbols"]
            if str(s.get("notes", "")).startswith(TAG)
        }
        for key in drift:
            live_keys[key].update(
                next(r for r in rows if (r["address"], r["name"]) == key)
            )
        for row in to_add:
            if (row["address"], row["name"]) not in live_keys:
                _symbols_io.append_symbol(live, dict(row))
    print(f"wrote {len(to_add)} new rows and refreshed {len(drift)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
