"""Gate for the client-structure IR and its curated overlay.

Two schemas under `schemas/` are loaded from disk and enforced here, so the
directory is a contract rather than documentation. On top of schema shape,
thirteen invariants encode the things a schema cannot say: that the IR did not
renumber a BCS identifier, did not move a confidence tier, did not lose a
source reference, did not quietly begin populating a dimension a later phase
owns, and that every relationship edge resolves in both directions.

CLI:
  python tools/validate_ir.py
Exit 0 when every invariant holds, 1 otherwise.

Pure stdlib. `jsonschema`, when installed, is consulted as a second opinion
on the in-repo schema interpreter and reported, never gated on.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _schema_check  # noqa: E402
import _symbols_io  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
IR_PATH = REPO / "manifests" / "ir_catalog.json"
OVERLAY_PATH = REPO / "manifests" / "ir_overlay.json"
STRUCTS_PATH = REPO / "manifests" / "structs.json"
IR_SCHEMA_PATH = REPO / "schemas" / "ir-v1.schema.json"
OVERLAY_SCHEMA_PATH = REPO / "schemas" / "ir-overlay-v1.schema.json"

# Cap each invariant's sample so systemic failures do not hide other results.
SAMPLE = 8


def _load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


class Report:
    def __init__(self) -> None:
        self.results: list[tuple[str, str, list[str]]] = []

    def record(self, name: str, failures: list[str]) -> None:
        self.results.append((name, "FAIL" if failures else "ok", failures))

    @property
    def failed(self) -> int:
        return sum(1 for _, status, _ in self.results if status == "FAIL")

    def render(self) -> None:
        print("=" * 72)
        print("IR VALIDATOR REPORT")
        print("=" * 72)
        for name, status, failures in self.results:
            marker = "FAIL" if status == "FAIL" else "  ok"
            suffix = f" ({len(failures)} findings)" if failures else ""
            print(f"[{marker}] {name}{suffix}")
            for line in failures[:SAMPLE]:
                print(f"         {line}")
            if len(failures) > SAMPLE:
                print(f"         ... {len(failures) - SAMPLE} more suppressed")
        print("-" * 72)
        print(f"{len(self.results)} invariants checked, {self.failed} failed")


def i1_ir_schema(ir, report: Report) -> None:
    schema = _schema_check.load_schema(IR_SCHEMA_PATH)
    report.record("I1  ir_catalog.json conforms to schemas/ir-v1.schema.json",
                  _schema_check.validate(ir, schema))
    note = _schema_check.crosscheck(ir, schema)
    if note:
        print(f"note: schema interpreter cross-check disagreement: {note}")


def i2_overlay_schema(overlay, report: Report) -> None:
    schema = _schema_check.load_schema(OVERLAY_SCHEMA_PATH)
    report.record(
        "I2  ir_overlay.json conforms to schemas/ir-overlay-v1.schema.json",
        _schema_check.validate(overlay, schema))


def i3_deferred_dimensions(ir, report: Report) -> None:
    """A deferred dimension must be empty everywhere, not merely labelled."""
    failures: list[str] = []
    dims = ir["dimensions"]

    if dims["bases"]["status"] == "deferred":
        for t in ir["types"]:
            if t["bases"] != {"status": "deferred", "owner": dims["bases"]["owner"]}:
                failures.append(f"{t['id']}: bases populated while the dimension "
                                "is deferred")
    if dims["vtables"]["status"] == "deferred":
        for t in ir["types"]:
            if t["vtable"] != {"status": "deferred",
                               "owner": dims["vtables"]["owner"]}:
                failures.append(f"{t['id']}: vtable populated while the dimension "
                                "is deferred")
    if dims["alignment"]["status"] == "declared-unknown":
        for t in ir["types"]:
            if t["alignment"]["kind"] != "unknown":
                failures.append(f"{t['id']}: alignment is "
                                f"{t['alignment']['kind']!r} while the dimension "
                                "is declared-unknown; move the dimension status "
                                "in the same change")
    if dims["payloadRelationships"]["status"] == "deferred":
        for key in ("relationships", "payloads", "opcodes"):
            if key in ir:
                failures.append(f"top-level {key!r} present while "
                                "payloadRelationships is deferred")
    report.record("I3  deferred and unknown dimensions carry no values", failures)


def i4_identifier_preservation(ir, symbols_doc, structs_doc,
                               report: Report) -> None:
    """BCS ids are the citation surface other repos promote against."""
    failures: list[str] = []
    for label, ir_key, source, source_key in (
            ("BCS-S", "types", structs_doc, "structs"),
            ("BCS-Y", "symbols", symbols_doc, "symbols")):
        ir_ids = [e["id"] for e in ir[ir_key]]
        source_ids = {e["id"] for e in source[source_key]}
        if len(ir_ids) != len(set(ir_ids)):
            failures.append(f"{label}: duplicate ids in the IR")
        missing = source_ids - set(ir_ids)
        added = set(ir_ids) - source_ids
        for i in sorted(missing):
            failures.append(f"{label}: {i} present in the catalog, dropped "
                            "from the IR")
        for i in sorted(added):
            failures.append(f"{label}: {i} present in the IR, absent from the "
                            "catalog")
    report.record("I4  every BCS identifier survives unrenumbered", failures)


def i5_confidence_preservation(ir, symbols_doc, structs_doc,
                               report: Report) -> None:
    """Evidence tiers and reverification state are copied unchanged."""
    failures: list[str] = []
    for ir_key, source, source_key in (("types", structs_doc, "structs"),
                                       ("symbols", symbols_doc, "symbols")):
        source_rows = {e["id"]: e for e in source[source_key]}
        for entry in ir[ir_key]:
            source_entry = source_rows.get(entry["id"])
            if source_entry is None:
                continue
            expected = source_entry["confidence"]
            if entry["confidence"] != expected:
                failures.append(f"{entry['id']}: confidence "
                                f"{entry['confidence']!r} != catalog "
                                f"{expected!r}")
            for key in ("needsReverify", "reverifyMethod"):
                if entry.get(key) != source_entry.get(key):
                    failures.append(
                        f"{entry['id']}: {key} {entry.get(key)!r} != catalog "
                        f"{source_entry.get(key)!r}"
                    )
    report.record("I5  confidence and reverify state are copied unchanged",
                  failures)


def i7_citation_round_trip(ir, symbols_doc, structs_doc, report: Report) -> None:
    """Every sourceRef must still be reachable, unresolved ones included."""
    failures: list[str] = []
    by_id = {c["id"]: c for c in ir["citations"]}
    if len(by_id) != len(ir["citations"]):
        failures.append("duplicate citation ids")

    source_pairs: set[tuple[str, str]] = set()
    for doc, key in ((structs_doc, "structs"), (symbols_doc, "symbols")):
        for entry in doc[key]:
            for ref in entry.get("sourceRefs", []):
                if ref:
                    source_pairs.add((entry["id"], ref))

    ir_pairs: set[tuple[str, str]] = set()
    for ir_key in ("types", "symbols"):
        for entry in ir[ir_key]:
            for cid in entry["citations"]:
                citation = by_id.get(cid)
                if citation is None:
                    failures.append(f"{entry['id']}: cites unknown {cid}")
                    continue
                ir_pairs.add((entry["id"], citation["raw"]))

    for owner, ref in sorted(source_pairs - ir_pairs)[:SAMPLE * 4]:
        failures.append(f"{owner}: sourceRef {ref!r} lost in normalization")
    for owner, ref in sorted(ir_pairs - source_pairs)[:SAMPLE * 4]:
        failures.append(f"{owner}: IR invents sourceRef {ref!r}")

    for citation in ir["citations"]:
        owners = {owner for owner, ref in source_pairs if ref == citation["raw"]}
        if set(citation["referencedBy"]) != owners:
            failures.append(f"{citation['id']}: referencedBy disagrees with the "
                            "catalogs")
    report.record("I7  every sourceRef round-trips through a citation record",
                  failures)


def i8_raw_fidelity(ir, symbols_doc, structs_doc, report: Report) -> None:
    """Parsed values sit beside the original string, never in place of it."""
    failures: list[str] = []
    structs_by_id = {s["id"]: s for s in structs_doc["structs"]}
    for t in ir["types"]:
        source = structs_by_id.get(t["id"])
        if source is None:
            continue
        if t["size"]["raw"] != source["size"]:
            failures.append(f"{t['id']}: size raw {t['size']['raw']!r} != "
                            f"catalog {source['size']!r}")
        if t["namespace"]["raw"] != source["namespace"]:
            failures.append(f"{t['id']}: namespace raw differs from the catalog")
        by_name: dict[str, list[dict]] = {}
        for field in source["fields"]:
            by_name.setdefault(field["name"], []).append(field)
        for member in t["members"]:
            if member["kind"] != "field":
                continue
            candidates = by_name.get(member["name"], [])
            if not any(c["offset"] == member["offset"]["raw"]
                       and c["size"] == member["size"]["raw"]
                       and c["type"] == member["type"] for c in candidates):
                failures.append(f"{t['id']}.{member['name']}: no catalog field "
                                "with this offset, size and type")

    symbols_by_id = {s["id"]: s for s in symbols_doc["symbols"]}
    for sym in ir["symbols"]:
        source = symbols_by_id.get(sym["id"])
        if source is None:
            continue
        if sym["address"]["raw"] != source["address"]:
            failures.append(f"{sym['id']}: address raw "
                            f"{sym['address']['raw']!r} != catalog "
                            f"{source['address']!r}")
        if sym["name"] != source["name"] or sym["kind"] != source["kind"]:
            failures.append(f"{sym['id']}: name or kind differs from the catalog")
    report.record("I8  every parsed value preserves its raw catalog string",
                  failures)


def i9_layout_arithmetic(ir, report: Report) -> None:
    failures: list[str] = []
    span_total = 0
    for t in ir["types"]:
        layout = t["layout"]
        spans = [m for m in t["members"] if m["kind"] == "unknown-span"]
        span_total += len(spans)
        span_bytes = sum(m["size"]["bytes"] for m in spans)
        if span_bytes != layout["unknownBytes"]:
            failures.append(f"{t['id']}: unknown spans total {span_bytes} but "
                            f"layout says {layout['unknownBytes']}")
        if layout["status"] == "modeled":
            declared = layout["declaredBytes"]
            if layout["coveredBytes"] + layout["unknownBytes"] != declared:
                failures.append(f"{t['id']}: covered {layout['coveredBytes']} + "
                                f"unknown {layout['unknownBytes']} != declared "
                                f"{declared}")
        if layout["status"] == "unmodeled" and spans:
            failures.append(f"{t['id']}: unmodeled layout with derived spans")
        starts = [m["offset"]["bytes"] for m in t["members"]
                  if m["kind"] == "field" and m["offset"]["kind"] == "exact"]
        for span in spans:
            begin = span["offset"]["bytes"]
            end = begin + span["size"]["bytes"]
            for start in starts:
                if begin <= start < end:
                    failures.append(
                        f"{t['id']}: unknown span 0x{begin:X}..0x{end:X} covers a "
                        f"field declared at 0x{start:X}")
    if span_total != ir["counts"]["unknownSpans"]:
        failures.append(f"counts.unknownSpans {ir['counts']['unknownSpans']} != "
                        f"{span_total} spans present")
    report.record("I9  layout arithmetic closes and no span covers a field",
                  failures)


def i10_overlay_reach(ir, overlay, report: Report) -> None:
    """Overlay entries must land, and non-overlay values must not claim to."""
    failures: list[str] = []
    alignment_overlay = overlay["alignment"]
    span_overlay = overlay["unknownSpanAnnotations"]
    seen_spans: set[str] = set()

    for t in ir["types"]:
        has_entry = t["id"] in alignment_overlay
        claims_overlay = t["alignment"].get("source") == "overlay"
        if has_entry != claims_overlay:
            failures.append(f"{t['id']}: alignment overlay entry "
                            f"{'present' if has_entry else 'absent'} but the IR "
                            f"{'claims' if claims_overlay else 'does not claim'} "
                            "an overlay source")
        if has_entry and t["alignment"].get("bytes") != alignment_overlay[
                t["id"]]["bytes"]:
            failures.append(f"{t['id']}: alignment bytes differ from the overlay")
        for member in t["members"]:
            if member["kind"] != "unknown-span":
                continue
            key = f"{t['id']}@{member['offset']['raw']}"
            has_span = key in span_overlay
            if has_span:
                seen_spans.add(key)
            claims = member["annotation"].get("source") == "overlay"
            if has_span != claims:
                failures.append(f"{key}: span annotation and overlay disagree")
            if not has_span and member["annotation"]["kind"] != "unmapped":
                failures.append(f"{key}: annotated {member['annotation']['kind']!r} "
                                "with no overlay entry behind it")
    for key in sorted(set(span_overlay) - seen_spans):
        failures.append(f"{key}: overlay annotates a span the build does not derive")
    for tid in sorted(set(alignment_overlay) - {t["id"] for t in ir["types"]}):
        failures.append(f"{tid}: overlay aligns a type the IR does not hold")
    report.record("I10 every overlay entry reaches exactly one IR value",
                  failures)


def i11_relationship_symbols(ir, symbols_doc, report: Report) -> None:
    """Relationship edges may only cite symbols the catalog holds."""
    failures: list[str] = []
    known = {s["id"] for s in symbols_doc["symbols"]}
    rel = ir["relationships"]
    for opcode in rel["opcodes"]:
        for bcs_id in opcode["symbols"]:
            if bcs_id not in known:
                failures.append(f"{opcode['id']}: cites unknown {bcs_id}")
    for opcode in rel["opcodes"]:
        for binding in opcode.get("c2sBindings", []):
            for bcs_id in binding.get("symbols", []):
                if bcs_id not in known:
                    failures.append(f"{opcode['id']}: c2s binding "
                                    f"{binding['luaApi']} cites unknown "
                                    f"{bcs_id}")
                elif bcs_id not in opcode["symbols"]:
                    failures.append(f"{opcode['id']}: c2s binding "
                                    f"{binding['luaApi']} cites {bcs_id}, "
                                    "which the opcode does not carry")
    for receiver in rel["receivers"]:
        for role, ids in receiver["symbolsByRole"].items():
            for bcs_id in ids:
                if bcs_id not in known:
                    failures.append(f"receiver {receiver['name']}: {role} cites "
                                    f"unknown {bcs_id}")
    for operation in rel["operations"]:
        for bcs_id in operation["symbols"]:
            if bcs_id not in known:
                failures.append(f"operation {operation['retailClass']}: cites "
                                f"unknown {bcs_id}")
    for binding in rel["luaBindings"]:
        for bcs_id in binding["symbols"]:
            if bcs_id not in known:
                failures.append(f"lua {binding['luaName']}: cites unknown "
                                f"{bcs_id}")
    report.record("I11 every relationship edge cites a known symbol", failures)


def i12_relationship_closure(ir, report: Report) -> None:
    """Opcode references resolve, and edges agree in both directions."""
    failures: list[str] = []
    rel = ir["relationships"]
    by_id = {o["id"]: o for o in rel["opcodes"]}
    if len(by_id) != len(rel["opcodes"]):
        failures.append("duplicate opcode ids")

    for kind, records, name_key, back in (
            ("receiver", rel["receivers"], "name", "receivers"),
            ("operation", rel["operations"], "retailClass", "operations"),
            ("lua", rel["luaBindings"], "luaName", "luaBindings")):
        for record in records:
            for ref in record["opcodes"]:
                oid = ref["id"] if isinstance(ref, dict) else ref
                opcode = by_id.get(oid)
                if opcode is None:
                    failures.append(f"{kind} {record[name_key]}: names {oid}, "
                                    "which the opcode set does not hold")
                    continue
                if record[name_key] not in opcode[back]:
                    failures.append(f"{kind} {record[name_key]}: claims {oid} "
                                    "but the opcode does not name it back")

    # Check the reverse direction so every named edge has an owning record.
    known_names = {
        "receivers": {r["name"] for r in rel["receivers"]},
        "operations": {o["retailClass"] for o in rel["operations"]},
        "luaBindings": {b["luaName"] for b in rel["luaBindings"]},
    }
    for opcode in rel["opcodes"]:
        for key, names in known_names.items():
            for name in opcode[key]:
                if name not in names:
                    failures.append(f"{opcode['id']}: names {key[:-1]} "
                                    f"{name!r}, which that set does not hold")
                    continue
                records = {"receivers": rel["receivers"],
                           "operations": rel["operations"],
                           "luaBindings": rel["luaBindings"]}[key]
                name_key = {"receivers": "name", "operations": "retailClass",
                            "luaBindings": "luaName"}[key]
                owners = [r for r in records if r[name_key] == name]
                if not any(opcode["id"] == (ref["id"] if isinstance(ref, dict)
                                            else ref)
                           for r in owners for ref in r["opcodes"]):
                    failures.append(f"{opcode['id']}: names {name!r} but no "
                                    f"{key[:-1]} record claims it back")
    report.record("I12 every relationship reference resolves both ways",
                  failures)


def i13_opcode_identity(ir, report: Report) -> None:
    failures: list[str] = []
    summary = ir["relationships"]["summary"]
    counted = {"s2c": 0, "c2s": 0}
    for opcode in ir["relationships"]["opcodes"]:
        if opcode["id"] != f"{opcode['direction']}:{opcode['hex']}":
            failures.append(f"{opcode['id']}: id disagrees with direction and "
                            "hex")
        if opcode["int"] != int(opcode["hex"], 16):
            failures.append(f"{opcode['id']}: int {opcode['int']} != "
                            f"int({opcode['hex']!r}, 16)")
        counted[opcode["direction"]] += 1
        if not opcode["sources"]:
            failures.append(f"{opcode['id']}: no source named it")
    for direction, count in counted.items():
        if summary[direction] != count:
            failures.append(f"summary.{direction} {summary[direction]} != "
                            f"{count} present")
    if summary["opcodes"] != len(ir["relationships"]["opcodes"]):
        failures.append("summary.opcodes disagrees with the opcode list")
    if ir["counts"]["opcodes"] != summary["opcodes"]:
        failures.append("counts.opcodes disagrees with the relationship summary")
    report.record("I13 opcode identity and the summary agree with the rows",
                  failures)


def i14_payload_type_bindings_deferred(ir, report: Report) -> None:
    """Type-to-opcode bindings stay absent until that dimension is owned."""
    failures: list[str] = []
    if ir["dimensions"]["payloadTypeBindings"]["status"] == "deferred":
        for t in ir["types"]:
            if "opcodes" in t or "relationships" in t:
                failures.append(f"{t['id']}: carries an opcode binding while "
                                "payloadTypeBindings is deferred")
    report.record("I14 payload type bindings stay deferred", failures)


def main() -> int:
    ir = _load(IR_PATH)
    overlay = _load(OVERLAY_PATH)
    structs_doc = _load(STRUCTS_PATH)
    symbols_doc = _symbols_io.load_symbols()

    report = Report()
    i1_ir_schema(ir, report)
    i2_overlay_schema(overlay, report)
    i3_deferred_dimensions(ir, report)
    i4_identifier_preservation(ir, symbols_doc, structs_doc, report)
    i5_confidence_preservation(ir, symbols_doc, structs_doc, report)
    i7_citation_round_trip(ir, symbols_doc, structs_doc, report)
    i8_raw_fidelity(ir, symbols_doc, structs_doc, report)
    i9_layout_arithmetic(ir, report)
    i10_overlay_reach(ir, overlay, report)
    i11_relationship_symbols(ir, symbols_doc, report)
    i12_relationship_closure(ir, report)
    i13_opcode_identity(ir, report)
    i14_payload_type_bindings_deferred(ir, report)
    report.render()
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
