"""Validate the s2c 0x018D MapScreenControl presentation catalog."""

from __future__ import annotations

import json
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _by_id(document: dict, collection: str) -> dict[str, dict]:
    return {entry["id"]: entry for entry in document[collection]}


def _byte_accounted(struct: dict) -> bool:
    cursor = 0
    for field in struct.get("fields", []):
        if int(field["offset"], 16) != cursor:
            return False
        cursor += int(field["size"], 16)
    return cursor == int(struct.get("size", "0"), 16)


EXPECTED_SYMBOLS = {
    "BCS-Y-2201": "0x004D7610",
    "BCS-Y-2202": "0x004D7620",
    "BCS-Y-2203": "0x00679ED0",
    "BCS-Y-2204": "0x00672690",
    "BCS-Y-2205": "0x00678640",
    "BCS-Y-2206": "0x00680710",
    "BCS-Y-2207": "0x00671400",
    "BCS-Y-2208": "0x009442B0",
    "BCS-Y-2209": "0x009426D0",
    "BCS-Y-2210": "0x009455A0",
    "BCS-Y-2211": "0x00942DB0",
    "BCS-Y-2212": "0x00573970",
    "BCS-Y-2213": "0x00573A50",
    "BCS-Y-2214": "0x00573FC0",
    "BCS-Y-2215": "0x0055D020",
    "BCS-Y-2216": "0x0055D030",
    "BCS-Y-2217": "0x0055D050",
    "BCS-Y-2218": "0x0055D070",
    "BCS-Y-2219": "0x0055D090",
    "BCS-Y-2220": "0x0055D0B0",
    "BCS-Y-2221": "0x00691F30",
    "BCS-Y-2222": "0x0092CFB0",
    "BCS-Y-2223": "0x00983A20",
    "BCS-Y-2224": "0x009830F0",
    "BCS-Y-2225": "0x00983BE0",
    "BCS-Y-2226": "0x00985160",
    "BCS-Y-2227": "0x0094A330",
    "BCS-Y-2228": "0x0094E800",
    "BCS-Y-2229": "0x009857F0",
}


EXPECTED_DECOMP_ARCHIVES = [
    "tools/ghidra/logs/c540_018d-presentation-ownership.txt",
    "tools/ghidra/logs/c540_018d-record-projection.txt",
    "tools/ghidra/logs/c540_018d-pcsearch-gate.txt",
    "tools/ghidra/logs/c540_018d-xml-document-layout.txt",
    "tools/ghidra/logs/c541_018d-resource-registration.txt",
    "tools/ghidra/logs/c541_018d-package-correlation.txt",
]


EXPECTED_RECORD_FIELDS = [
    ("0x00", "0x04", "value_00"),
    ("0x04", "0x04", "opaque_04"),
    ("0x08", "0x04", "value_08"),
    ("0x0C", "0x04", "value_0c"),
    ("0x10", "0x04", "value_10"),
    ("0x14", "0x04", "value_14"),
    ("0x18", "0x04", "value_18"),
    ("0x1C", "0x04", "opaque_1c"),
    ("0x20", "0x54", "projected_helper_state"),
    ("0x74", "0x04", "projected_tail_value"),
]


def validate(manifest: dict, structs_doc: dict, symbols_doc: dict) -> list[str]:
    errors: list[str] = []
    structs = _by_id(structs_doc, "structs")
    symbols = _by_id(symbols_doc, "symbols")

    identity = manifest.get("identity", {})
    if (identity.get("opcode"), identity.get("canonicalName"), identity.get("rejectedCanonicalName")) != (
        "0x018D", "_0x018D", "PartyMapMarkerUpdatePacket"
    ):
        errors.append("neutral opcode identity or rejected alias drifted")
    if "67b709d5ffd90b8dc10a699e608fa1216e40660d" not in identity.get("wireContract", ""):
        errors.append("immutable wire-contract citation drifted")

    evidence = manifest.get("evidence", {})
    if evidence.get("decompArchives") != EXPECTED_DECOMP_ARCHIVES:
        errors.append("decomp archive set drifted")
    if evidence.get("resourceRttiDetails") != "tools/ghidra/logs/c541_018d-resource-rtti.tsv":
        errors.append("resource RTTI evidence drifted")
    resource_refs = evidence.get("resourceReferenceExport", {})
    if (resource_refs.get("path"), resource_refs.get("completion")) != (
        "tools/ghidra/logs/c541_018d-resource-strings.txt",
        "COMPLETE: FindReferences defined_strings=28414 queries=7 matches=4 references=5",
    ):
        errors.append("resource string-reference evidence drifted")
    package_instances = evidence.get("packageInstanceReferenceExport", {})
    if (package_instances.get("path"), package_instances.get("completion")) != (
        "tools/ghidra/logs/c541_018d-package-instances.txt",
        "COMPLETE: FindReferences defined_strings=28414 queries=2 matches=2 references=2",
    ):
        errors.append("package instance-reference evidence drifted")
    xaml_vtable = evidence.get("xamlVtableListing", {})
    if (xaml_vtable.get("path"), xaml_vtable.get("completion")) != (
        "tools/ghidra/logs/c541_018d-xaml-vtable.txt",
        "COMPLETE: read 9 contiguous little-endian code pointers from the retail PE",
    ):
        errors.append("XAML vtable evidence drifted")
    if evidence.get("referenceExport", {}).get("completion") != "COMPLETE: FindReferences targets=14 references=44":
        errors.append("reference-export completion marker drifted")
    rtti_index = evidence.get("rttiIndex", {})
    if (rtti_index.get("rows"), rtti_index.get("mapMarkerPartyMatches")) != (5623, 0):
        errors.append("complete RTTI-index boundary drifted")

    for symbol_id, address in EXPECTED_SYMBOLS.items():
        symbol = symbols.get(symbol_id, {})
        if (symbol.get("address", "").lower(), symbol.get("kind")) != (address.lower(), "function"):
            errors.append(f"{symbol_id} address or kind drifted")

    expected_sizes = {
        "BCS-S-0316": "0x28",
        "BCS-S-0317": "0x298",
        "BCS-S-0078": "0x78",
        "BCS-S-0079": "0x7A0",
        "BCS-S-0080": "0x838",
        "BCS-S-0492": "0xA70",
        "BCS-S-0493": "0xE4",
        "BCS-S-0494": "0x210",
        "BCS-S-0495": "0x18",
        "BCS-S-0496": "0xC4",
    }
    for struct_id, size in expected_sizes.items():
        struct = structs.get(struct_id, {})
        if struct.get("size", "").lower() != size.lower():
            errors.append(f"{struct_id} size drifted")
        if not _byte_accounted(struct):
            errors.append(f"{struct_id} is not byte-accounted")

    wire_record = structs.get("BCS-S-0316", {})
    wire_application = structs.get("BCS-S-0317", {})
    if (wire_record.get("name"), wire_application.get("name"), symbols.get("BCS-Y-0890", {}).get("name")) != (
        "S2c018DWireRecord", "S2c018DApplication", "S2c018D_ApplyClientWork_FUN_0055CF70"
    ):
        errors.append("neutral legacy 0x018D catalog identity drifted")
    forbidden_nouns = ("player", "coordinate", "orientation", "actor", "icon", "label", "server", "marker")
    wire_field_names = [
        field.get("name", "").lower()
        for struct in (wire_record, wire_application)
        for field in struct.get("fields", [])
    ]
    if any(noun in name for noun in forbidden_nouns for name in wire_field_names):
        errors.append("unsupported semantic noun returned to the 0x018D wire catalog")

    record_fields = [(f.get("offset"), f.get("size"), f.get("name")) for f in structs.get("BCS-S-0078", {}).get("fields", [])]
    if record_fields != EXPECTED_RECORD_FIELDS:
        errors.append("ClientWorkRecord field partition drifted")
    storage_fields = {field.get("offset"): field for field in structs.get("BCS-S-0079", {}).get("fields", [])}
    if (storage_fields.get("0x014", {}).get("name"), storage_fields.get("0x018", {}).get("size"), storage_fields.get("0x798", {}).get("size")) != ("record_count", "0x780", "0x001"):
        errors.append("ClientWorkStorage count, records, or tail gate drifted")
    map_fields = {field.get("offset"): field for field in structs.get("BCS-S-0492", {}).get("fields", [])}
    if (map_fields.get("0x294", {}).get("name"), map_fields.get("0x448", {}).get("name"), map_fields.get("0x57C", {}).get("size"), map_fields.get("0x5F0", {}).get("type"), map_fields.get("0x9E8", {}).get("type")) != (
        "resource_collection", "registration_gate", "0x001", "ApplicationMainRaptureElementContainer *", "SqwtDataSqwtXmlDataMaker *"
    ):
        errors.append("MapScreenControl route fields drifted")
    maker_fields = {field.get("offset"): field for field in structs.get("BCS-S-0494", {}).get("fields", [])}
    if (maker_fields.get("0x0CC", {}).get("name"), maker_fields.get("0x0DC", {}).get("name"), maker_fields.get("0x11C", {}).get("type"), maker_fields.get("0x20C", {}).get("name")) != (
        "presentation_index_property", "row_count_property", "SqwtXmlXmlDocument", "mutation_in_progress"
    ):
        errors.append("SqwtXmlDataMaker row-domain fields drifted")
    dictionary_fields = {field.get("offset"): field for field in structs.get("BCS-S-0496", {}).get("fields", [])}
    if (dictionary_fields.get("0x000", {}).get("name"), dictionary_fields.get("0x024", {}).get("name"), dictionary_fields.get("0x04C", {}).get("name"), dictionary_fields.get("0x0BC", {}).get("size")) != (
        "primary_vftable", "secondary_vftable_24", "resource_key", "0x008"
    ):
        errors.append("ResourceDictionary key/lifetime fields drifted")
    context_fields = [(f.get("offset"), f.get("size")) for f in structs.get("BCS-S-0495", {}).get("fields", [])]
    if context_fields != [("0x00", "0x004"), ("0x04", "0x004"), ("0x08", "0x010")]:
        errors.append("projection-context layout drifted")

    owner = manifest.get("ownershipTree", {})
    if len(owner.get("route", [])) != 8 or owner.get("clientWork", {}).get("recordStride") != "0x78":
        errors.append("ownership route or ClientWork stride drifted")
    map_owner = owner.get("mapScreen", {})
    if (map_owner.get("size"), map_owner.get("ownerPointerOffset"), map_owner.get("ownerRegistryOffset"), map_owner.get("registrationGateOffset")) != (
        "0xA70", "0x5F0", "0x17858", "0x448"
    ):
        errors.append("MapScreenControl owner or lifetime offsets drifted")
    if "non-owning registration" not in map_owner.get("ownershipVerdict", ""):
        errors.append("MapScreenControl registration ownership boundary drifted")

    projection = manifest.get("wireStorageProjection", {})
    if (projection.get("wireApplicationSize"), projection.get("wireRecordOffset"), projection.get("wireRecordStride"), projection.get("storageRecordOffset"), projection.get("storageRecordStride")) != (
        "0x298", "0x10", "0x28", "0x18", "0x78"
    ):
        errors.append("wire/storage extent distinction drifted")
    projected = [(item.get("wire"), item.get("storageRecord")) for item in projection.get("records", [])]
    if projected != [("+0x00", "+0x00"), ("+0x08", "+0x08"), ("+0x0C", "+0x0C"), ("+0x14", "+0x10"), ("+0x18", "+0x14"), ("+0x1C", "+0x18")]:
        errors.append("wire-to-record projection map drifted")
    if "not assigned" not in projection.get("boundary", "").lower() or "clamp" not in projection.get("count", {}).get("boundary", ""):
        errors.append("wire semantic or count-clamp boundary drifted")

    context = manifest.get("projectionContext", {})
    if (context.get("struct"), context.get("size"), context.get("copyConstructor", {}).get("bcsId"), context.get("recordProjector", {}).get("bcsId")) != (
        "BCS-S-0495", "0x18", "BCS-Y-2212", "BCS-Y-2214"
    ):
        errors.append("temporary projection-context contract drifted")
    if not context.get("catalogNameKind", "").startswith("descriptive"):
        errors.append("descriptive helper-context naming boundary drifted")

    map_layout = manifest.get("mapScreenLayout", {})
    vtables = [(v.get("offset"), v.get("address"), v.get("col"), v.get("slots")) for v in map_layout.get("vftables", [])]
    expected_vtables = [
        ("0x000", "0x00FC358C", "0x01158834", 65),
        ("0x0B4", "0x00FC3464", "0x01158924", 72),
        ("0x194", "0x00FC3450", "0x01158938", 4),
        ("0x2A4", "0x00FC3444", "0x0115894C", 2),
    ]
    if vtables != expected_vtables:
        errors.append("MapScreenControl RTTI/vftable layout drifted")
    gate = map_layout.get("presentationGate", {})
    if set(gate) != {"valueOffset", "condition", "boundary"} or gate.get("valueOffset") != "0x57C":
        errors.append("MapScreenControl presentation-gate boundary drifted")
    cache = map_layout.get("groupMarkerDataCache", {})
    if (cache.get("offset"), cache.get("resourceName"), cache.get("targetRtti"), cache.get("ownership")) != (
        "0x9E8", "group_marker_data", "Sqwt::Data::SqwtXmlDataMaker", "borrowed; MapScreenControl teardown does not release this pointer"
    ):
        errors.append("group_marker_data cache contract drifted")
    lookup = cache.get("lookup", {})
    if (lookup.get("address"), lookup.get("bcsId"), lookup.get("primaryVtableSlot"), lookup.get("localCollectionOffset"), lookup.get("collectionPointerRange"), lookup.get("keyOffset"), lookup.get("fallback")) != (
        "0x0092CFB0", "BCS-Y-2222", 7, "0x294", "+0x08 begin, +0x0C end", "0x4C", "delegates the same lookup through the parent resource chain"
    ):
        errors.append("group_marker_data lookup route drifted")

    group = manifest.get("groupMarkerData", {})
    if (group.get("dataMakerStruct"), group.get("dataMakerSize"), group.get("xmlDocument", {}).get("struct"), group.get("xmlDocument", {}).get("offset")) != (
        "BCS-S-0494", "0x210", "BCS-S-0493", "0x11C"
    ):
        errors.append("SqwtXmlDataMaker or XmlDocument embedding drifted")
    if "dense zero-based" not in group.get("keyOwnership", "") or "five string-like wrappers" not in group.get("valueOwnership", ""):
        errors.append("row key/value ownership drifted")
    dictionary = group.get("resourceDictionary", {})
    dictionary_lifecycle = (
        dictionary.get("struct"), dictionary.get("size"),
        dictionary.get("constructor", {}).get("address"), dictionary.get("constructor", {}).get("bcsId"),
        dictionary.get("destructor", {}).get("address"), dictionary.get("destructor", {}).get("bcsId"),
        dictionary.get("factory", {}).get("address"), dictionary.get("factory", {}).get("bcsId"),
        dictionary.get("deletingDestructor", {}).get("address"), dictionary.get("deletingDestructor", {}).get("bcsId"),
    )
    if dictionary_lifecycle != (
        "BCS-S-0496", "0xC4", "0x00983A20", "BCS-Y-2223", "0x009830F0", "BCS-Y-2224",
        "0x00983BE0", "BCS-Y-2225", "0x00985160", "BCS-Y-2226",
    ):
        errors.append("ResourceDictionary lifecycle drifted")
    removal = group.get("removal", {})
    if (removal.get("bcsId"), removal.get("range"), removal.get("order"), removal.get("operation")) != (
        "BCS-Y-2211", "inclusive [accepted count, existing count - 1]", "descending", "RemoveIndex"
    ):
        errors.append("trailing-row lifetime contract drifted")

    accessors = [(item.get("bcsId"), item.get("address"), item.get("result")) for item in manifest.get("accessorMap", [])]
    expected_accessors = [
        ("BCS-Y-2215", "0x0055D020", "storage+0x14 record count"),
        ("BCS-Y-2216", "0x0055D030", "record+0x20 helper-state address"),
        ("BCS-Y-2217", "0x0055D050", "record+0x10 value-pair address"),
        ("BCS-Y-2218", "0x0055D070", "record+0x74 dword"),
        ("BCS-Y-2219", "0x0055D090", "record+0x00 dword"),
        ("BCS-Y-2220", "0x0055D0B0", "record+0x08 in EAX and record+0x0C in EDX"),
    ]
    if accessors != expected_accessors:
        errors.append("record accessor map drifted")

    rows = manifest.get("presentationRows", {})
    properties = [(p.get("uiProperty"), p.get("uiType"), p.get("value")) for p in rows.get("propertyWrites", [])]
    if properties != [("X", "Int", None), ("Z", "Int", None), ("Layout", "Int", None), ("Text", "String", None), ("Visibility", "String", "Visible"), ("SparkleSequence", "String", "m00002"), ("Template", "String", "MapMarkerParty")]:
        errors.append("exact UI property write sequence drifted")
    if "do not establish" not in rows.get("fieldBoundary", ""):
        errors.append("UI-property versus wire-field boundary drifted")

    marker = manifest.get("mapMarkerPartyVerdict", {})
    if (marker.get("nativeClass"), marker.get("rttiMatches")) != ("not established", 0):
        errors.append("MapMarkerParty native-class verdict drifted")
    if "No native constructor" not in marker.get("construction", "") or "no separately allocated native marker object" not in marker.get("propertyState", ""):
        errors.append("MapMarkerParty construction or property-state boundary drifted")

    registration = manifest.get("resourceRegistration", {})
    static_refs = registration.get("groupMarkerDataStaticReferences", {})
    if (static_refs.get("count"), static_refs.get("address"), static_refs.get("reference"), static_refs.get("owner")) != (
        1, "0x00FC28A8", "0x00671458", "FUN_00671400"
    ):
        errors.append("group_marker_data static-reference boundary drifted")
    producer = registration.get("producer", {})
    producer_contract = (
        producer.get("parser", {}).get("address"), producer.get("parser", {}).get("bcsId"),
        producer.get("xamlClass"), producer.get("xamlVftable", {}).get("address"),
        producer.get("xamlVftable", {}).get("col"), producer.get("xamlVftable", {}).get("slots"),
        producer.get("xamlFactory", {}).get("address"), producer.get("xamlFactory", {}).get("bcsId"),
        producer.get("xamlFactory", {}).get("vtableSlot"), producer.get("xamlFactory", {}).get("allocation"),
        producer.get("xamlFactory", {}).get("result"), producer.get("alternateFactory", {}).get("address"),
        producer.get("alternateFactory", {}).get("bcsId"), producer.get("alternateFactory", {}).get("allocation"),
        producer.get("alternateFactory", {}).get("result"),
    )
    if producer_contract != (
        "0x0094A330", "BCS-Y-2227", "Sqwt::Markup::XamlSqwtXmlDataMaker", "0x0106D9A4",
        "0x0117A830", 9, "0x0094E800", "BCS-Y-2228", 8, "0x210",
        "Sqwt::Data::SqwtXmlDataMaker", "0x009857F0", "BCS-Y-2229", "0x210",
        "Sqwt::Data::SqwtXmlDataMaker",
    ):
        errors.append("SqwtXmlDataMaker markup producer drifted")
    packages = registration.get("packagePaths", [])
    package_rows = [
        (row.get("path"), row.get("definedAddress"), row.get("staticReferenceCount"), row.get("consumers"), row.get("observedUse"), row.get("ownershipBoundary"))
        for row in packages
    ]
    if package_rows != [
        ("common/mapMarker.le.spk", "0x00FC3390", 2, ["FUN_0067C220@0x0067C30A", "FUN_00680810@0x00680A13"], "MapScreen callbacks apply the package path to RTTI-cast Sqwt::Controls::SparkleControl objects with instance strings m00010 and m00020.", "No observed call inserts group_marker_data or passes its key; shared MapScreen co-residence is not resource ownership."),
        ("debug/pc_mark_sample.le.spk", "0x00FC288C", 1, ["FUN_006737A0@0x00673923"], "MapScreenControl property-handler case 0x1F assigns the path to complete-object +0xA00.", "The handler does not call the group_marker_data lookup or a proven registration writer; the property value is not a source-package edge."),
    ]:
        errors.append("MapScreen package-path census drifted")
    if registration.get("registrationWriterVerdict") != "No static writer for the exact group_marker_data key is recorded outside the presenter literal. Key installation is therefore bounded at parsed package/markup state entering the generic XAML producer and the runtime +0x294 resource collection; computed, indirect, dynamic, package-data, and runtime-only registration remain possible.":
        errors.append("runtime registration-writer boundary drifted")

    gate = manifest.get("pcSearchGate", {})
    if (gate.get("class"), gate.get("method", {}).get("bcsId"), gate.get("vftable"), gate.get("slot")) != (
        "Application::Main::Element::Form::PcSearchWidgetOperator", "BCS-Y-2221", "0x00FC8424", 29
    ):
        errors.append("PcSearchWidgetOperator RTTI/slot gate drifted")
    if "not part of MapMarkerParty presentation" not in gate.get("ownershipBoundary", ""):
        errors.append("PcSearch versus marker-presentation boundary drifted")

    rejected = " ".join(manifest.get("rejectedInterpretations", []))
    for required in ("canonical opcode identity", "native marker class", "source-keyed", "not allocation ownership", "not ownership", "common/mapMarker.le.spk", "debug/pc_mark_sample.le.spk", "coordinate", "not marker presentation"):
        if required not in rejected:
            errors.append(f"rejected interpretation missing: {required}")
    return errors


def main() -> int:
    errors = validate(
        _load(REPO / "manifests" / "s2c_018d_map_marker_presentation.json"),
        _load(REPO / "manifests" / "structs.json"),
        _load(REPO / "manifests" / "symbols.json"),
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("s2c 0x018D presentation: 69 invariants passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
