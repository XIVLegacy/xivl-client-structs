"""Mutation tests for the selector-0x0D ClientWorkElement validator."""

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
        raise AssertionError("baseline selector-0x0D catalogs failed validation")

    mutations = []
    changed = copy.deepcopy(manifest)
    changed["selectorTrace"]["tableEntry"]["callback"] = "0x005334D0"
    mutations.append(("factory callback", changed, structs, symbols))

    changed = copy.deepcopy(manifest)
    changed["createdObject"]["allocationSize"] = "0x834"
    mutations.append(("allocation size", changed, structs, symbols))

    changed = copy.deepcopy(manifest)
    changed["createdObject"]["primaryVftable"]["address"] = "0x00FA418C"
    mutations.append(("primary vftable", changed, structs, symbols))

    changed = copy.deepcopy(manifest)
    changed["selectorTrace"]["invoker"]["containerAlias"] = "unresolved"
    mutations.append(("container cache alias", changed, structs, symbols))

    changed = copy.deepcopy(manifest)
    changed["lifecycle"]["ordinaryClear"] = "unresolved"
    mutations.append(("encoded selector clear", changed, structs, symbols))

    changed_structs = copy.deepcopy(structs)
    storage = next(item for item in changed_structs["structs"] if item["id"] == "BCS-S-0079")
    next(item for item in storage["fields"] if item["offset"] == "0x014")["offset"] = "0x010"
    mutations.append(("record count offset", manifest, changed_structs, symbols))

    changed_structs = copy.deepcopy(structs)
    container = next(item for item in changed_structs["structs"] if item["id"] == "BCS-S-0053")
    next(item for item in container["fields"] if item["offset"] == "0x004D8")["type"] = "void *"
    mutations.append(("container pointee type", manifest, changed_structs, symbols))

    changed_structs = copy.deepcopy(structs)
    record = next(item for item in changed_structs["structs"] if item["id"] == "BCS-S-0078")
    record["size"] = "0x74"
    mutations.append(("record stride", manifest, changed_structs, symbols))

    changed_symbols = copy.deepcopy(symbols)
    factory = next(item for item in changed_symbols["symbols"] if item["id"] == "BCS-Y-2169")
    factory["address"] = "0x005334D0"
    mutations.append(("factory symbol address", manifest, structs, changed_symbols))

    changed = copy.deepcopy(manifest)
    changed["consumers"][0]["apply"] = "unresolved"
    mutations.append(("marker consumer", changed, structs, symbols))

    changed = copy.deepcopy(manifest)
    changed["consumers"][1]["predicate"] = "unresolved"
    mutations.append(("maintenance consumer", changed, structs, symbols))

    for label, test_manifest, test_structs, test_symbols in mutations:
        if not validate(test_manifest, test_structs, test_symbols):
            raise AssertionError(f"mutation escaped validation: {label}")

    print(f"selector-0x0D ClientWorkElement: {len(mutations)} mutations rejected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
