"""Hygiene scans for the xivl-client-structs repo.

Read-only. Produces a structured report covering:
  A1: pcap coverage matrix vs symbols.json reconciliation
  A2: Duplicate-address scan in symbols.json
  A3: SourceRef path normalization inventory (symbols.json + structs.json).
      Every parent-dir ref ("../..." or "..\\...") is a defect
      (live_parent_path): sibling-repo citations must be repo:path
      strings, not live filesystem paths, so this check never resolves
      anything outside this repo's own checkout. A ref matching the
      citation form (repo:path; legacy repo@40-hex-commit[:path] also
      accepted) is ok (category "citation") and is validated by shape
      only. Maintainer-record labels (ledger:/notes:/mdi-N/finding-N and
      the register names) are ok (category "record_label"). An in-repo
      relative path is still resolved on disk and reported if missing.
      Absolute paths and other shapes keep their prior buckets.
  A4: Wiki-link integrity sweep (folds in the earlier manual pass) over
      docs/*.md, symbols.json/structs.json notes, snapshot-manifest
      string values, and tools/extractors/*.py. Classifies each [[link]] as
      PASS (target in valid set), SKIP (known false positive), or FAIL
      (real broken link). Skip categories:
        meta_placeholder target is the literal '...' placeholder
        python_interp target contains a Python f-string {var} or %s
        historical_extractor   [[link]] sits in tools/extractors/*.py (write-
                            once scripts whose JSON output is the artifact
                            of record; the script text is not maintained)
  A5: Embedded {bcsId, address} pairs in the derived snapshot manifests
      vs the canonical address in symbols.json. Advisory: drift means a
      generated manifest predates a symbols.json address rebase and needs
      regeneration.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import _symbols_io  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
SYMBOLS = REPO / "manifests" / "symbols.json"
STRUCTS = REPO / "manifests" / "structs.json"
MATRIX = REPO / "manifests" / "pcap_opcode_coverage_matrix.json"

# Named catalogs are maintained products. Every other JSON manifest is a snapshot.
NAMED_CATALOGS = frozenset({
    "c2s_bridge_skeleton.json", "client_class_registry.json",
    "control_class_napi_field_access.json",
    "control_class_napi_field_access_recursive.json",
    "control_class_napi_map.json", "data_dependency_catalog.json",
    "gam_hash_names.json", "ir_catalog.json", "ir_overlay.json", "lua_api_index.json",
    "lua_apply_chain_firers.json", "lua_to_opcode.json",
    "operation_opcode_map_outbound.json", "operation_opcode_map_overlay.json",
    "receiver_field_writes.json", "receiver_opcode_map_inbound.json",
    "receiver_opcode_map_overlay.json", "retail_actor_rebuild_check.json",
    "retail_inputs.json", "rtti_vftable_index.json",
    "structs.json", "symbols.json",
})


def _snapshots():
    """Return per-investigation snapshot manifests."""
    return sorted(p for p in MANIFESTS_DIR.glob("*.json")
                  if p.name not in NAMED_CATALOGS)
MANIFESTS_DIR = REPO / "manifests"
DOCS_DIR = REPO / "docs"
LOCAL_DOCS_DIR = DOCS_DIR / "ai_agents" / "local"
EXTRACTORS_DIR = REPO / "tools" / "extractors"

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
# Python interpolation placeholders inside link targets: f-string {var}, %s, etc.
PY_INTERP_RE = re.compile(r"\{[^}]*\}|%[sdrfx]")


def load_symbols():
    return _symbols_io.load_symbols(SYMBOLS)


def load_matrix():
    with MATRIX.open(encoding="utf-8") as f:
        return json.load(f)


def load_structs():
    with STRUCTS.open(encoding="utf-8") as f:
        return json.load(f)


def scan_a1_matrix_vs_symbols(symbols, matrix):
    """For each matrix row, find symbols.json entries whose notes/name mention
    that opcode. Report:
      - matrix-gap rows where symbols.json HAS references (potential stale gap)
      - matrix-listed BCS-Y IDs that don't exist in symbols.json
    """
    by_id = {s["id"]: s for s in symbols["symbols"]}

    def opcode_variants(opcode_hex: str) -> list[str]:
        canonical = opcode_hex.lower()
        as_int = int(canonical, 16)
        short_hex = hex(as_int)
        wide_hex = f"0x{as_int:04x}"
        return list({canonical, short_hex.lower(), wide_hex.lower(),
                     canonical.upper(),
                     wide_hex.upper(), short_hex.upper(),
                     f"case 0x{as_int:X}", f"case 0x{as_int:x}",
                     f"case {as_int}"})

    def references_opcode(sym, variants: list[str]) -> bool:
        if sym.get("kind") == "global" and sym.get("name", "").lower().startswith("phase"):
            return False
        if sym.get("address", "").lower() == "0x00000000":
            return False
        blob = (sym.get("notes", "") + " " + sym.get("name", "")).lower()
        return any(v.lower() in blob for v in variants)

    results = {
        "matrix_gaps_with_symbol_refs": [],
        "matrix_listed_ids_missing": [],
        "matrix_empty_bcs_ids_with_symbol_refs": [],
    }

    for direction, table_key in [("s2c", "s2cOpcodeTable"),
                                  ("c2s", "c2sOpcodeTable")]:
        for row in matrix[table_key]:
            opcode = row["opcode"]
            variants = opcode_variants(opcode)
            bcs_ids_raw = row.get("bcsYIds", [])
            bcs_ids = [re.match(r"(BCS-Y-\d+)", x).group(1)
                       for x in bcs_ids_raw if re.match(r"BCS-Y-\d+", x)]
            status = row.get("catalogStatus", "")

            for bid in bcs_ids:
                if bid not in by_id:
                    results["matrix_listed_ids_missing"].append({
                        "direction": direction,
                        "opcode": opcode,
                        "missing_id": bid,
                        "row_status": status,
                    })

            if status == "gap" or not bcs_ids:
                refs = [s["id"] for s in symbols["symbols"]
                        if references_opcode(s, variants)]
                if refs and status == "gap":
                    results["matrix_gaps_with_symbol_refs"].append({
                        "direction": direction,
                        "opcode": opcode,
                        "pcapCount": row.get("pcapCount"),
                        "status": status,
                        "matrix_notes": row.get("notes", "")[:120],
                        "symbol_refs": refs[:10],
                        "ref_count": len(refs),
                    })
                elif refs and not bcs_ids and status != "gap":
                    results["matrix_empty_bcs_ids_with_symbol_refs"].append({
                        "direction": direction,
                        "opcode": opcode,
                        "pcapCount": row.get("pcapCount"),
                        "status": status,
                        "matrix_notes": row.get("notes", "")[:120],
                        "symbol_refs": refs[:10],
                        "ref_count": len(refs),
                    })

    return results


def scan_a2_duplicate_addresses(symbols):
    addr_map = defaultdict(list)
    for s in symbols["symbols"]:
        addr = s.get("address", "").lower()
        if addr:
            addr_map[addr].append((s["id"], s["name"], s.get("kind", "")))

    dupes = {addr: entries for addr, entries in addr_map.items() if len(entries) > 1}
    return dupes


def scan_a3_orphaned_manifests(ledger_path: pathlib.Path):
    """Snapshot manifests the ledger never names. Advisory, never gating."""
    manifest_files = _snapshots()
    ledger_text = ledger_path.read_text(encoding="utf-8")

    orphans = []
    for mf in manifest_files:
        if mf.stem in ledger_text or mf.name in ledger_text:
            continue
        orphans.append({"manifest": mf.name, "files": [mf.name]})

    return orphans, len(manifest_files)


# Validate `repo:path` citations by shape. Provenance hashes establish byte identity.
# Reject commit pins because flattened sibling histories make them dangling.
A3_CITATION_RE = re.compile(
    r"^[A-Za-z][A-Za-z0-9._-]+:(?![\\/])\S.*$")

# Maintainer-record labels: identifiers for retired or islanded maintainer
# records (not paths). ledger:/notes: name a topic. mdi-N and finding-N name
# numbered register entries.
A3_RECORD_LABEL_RE = re.compile(
    r"^(ledger:|notes:|mdi-\d+$|finding-\d+$|promotion-register$|"
    r"maintainer-ledger$|open-questions-register$|"
    r"architectural-findings-register$)")


def _exists_on_disk(rel_path: str) -> bool:
    try:
        return (REPO / rel_path).resolve().exists()
    except OSError:
        return False


def _classify_ref(ref: str, exists=_exists_on_disk) -> tuple[str, str | None]:
    """Classify a sourceRef. Returns (status, category).

    status is 'ok' or 'defect'. A live parent-dir path ("../..." or
    "..\\...") is always a defect - sibling-repo references must be
    repo:path citations, never a path into a sibling checkout on disk. An in-repo relative path is resolved through the
    `exists` predicate, which defaults to this checkout's filesystem.

    `exists` is injectable because this vocabulary has one home but two
    readers with different notions of "present": this scan reports on the
    working tree an author is looking at, while tools/build_ir.py must
    decide from tracked content, so that a generated artifact does not
    depend on untracked or gitignored files.
    """
    if ref.startswith("../") or ref.startswith("..\\"):
        return ("defect", "live_parent_path")
    if A3_RECORD_LABEL_RE.match(ref):
        return ("ok", "record_label")
    if A3_CITATION_RE.match(ref):
        return ("ok", "citation")
    return (("ok", "repo_relative") if exists(ref.split("#")[0])
            else ("defect", "missing_repo_relative"))


def scan_a3_sourcerefs(symbols, structs):
    categories = defaultdict(int)
    backslash_paths = []
    absolute_paths = []
    citation_examples = []
    live_parent_paths = []
    missing_repo_relative = []

    entries = [(s["id"], s) for s in symbols["symbols"]]
    entries += [(st["id"], st) for st in structs.get("structs", [])]

    for eid, s in entries:
        for ref in s.get("sourceRefs", []):
            if not ref:
                continue
            has_backslash = "\\" in ref
            is_absolute = bool(re.match(r"^[A-Za-z]:", ref))

            status, category = _classify_ref(ref)

            if is_absolute:
                categories["absolute"] += 1
                absolute_paths.append({"id": eid, "ref": ref})
                continue

            if category == "live_parent_path":
                categories["live_parent_path"] += 1
                live_parent_paths.append({"id": eid, "ref": ref})
            elif category == "citation":
                categories["citation"] += 1
                if len(citation_examples) < 10:
                    citation_examples.append({"id": eid, "ref": ref})
            elif category == "missing_repo_relative":
                categories["missing_repo_relative"] += 1
                missing_repo_relative.append({"id": eid, "ref": ref})
            elif has_backslash:
                categories["repo_relative_backslash"] += 1
                backslash_paths.append({"id": eid, "ref": ref})
            else:
                categories["repo_relative_forward"] += 1

    return {
        "categories": dict(categories),
        "backslash_examples": backslash_paths[:10],
        "absolute_examples": absolute_paths[:20],
        "citation_examples": citation_examples,
        "live_parent_paths": live_parent_paths,
        "missing_repo_relative": missing_repo_relative,
    }


def _walk_json_strings(node):
    """Yield every string value reachable from a JSON-decoded structure."""
    if isinstance(node, dict):
        for v in node.values():
            yield from _walk_json_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk_json_strings(v)
    elif isinstance(node, str):
        yield node


def _build_valid_targets(symbols, structs):
    """Build the set of acceptable [[link]] targets.

    Includes:
      - All symbol names and BCS-Y ids from symbols.json
      - All struct names and BCS-S ids from structs.json
      - All tracked docs/*.md and local maintainer-doc basenames (without .md)
        for doc cross-refs
      - All snapshot-manifest basenames (without .json)

    BCS-Y / BCS-S ids are first-class link targets ([[BCS-Y-0309]] is the
    canonical way notes cross-reference a catalog entry). Omitting them made
    A5 flag every id-link as broken, drowning the genuine stale-name breaks.
    """
    valid = set()
    for s in symbols.get("symbols", []):
        name = s.get("name")
        if name:
            valid.add(name)
        sid = s.get("id")
        if sid:
            valid.add(sid)
    for st in structs.get("structs", []):
        name = st.get("name")
        if name:
            valid.add(name)
        sid = st.get("id")
        if sid:
            valid.add(sid)
    for p in _consumer_docs():
        valid.add(p.stem)
    for p in MANIFESTS_DIR.glob("*.json"):
        valid.add(p.stem)
    return valid


EXTRACTORS_REL_PREFIX = "tools/extractors/"


def _consumer_docs():
    """Yield tracked-tier docs while excluding the ignored maintainer island."""
    for path in sorted(DOCS_DIR.rglob("*.md")):
        if LOCAL_DOCS_DIR in path.parents:
            continue
        yield path


def _classify_link(target: str, valid: set[str], source: str = ""):
    """Return ('pass'|'skip'|'fail', category_or_None).

    Skip categories:
      meta_placeholder target is the literal '...' placeholder
      python_interp target contains a Python f-string {var} or %s
      historical_extractor source is tools/extractors/*.py (write-once
                            scripts; their JSON outputs are committed and
                            edits to the script text have no effect)
    """
    if target in valid:
        return ("pass", None)
    if target == "...":
        return ("skip", "meta_placeholder")
    if PY_INTERP_RE.search(target):
        return ("skip", "python_interp")
    if source.startswith(EXTRACTORS_REL_PREFIX):
        return ("skip", "historical_extractor")
    return ("fail", None)


def _suggest(target: str, valid: set[str], limit: int = 3) -> list[str]:
    """Cheap substring-based suggestion: look for valid names that share the
    final FUN_xxx token, or otherwise share a long substring with the target."""
    suggestions = []
    fun_match = re.search(r"FUN_[0-9A-Fa-f]+", target)
    if fun_match:
        token = fun_match.group(0).lower()
        for v in valid:
            if token in v.lower() and v != target:
                suggestions.append(v)
                if len(suggestions) >= limit:
                    return suggestions
    # fallback: last underscore-delimited token of length >= 6
    parts = [p for p in re.split(r"[_:\s]+", target) if len(p) >= 6]
    if parts:
        tail = parts[-1].lower()
        for v in valid:
            if tail in v.lower() and v != target and v not in suggestions:
                suggestions.append(v)
                if len(suggestions) >= limit:
                    break
    return suggestions


def scan_a4_wikilinks(symbols, structs):
    """Walk docs, manifests (notes + recursive snapshot manifests), and extractor
    scripts; classify every [[name]] occurrence against the valid-target set.
    """
    valid = _build_valid_targets(symbols, structs)

    occurrences = []  # (source_path_relative, line_or_None, target)

    # 1) tracked-tier docs - line-numbered scan
    for md in _consumer_docs():
        try:
            text = md.read_text(encoding="utf-8")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for m in WIKILINK_RE.finditer(line):
                occurrences.append((md.relative_to(REPO).as_posix(),
                                    lineno, m.group(1)))

    # 2) symbols.json notes
    for s in symbols.get("symbols", []):
        notes = s.get("notes", "") or ""
        for m in WIKILINK_RE.finditer(notes):
            occurrences.append((f"manifests/symbols.json#{s['id']}",
                                None, m.group(1)))

    # 3) structs.json notes (struct-level + per-field)
    for st in structs.get("structs", []):
        notes = st.get("notes", "") or ""
        for m in WIKILINK_RE.finditer(notes):
            occurrences.append((f"manifests/structs.json#{st['id']}",
                                None, m.group(1)))
        for fld in st.get("fields", []) or []:
            fnotes = (fld.get("notes") or "") if isinstance(fld, dict) else ""
            for m in WIKILINK_RE.finditer(fnotes):
                occurrences.append(
                    (f"manifests/structs.json#{st['id']}.{fld.get('name','?')}",
                     None, m.group(1)))

    # 4) snapshot manifests - recursive over all string values
    for mf in _snapshots():
        try:
            with mf.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        rel = mf.relative_to(REPO).as_posix()
        for s in _walk_json_strings(data):
            for m in WIKILINK_RE.finditer(s):
                occurrences.append((rel, None, m.group(1)))

    # 5) tools/extractors/*.py - line-numbered scan
    if EXTRACTORS_DIR.exists():
        for py in sorted(EXTRACTORS_DIR.glob("*.py")):
            try:
                text = py.read_text(encoding="utf-8")
            except OSError:
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                for m in WIKILINK_RE.finditer(line):
                    occurrences.append((py.relative_to(REPO).as_posix(),
                                        lineno, m.group(1)))

    results = {
        "valid_target_count": len(valid),
        "total_occurrences": len(occurrences),
        "pass": 0,
        "skip_by_category": defaultdict(int),
        "fail": [],
    }

    for source, lineno, target in occurrences:
        verdict, category = _classify_link(target, valid, source)
        if verdict == "pass":
            results["pass"] += 1
        elif verdict == "skip":
            results["skip_by_category"][category] += 1
        else:
            results["fail"].append({
                "source": source,
                "line": lineno,
                "target": target,
                "suggestions": _suggest(target, valid),
            })

    # convert defaultdict for stable printing
    results["skip_by_category"] = dict(results["skip_by_category"])
    return results


def _walk_json_objects(node):
    """Yield every dict node reachable from a JSON-decoded structure."""
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk_json_objects(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk_json_objects(v)


def scan_a5_embedded_addresses(symbols):
    """Check embedded {bcsId, address} pairs in the derived snapshot
    manifests against the canonical address in symbols.json.

    The bridge/index manifests denormalize each BCS-Y entry's address next
    to its id at generation time. The catalog identity scans verify the id
    join key; the embedded address is a convenience copy that
    goes stale when symbols.json is rebased (e.g. an image-base
    shift) but the derived manifest is not regenerated. The fix is to
    regenerate the manifest, never to hand-edit an address (they
    are hand-derived, and the id remains authoritative).
    """
    canonical = {}
    for s in symbols["symbols"]:
        addr = s.get("address")
        if isinstance(addr, str):
            canonical[s["id"]] = addr.lower()

    results = {"manifests_scanned": 0, "pairs_checked": 0, "drift": []}
    for mf in sorted(MANIFESTS_DIR.glob("*.json")):
        if mf.name not in NAMED_CATALOGS or mf.name in ("symbols.json", "structs.json"):
            continue
        try:
            with mf.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        results["manifests_scanned"] += 1
        for obj in _walk_json_objects(data):
            bid = obj.get("bcsId")
            addr = obj.get("address")
            if not isinstance(bid, str) or not isinstance(addr, str):
                continue
            canon = canonical.get(bid)
            if canon is None:
                continue  # unresolved ids are handled by the identity scans
            # Composite / placeholder canonical forms have no single VA to match.
            if ";" in canon or ".." in canon or canon in ("0x00000000", "0x0", ""):
                continue
            results["pairs_checked"] += 1
            if addr.lower() != canon:
                results["drift"].append({
                    "manifest": mf.name,
                    "bcsId": bid,
                    "embedded": addr,
                    "canonical": canon,
                })
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run repository-local catalog hygiene scans.")
    parser.add_argument(
        "--phase-ledger", type=pathlib.Path,
        dest="phase_ledger",
        help=("Optional maintainer investigation ledger used only for the advisory "
              "A3 orphaned-manifest scan."),
    )
    args = parser.parse_args(argv)
    ledger_path = args.phase_ledger
    if ledger_path is not None:
        if not ledger_path.is_absolute():
            ledger_path = REPO / ledger_path
        if not ledger_path.is_file():
            parser.error(f"ledger does not exist: {ledger_path}")

    symbols = load_symbols()
    matrix = load_matrix()

    print("=" * 72)
    print(f"HYGIENE SCAN REPORT (symbols.json: {symbols['symbolCount']} entries)")
    print("=" * 72)

    print("\n--- A1: matrix vs symbols.json reconciliation ---\n")
    a1 = scan_a1_matrix_vs_symbols(symbols, matrix)

    print(f"matrix-gap rows with symbol references (advisory - not gated): {len(a1['matrix_gaps_with_symbol_refs'])}")
    for row in a1["matrix_gaps_with_symbol_refs"]:
        print(f"  {row['direction']} {row['opcode']} (pcap={row['pcapCount']}): {row['ref_count']} refs")
        for rid in row["symbol_refs"][:5]:
            print(f"    -> {rid}")

    print(f"\nmatrix-listed BCS-Y IDs missing from symbols.json: {len(a1['matrix_listed_ids_missing'])}")
    for row in a1["matrix_listed_ids_missing"]:
        print(f"  {row['direction']} {row['opcode']}: missing {row['missing_id']}")

    print(f"\nrows with empty bcsYIds but non-gap status (low priority - may be by design): {len(a1['matrix_empty_bcs_ids_with_symbol_refs'])}")
    # noisy - only show count

    print("\n--- A2: duplicate addresses in symbols.json ---\n")
    dupes = scan_a2_duplicate_addresses(symbols)
    print(f"distinct addresses with multiple BCS-Y entries: {len(dupes)}")
    for addr, entries in sorted(dupes.items()):
        print(f"  {addr}:")
        for eid, name, kind in entries:
            print(f"    {eid} [{kind}] {name}")

    print("\n--- A3: orphaned manifests (no ledger entry) ---\n")
    if ledger_path is None:
        print("not run: pass --phase-ledger PATH to check the maintainer ledger")
    else:
        orphans, total_files = scan_a3_orphaned_manifests(ledger_path)
        print(f"manifest files total: {total_files}")
        print(f"orphaned manifests (no ledger entry): {len(orphans)}")
        for o in orphans:
            for f in o["files"]:
                print(f"  {f}")

    print("\n--- A4: sourceRef path inventory ---\n")
    structs = load_structs()
    a3 = scan_a3_sourcerefs(symbols, structs)
    print("category counts:")
    for cat, count in sorted(a3["categories"].items()):
        print(f"  {cat}: {count}")
    print(f"\nabsolute-path examples ({len(a3['absolute_examples'])} total shown up to 20):")
    for ex in a3["absolute_examples"]:
        print(f"  {ex['id']}: {ex['ref']}")
    print(f"\nrepo-relative-backslash examples ({len(a3['backslash_examples'])} total shown up to 10):")
    for ex in a3["backslash_examples"]:
        print(f"  {ex['id']}: {ex['ref']}")
    print(f"\ncitation examples ({a3['categories'].get('citation', 0)} total shown up to 10):")
    for ex in a3["citation_examples"]:
        print(f"  {ex['id']}: {ex['ref']}")
    print(f"\nlive parent-dir paths (defect - gated): {len(a3['live_parent_paths'])}")
    for ex in a3["live_parent_paths"]:
        print(f"  {ex['id']}: {ex['ref']}")
    print(f"\nin-repo relative refs MISSING on disk (reported - not gated, "
          f"see exit-code note): {len(a3['missing_repo_relative'])}")
    for ex in a3["missing_repo_relative"][:10]:
        print(f"  {ex['id']}: {ex['ref']}")

    print("\n--- A4: wiki-link [[name]] integrity sweep ---\n")
    a4 = scan_a4_wikilinks(symbols, structs)
    print(f"valid target set size: {a4['valid_target_count']}")
    print(f"total [[link]] occurrences: {a4['total_occurrences']}")
    print(f"  pass: {a4['pass']}")
    skip_total = sum(a4["skip_by_category"].values())
    print(f"  skip (false positives): {skip_total}")
    for cat, count in sorted(a4["skip_by_category"].items()):
        print(f"    {cat}: {count}")
    print(f"  fail (real broken links): {len(a4['fail'])}")
    for f in a4["fail"]:
        loc = f["source"] + (f":{f['line']}" if f["line"] else "")
        print(f"    {loc}  ->  [[{f['target']}]]")
        if f["suggestions"]:
            for sug in f["suggestions"]:
                print(f"      suggest: {sug}")

    print("\n--- A5: embedded manifest address vs symbols.json canonical ---\n")
    a5 = scan_a5_embedded_addresses(symbols)
    print(f"derived manifests scanned: {a5['manifests_scanned']}")
    print(f"embedded bcsId+address pairs checked: {a5['pairs_checked']}")
    print(f"pairs whose address drifts from symbols.json: {len(a5['drift'])} "
          f"(gated - regenerate the manifest; do not hand-edit addresses)")
    by_manifest = defaultdict(lambda: defaultdict(int))
    for d in a5["drift"]:
        try:
            delta = int(d["embedded"], 16) - int(d["canonical"], 16)
        except ValueError:
            delta = None
        by_manifest[d["manifest"]][delta] += 1
    for manifest in sorted(by_manifest):
        deltas = by_manifest[manifest]
        total = sum(deltas.values())
        parts = ", ".join(
            f"{cnt}x {('%+#x' % dl) if dl is not None else 'non-scalar'}"
            for dl, cnt in sorted(deltas.items(),
                                  key=lambda kv: (-kv[1], kv[0] or 0)))
        print(f"  {manifest}: {total} drifted ({parts})")

    # Gate broken IDs, live parent paths, broken wiki-links, and stale
    # denormalized addresses in generated catalogs.
    # Missing repo-relative refs include local Ghidra state and remain advisory.
    defects = (
        len(a1["matrix_listed_ids_missing"])
        + len(a3["live_parent_paths"])
        + len(a4["fail"])
        + len(a5["drift"])
    )
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
