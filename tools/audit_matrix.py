"""Matrix attribution and downstream-drift audits.

Read-only. The ``attribution`` mode detects missing RTTI, case-handler, and
wire-name links. The ``drift`` mode detects stale downstream BCS-Y links.
Both modes read the same symbols and opcode coverage manifests.

CLI:
  python tools/audit_matrix.py attribution [options]
  python tools/audit_matrix.py drift [options]
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
MATRIX_PATH = REPO / "manifests" / "pcap_opcode_coverage_matrix.json"

BCS_Y_PREFIX_RE = re.compile(r"^(BCS-Y-\d{4})\b")

# Empty bcsYIds[] is a candidate only for these catalog statuses. `noise`
# (parser garbage) and the c2s `control` heartbeat row are excluded because
# both are intentionally unattributed by design.
LATENT_CANDIDATE_STATUSES = frozenset({
    "gap",
    "covered_pattern",
    "covered_pipeline",
    "covered_pipeline_hybrid",
    "covered_pipeline_nullstub",
    "covered_receiver",
    "covered_emitter",
})

# Do not attribute direction-specific names across s2c/c2s rows. Ambiguous names remain eligible.
S2C_NAME_PATTERNS = (
    re.compile(r"S2cDispatcher_"),
    re.compile(r"ThirdRouter_"),
    re.compile(r"EventFamilyDispatcher_"),
    re.compile(r"CharaElement_Vftable"),
    re.compile(r"CharaElement_Case"),
    re.compile(r"Receiver", re.IGNORECASE),
    re.compile(r"LuaActorImpl_Slot\d+Trampoline"),
    re.compile(r"MapLayoutElement_Dispatcher"),
    re.compile(r"Chara(?:Action|Position)"),
    re.compile(r"(?:^|_)s2c(?:_|$)", re.IGNORECASE),
    re.compile(r"(?:^|_)inbound(?:_|$)", re.IGNORECASE),
    re.compile(r"(?:^|_)clientbound(?:_|$)", re.IGNORECASE),
)
C2S_NAME_PATTERNS = (
    re.compile(r"PacketBuilder"),
    re.compile(r"_Builder(?:_|$)"),
    re.compile(r"Emitter"),
    re.compile(r"Operation"),
    re.compile(r"_C2S_"),
    re.compile(r"SendRequest"),
    re.compile(r"ZoneOutbound_"),
    re.compile(r"_emit_", re.IGNORECASE),
    re.compile(r"(?:^|_)c2s(?:_|$)", re.IGNORECASE),
    re.compile(r"(?:^|_)outbound(?:_|$)", re.IGNORECASE),
    re.compile(r"(?:^|_)serverbound(?:_|$)", re.IGNORECASE),
)


def _infer_direction(name: str) -> str | None:
    """Return 's2c', 'c2s', or None (ambiguous/agnostic) based on name."""
    s2c_hit = any(p.search(name) for p in S2C_NAME_PATTERNS)
    c2s_hit = any(p.search(name) for p in C2S_NAME_PATTERNS)
    if s2c_hit and not c2s_hit:
        return "s2c"
    if c2s_hit and not s2c_hit:
        return "c2s"
    return None


def _row_direction(table_key: str) -> str:
    return "s2c" if table_key.startswith("s2c") else "c2s"


def _load_json(path: pathlib.Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _extract_bcs_y(token: str) -> str | None:
    """Extract the canonical BCS-Y-NNNN id from a token that may have
    trailing prose (e.g. 'BCS-Y-0743 RTTI')."""
    m = BCS_Y_PREFIX_RE.match(token)
    return m.group(1) if m else None


def _row_bcs_ids(row: dict) -> set[str]:
    """Return the set of canonical BCS-Y ids already referenced by a row."""
    ids: set[str] = set()
    for raw in row.get("bcsYIds", []) or []:
        if isinstance(raw, str):
            bid = _extract_bcs_y(raw)
            if bid:
                ids.add(bid)
    return ids


def _opcode_case_patterns(opcode_hex: str) -> list[re.Pattern[str]]:
    """Return regex patterns we expect to see in a BCS-Y entry's `name`
    or `notes` field that would identify it as a case-handler for the
    given opcode. The patterns are anchored with a non-hex-word-character
    lookahead so we don't get false positives where the opcode digit is a
    prefix of a longer hex number (e.g. `CaseC` must not match `CaseCA`).

    Naming conventions enumerated from the catalog:
        S2cDispatcher_*_Case<NN>_FUN_...    # NN in hex, no 0x prefix
        S2cDispatcher_HighSwitch_Case<NN>_FUN_...
        *_Case0x<NN>_*                       # NN in hex, with 0x prefix
        *_Case_0x<NN>_*                      # underscore separator
        EventFamilyDispatcher_Case0x<NN>_FUN_...
        notes: 'case 0x<NN>' / 'case_0x<NN>' / 'case <NN>'
    """
    op = opcode_hex.lower()
    n = int(op, 16)
    upper = f"{n:X}"
    lower = f"{n:x}"
    # This lookahead is what kills the `CaseC -> CaseCA` false match.
    terminator = r"(?![0-9A-Fa-f])"
    raw_patterns = {
        rf"Case0x{upper}{terminator}",
        rf"Case0x{lower}{terminator}",
        rf"Case_0x{upper}{terminator}",
        rf"Case_0x{lower}{terminator}",
        rf"Case{upper}{terminator}",
        rf"Case_{upper}{terminator}",
        rf"case 0x{upper}{terminator}",
        rf"case 0x{lower}{terminator}",
        rf"case_0x{upper}{terminator}",
        rf"case_0x{lower}{terminator}",
    }
    return [re.compile(p) for p in raw_patterns]


def _candidate_wire_names_in_notes(notes: str) -> set[str]:
    """Extract Packet/Receiver class-like identifiers from a notes blob.
    Looks for CamelCase tokens ending in Packet/Receiver/Operation/Builder.
    """
    if not notes:
        return set()
    tok_re = re.compile(r"\b([A-Z][A-Za-z0-9_]{2,}?"
                        r"(?:Packet|Receiver|Operation|Builder))\b")
    return set(tok_re.findall(notes))


def find_latent_rtti_attribution(symbols: list[dict],
                                 matrix: dict) -> list[dict]:
    """Surface RTTI BCS-Y entries that match a matrix row's
    bcsYReceiverNames[] placeholder but are not yet in bcsYIds[]."""
    findings: list[dict] = []

    rtti_by_name: list[tuple[str, str]] = [
        (s["id"], s.get("name", "")) for s in symbols
        if s.get("kind") == "rtti"
    ]

    for table_key in ("s2cOpcodeTable", "c2sOpcodeTable"):
        for row in matrix.get(table_key, []) or []:
            receiver_names = row.get("bcsYReceiverNames", []) or []
            if not receiver_names:
                continue
            existing_ids = _row_bcs_ids(row)
            for rname in receiver_names:
                if not isinstance(rname, str) or not rname:
                    continue
                matches: list[tuple[str, str]] = [
                    (rid, rfullname) for rid, rfullname in rtti_by_name
                    if rname in rfullname
                ]
                for rid, rfullname in matches:
                    if rid in existing_ids:
                        continue
                    findings.append({
                        "invariant": "latent_rtti_attribution",
                        "table": table_key,
                        "opcode": row.get("opcode"),
                        "placeholder": rname,
                        "candidate_id": rid,
                        "candidate_name": rfullname,
                        "row_bcs_ids": sorted(existing_ids),
                        "row_status": row.get("catalogStatus"),
                        "suggestion": (
                            f"ADD '{rid} RTTI' to bcsYIds[] for "
                            f"{row.get('opcode')} (matches placeholder "
                            f"{rname})"
                        ),
                    })
    return findings


def find_latent_case_handler_attribution(symbols: list[dict],
                                         matrix: dict) -> list[dict]:
    """For each matrix row with bcsYIds=[], search symbols.json for any
    BCS-Y entry whose name or notes references the row's opcode using a
    case-index naming pattern. Surface a suggestion to link the BCS-Y
    entry into the row."""
    findings: list[dict] = []

    for table_key in ("s2cOpcodeTable", "c2sOpcodeTable"):
        for row in matrix.get(table_key, []) or []:
            if row.get("bcsYIds"):
                continue
            status = row.get("catalogStatus", "")
            if status not in LATENT_CANDIDATE_STATUSES:
                continue
            opcode = row.get("opcode")
            if not isinstance(opcode, str):
                continue
            patterns = _opcode_case_patterns(opcode)
            existing_ids = _row_bcs_ids(row)
            row_dir = _row_direction(table_key)

            for s in symbols:
                # Exclude placeholders, findings, and range-cluster summaries.
                if s.get("kind") in {"finding", "note"}:
                    continue
                addr = s.get("address", "")
                if isinstance(addr, str) and addr.lower() == "0x00000000":
                    continue
                name = s.get("name", "") or ""
                notes = s.get("notes", "") or ""
                # Notes can disambiguate direction when an accessor name cannot.
                sym_dir = _infer_direction(name) or _infer_direction(notes)
                if sym_dir is not None and sym_dir != row_dir:
                    continue
                # Prefer a name match because notes can mention neighbor opcodes.
                matched_pat: re.Pattern[str] | None = None
                for p in patterns:
                    if p.search(name):
                        matched_pat = p
                        break
                if matched_pat is None:
                    for p in patterns:
                        if p.search(notes):
                            matched_pat = p
                            break
                if matched_pat is None:
                    continue
                if s["id"] in existing_ids:
                    continue
                findings.append({
                    "invariant": "latent_case_handler_attribution",
                    "table": table_key,
                    "opcode": opcode,
                    "row_status": status,
                    "candidate_id": s["id"],
                    "candidate_name": name,
                    "candidate_kind": s.get("kind"),
                    "candidate_direction": sym_dir,
                    "matched_pattern": matched_pat.pattern,
                    "matched_in": "name" if matched_pat.search(name) else "notes",
                    "suggestion": (
                        f"ADD '{s['id']}' to bcsYIds[] for {opcode} "
                        f"(catalog name contains case-handler pattern)"
                    ),
                })
    return findings


# Bind only immediate neighbors. Reject list punctuation, multi-opcode operators, and bare `-`.
# Accept `0x0005 SessionPacket`, `0x0006 = LanguageCodePacket`, `0x012E -> Receiver`,
# and `s2c 0x0177 Packet`; reject `0x0144),` and `(0x0130) - Receiver (0x019C)`.
FORWARD_GLUE_RE = re.compile(r"^(?:\s|:|=|->)*$")
BACKWARD_GLUE_RE = re.compile(r"^\s*$")
# Bound the forward window. 32 still accepts `0x0006 = LanguageCodePacket`.
FORWARD_WINDOW = 32
# The backward window accommodates `SetPushEventConditionWithTriggerBoxReceiver`.
BACKWARD_WINDOW = 48

WIRE_TOKEN_RE = re.compile(
    r"\b([A-Z][A-Za-z0-9_]{2,}?(?:Packet|Receiver|Operation|Builder))\b"
)

MULTI_OPCODE_NEIGHBOR_CHARS = set(",;+/")

# BCS-Y-0345 uses `(0x10)` as a struct size, not opcode 0x0010.
WIRE_NAME_DENY_LIST: dict[tuple[str, str], frozenset[str]] = {
    ("BCS-Y-0345", "0x0010"): frozenset({"BasePacket", "SubPacket", "GameMessage"}),
}


def _opcode_match_spans(opcode_hex: str, blob: str) -> list[tuple[int, int]]:
    """Return (start, end) positions of every standalone opcode mention."""
    n = int(opcode_hex.lower(), 16)
    forms = sorted({
        opcode_hex.lower(),
        f"0x{n:X}",
        f"0x{n:x}",
        f"0x{n:04X}",
        f"0x{n:04x}",
    })
    alternation = "|".join(re.escape(f) for f in forms)
    pat = re.compile(rf"(?<![0-9A-Fa-f])(?:{alternation})(?![0-9A-Fa-f])")
    return [m.span() for m in pat.finditer(blob)]


def _opcode_is_in_multi_group(blob: str, op_s: int, op_e: int) -> bool:
    """True if the opcode mention sits inside a multi-opcode group such
    as `0x012E + 0x016B`, `0x12E/0x16B`, or `0x012e..0x01f5`. The check
    looks at the immediate non-space neighbors on each side."""
    i = op_s - 1
    while i >= 0 and blob[i] == " ":
        i -= 1
    if i >= 0 and blob[i] in {"+", "/"}:
        return True
    if i >= 1 and blob[i - 1:i + 1] == "..":
        return True
    j = op_e
    while j < len(blob) and blob[j] == " ":
        j += 1
    if j < len(blob) and blob[j] in {"+", "/"}:
        return True
    if j + 1 < len(blob) and blob[j:j + 2] == "..":
        return True
    return False


def _forward_bound_wire_name(blob: str, op_s: int, op_e: int) -> str | None:
    """Return the wire-name token that is the FIRST capitalized neighbor
    AFTER the opcode, only if the intervening glue is binding-only
    (whitespace, `:`, `=`, `->`). Reject if `,`, `;`, `)`, `(`, or a bare
    `-` (not `->`) sits between the opcode and the candidate."""
    if op_e < len(blob) and blob[op_e] in MULTI_OPCODE_NEIGHBOR_CHARS:
        return None
    window = blob[op_e:op_e + FORWARD_WINDOW]
    tok_m = WIRE_TOKEN_RE.search(window)
    if not tok_m:
        return None
    glue = window[:tok_m.start()]
    if not FORWARD_GLUE_RE.match(glue):
        return None
    return tok_m.group(1)


def _backward_bound_wire_name(blob: str, op_s: int, op_e: int) -> str | None:
    """Return the wire-name token that is the LAST capitalized neighbor
    BEFORE the opcode, only if the opcode is wrapped in parens like
    `(0x12F)` and only whitespace sits between the wire name and the
    opening paren."""
    if op_e >= len(blob) or blob[op_e] != ")":
        return None
    open_idx = blob.rfind("(", max(0, op_s - 8), op_s)
    if open_idx < 0:
        return None
    if not BACKWARD_GLUE_RE.match(blob[open_idx + 1:op_s]):
        return None
    window_start = max(0, open_idx - BACKWARD_WINDOW)
    last: re.Match[str] | None = None
    for m in WIRE_TOKEN_RE.finditer(blob, window_start, open_idx):
        last = m
    if last is None:
        return None
    glue = blob[last.end():open_idx]
    if not BACKWARD_GLUE_RE.match(glue):
        return None
    return last.group(1)


def _bound_wire_names_for_opcode(opcode_hex: str,
                                 blob: str) -> set[str]:
    """Apply the directional binding heuristic to every opcode mention in
    `blob` and return the union of wire names that survive."""
    names: set[str] = set()
    for (op_s, op_e) in _opcode_match_spans(opcode_hex, blob):
        if _opcode_is_in_multi_group(blob, op_s, op_e):
            continue
        fwd = _forward_bound_wire_name(blob, op_s, op_e)
        if fwd is not None:
            names.add(fwd)
        bwd = _backward_bound_wire_name(blob, op_s, op_e)
        if bwd is not None:
            names.add(bwd)
    return names


def find_latent_wire_name_curation(symbols: list[dict],
                                   matrix: dict) -> list[dict]:
    """Lower-priority curation hint. For each matrix row, check if any
    BCS-Y entry's notes contain a wire-packet name in a recognised
    immediate-neighbor binding shape with the row's opcode (see the
    module-level note above), where the matrix row's own notes do NOT
    already mention that wire name.
    """
    findings: list[dict] = []

    for table_key in ("s2cOpcodeTable", "c2sOpcodeTable"):
        row_dir = _row_direction(table_key)
        for row in matrix.get(table_key, []) or []:
            opcode = row.get("opcode")
            if not isinstance(opcode, str):
                continue
            row_notes = row.get("notes", "") or ""
            row_wire_names = _candidate_wire_names_in_notes(row_notes)

            for s in symbols:
                sym_notes = s.get("notes", "") or ""
                if not sym_notes:
                    continue
                bound_names = _bound_wire_names_for_opcode(opcode, sym_notes)
                if not bound_names:
                    continue
                # Skip opposite-direction names. Ambiguous names remain eligible.
                sym_dir = _infer_direction(s.get("name", "") or "")
                if sym_dir is not None and sym_dir != row_dir:
                    continue
                # Apply the per-entry deny-list after binding detection.
                deny_key = (s.get("id", ""), opcode.lower())
                denied = WIRE_NAME_DENY_LIST.get(deny_key, frozenset())
                if denied:
                    bound_names = bound_names - denied
                    if not bound_names:
                        continue
                missing = sorted(bound_names - row_wire_names)
                if not missing:
                    continue
                findings.append({
                    "invariant": "latent_wire_name_curation",
                    "table": table_key,
                    "opcode": opcode,
                    "candidate_id": s["id"],
                    "candidate_name": s.get("name", ""),
                    "candidate_direction": sym_dir,
                    "wire_names_in_symbol": sorted(bound_names),
                    "missing_from_row": missing,
                    "row_notes_excerpt": row_notes[:80],
                    "suggestion": (
                        f"CONSIDER adding wire name(s) {missing} to notes "
                        f"of {opcode} (sourced from {s['id']})"
                    ),
                })
    return findings


def print_markdown_report(findings_by_invariant: dict[str, list[dict]]) -> None:
    rtti = findings_by_invariant.get("latent_rtti_attribution", [])
    case = findings_by_invariant.get("latent_case_handler_attribution", [])
    wire = findings_by_invariant.get("latent_wire_name_curation", [])

    print("matrix-vs-catalog attribution audit")
    print("====================================")
    print()
    print(f"[Latent RTTI attribution] {len(rtti)} findings")
    for f in rtti:
        print(f"  {f['opcode']}: row has bcsYReceiverNames={f['placeholder']!r} "
              f"but {f['candidate_id']} matches in symbols.json")
        print(f"    suggest: ADD '{f['candidate_id']} RTTI' to bcsYIds[]")
        print(f"    candidate: {f['candidate_name']}")
    if not rtti:
        print("  (none)")
    print()

    print(f"[Latent case-handler attribution] {len(case)} findings")
    by_opcode: dict[str, list[dict]] = {}
    for f in case:
        by_opcode.setdefault(f["opcode"], []).append(f)
    for opcode in sorted(by_opcode.keys()):
        rows = by_opcode[opcode]
        for f in rows:
            where = f.get("matched_in", "?")
            print(f"  {opcode}: row has bcsYIds=[] but {f['candidate_id']} "
                  f"{where} mentions {f['matched_pattern']!r}")
            print(f"    suggest: ADD '{f['candidate_id']}' to bcsYIds[]")
            print(f"    candidate: {f['candidate_name']}")
    if not case:
        print("  (none)")
    print()

    print(f"[Latent wire-name curation] {len(wire)} findings "
          f"(lower priority - advisory, does not fail the gate)")
    seen: set[tuple[str, str]] = set()
    aggregated: list[tuple[str, str, str]] = []
    for f in wire:
        for wn in f["missing_from_row"]:
            key = (f["opcode"], wn)
            if key in seen:
                continue
            seen.add(key)
            aggregated.append((f["opcode"], wn, f["candidate_id"]))
    aggregated.sort()
    for opcode, wn, cid in aggregated[:40]:
        print(f"  {opcode}: catalog notes mention '{wn}' (sourced from {cid})")
    extra = max(0, len(aggregated) - 40)
    if extra:
        print(f"  ... and {extra} more (omitted; use --json for full list)")
    if not wire:
        print("  (none)")
    print()

    total = len(rtti) + len(case) + len(wire)
    print(f"Summary: {len(rtti)} latent RTTI + {len(case)} latent "
          f"case-handler + {len(wire)} latent wire-name = "
          f"{total} total findings")


def _run_attribution(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="audit_matrix_attribution",
        description=(
            "Detect matrix attribution gaps where symbols.json already has "
            "the BCS-Y entry but the matrix row is not pointing to it."
        ),
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Emit machine-readable JSON report on stdout.",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Reserved compatibility no-op.",
    )
    parser.add_argument(
        "--invariant", choices=("rtti", "case_handler", "wire_name", "all"),
        default="all",
        help="Run only one invariant (default: all).",
    )
    args = parser.parse_args(argv)

    if args.apply:
        print("--apply is reserved; no write performed.", file=sys.stderr)

    symbols_doc = _load_json(SYMBOLS_PATH)
    matrix_doc = _load_json(MATRIX_PATH)
    symbols = symbols_doc["symbols"]

    findings_by_invariant: dict[str, list[dict]] = {
        "latent_rtti_attribution": [],
        "latent_case_handler_attribution": [],
        "latent_wire_name_curation": [],
    }

    if args.invariant in ("rtti", "all"):
        findings_by_invariant["latent_rtti_attribution"] = (
            find_latent_rtti_attribution(symbols, matrix_doc))
    if args.invariant in ("case_handler", "all"):
        findings_by_invariant["latent_case_handler_attribution"] = (
            find_latent_case_handler_attribution(symbols, matrix_doc))
    if args.invariant in ("wire_name", "all"):
        findings_by_invariant["latent_wire_name_curation"] = (
            find_latent_wire_name_curation(symbols, matrix_doc))

    if args.json:
        report = {
            "tool": "audit_matrix_attribution",
            "symbols_source": str(SYMBOLS_PATH.relative_to(REPO)),
            "matrix_source": str(MATRIX_PATH.relative_to(REPO)),
            "findings": findings_by_invariant,
            "totals": {k: len(v) for k, v in findings_by_invariant.items()},
        }
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print_markdown_report(findings_by_invariant)

    # Only latent RTTI and case-handler findings fail. Wire-name findings are advisory.
    structural = (len(findings_by_invariant["latent_rtti_attribution"])
                  + len(findings_by_invariant["latent_case_handler_attribution"]))
    return 1 if structural else 0


FUN_VA_RE = re.compile(r"\bFUN_([0-9a-fA-F]{8})\b")
# Case0xNN tokens identify sibling handlers with a different opcode.
HEX_TOKEN_RE = re.compile(r"0x([0-9a-fA-F]+)")
CASE_PREFIX_RE = re.compile(r"(?:Case|Cases)_?0x", re.IGNORECASE)

# Exclude upstream Callers lists and negated FUN_VA mentions from drift.
NEG_CONTEXT_WINDOW = 80
CALLERS_PREFIX_RE = re.compile(r"\bCallers?:", re.IGNORECASE)
NEGATION_PREFIX_RE = re.compile(
    r"\b(NOT|never|bypass(?:es)?)\b", re.IGNORECASE
)
# A period or newline ends the Callers/negation scope.
SCOPE_END_RE = re.compile(r"[.\n]")

# Shared utilities appeared across 14 and 11 rows. BCS-Y-1801 is the 11-row case.
# Demote only LOW findings above this threshold. HIGH findings name the opcode directly.
UBIQUITOUS_ROW_THRESHOLD = 4

DRIFT_AUDIT_STATUSES = frozenset({
    "covered_pattern",
    "covered_pipeline_hybrid",
})


def _opcode_mention_patterns(opcode_hex: str) -> list[re.Pattern[str]]:
    """Patterns that indicate a notes string is explicitly naming the
    given opcode. Mirrors _opcode_case_patterns
    but tuned for downstream-entry note phrasing (where the BCS-Y is the
    callee, not the case-handler itself).

    Recognized phrasings:
        "for s2c 0x017A"       schema-rescue convention
        "s2c 0x017A"           plain
        "0x0183 ultimate_callee" / "opcode_table 0x0183"
        "Consumes s2c 0x0183"
        "for c2s 0x012D"
        "case 0x18D" / "Case0x18D"  (also matches case-handler self refs;
                                     conservative but fine for drift use)

    Both stripped-zero (0x187) and 4-digit zero-padded (0x0187) forms are
    generated. Matrix rows use the 4-digit form by convention, but in-
    notes opcode mentions vary between the two. Generating both catches
    both phrasings without false-positive risk (the (?![0-9A-Fa-f])
    terminator prevents 0x187 from matching inside 0x1876).
    """
    op = opcode_hex.lower().removeprefix("0x")
    n = int(op, 16)
    terminator = r"(?![0-9A-Fa-f])"
    forms: set[str] = {f"{n:X}", f"{n:x}", f"{n:04X}", f"{n:04x}"}
    raw_patterns: set[str] = set()
    for form in forms:
        raw_patterns.add(rf"\b0x{form}{terminator}")
        raw_patterns.add(rf"Case0x{form}{terminator}")
        raw_patterns.add(rf"Case_0x{form}{terminator}")
    return [re.compile(p) for p in raw_patterns]


def build_address_index(symbols: list[dict]) -> dict[str, dict]:
    """Map canonical lowercase 0xXXXXXXXX address -> BCS-Y entry."""
    idx: dict[str, dict] = {}
    for s in symbols:
        addr = s.get("address")
        if not isinstance(addr, str):
            continue
        addr_lower = addr.lower()
        if addr_lower == "0x00000000" or addr_lower == "0x0":
            continue
        # Composite addresses are not scalar targets for this audit.
        if ";" in addr or ".." in addr:
            continue
        idx[addr_lower] = s
    return idx


def build_id_index(symbols: list[dict]) -> dict[str, dict]:
    """Map BCS-Y-NNNN id -> entry."""
    return {s["id"]: s for s in symbols if isinstance(s.get("id"), str)}


def is_negative_context(notes: str, va_match: re.Match) -> bool:
    """Return True if the FUN_VA at va_match appears in a "Callers:"
    list or in a negation context (NOT, never, bypass) within the
    primary's notes.

    Window: NEG_CONTEXT_WINDOW chars before the match. The keyword must
    be inside the window AND no sentence-ending punctuation (.\\n) may
    appear between the keyword and the VA (otherwise the keyword scope
    has ended).

    Catches the C50 false-positive class:
      - BCS-Y-0124 / 0125 notes use "Callers: FUN_0076D450 ..." to list
        upstream callers of the receiver; drift tool was flagging the
        listed FUN_VAs as downstream pipeline candidates.
      - BCS-Y-0662 notes explicitly say "NOT forwarded to FUN_004D8860";
        drift tool was matching the FUN_VA and ignoring the NOT.
    """
    start = max(0, va_match.start() - NEG_CONTEXT_WINDOW)
    before = notes[start:va_match.start()]
    if not before:
        return False
    for prefix_re in (CALLERS_PREFIX_RE, NEGATION_PREFIX_RE):
        kw_matches = list(prefix_re.finditer(before))
        if not kw_matches:
            continue
        last_kw = kw_matches[-1]
        between = before[last_kw.end():]
        if not SCOPE_END_RE.search(between):
            return True
    return False


def is_sibling_context(downstream_name: str, row_opcode_hex: str) -> bool:
    """Return True if downstream entry's name encodes a Case0xNN opcode
    different from the row's opcode (i.e., the downstream is for a
    SIBLING case, not a downstream of this row).

    Heuristic:
      1. Extract all 0x... hex tokens from name (excludes longer FUN_VAs
         by length filter: case ids are 1-4 hex digits, FUN_VAs are 8).
      2. If any opcode-length token equals the row opcode -> NOT sibling
         (downstream legitimately covers this opcode, possibly among
         several in a paired Cases0xNN_0xMM form).
      3. If all opcode-length tokens are non-matching AND the name has
         Case/Cases prefix (indicating it IS a case handler) -> sibling.
      4. Otherwise (no Case prefix, just incidental hex) -> NOT sibling
         (insufficient evidence to flag).

    Catches the C34 false-positive class: BCS-Y-0625
    ThirdRouter_Case0xDA_DefaultsForwardWrapper_FUN_0058CAD0 flagged as
    HIGH drift for row 0x00E1 because BCS-Y-0631 (0x00E1 primary)
    mentioned the shared FUN_VA. The downstream's name says 0xDA, not
    0xE1 -> SIBLING_CONTEXT, not a true drift target.
    """
    try:
        row_n = int(row_opcode_hex.removeprefix("0x"), 16)
    except (ValueError, AttributeError):
        return False
    hex_tokens = HEX_TOKEN_RE.findall(downstream_name)
    opcode_tokens = [t for t in hex_tokens if 1 <= len(t) <= 4]
    if not opcode_tokens:
        return False
    if any(int(t, 16) == row_n for t in opcode_tokens):
        return False
    if CASE_PREFIX_RE.search(downstream_name):
        return True
    return False


def audit_row(row: dict, table_key: str, addr_idx: dict, id_idx: dict
              ) -> list[dict]:
    """Return drift findings for a single row."""
    findings: list[dict] = []
    opcode = row.get("opcode", "<?>")
    existing_ids = _row_bcs_ids(row)
    pcap = row.get("pcapCount", 0)
    op_patterns = _opcode_mention_patterns(opcode)

    for primary_id in existing_ids:
        primary = id_idx.get(primary_id)
        if not primary:
            continue
        notes = primary.get("notes", "")
        if not isinstance(notes, str):
            continue
        seen_vas: set[str] = set()
        for m in FUN_VA_RE.finditer(notes):
            va = "0x" + m.group(1).lower()
            if va in seen_vas:
                continue
            seen_vas.add(va)
            primary_addr = primary.get("address", "").lower()
            if va == primary_addr:
                continue
            downstream = addr_idx.get(va)
            if not downstream:
                continue
            downstream_id = downstream.get("id")
            if downstream_id in existing_ids:
                continue
            downstream_name = downstream.get("name", "")
            if is_negative_context(notes, m):
                conf = "NEGATIVE_CONTEXT"
            elif is_sibling_context(downstream_name, opcode):
                conf = "SIBLING_CONTEXT"
            else:
                ds_notes = downstream.get("notes", "")
                high_conf = isinstance(ds_notes, str) and any(
                    p.search(ds_notes) for p in op_patterns
                )
                conf = "HIGH" if high_conf else "LOW"
            findings.append({
                "table": table_key,
                "opcode": opcode,
                "pcap": pcap,
                "status": row.get("catalogStatus"),
                "primaryId": primary_id,
                "downstreamId": downstream_id,
                "downstreamFunVa": va,
                "downstreamName": downstream_name,
                "confidence": conf,
            })
    return findings


def demote_ubiquitous(findings: list[dict]) -> list[dict]:
    """Demote LOW findings whose downstream spans too many distinct rows.

    Ubiquity is a property of the downstream symbol, so the row spread is
    counted across every bucket, not just LOW. Only LOW findings are
    demoted: HIGH means the downstream's own notes name this row's opcode,
    which is stronger evidence than the heuristic and must not be
    overridden. Mutates and returns the same list.

    Catches the C131 false-positive class: BCS-Y-1801
    ScopedSidHandle_ctor_FUN_00CC9320, a generic RAII helper cataloged in
    C119, matched every row whose primary notes mention FUN_00CC9320 and
    put 12 findings across 11 rows into the LOW bucket - one false
    positive multiplied, not 12 drift cases.
    """
    spread: dict[str, set[tuple[str, str]]] = {}
    for f in findings:
        spread.setdefault(f["downstreamId"], set()).add(
            (f["table"], f["opcode"])
        )
    for f in findings:
        rows = len(spread[f["downstreamId"]])
        f["ubiquityRows"] = rows
        if f["confidence"] == "LOW" and rows > UBIQUITOUS_ROW_THRESHOLD:
            f["confidence"] = "UBIQUITOUS_HELPER"
    return findings


def audit_matrix(matrix: dict, symbols: list[dict]) -> list[dict]:
    addr_idx = build_address_index(symbols)
    id_idx = build_id_index(symbols)
    all_findings: list[dict] = []
    for table_key in ("s2cOpcodeTable", "c2sOpcodeTable"):
        for row in matrix.get(table_key, []):
            if row.get("catalogStatus") not in DRIFT_AUDIT_STATUSES:
                continue
            all_findings.extend(audit_row(row, table_key, addr_idx, id_idx))
    return demote_ubiquitous(all_findings)


_BUCKET_BLURBS = {
    "HIGH": ("downstream BCS-Y explicitly names the row opcode;"
             " safe for immediate matrix sync"),
    "LOW": ("downstream BCS-Y cataloged at FUN_VA from primary notes"
            " but opcode not stated; manual review"),
    "SIBLING_CONTEXT": ("downstream BCS-Y's name encodes a Case0xNN opcode"
                        " DIFFERENT from this row's opcode; the primary's"
                        " notes mention it as a shared/sibling helper, not"
                        " as a downstream pipeline step (D17 filter)"),
    "NEGATIVE_CONTEXT": ("FUN_VA appears in primary's notes inside a"
                         " 'Callers:' list (upstream caller, not downstream)"
                         " or in a NOT/never/bypass negation context"
                         " (C50 filter)"),
    "UBIQUITOUS_HELPER": ("same downstream cited as a drift-add across more"
                          f" than {UBIQUITOUS_ROW_THRESHOLD} distinct rows;"
                          " a shared utility, not one row's pipeline step"
                          " (C132 filter)"),
}

# Buckets that are documented false-positive classes: hidden by default and
# never gating. HIGH and LOW are the reviewable ones.
FP_BUCKETS = ("SIBLING_CONTEXT", "NEGATIVE_CONTEXT", "UBIQUITOUS_HELPER")


def _render_text(findings: list[dict], high_only: bool,
                 include_sibling: bool) -> str:
    out: list[str] = []
    out.append("=" * 72)
    out.append("MATRIX DRIFT AUDIT")
    out.append("=" * 72)
    by_conf: dict[str, list[dict]] = {"HIGH": [], "LOW": []}
    for b in FP_BUCKETS:
        by_conf[b] = []
    for f in findings:
        by_conf.setdefault(f["confidence"], []).append(f)

    buckets_to_show = ["HIGH"]
    if not high_only:
        buckets_to_show.append("LOW")
    if include_sibling:
        buckets_to_show.extend(FP_BUCKETS)

    for conf in buckets_to_show:
        bucket = by_conf[conf]
        if not bucket:
            out.append(f"\n--- {conf} CONFIDENCE: 0 findings ---")
            continue
        bucket.sort(key=lambda f: (-f["pcap"], f["table"], f["opcode"]))
        total_pcap = sum(f["pcap"] for f in bucket)
        unique_rows = len({(f["table"], f["opcode"]) for f in bucket})
        out.append(f"\n--- {conf} CONFIDENCE: {len(bucket)} findings "
                   f"across {unique_rows} rows ({total_pcap} pcap) ---")
        out.append(f"    ({_BUCKET_BLURBS[conf]})")
        for f in bucket:
            direction = "s2c" if f["table"].startswith("s2c") else "c2s"
            out.append(
                f"\n  {direction} {f['opcode']} (pcap={f['pcap']}, "
                f"status={f['status']})"
            )
            out.append(
                f"    primary  : {f['primaryId']}"
            )
            out.append(
                f"    drift add: {f['downstreamId']} {f['downstreamName']}"
            )
            out.append(
                f"               (at {f['downstreamFunVa']})"
            )

    out.append("\n" + "=" * 72)
    summary_bits = [
        f"{len(by_conf['HIGH'])} HIGH",
        f"{len(by_conf['LOW'])} LOW",
    ]
    summary_bits += [f"{len(by_conf[b])} {b}" for b in FP_BUCKETS]
    out.append(f"SUMMARY: {' + '.join(summary_bits)}"
               f" = {len(findings)} total findings")
    high_pcap = sum(f["pcap"] for f in by_conf["HIGH"])
    high_rows = len({(f["table"], f["opcode"]) for f in by_conf["HIGH"]})
    out.append(f"HIGH-confidence: {high_rows} rows, {high_pcap} pcap "
               f"re-classifiable via matrix sync (zero new BCS-Y needed)")
    hidden_bits = []
    if not include_sibling:
        hidden_bits = [f"{len(by_conf[b])} {b}" for b in FP_BUCKETS
                       if by_conf[b]]
    if hidden_bits:
        out.append("(" + " + ".join(hidden_bits)
                   + " findings hidden; pass --include-sibling to see them)")
    out.append("=" * 72)
    return "\n".join(out)


def _actionable_count(findings: list[dict], high_only: bool,
                      include_sibling: bool) -> int:
    """Count findings in the buckets the current flags actually surface.

    The exit code must track what the run displays: `--high-only` shows only
    HIGH, so it must not fail on the hidden buckets. The FP_BUCKETS are
    triaged false-positive classes and never gate; LOW is reviewable but
    only gates on a default run, which is why `--high-only` is the clean
    actionable gate documented in tools/README.md.
    """
    shown = {"HIGH"}
    if not high_only:
        shown.add("LOW")
    if include_sibling:
        shown.update(FP_BUCKETS)
    return sum(1 for f in findings if f["confidence"] in shown)


def _run_drift(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--json", action="store_true",
                   help="emit machine-readable JSON instead of text report")
    p.add_argument("--high-only", action="store_true",
                   help="suppress LOW-confidence findings in text report")
    p.add_argument("--include-sibling", action="store_true",
                   help="also show the triaged false-positive buckets"
                        " (SIBLING_CONTEXT, NEGATIVE_CONTEXT,"
                        " UBIQUITOUS_HELPER), hidden by default")
    args = p.parse_args(argv)

    try:
        symbols_doc = _load_json(SYMBOLS_PATH)
        matrix_doc = _load_json(MATRIX_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2

    symbols = symbols_doc.get("symbols", [])
    findings = audit_matrix(matrix_doc, symbols)

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        print(_render_text(findings, args.high_only, args.include_sibling))

    return 1 if _actionable_count(
        findings, args.high_only, args.include_sibling) else 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("attribution", "drift"):
        print("usage: audit_matrix.py {attribution,drift} [options]", file=sys.stderr)
        return 2
    mode, *mode_args = argv
    if mode == "attribution":
        return _run_attribution(mode_args)
    return _run_drift(mode_args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
