"""Mutation tests for the RaptureElement registry validator."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

from validate_rapture_selector_0d import validate


REPO = Path(__file__).resolve().parents[1]


def _load(name: str) -> dict:
    return json.loads((REPO / "manifests" / name).read_text(encoding="utf-8"))


def main() -> int:
    manifest = _load("rapture_selector_0d_clientwork.json")
    structs = _load("structs.json")
    symbols = _load("symbols.json")
    if validate(manifest, structs, symbols):
        raise AssertionError("baseline registry catalogs failed validation")
    mutations = []
    for label, path, value in [
        ("extent", ("identityVerdict", "size"), "0x44"),
        ("constructor", ("lifetime", "memberConstructor", "address"), "0x0053B240"),
        ("factory callback", ("installedSelectors", 13, "callback"), "0x005334D0"),
        ("allocation size", ("installedSelectors", 8, "allocationSize"), "0xEEC"),
        ("class identity", ("installedSelectors", 24, "class"), "unresolved"),
        ("cache slot", ("installedSelectors", 4, "cache"), "no direct invoker cache"),
        ("null selector", ("nullSelectors", 2), "0x1A"),
        ("factory return", ("factoryContract", "returnType"), "void *"),
        ("fixed pair", ("deterministicProducers", 0, "pairs", 0, 0), "0x03"),
        ("resolved producer id", ("deterministicProducers", 4, "encodedId"), "unresolved"),
        ("resolved producer listing", ("deterministicProducers", 4, "notes"), "decompiler guess"),
        ("dynamic selector domain", ("deterministicProducers", 12, "selector"), "caller-supplied"),
        ("packet selector domain", ("deterministicProducers", 2, "selector"), "0x08"),
        ("bounded selector-0x08 ids", ("deterministicProducers", 3, "encodedId"), "caller-supplied"),
        ("literal selector domain", ("deterministicProducers", 8, "selector"), "0x0A"),
        ("clear mismatch", ("clearRoutes", 5, "encodedId"), "0xC000000C"),
        ("clear route", ("clearRoutes", 0, "selector"), "0x03"),
        ("cache map", ("cacheMap", 6, "interfaceOffset"), "0x34"),
        ("vtable owner", ("dynamicSelectorDomain", "vtableOwners", 1, "vtable"), "0x00FD5A78"),
        ("vtable result", ("dynamicSelectorDomain", "vtableOwners", 2, "result"), "0x00"),
        ("auto-id callers", ("dynamicSelectorDomain", "autoIdWrapper", "directCallers", 1), "0x006E3650"),
        ("FormElement fixed id", ("selector1AClosure", "fixedId"), "0xC0000025"),
        ("FormElement lifecycle", ("selector1AClosure", "lifecycleVerdict"), "actor creation"),
        ("FormElement cache", ("selector1AClosure", "cacheEffect"), "fixed cache"),
        ("producer boundary", ("otherSelectorProducer", "interfaceVerdict"), "connected"),
        ("effect upper-id boundary", ("otherSelectorProducer", "upperIdBoundary"), "unresolved"),
        ("reference completion", ("evidence", "referenceCompletion"), "partial"),
        ("evidence recipe", ("method", "commands", 4), "tools/ghidra/export-references.ps1 -Address bad -Output bad"),
        ("producer listing", ("evidence", "producerInstructionListing"), "missing"),
        ("producer listing recipe", ("method", "commands", 5), "DumpFunctionListing.java"),
        ("producer reference completion", ("evidence", "producerReferenceExports", 0, "completion"), "partial"),
        ("ClientWork closure", ("clientWorkClosure", "allocationSize"), "0x834"),
        ("ClientWork consumer", ("clientWorkClosure", "consumers", 1, "clear"), "unresolved"),
    ]:
        changed = copy.deepcopy(manifest)
        target = changed
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append((label, changed, structs, symbols))
    changed_structs = copy.deepcopy(structs)
    registry = next(s for s in changed_structs["structs"] if s["id"] == "BCS-S-0491")
    registry["fields"][14]["size"] = "0x08"
    mutations.append(("map extent", manifest, changed_structs, symbols))
    changed_structs = copy.deepcopy(structs)
    container = next(s for s in changed_structs["structs"] if s["id"] == "BCS-S-0053")
    next(f for f in container["fields"] if f["offset"] == "0x004AC")["type"] = "unknown[0x48]"
    mutations.append(("container embedding", manifest, changed_structs, symbols))
    changed_symbols = copy.deepcopy(symbols)
    next(s for s in changed_symbols["symbols"] if s["id"] == "BCS-Y-2182")["address"] = "0x00533550"
    mutations.append(("factory symbol", manifest, structs, changed_symbols))
    changed_symbols = copy.deepcopy(symbols)
    next(s for s in changed_symbols["symbols"] if s["id"] == "BCS-Y-2197")["address"] = "0x005F5F80"
    mutations.append(("selector producer symbol", manifest, structs, changed_symbols))
    changed_structs = copy.deepcopy(structs)
    storage = next(s for s in changed_structs["structs"] if s["id"] == "BCS-S-0079")
    next(f for f in storage["fields"] if f["offset"] == "0x014")["offset"] = "0x010"
    mutations.append(("ClientWorkStorage field", manifest, changed_structs, symbols))
    for label, test_manifest, test_structs, test_symbols in mutations:
        if not validate(test_manifest, test_structs, test_symbols):
            raise AssertionError(f"mutation escaped validation: {label}")
    print(f"RaptureElement registry: {len(mutations)} mutations rejected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
