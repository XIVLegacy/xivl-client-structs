"""Bite proofs for the IR builder's refusals and the IR validator's invariants.

A green gate proves nothing unless it would go red on the defect it claims to
guard. Every case here plants exactly one defect into a copy of the real
inputs and asserts the named gate fires.

Two limits worth knowing rather than discovering. The cross-talk check
(`expect_others_quiet`, "only this gate fired") runs over five of the thirteen
invariants, the ones taking documents this harness can hand them. And the
determinism cases compare two builds inside one process, so they catch
ordering and iteration bugs but not cross-machine ones -- line endings,
locale, and untracked working-tree state are handled at the source instead:
`.gitattributes` pins the inputs to LF and `build_ir.tracked_paths()` decides
citation resolution from tracked content rather than from disk.

CLI:
  python tools/test_ir_gates.py
Exit 0 when every gate bit, 1 otherwise.

Pure stdlib.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _symbols_io  # noqa: E402
import build_ir  # noqa: E402
import validate_ir  # noqa: E402

REPO = Path(__file__).resolve().parents[1]

PASSED: list[str] = []
FAILED: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSED.append(name)
    else:
        FAILED.append(f"{name}{': ' + detail if detail else ''}")


def expect_build_error(name: str, fn, needle: str) -> None:
    try:
        fn()
    except build_ir.BuildError as e:
        check(name, needle in str(e), f"message {str(e)!r} lacks {needle!r}")
        return
    check(name, False, "build accepted the planted defect")


def expect_invariant_fails(name: str, invariant, ir, *rest) -> None:
    """Run one invariant over a mutated document and require it to fail."""
    report = validate_ir.Report()
    invariant(ir, *rest, report)
    check(name, report.failed == 1, "invariant stayed green")


def expect_others_quiet(name: str, ir, symbols_doc, structs_doc, overlay,
                        expected_failure: str) -> None:
    """Only the named invariant may fail on a single planted defect."""
    report = validate_ir.Report()
    validate_ir.i3_deferred_dimensions(ir, report)
    validate_ir.i4_identifier_preservation(ir, symbols_doc, structs_doc, report)
    validate_ir.i5_confidence_preservation(ir, symbols_doc, structs_doc, report)
    validate_ir.i9_layout_arithmetic(ir, report)
    validate_ir.i10_overlay_reach(ir, overlay, report)
    failing = [n for n, status, _ in report.results if status == "FAIL"]
    check(name, failing == [expected_failure], f"failing set was {failing}")


def main() -> int:
    symbols_doc = _symbols_io.load_symbols()
    structs_doc = json.loads(
        (REPO / "manifests" / "structs.json").read_text(encoding="utf-8"))
    overlay = json.loads(
        (REPO / "manifests" / "ir_overlay.json").read_text(encoding="utf-8"))
    baseline = build_ir.build(symbols_doc, structs_doc, overlay)

    expect_build_error(
        "B1 an unrecognised size raises instead of degrading to 'unknown'",
        lambda: build_ir.parse_size("about half a cache line", "planted"),
        "unrecognised size")
    expect_build_error(
        "B2 an unrecognised offset raises",
        lambda: build_ir.parse_offset("somewhere after the name", "planted"),
        "unrecognised offset")
    expect_build_error(
        "B3 an unrecognised address raises",
        lambda: build_ir.parse_address("0x1234", "planted"),
        "unrecognised address")
    expect_build_error(
        "B3b a field extending beyond its declared type is refused",
        lambda: build_ir.derive_layout(
            [(build_ir.parse_offset("0x03", "planted"),
              build_ir.parse_size("0x04", "planted"))],
            build_ir.parse_size("0x04", "planted type")),
        "exceeds declared type size")
    expect_build_error(
        "B4 a live sibling-checkout path is refused as a citation",
        lambda: build_ir.build_citations(
            [("BCS-Y-0001", ["../xivl-opcodes/opcodes.json"])]),
        "live_parent_path")
    expect_build_error(
        "B4b an absolute path is refused as a citation",
        lambda: build_ir.build_citations(
            [("BCS-Y-0001", [r"C:" + r"\example\notes.md"])]),
        "absolute path")
    expect_build_error(
        "B4c an overlay reference gets the same refusal as a catalog one",
        lambda: build_ir.refuse_unsafe_ref("../xivl-captures/docs/README.md",
                                           "overlay sourceRef"),
        "live_parent_path")
    check("B4d citation resolution reads tracked content, not the working tree",
          not build_ir._is_tracked("tools/ghidra/logs/c134_seam_self_addactor.txt")
          and build_ir._is_tracked("manifests/structs.json"))

    planted_overlay = copy.deepcopy(overlay)
    planted_overlay["alignment"]["BCS-S-9999"] = {
        "bytes": 4, "reason": "planted", "sourceRefs": ["planted"]}
    expect_build_error(
        "B6 an overlay alignment for an unknown type is refused",
        lambda: build_ir.build(symbols_doc, structs_doc, planted_overlay),
        "unknown types")

    planted_overlay = copy.deepcopy(overlay)
    planted_overlay["unknownSpanAnnotations"]["BCS-S-0001@0xFF"] = {
        "kind": "padding", "note": "planted", "sourceRefs": ["planted"]}
    expect_build_error(
        "B7 an overlay annotation for a span the build never derives is refused",
        lambda: build_ir.build(symbols_doc, structs_doc, planted_overlay),
        "does not derive")

    ir = copy.deepcopy(baseline)
    ir["types"][0]["size"]["kind"] = "enormous"
    expect_invariant_fails("I1 schema rejects a value outside an enum",
                           validate_ir.i1_ir_schema, ir)

    bad_overlay = copy.deepcopy(overlay)
    bad_overlay["alignment"]["BCS-S-0001"] = {"bytes": 0, "reason": "planted",
                                              "sourceRefs": []}
    expect_invariant_fails("I2 overlay schema rejects a zero alignment",
                           validate_ir.i2_overlay_schema, bad_overlay)

    ir = copy.deepcopy(baseline)
    ir["types"][0]["alignment"] = {"kind": "exact", "bytes": 4,
                                   "reason": "planted"}
    expect_invariant_fails(
        "I3 a value appearing in a declared-unknown dimension is caught",
        validate_ir.i3_deferred_dimensions, ir)
    expect_others_quiet("I3 plants nothing else", ir, symbols_doc, structs_doc,
                        overlay,
                        "I3  deferred and unknown dimensions carry no values")

    ir = copy.deepcopy(baseline)
    ir["types"][0]["bases"] = {"status": "deferred", "owner": "C1b"}
    expect_invariant_fails(
        "I3 a base list assigned to the wrong owning phase is caught",
        validate_ir.i3_deferred_dimensions, ir)

    ir = copy.deepcopy(baseline)
    ir["payloads"] = []
    ir["dimensions"]["payloadRelationships"]["status"] = "deferred"
    expect_invariant_fails(
        "I3 a payload layer appearing while its dimension is deferred is caught",
        validate_ir.i3_deferred_dimensions, ir)

    ir = copy.deepcopy(baseline)
    ir["symbols"][5]["id"] = "BCS-Y-9999"
    expect_invariant_fails("I4 a renumbered BCS-Y identifier is caught",
                           validate_ir.i4_identifier_preservation, ir,
                           symbols_doc, structs_doc)

    ir = copy.deepcopy(baseline)
    promoted = next(s for s in ir["symbols"] if s["confidence"] == "probable")
    promoted["confidence"] = "confirmed"
    expect_invariant_fails("I5 a promoted confidence tier is caught",
                           validate_ir.i5_confidence_preservation, ir,
                           symbols_doc, structs_doc)

    ir = copy.deepcopy(baseline)
    reverify = next(s for s in ir["symbols"] if s.get("needsReverify"))
    del reverify["reverifyMethod"]
    expect_invariant_fails("I1 schema catches a dropped reverify method",
                           validate_ir.i1_ir_schema, ir)
    expect_invariant_fails("I5 a dropped reverify method is caught",
                           validate_ir.i5_confidence_preservation, ir,
                           symbols_doc, structs_doc)

    ir = copy.deepcopy(baseline)
    ir["types"][0]["citations"] = ir["types"][0]["citations"][1:]
    expect_invariant_fails("I7 a dropped source reference is caught",
                           validate_ir.i7_citation_round_trip, ir, symbols_doc,
                           structs_doc)

    ir = copy.deepcopy(baseline)
    ir["symbols"][0]["address"]["raw"] = "0xDEADBEEF"
    expect_invariant_fails("I8 a rewritten raw address is caught",
                           validate_ir.i8_raw_fidelity, ir, symbols_doc,
                           structs_doc)

    ir = copy.deepcopy(baseline)
    field = next(m for t in ir["types"] for m in t["members"]
                 if m["kind"] == "field")
    field["type"] = "uint64_t"
    expect_invariant_fails("I8 a rewritten field type is caught",
                           validate_ir.i8_raw_fidelity, ir, symbols_doc,
                           structs_doc)

    ir = copy.deepcopy(baseline)
    victim = next(t for t in ir["types"]
                  if any(m["kind"] == "unknown-span" for m in t["members"]))
    victim["members"] = [m for m in victim["members"]
                         if m["kind"] != "unknown-span"]
    expect_invariant_fails("I9 a deleted unknown span breaks the byte arithmetic",
                           validate_ir.i9_layout_arithmetic, ir)

    ir = copy.deepcopy(baseline)
    victim = next(t for t in ir["types"]
                  if any(m["kind"] == "unknown-span" for m in t["members"]))
    span = next(m for m in victim["members"] if m["kind"] == "unknown-span")
    span["size"]["bytes"] += 0x100
    victim["layout"]["unknownBytes"] += 0x100
    expect_invariant_fails(
        "I9 a span stretched over a declared field is caught",
        validate_ir.i9_layout_arithmetic, ir)

    ir = copy.deepcopy(baseline)
    span = next(m for t in ir["types"] for m in t["members"]
                if m["kind"] == "unknown-span")
    span["annotation"] = {"kind": "padding", "note": "planted"}
    expect_invariant_fails(
        "I10 a span annotated with no overlay entry behind it is caught",
        validate_ir.i10_overlay_reach, ir, overlay)

    # Exercise overlay reachability with a populated overlay as well as the empty committed overlay.
    span = next(m for t in baseline["types"] for m in t["members"]
                if m["kind"] == "unknown-span")
    span_owner = next(t["id"] for t in baseline["types"]
                      if any(m is span for m in t["members"]))
    live_overlay = {
        "overlayVersion": "1.0", "gameVersion": "1.23b",
        "schema": "schemas/ir-overlay-v1.schema.json",
        "alignment": {baseline["types"][0]["id"]: {
            "bytes": 4, "reason": "planted", "sourceRefs": ["planted"]}},
        "unknownSpanAnnotations": {
            f"{span_owner}@{span['offset']['raw']}": {
                "kind": "padding", "note": "planted",
                "sourceRefs": ["planted"]}},
    }
    populated = build_ir.build(symbols_doc, structs_doc, live_overlay)
    report = validate_ir.Report()
    validate_ir.i10_overlay_reach(populated, live_overlay, report)
    check("I10 a populated overlay reaches its two IR values cleanly",
          report.failed == 0)
    check("I10 the overlay alignment actually lands on the type",
          populated["types"][0]["alignment"] == {
              "kind": "exact", "bytes": 4, "reason": "planted",
              "source": "overlay"})

    ir = copy.deepcopy(populated)
    next(t for t in ir["types"]
         if t["id"] == baseline["types"][0]["id"])["alignment"] = {
        "kind": "unknown", "reason": "planted"}
    expect_invariant_fails(
        "I10 an overlay alignment silently dropped from the IR is caught",
        validate_ir.i10_overlay_reach, ir, live_overlay)

    rel_sources = {role: json.loads((REPO / path).read_text(encoding="utf-8"))
                   for role, path in build_ir.RELATIONSHIP_SOURCES.items()}

    planted = copy.deepcopy(rel_sources)
    planted["receiver-map"]["inboundReceivers"][0]["bcsRefs"]["class"][0][
        "bcsId"] = "BCS-Y-9999"
    expect_build_error(
        "B8 a relationship edge citing an uncataloged symbol is refused",
        lambda: build_ir.build(symbols_doc, structs_doc, overlay,
                               planted),
        "BCS-Y-9999")

    planted = copy.deepcopy(rel_sources)
    planted["operation-map"]["operationClasses"][0]["opcodes"][0][
        "direction"] = "clientbound"
    expect_build_error(
        "B9 an operation claiming a direction the model does not carry is "
        "refused",
        lambda: build_ir.build(symbols_doc, structs_doc, overlay,
                               planted),
        "only serverbound is modeled")

    planted = copy.deepcopy(rel_sources)
    planted["receiver-map"]["inboundReceivers"][0]["opcodes"][0][
        "opcodeHex"] = "0xABCD"
    expect_build_error(
        "B10 an opcode outside the 0x[0-9a-f]{4} form is refused",
        lambda: build_ir.build(symbols_doc, structs_doc, overlay,
                               planted),
        "0xABCD")

    planted = copy.deepcopy(rel_sources)
    row = next(r for r in planted["c2s-skeleton"]["rows"]
               if r.get("confirmedBinding"))
    row["confirmedBinding"] = "OnlyOne._method"
    row["confirmedBindings"] = []
    expect_build_error(
        "B11 a joined confirmedBinding whose id count disagrees is refused",
        lambda: build_ir.build(symbols_doc, structs_doc, overlay,
                               planted),
        "the pairing is ambiguous")

    planted = copy.deepcopy(rel_sources)
    planted["receiver-map"]["inboundReceivers"].append(
        copy.deepcopy(planted["receiver-map"]["inboundReceivers"][0]))
    expect_build_error(
        "B12 two receiver rows sharing one name and vftable are refused",
        lambda: build_ir.build(symbols_doc, structs_doc, overlay,
                               planted),
        "is not unique")

    planted = copy.deepcopy(rel_sources)
    victim = next(b for b in planted["lua-bridge"]["bindings"].values()
                  if b.get("opcodes"))
    victim["opcodes"][0]["direction"] = "sideways"
    expect_build_error(
        "B13 a Lua binding direction the model does not carry is refused",
        lambda: build_ir.build(symbols_doc, structs_doc, overlay,
                               planted),
        "only inbound and outbound are modeled")

    ir = copy.deepcopy(baseline)
    ir["relationships"]["opcodes"][0]["symbols"].append("BCS-Y-9999")
    expect_invariant_fails("I11 a relationship citing an unknown symbol is "
                           "caught", validate_ir.i11_relationship_symbols, ir,
                           symbols_doc)

    ir = copy.deepcopy(baseline)
    bound = next(o for o in ir["relationships"]["opcodes"]
                 if "c2sBindings" in o)
    bound["symbols"] = [s for s in bound["symbols"]
                        if s not in bound["c2sBindings"][0].get("symbols", [])]
    expect_invariant_fails(
        "I11 a c2s binding whose symbol the opcode dropped is caught",
        validate_ir.i11_relationship_symbols, ir, symbols_doc)

    ir = copy.deepcopy(baseline)
    receiver = next(r for r in ir["relationships"]["receivers"] if r["opcodes"])
    oid = receiver["opcodes"][0]
    opcode = next(o for o in ir["relationships"]["opcodes"] if o["id"] == oid)
    opcode["receivers"] = [n for n in opcode["receivers"]
                           if n != receiver["name"]]
    expect_invariant_fails(
        "I12 an edge the far side does not name back is caught",
        validate_ir.i12_relationship_closure, ir)

    ir = copy.deepcopy(baseline)
    ir["relationships"]["opcodes"][0]["luaBindings"].append("_noSuchLuaName")
    expect_invariant_fails(
        "I12 an opcode naming a Lua binding that does not exist is caught",
        validate_ir.i12_relationship_closure, ir)

    ir = copy.deepcopy(baseline)
    bound = next(o for o in ir["relationships"]["opcodes"] if o["luaBindings"])
    name = bound["luaBindings"][0]
    for record in ir["relationships"]["luaBindings"]:
        if record["luaName"] == name:
            record["opcodes"] = [o for o in record["opcodes"]
                                 if o != bound["id"]]
    expect_invariant_fails(
        "I12 a Lua binding that stops claiming an opcode back is caught",
        validate_ir.i12_relationship_closure, ir)

    ir = copy.deepcopy(baseline)
    ir["relationships"]["opcodes"][0]["int"] += 1
    expect_invariant_fails("I13 an opcode int disagreeing with its hex is caught",
                           validate_ir.i13_opcode_identity, ir)

    ir = copy.deepcopy(baseline)
    ir["relationships"]["summary"]["s2c"] += 1
    expect_invariant_fails("I13 a summary count drifting from the rows is caught",
                           validate_ir.i13_opcode_identity, ir)

    ir = copy.deepcopy(baseline)
    ir["types"][0]["opcodes"] = ["s2c:0x00ca"]
    expect_invariant_fails(
        "I14 a type-to-opcode binding while that dimension is deferred is caught",
        validate_ir.i14_payload_type_bindings_deferred, ir)

    rebuilt = build_ir.build(symbols_doc, structs_doc, overlay)
    check("D1 two builds from identical inputs are byte-identical",
          build_ir.serialize(rebuilt) == build_ir.serialize(baseline))
    check("D2 the committed ir_catalog.json is what the builder produces",
          build_ir.OUT_PATH.read_text(encoding="utf-8")
          == build_ir.serialize(baseline))

    print("=" * 72)
    print("IR GATE BITE PROOFS")
    print("=" * 72)
    for name in PASSED:
        print(f"[  ok] {name}")
    for name in FAILED:
        print(f"[FAIL] {name}")
    print("-" * 72)
    print(f"{len(PASSED)} bit, {len(FAILED)} did not")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
