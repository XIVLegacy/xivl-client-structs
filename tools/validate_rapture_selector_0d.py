"""Validate the RaptureElement registry and selector factory catalog."""

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
    return next((item for item in struct.get("fields", []) if item["offset"] == offset), None)


EXPECTED_SELECTORS = [
    ("0x00", "0x00532FC0", "BCS-Y-2174", "0x94", "0x00532F40", "Application::Main::Element::DaemonElement", "no direct invoker cache"),
    ("0x01", "0x00533040", "BCS-Y-2175", "0x98", "0x0055F940", "Application::Main::Element::System::CommonResourceElement", "no direct invoker cache"),
    ("0x02", "0x005330C0", "BCS-Y-2176", "0x194", "0x00566380", "Application::Main::Element::System::CameraElement", "interface+0x18/container+0x4C4"),
    ("0x03", "0x00533140", "BCS-Y-2177", "0x120", "0x00565170", "Application::Main::Element::System::CutManagerElement", "interface+0x1C/container+0x4C8"),
    ("0x04", "0x005331C0", "BCS-Y-2178", "0x260", "0x005600B0", "Application::Main::Element::System::GameManagerElement", "interface+0x20/container+0x4CC"),
    ("0x05", "0x005333C0", "BCS-Y-2179", "0x130", "0x0055EB70", "Application::Main::Element::System::BootupElement", "interface+0x24/container+0x4D0"),
    ("0x06", "0x00533240", "BCS-Y-2180", "0xCC", "0x00564F80", "Application::Main::Element::System::MainElement", "interface+0x10/container+0x4BC"),
    ("0x07", "0x005332C0", "BCS-Y-2181", "0x104", "0x00566880", "Application::Main::Element::System::TargetElement", "interface+0x14/container+0x4C0"),
    ("0x08", "0x00533540", "BCS-Y-2182", "0xEF0", "0x0058B4E0", "Application::Main::Element::Chara::CharaElement", "interface+0x38/container+0x4E4 map-like cache keyed by encoded object id"),
    ("0x09", "0x005335C0", "BCS-Y-2183", "0x208", "0x0059EE50", "Application::Main::Element::Map::MapLayoutElement", "interface+0x34/container+0x4E0"),
    ("0x0A", "0x00533640", "BCS-Y-2184", "0x9C", "0x00687320", "Application::Main::Element::Effect::EffectElement", "no direct invoker cache"),
    ("0x0B", "0x00533340", "BCS-Y-2185", "0x98", "0x0055D170", "Application::Main::Element::System::CustomControlElement", "no direct invoker cache"),
    ("0x0C", "0x00533440", "BCS-Y-2186", "0x1B8", "0x00561190", "Application::Main::Element::System::ScreenshotManagerElement", "interface+0x28/container+0x4D4"),
    ("0x0D", "0x005334C0", "BCS-Y-2169", "0x838", "0x0055F8B0", "Application::Main::Element::System::ClientWorkElement", "interface+0x2C/container+0x4D8"),
    ("0x0E", "0x00533740", "BCS-Y-2187", "0xFB0", "0x0066F770", "Application::Main::Element::Window::WidgetElement", "interface+0x30/container+0x4DC"),
    ("0x0F", "0x005336C0", "BCS-Y-2188", "0x98", "0x0066EB80", "Application::Main::Element::Window::SqwtElement", "no direct invoker cache"),
    ("0x10", "0x005337C0", "BCS-Y-2189", "0x1E78", "0x00688710", "Application::Main::Element::Window::Debug::DebugWindow", "no direct invoker cache"),
    ("0x11", "0x00533840", "BCS-Y-1330", "0xF0", "0x00599CB0", "Application::Main::Element::Window::LuaDebug::LuaDebugLog", "interface+0x44/container+0x4F0"),
    ("0x12", "0x00533940", "BCS-Y-1332", "0x100", "0x0068DDF0", "Application::Main::Element::Window::LuaDebug::LuaDebugSelect", "no direct invoker cache"),
    ("0x13", "0x005338C0", "BCS-Y-2190", "0xBC8", "0x0068D510", "Application::Main::Element::Window::LuaDebug::LuaDebugOut", "no direct invoker cache"),
    ("0x14", "0x005339C0", "BCS-Y-2191", "0x94", "0x0068E4C0", "Application::Main::Element::Light::LightElement", "no direct invoker cache"),
    ("0x15", "0x00533A40", "BCS-Y-2192", "0x94", "0x0068E680", "Application::Main::Element::Debug::DebugInfoElement", "no direct invoker cache"),
    ("0x16", "0x00533AC0", "BCS-Y-2193", "0x120", "0x00686FB0", "Application::Main::Element::Effect::EffectDebugElement", "no direct invoker cache"),
    ("0x19", "0x00539940", "BCS-Y-2194", "0xB8", "0x00539890", "Application::Main::Element::XamlElement", "no direct invoker cache"),
    ("0x1A", "0x0053B1B0", "BCS-Y-2195", "0x280", "0x0053AF60", "Application::Main::Element::FormElement", "no direct invoker cache"),
]


def validate(manifest: dict, structs_doc: dict, symbols_doc: dict) -> list[str]:
    errors: list[str] = []
    structs = _by_id(structs_doc, "structs")
    symbols = _by_id(symbols_doc, "symbols")
    identity = manifest.get("identityVerdict", {})
    if (identity.get("offset"), identity.get("size"), identity.get("classification"), identity.get("retailClassName")) != (
        "0x4AC", "0x48", "structurally bounded anonymous registry/cache member", "unresolved"
    ):
        errors.append("registry identity or byte extent drifted")
    lifetime = manifest.get("lifetime", {})
    if (lifetime.get("memberConstructor", {}).get("address"), lifetime.get("memberDestructor", {}).get("address")) != ("0x0053B230", "0x004DED90"):
        errors.append("registry construction or destruction drifted")

    actual_selectors = [(e.get("selector"), e.get("callback"), e.get("callbackBcsId"), e.get("allocationSize"), e.get("constructor"), e.get("class"), e.get("cache")) for e in manifest.get("installedSelectors", [])]
    if actual_selectors != EXPECTED_SELECTORS:
        errors.append("installed selector/factory/class/cache table drifted")
    if manifest.get("nullSelectors") != ["0x17", "0x18", "0x1B"]:
        errors.append("null selector set drifted")
    contract = manifest.get("factoryContract", {})
    if contract.get("bodyBytes") != 117 or "unknown 32-bit" not in contract.get("returnType", ""):
        errors.append("factory return boundary or uniform body size drifted")
    for _, address, symbol_id, *_ in EXPECTED_SELECTORS:
        symbol = symbols.get(symbol_id, {})
        if (symbol.get("address"), symbol.get("kind")) != (address, "function"):
            errors.append(f"{symbol_id} factory address or kind drifted")
    for symbol_id, address in (("BCS-Y-2171", "0x0053B230"), ("BCS-Y-2172", "0x004DED90"), ("BCS-Y-2173", "0x005374D0")):
        if symbols.get(symbol_id, {}).get("address") != address:
            errors.append(f"{symbol_id} registry helper address drifted")

    registry = structs.get("BCS-S-0491", {})
    expected_fields = [
        ("0x00", "0x04", "unknown_00"), ("0x04", "0x04", "callback_table_begin"), ("0x08", "0x04", "callback_table_end"), ("0x0C", "0x04", "callback_table_capacity_end"),
        ("0x10", "0x04", "main_element"), ("0x14", "0x04", "target_element"), ("0x18", "0x04", "camera_element"), ("0x1C", "0x04", "cut_manager_element"),
        ("0x20", "0x04", "game_manager_element"), ("0x24", "0x04", "bootup_element"), ("0x28", "0x04", "screenshot_manager_element"), ("0x2C", "0x04", "client_work_element"),
        ("0x30", "0x04", "widget_element"), ("0x34", "0x04", "map_layout_element"), ("0x38", "0x0C", "chara_element_map"), ("0x44", "0x04", "lua_debug_log"),
    ]
    actual_fields = [(f.get("offset"), f.get("size"), f.get("name")) for f in registry.get("fields", [])]
    if registry.get("size") != "0x48" or actual_fields != expected_fields:
        errors.append("BCS-S-0491 byte-accounted layout drifted")
    container_field = _field(structs.get("BCS-S-0053", {}), "0x004AC")
    if not container_field or (container_field.get("size"), container_field.get("name"), container_field.get("type")) != ("0x048", "element_registry", "ApplicationMainRaptureElementRegistry"):
        errors.append("RaptureElementContainer registry embedding drifted")

    fixed_pairs = manifest.get("deterministicProducers", [{}])[0].get("pairs")
    expected_pairs = [["0x02", "0xC0000004"], ["0x01", "0xC0000003"], ["0x03", "0xC0000005"], ["0x07", "0xC0000007"], ["0x04", "0xC0000006"], ["0x0C", "0xC000000C"], ["0x0D", "0xC000000D"], ["0x0E", "0xC000000E"], ["0x15", "0xC0000001"], ["0x09", "0xC000001E"], ["0x06", "0xC0000009"]]
    if fixed_pairs != expected_pairs:
        errors.append("fixed initialization selector/id pairs drifted")
    if not any("0xC1000000 + allocator index" in p.get("encodedId", "") for p in manifest.get("deterministicProducers", [])):
        errors.append("upper encoded-id producer range is missing")
    ad0 = next((p for p in manifest.get("deterministicProducers", []) if p.get("producer") == "0x00774AD0"), {})
    if (ad0.get("selector"), ad0.get("encodedId")) != ("0x1A", "unresolved"):
        errors.append("FUN_00774AD0 unresolved encoded-id boundary drifted")
    screenshot = next((r for r in manifest.get("clearRoutes", []) if r.get("selector") == "0x0C"), {})
    if screenshot.get("encodedId") != "0x0000000C":
        errors.append("literal selector-0x0C clear mismatch was normalized away")
    other = manifest.get("otherSelectorProducer", {})
    if (other.get("address"), len(other.get("directCallers", []))) != ("0x00585800", 8) or "does not establish" not in other.get("interfaceVerdict", ""):
        errors.append("FUN_00585800 producer boundary drifted")
    if "0x0D..0x13 and 0x0FE9" not in other.get("upperIdBoundary", "") or len(other.get("classifiedCases", [])) != 11:
        errors.append("FUN_00585800 upper-id classification boundary drifted")
    if manifest.get("evidence", {}).get("referenceCompletion") != "COMPLETE: FindReferences targets=32 references=64":
        errors.append("reference-export completion marker drifted")
    commands = manifest.get("method", {}).get("commands", [])
    if len(commands) != 5 or any("-ScriptPath @('ghidra') -ReadOnly" not in command for command in commands[:4]) or "-Addresses " not in commands[4] or " -Out " not in commands[4]:
        errors.append("read-only evidence reproduction recipe drifted")
    closure = manifest.get("clientWorkClosure", {})
    if (closure.get("class"), closure.get("structBcsId"), closure.get("allocationSize"), closure.get("factoryBcsId"), closure.get("constructorBcsId"), closure.get("cache"), closure.get("completeTeardownBcsId")) != (
        "Application::Main::Element::System::ClientWorkElement", "BCS-S-0080", "0x838", "BCS-Y-2169", "BCS-Y-2052", "interface+0x2C/container+0x4D8", "BCS-Y-2170"
    ):
        errors.append("selector-0x0D ClientWorkElement closure drifted")
    if symbols.get("BCS-Y-2170", {}).get("address") != "0x0055D100":
        errors.append("BCS-Y-2170 ClientWorkElement teardown address drifted")
    storage = structs.get("BCS-S-0079", {})
    for offset, size, name in (("0x014", "0x004", "record_count"), ("0x018", "0x780", "records"), ("0x798", "0x001", "tail_flag")):
        field = _field(storage, offset)
        if not field or (field.get("size"), field.get("name")) != (size, name):
            errors.append(f"BCS-S-0079 ClientWorkStorage field {offset} drifted")
    embedded = _field(structs.get("BCS-S-0080", {}), "0x098")
    if not embedded or (embedded.get("size"), embedded.get("name")) != ("0x7A0", "client_work_storage"):
        errors.append("BCS-S-0080 embedded ClientWorkStorage drifted")
    routes = {item.get("route"): item for item in closure.get("consumers", [])}
    if (routes.get("s2c:0x018D", {}).get("apply"), routes.get("internal maintenance", {}).get("clear")) != ("0x0055CF70", "0x0055D0F0"):
        errors.append("ClientWorkElement consumer routes drifted")
    return errors


def main() -> int:
    errors = validate(_load(REPO / "manifests" / "rapture_selector_0d_clientwork.json"), _load(REPO / "manifests" / "structs.json"), _load(REPO / "manifests" / "symbols.json"))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("RaptureElement registry: 51 invariants passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
