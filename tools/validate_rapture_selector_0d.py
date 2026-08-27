"""Validate the selector-0x0D ClientWorkElement catalog boundary."""

from __future__ import annotations

import json
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _by_id(document: dict, collection: str) -> dict[str, dict]:
    return {entry["id"]: entry for entry in document[collection]}


def _field(struct: dict, offset: str) -> dict | None:
    return next((item for item in struct["fields"] if item["offset"] == offset), None)


def validate(manifest: dict, structs_doc: dict, symbols_doc: dict) -> list[str]:
    errors: list[str] = []
    structs = _by_id(structs_doc, "structs")
    symbols = _by_id(symbols_doc, "symbols")

    table_entry = manifest.get("selectorTrace", {}).get("tableEntry", {})
    if table_entry != {
        "selector": "0x0D",
        "tableByteOffset": "0x34",
        "callback": "0x005334C0",
        "callbackBcsId": "BCS-Y-2169",
    }:
        errors.append("selector 0x0D must map table +0x34 to BCS-Y-2169")

    created = manifest.get("createdObject", {})
    if (created.get("class"), created.get("allocationSize"), created.get("structBcsId")) != (
        "Application::Main::Element::System::ClientWorkElement",
        "0x838",
        "BCS-S-0080",
    ):
        errors.append("created object identity or allocation size drifted")
    if (
        created.get("constructor", {}).get("address"),
        created.get("primaryVftable", {}).get("address"),
        created.get("secondaryInputVftable", {}).get("address"),
    ) != ("0x0055F8B0", "0x00FA42B0", "0x00FA418C"):
        errors.append("constructor or ClientWorkElement vftable address drifted")

    invoker = manifest.get("selectorTrace", {}).get("invoker", {})
    if (invoker.get("cacheOffset"), invoker.get("containerAlias")) != (
        "0x2C",
        "0x4AC+0x2C=0x4D8",
    ):
        errors.append("indexed-interface cache alias drifted")

    lifecycle = manifest.get("lifecycle", {})
    if (
        lifecycle.get("completeTeardown", {}).get("address"),
        lifecycle.get("completeTeardown", {}).get("storageDestructor"),
        lifecycle.get("completeTeardown", {}).get("scalarDeletingWrapper"),
    ) != ("0x0055D100", "0x0055CF20", "0x00567A60"):
        errors.append("ClientWorkElement teardown chain drifted")
    if "0xC000000D" not in lifecycle.get("ordinaryClear", ""):
        errors.append("selector 0xC000000D clear route drifted")

    expected_symbols = {
        "BCS-Y-2169": ("0x005334C0", "function"),
        "BCS-Y-2170": ("0x0055D100", "function"),
    }
    for symbol_id, expected in expected_symbols.items():
        symbol = symbols.get(symbol_id, {})
        if (symbol.get("address"), symbol.get("kind")) != expected:
            errors.append(f"{symbol_id} address or kind drifted")

    expected_structs = {
        "BCS-S-0053": (
            "0x004D8",
            "0x004",
            "client_work_element",
            "ApplicationMainElementSystemClientWorkElement *",
        ),
        "BCS-S-0079": ("0x014", "0x004", "record_count", "int32_t"),
        "BCS-S-0080": (
            "0x098",
            "0x7A0",
            "client_work_storage",
            "ApplicationMainElementSystemClientWorkStorage",
        ),
    }
    for struct_id, expected in expected_structs.items():
        struct = structs.get(struct_id)
        field = _field(struct, expected[0]) if struct else None
        actual = (
            field.get("offset"), field.get("size"), field.get("name"), field.get("type")
        ) if field else None
        if actual != expected:
            errors.append(f"{struct_id} field at {expected[0]} drifted")

    storage = structs.get("BCS-S-0079", {})
    for expected in [
        ("0x008", "0x00C", "header_values", "uint32_t[3]"),
        ("0x018", "0x780", "records", "ApplicationMainElementSystemClientWorkRecord[16]"),
        ("0x798", "0x001", "tail_flag", "uint8_t"),
    ]:
        field = _field(storage, expected[0]) if storage else None
        actual = (
            field.get("offset"), field.get("size"), field.get("name"), field.get("type")
        ) if field else None
        if actual != expected:
            errors.append(f"BCS-S-0079 field at {expected[0]} drifted")

    record = structs.get("BCS-S-0078", {})
    record_field = _field(record, "0x00") if record else None
    if (record.get("size"), record_field.get("size") if record_field else None) != (
        "0x78",
        "0x78",
    ):
        errors.append("BCS-S-0078 record stride drifted")

    consumers = manifest.get("consumers", [])
    routes = {item.get("route"): item for item in consumers}
    marker = routes.get("s2c:0x018D", {})
    maintenance = routes.get("internal maintenance", {})
    if (marker.get("dispatcher"), marker.get("apply")) != (
        "0x004DC690",
        "0x0055CF70",
    ):
        errors.append("s2c 0x018D consumer route drifted")
    if (
        maintenance.get("owner"),
        maintenance.get("accessor"),
        maintenance.get("predicate"),
        maintenance.get("clear"),
    ) != ("0x00691F30", "0x004D7370", "0x0055D0D0", "0x0055D0F0"):
        errors.append("internal maintenance consumer route drifted")

    evidence = manifest.get("evidence", {})
    if evidence.get("instructionListing") != (
        "tools/ghidra/logs/c537_rapture-selector-0d-listing.txt"
    ):
        errors.append("direct dispatcher instruction listing is missing")

    return errors


def main() -> int:
    errors = validate(
        _load(REPO / "manifests" / "rapture_selector_0d_clientwork.json"),
        _load(REPO / "manifests" / "structs.json"),
        _load(REPO / "manifests" / "symbols.json"),
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("selector-0x0D ClientWorkElement: 18 invariants passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
