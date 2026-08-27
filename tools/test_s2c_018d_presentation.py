"""Plant focused defects in the s2c 0x018D presentation catalog."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
from validate_s2c_018d_presentation import validate


def _load(name: str) -> dict:
    return json.loads((REPO / "manifests" / name).read_text(encoding="utf-8"))


def _set(document: dict, path: tuple, value) -> None:
    target = document
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def main() -> int:
    manifest = _load("s2c_018d_map_marker_presentation.json")
    structs = _load("structs.json")
    symbols = _load("symbols.json")
    mutations = [
        ("neutral opcode identity", "manifest", ("identity", "canonicalName"), "PartyMapMarkerUpdatePacket"),
        ("wire commit", "manifest", ("identity", "wireContract"), "mutable"),
        ("RTTI negative", "manifest", ("evidence", "rttiIndex", "mapMarkerPartyMatches"), 1),
        ("reference completion", "manifest", ("evidence", "referenceExport", "completion"), "INCOMPLETE"),
        ("decomp archive path", "manifest", ("evidence", "decompArchives", 4), "wrong.txt"),
        ("resource reference path", "manifest", ("evidence", "resourceReferenceExport", "path"), "wrong.txt"),
        ("package instance completion", "manifest", ("evidence", "packageInstanceReferenceExport", "completion"), "INCOMPLETE"),
        ("XAML vtable completion", "manifest", ("evidence", "xamlVtableListing", "completion"), "INCOMPLETE"),
        ("MapScreen size", "manifest", ("ownershipTree", "mapScreen", "size"), "0xA6C"),
        ("owner registry", "manifest", ("ownershipTree", "mapScreen", "ownerRegistryOffset"), "0x17854"),
        ("wire stride", "manifest", ("wireStorageProjection", "wireRecordStride"), "0x78"),
        ("storage stride", "manifest", ("wireStorageProjection", "storageRecordStride"), "0x28"),
        ("context size", "manifest", ("projectionContext", "size"), "0x20"),
        ("MapScreen vtable", "manifest", ("mapScreenLayout", "vftables", 0, "address"), "0x00FC3444"),
        ("cache ownership", "manifest", ("mapScreenLayout", "groupMarkerDataCache", "ownership"), "owned"),
        ("resource lookup slot", "manifest", ("mapScreenLayout", "groupMarkerDataCache", "lookup", "primaryVtableSlot"), 8),
        ("resource lookup address", "manifest", ("mapScreenLayout", "groupMarkerDataCache", "lookup", "address"), "0x0092CFC0"),
        ("resource collection range", "manifest", ("mapScreenLayout", "groupMarkerDataCache", "lookup", "collectionPointerRange"), "+0x04 begin"),
        ("XmlDocument offset", "manifest", ("groupMarkerData", "xmlDocument", "offset"), "0x120"),
        ("ResourceDictionary size", "manifest", ("groupMarkerData", "resourceDictionary", "size"), "0xC8"),
        ("ResourceDictionary factory address", "manifest", ("groupMarkerData", "resourceDictionary", "factory", "address"), "0x00983BF0"),
        ("row key ownership", "manifest", ("groupMarkerData", "keyOwnership"), "source actor key"),
        ("removal order", "manifest", ("groupMarkerData", "removal", "order"), "ascending"),
        ("group key static refs", "manifest", ("resourceRegistration", "groupMarkerDataStaticReferences", "count"), 2),
        ("XAML factory", "manifest", ("resourceRegistration", "producer", "xamlFactory", "bcsId"), "BCS-Y-2229"),
        ("XAML parser address", "manifest", ("resourceRegistration", "producer", "parser", "address"), "0x0094A340"),
        ("XAML class", "manifest", ("resourceRegistration", "producer", "xamlClass"), "MapMarkerParty"),
        ("XAML factory result", "manifest", ("resourceRegistration", "producer", "xamlFactory", "result"), "MapMarkerParty"),
        ("common package refs", "manifest", ("resourceRegistration", "packagePaths", 0, "staticReferenceCount"), 1),
        ("common package consumer", "manifest", ("resourceRegistration", "packagePaths", 0, "consumers", 0), "FUN_00000000@0x00000000"),
        ("common package ownership", "manifest", ("resourceRegistration", "packagePaths", 0, "ownershipBoundary"), "owns group_marker_data"),
        ("debug package address", "manifest", ("resourceRegistration", "packagePaths", 1, "definedAddress"), "0x00FC3390"),
        ("registration writer", "manifest", ("resourceRegistration", "registrationWriterVerdict"), "direct writer proven"),
        ("accessor result", "manifest", ("accessorMap", 2, "result"), "record+0x14"),
        ("template value", "manifest", ("presentationRows", "propertyWrites", 6, "value"), "MarkerObject"),
        ("native marker class", "manifest", ("mapMarkerPartyVerdict", "nativeClass"), "MapMarkerParty"),
        ("PcSearch slot", "manifest", ("pcSearchGate", "slot"), 28),
    ]
    failures = []
    for label, owner, path, value in mutations:
        test_manifest = deepcopy(manifest)
        test_structs = deepcopy(structs)
        test_symbols = deepcopy(symbols)
        target = {"manifest": test_manifest, "structs": test_structs, "symbols": test_symbols}[owner]
        _set(target, path, value)
        if not validate(test_manifest, test_structs, test_symbols):
            failures.append(label)

    changed_structs = deepcopy(structs)
    record = next(item for item in changed_structs["structs"] if item["id"] == "BCS-S-0078")
    record["fields"][8]["size"] = "0x50"
    if not validate(manifest, changed_structs, symbols):
        failures.append("ClientWorkRecord partition")

    changed_structs = deepcopy(structs)
    maker = next(item for item in changed_structs["structs"] if item["id"] == "BCS-S-0494")
    maker["fields"][-2]["offset"] = "0x20D"
    if not validate(manifest, changed_structs, symbols):
        failures.append("SqwtXmlDataMaker accounting")

    changed_structs = deepcopy(structs)
    dictionary = next(item for item in changed_structs["structs"] if item["id"] == "BCS-S-0496")
    dictionary["fields"][3]["size"] = "0x020"
    if not validate(manifest, changed_structs, symbols):
        failures.append("ResourceDictionary accounting")

    changed_structs = deepcopy(structs)
    map_screen = next(item for item in changed_structs["structs"] if item["id"] == "BCS-S-0492")
    collection = next(item for item in map_screen["fields"] if item["offset"] == "0x294")
    collection["name"] = "pointer_array"
    if not validate(manifest, changed_structs, symbols):
        failures.append("MapScreen resource collection field")

    changed_symbols = deepcopy(symbols)
    presenter = next(item for item in changed_symbols["symbols"] if item["id"] == "BCS-Y-2207")
    presenter["address"] = "0x00671410"
    if not validate(manifest, structs, changed_symbols):
        failures.append("presenter symbol")

    changed_symbols = deepcopy(symbols)
    gate = next(item for item in changed_symbols["symbols"] if item["id"] == "BCS-Y-2221")
    gate["kind"] = "global"
    if not validate(manifest, structs, changed_symbols):
        failures.append("PcSearch symbol kind")

    changed_symbols = deepcopy(symbols)
    lookup = next(item for item in changed_symbols["symbols"] if item["id"] == "BCS-Y-2222")
    lookup["address"] = "0x0092CFC0"
    if not validate(manifest, structs, changed_symbols):
        failures.append("resource lookup symbol")

    changed_structs = deepcopy(structs)
    wire_record = next(item for item in changed_structs["structs"] if item["id"] == "BCS-S-0316")
    wire_record["fields"][0]["name"] = "player_id"
    if not validate(manifest, changed_structs, symbols):
        failures.append("wire semantic noun")

    changed_symbols = deepcopy(symbols)
    apply_symbol = next(item for item in changed_symbols["symbols"] if item["id"] == "BCS-Y-0890")
    apply_symbol["name"] = "PartyMapMarker_MarkerUpdateApply_FUN_0055CF70"
    if not validate(manifest, structs, changed_symbols):
        failures.append("legacy apply identity")

    if failures:
        for failure in failures:
            print(f"ERROR: mutation escaped: {failure}")
        return 1
    print(f"s2c 0x018D presentation mutations: {len(mutations) + 9} defects detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
