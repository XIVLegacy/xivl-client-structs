"""Structural validator for the xivl-client-structs manifests.

Read-only. Verifies that the three primary catalog files conform to the
shape invariants the rest of the tooling assumes. Goal: catch data
corruption (typos, copy-paste mistakes, schema drift) early -- before a
downstream tool silently does the wrong thing.

Files checked:
  manifests/symbols.json
  manifests/structs.json
  manifests/pcap_opcode_coverage_matrix.json
  manifests/role_refinements.json

Per-file checks live in independent `check_*` functions; each returns a
list of `(severity, location, message)` tuples. Cross-file checks run at
the end against all three loaded datasets.

Severities:
  ERROR    - shape violation; downstream tooling can reasonably break.
  WARNING  - suspicious or non-standard but tolerated in the current
             catalog (e.g. composite addresses, "variable" field sizes).
  INFO     - advisory only; no action required.

CLI:
  python tools/validate_catalog.py
Exit 0 if no ERRORs, 1 if any ERRORs.

Pure stdlib (json, re, pathlib, sys, collections, dataclasses, typing).
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

from verify_murmur2 import murmur2_backward

REPO = pathlib.Path(__file__).resolve().parents[1]
SYMBOLS_PATH = REPO / "manifests" / "symbols.json"
STRUCTS_PATH = REPO / "manifests" / "structs.json"
MATRIX_PATH = REPO / "manifests" / "pcap_opcode_coverage_matrix.json"
ROLE_REFINEMENTS_PATH = REPO / "manifests" / "role_refinements.json"
BATTLE_RESULT_PATH = REPO / "manifests" / "battle_result_field_semantics.json"
LUA_RESOURCE_INVENTORY_PATH = REPO / "manifests" / "preserved_lua_resource_inventory.json"
LUA_RESOURCE_PATH_PATH = REPO / "manifests" / "lua_resource_path_decoding.json"
LUA_CALLBACK_CONTRACT_PATH = REPO / "manifests" / "lua_callback_contract.json"
LUA_API_CONTRACT_PATH = REPO / "manifests" / "lua_api_contract.json"
CAST_CHANT_PRESENTATION_PATH = REPO / "manifests" / "cast_chant_presentation.json"
COMBAT_COMMAND_EMISSION_PATH = REPO / "manifests" / "combat_command_emission.json"
GAM_HASH_NAMES_PATH = REPO / "manifests" / "gam_hash_names.json"

SEVERITIES = ("ERROR", "WARNING", "INFO")


@dataclass(frozen=True)
class Finding:
    severity: str
    location: str
    message: str


BCS_Y_ID_RE = re.compile(r"^BCS-Y-\d{4}$")
BCS_S_ID_RE = re.compile(r"^BCS-S-\d{4}$")
BCS_Y_PREFIX_RE = re.compile(r"^(BCS-Y-\d{4})\b")

ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{8}$")
ADDRESS_PLACEHOLDER = "0x00000000"
# Accept semicolon VA sets (BCS-Y-0428/0432/0472/0475) and range VAs
# (BCS-Y-0500/0502) as non-scalar identities. Other non-scalars warn.
ADDRESS_CANONICAL_NONSCALAR_RES: tuple[re.Pattern[str], ...] = (
    re.compile(r"^0x[0-9a-fA-F]{8}(;0x[0-9a-fA-F]{8})+$"),
    re.compile(r"^0x[0-9a-fA-F]{8}\.\.0x[0-9a-fA-F]{8}$"),
)

OFFSET_HEX_RE = re.compile(r"^0x[0-9a-fA-F]+$")
SIZE_HEX_RE = re.compile(r"^0x[0-9a-fA-F]+$")
SIZE_INT_RE = re.compile(r"^\d+$")

# Accept `n/a` logical records (BCS-S-0029 / BCS-S-0030), `variable` fields
# (BCS-S-0008.payload_b at +0x50), and nested `element+0xNN` fields (BCS-S-0032).
OFFSET_CANONICAL_NONHEX_RES: tuple[re.Pattern[str], ...] = (
    re.compile(r"^n/a$"),
    re.compile(r"^variable$"),
    re.compile(r"^element\+0x[0-9a-fA-F]+$"),
)

# Logical sentinels: BCS-S-0005/0008/0009, BCS-S-0010/0011/0012, BCS-S-0029, BCS-S-0041/0043/0044.
# Lua labels use BCS-S-0030. Annotated or bounded sizes use BCS-S-0014,
# BCS-S-0032/0033/0034, BCS-S-0035, BCS-S-0036, BCS-S-0037, BCS-S-0038.payload, BCS-S-0041, BCS-S-0046.
SIZE_CANONICAL_NONHEX_RES: tuple[re.Pattern[str], ...] = (
    re.compile(r"^variable$"),
    re.compile(r"^varies$"),
    re.compile(r"^unknown$"),
    re.compile(r"^n/a$"),
    re.compile(r"^pointer/string$"),
    re.compile(r"^Lua\s+(?:table\s+entry|reference|string|closure|"
               r"call\s+expression)$"),
    # Require a separator after the hex token so malformed values like 0x12g do not match.
    re.compile(r"^0x[0-9a-fA-F]+[\s(/].+$"),
    re.compile(r"^variable\s*\(.+\)$"),
    re.compile(r"^(?:at\s+least|approximately|minimum|maximum)\s+"
               r"0x[0-9a-fA-F]+\b.*$"),
)

OPCODE_RE = re.compile(r"^0x[0-9a-f]{4}$")


def check_battle_result_fields(doc: dict[str, Any], structs_doc: dict[str, Any]) -> list[Finding]:
    """Lock the reviewed 0x0139..0x013C normalized queue contract."""
    findings: list[Finding] = []
    route = doc.get("route", {})
    expected_wrappers = {
        "0x0139": "FUN_0058C880",
        "0x013A": "FUN_0058C930",
        "0x013B": "FUN_0058C990",
        "0x013C": "FUN_0058C7D0",
    }
    if route.get("wrappers") != expected_wrappers:
        findings.append(Finding("ERROR", "battle-result.route", "wrapper map drifted"))

    queue = doc.get("queueEntry", {})
    dimensions = (
        queue.get("size"), queue.get("rowCapacity"), queue.get("rowOffset"), queue.get("rowStride")
    )
    if dimensions != (416, 18, 56, 20):
        findings.append(Finding("ERROR", "battle-result.queue", f"dimensions are {dimensions!r}"))

    variants = {
        row.get("opcodeHex"): (
            row.get("rowCapacity"), row.get("subpacketSize"), row.get("observedOccurrences"),
            row.get("captureCount"), row.get("retainedSamples"), row.get("status"),
        )
        for row in doc.get("wireVariants", [])
    }
    expected_variants = {
        "0x0139": (1, 88, 438, 21, 50, None),
        "0x013A": (10, 216, 66, 6, 14, None),
        "0x013B": (18, 328, 0, 0, 0, "static_shape_only_no_capture"),
        "0x013C": (0, 72, 27, 6, 18, None),
    }
    if variants != expected_variants:
        findings.append(Finding("ERROR", "battle-result.variants", "capture/static tuples drifted"))

    structs = {row.get("id"): row for row in structs_doc.get("structs", [])}
    entry = structs.get("BCS-S-0031", {})
    target = structs.get("BCS-S-0051", {})
    entry_fields = {field.get("offset"): (field.get("size"), field.get("name"), field.get("type")) for field in entry.get("fields", [])}
    if entry.get("size") != "0x1A0" or entry_fields.get("0x38") != ("0x168", "targetRows", "BattleResultTargetRow[18]"):
        findings.append(Finding("ERROR", "structs.json:BCS-S-0031", "18-row queue layout drifted"))
    target_fields = {field.get("offset"): field.get("name") for field in target.get("fields", [])}
    expected_target_fields = {
        "0x00": "targetActorId", "0x04": "numericValue", "0x08": "effectId",
        "0x0C": "worldMasterTextId", "0x0E": "textParam",
        "0x0F": "rowOrdinalOrFilter", "0x10": "reserved",
    }
    if target.get("size") != "0x14" or target_fields != expected_target_fields:
        findings.append(Finding("ERROR", "structs.json:BCS-S-0051", "target-row layout drifted"))
    return findings


def check_cast_chant_presentation(doc: dict[str, Any]) -> list[Finding]:
    """Keep the four cast/chant presentation surfaces distinct."""
    findings: list[Finding] = []
    if not isinstance(doc, dict):
        return [Finding("ERROR", "cast-chant", "manifest must be an object")]
    if (doc.get("version"), doc.get("generated"), doc.get("gameVersion"), doc.get("status")) != (
        1, "2026-08-14", "1.23b", "bounded_static_and_capture_closure"
    ):
        findings.append(Finding("ERROR", "cast-chant.metadata", "snapshot metadata drifted"))

    expected_snapshots = {
        "captures": {"repository": "XIVLegacy/xivl-captures", "commit": "48c7841c947ca07aecccd5fed3db6167b3efbac4"},
        "clientData": {"repository": "XIVLegacy/xivl-client-data", "commit": "566c5dc3ee5e1f036008e6758e8b7bbcf9663ea6"},
        "clientScripts": {"repository": "XIVLegacy/xivl-client-scripts", "commit": "6d0bc47dcf699408e0f3a004057bce9d62138b9b"},
        "decomp": {"repository": "XIVLegacy/xivl-decomp", "commit": "3f4bcb34a21dd3c3611f3eeafb11743f134d7c64"},
    }
    if doc.get("sourceSnapshots") != expected_snapshots:
        findings.append(Finding("ERROR", "cast-chant.sourceSnapshots", "source snapshot drifted"))

    gauge = doc.get("activeCastGauge", {})
    if not isinstance(gauge, dict):
        return findings + [Finding("ERROR", "cast-chant.activeCastGauge", "must be an object")]
    carrier = gauge.get("wireCarrier", {})
    if not isinstance(carrier, dict):
        return findings + [Finding("ERROR", "cast-chant.carrier", "must be an object")]
    if (carrier.get("opcodeHex"), carrier.get("subpacketSize"),
            carrier.get("observedPackets"), carrier.get("observedScenarios"),
            carrier.get("applicationPayloadSize")) != ("0x0137", 168, 1992, 36, 136):
        findings.append(Finding("ERROR", "cast-chant.carrier", "0x0137 capture tuple drifted"))
    expected_framing = ("168-byte subpacket = 16-byte outer subevent framing + 152-byte game message; "
                        "the game message is a 16-byte prefix plus the 136-byte application payload.")
    if carrier.get("framing") != expected_framing:
        findings.append(Finding("ERROR", "cast-chant.framing", "0x0137 framing drifted"))

    property_rows = gauge.get("properties", [])
    if not isinstance(property_rows, list):
        return findings + [Finding("ERROR", "cast-chant.properties", "must be an array")]
    properties = {
        row.get("name"): (
            row.get("idHex"), row.get("valueType"), row.get("observedRecords"),
            row.get("observedCaptures"), row.get("observedValuesHex")
        )
        for row in property_rows if isinstance(row, dict)
    }
    expected_properties = {
        "playerWork.castCommandClient": ("0xf683a451", "u32", 3, 1,
                                          ["d26a0000", "00000000"]),
        "playerWork.castEndClient": ("0x59c40d5d", "u32", 2, 1,
                                      ["dc1be150", "c21de150"]),
        "charaWork.battleTemp.castGauge_speed[0]": ("0x573fe04c", "float32", 11, 8,
                                                     ["0000803f"]),
        "charaWork.battleTemp.castGauge_speed[1]": ("0xbb9cc775", "float32", 11, 8,
                                                     ["0000803e"]),
    }
    if properties != expected_properties:
        findings.append(Finding("ERROR", "cast-chant.properties", "cast property contract drifted"))

    expected_route = [
        "FUN_004D8860", "FUN_00575070", "FUN_00759ED0", "FUN_0089E550",
        "FUN_00775A30", "FUN_00775180", "property-entry indirect call at 0x00775652",
        "FUN_00774220", "FUN_00773F10", "FUN_00CC7A90 _onUpdateWork",
    ]
    if gauge.get("propertyRoute") != expected_route:
        findings.append(Finding("ERROR", "cast-chant.propertyRoute", "native route drifted"))

    cross_check = gauge.get("captureCrossCheck", {})
    if not isinstance(cross_check, dict) or (
        cross_check.get("scenario"), cross_check.get("target"),
        cross_check.get("observedCommandId")
    ) != ("party_battle_leve.pcapng", "playerWork/castState", 27346):
        findings.append(Finding("ERROR", "cast-chant.cross-check", "Cure same-id cross-check drifted"))
    duration = gauge.get("uiDuration", {})
    expected_formula = ("remaining = player.getCastEndTime() - worldMaster._getServerTime(); "
                        "if remaining <= 0 then remaining = 1; progressRate = 1 / remaining")
    if not isinstance(duration, dict) or (
        duration.get("formula"), duration.get("widget"), duration.get("storyboard"),
        duration.get("units")
    ) != (expected_formula, "ProgressBar_MagicCast_Main", "UILuaCommands.StartCastGauge", "unresolved"):
        findings.append(Finding("ERROR", "cast-chant.uiDuration", "gauge formula drifted"))
    sheet = doc.get("localCommandCastTime", {})
    if not isinstance(sheet, dict):
        return findings + [Finding("ERROR", "cast-chant.sheet", "must be an object")]
    sheet_example = sheet.get("example", {})
    if not isinstance(sheet_example, dict):
        return findings + [Finding("ERROR", "cast-chant.sheet.example", "must be an object")]
    if (sheet.get("sheet"), sheet.get("column"), sheet.get("fieldName"),
            sheet.get("units"), sheet_example.get("rawCastTime")) != (
        "gameCommandBasic.csv", 76, "cast_time", "unresolved", 2
    ):
        findings.append(Finding("ERROR", "cast-chant.sheet", "raw cast-time contract drifted"))

    cast_vfx = doc.get("castReadyVfx", {})
    if not isinstance(cast_vfx, dict):
        return findings + [Finding("ERROR", "cast-chant.vfx", "must be an object")]
    vfx = cast_vfx.get("mapping", {})
    if not isinstance(vfx, dict):
        return findings + [Finding("ERROR", "cast-chant.vfx.mapping", "must be an object")]
    if (vfx.get("effectCategoryHighByte"), vfx.get("visualResultClass"), vfx.get("name")) != (
        "0x6f", 8, "CastOrReadyPreAction"
    ):
        findings.append(Finding("ERROR", "cast-chant.vfx", "cast-ready selector drifted"))

    chant = doc.get("chantStatusBoundary", {})
    if not isinstance(chant, dict):
        return findings + [Finding("ERROR", "cast-chant.chant", "must be an object")]
    if (chant.get("ingress"), chant.get("reader"), chant.get("bits")) != (
        "s2c 0x0179 SetActorStatusAll -> FUN_00707D60",
        "BCS-Y-0438 SubStat_getChantImpl_FUN_006F9EC0",
        "8..15; kind 1 reads bits 12..15 and kind 2 reads bits 8..11",
    ):
        findings.append(Finding("ERROR", "cast-chant.chant", "SubStat Chant boundary drifted"))
    rejected = doc.get("rejectedImports", [])
    unresolved = doc.get("unresolved", [])
    if not isinstance(rejected, list) or not isinstance(unresolved, list):
        findings.append(Finding("ERROR", "cast-chant.boundaries", "boundary sets must be arrays"))
    elif len(rejected) != 6 or len(unresolved) != 6:
        findings.append(Finding("ERROR", "cast-chant.boundaries",
                                "rejected-import or unresolved boundary set drifted"))
    source_refs = doc.get("sourceRefs", [])
    required_refs = {
        "manifests/gam_hash_names.json",
        "manifests/data_dependency_catalog.json#s2c_0x0137",
        "manifests/receiver_opcode_map_inbound.json",
        "manifests/selector_mapping_findings.json",
        "manifests/status_effect_findings.json",
        "xivl-captures:derived/property_targets.json",
        "xivl-client-data:docs/command-battle-params.md",
        "xivl-client-scripts:manifests/scripts.json",
        "xivl-client-scripts:lua/scripts/widget/actiongaugewidget.lua",
        "xivl-decomp:asm/ffxivgame/00375180_FUN_00775180.s",
        "xivl-decomp:asm/ffxivgame/00373f10_FUN_00773f10.s",
    }
    if not isinstance(source_refs, list) or not all(isinstance(ref, str) for ref in source_refs):
        findings.append(Finding("ERROR", "cast-chant.sourceRefs", "sourceRefs must be strings"))
    elif not required_refs.issubset(source_refs):
        findings.append(Finding("ERROR", "cast-chant.sourceRefs", "required evidence citation missing"))
    elif any("agent-islands" in ref or "agent-config" in ref for ref in source_refs):
        findings.append(Finding("ERROR", "cast-chant.sourceRefs", "private island citation found"))
    return findings


def check_lua_resource_inventory(doc: dict[str, Any]) -> list[Finding]:
    """Lock the reviewed preserved-script inventory and evidence boundaries."""
    findings: list[Finding] = []
    corpus = doc.get("canonicalCorpus", {})
    expected_counts = {
        "scriptCount": 2671,
        "totalCanonicalBytes": 13971401,
        "totalLineCount": 645709,
        "sidecarCount": 2671,
        "scriptsWithClassNames": 2650,
        "scriptsWithoutClassNames": 21,
        "scriptsWithMethods": 1492,
        "methodAssignments": 13782,
        "scriptsWithRequires": 2585,
        "requireReferences": 2602,
        "napiApiCount": 433,
        "napiCallsites": 17049,
    }
    for key, expected in expected_counts.items():
        if corpus.get(key) != expected:
            findings.append(Finding("ERROR", f"lua-resource-inventory.{key}",
                                    f"expected {expected}, got {corpus.get(key)!r}"))
    expected_top_level = {
        "root": 3, "area": 60, "chara": 1052, "command": 160,
        "commanddebugger": 5, "debug": 5, "director": 299, "gamedata": 6,
        "group": 26, "item": 26, "judge": 23, "quest": 629, "status": 158,
        "system": 10, "widget": 202, "world": 7,
    }
    if corpus.get("topLevelCounts") != expected_top_level:
        findings.append(Finding("ERROR", "lua-resource-inventory.topLevelCounts",
                                "top-level script counts drifted"))
    expected_hashes = {
        "scriptManifest": "86798306F71336EE494F12D395DB3B8EA571A21224FBD99E2EF87ECD18C61300",
        "registry": "957060C79FCCE34F90B1840251C889EF8EE354F8380000518B1FEB96F65DD78F",
        "napiIndex": "9E63DDCDA1C3E25DBDEA65082023C4CB23FE950FD53CFC7C57D5B76DCA1234EF",
    }
    for key, expected in expected_hashes.items():
        if corpus.get(key, {}).get("sha256") != expected:
            findings.append(Finding("ERROR", f"lua-resource-inventory.{key}",
                                    "source snapshot hash drifted"))
    resources = {row.get("kind"): row for row in doc.get("otherScriptLikeResources", [])}
    core = resources.get("embedded core Lua bytecode", {})
    if core.get("logicalCount") != 7 or core.get("blobAnchorCount") != 14:
        findings.append(Finding("ERROR", "lua-resource-inventory.embedded-core",
                                "embedded core inventory must remain 7 logical resources / 14 anchors"))
    if resources.get("runtime .lcb support", {}).get("logicalCount") != 0:
        findings.append(Finding("ERROR", "lua-resource-inventory.lcb",
                                "no captured .lcb payload may be claimed"))
    bootstrap = resources.get("embedded LGE bootstrap Lua text", {})
    if (bootstrap.get("logicalCount"), bootstrap.get("address"), bootstrap.get("bytes"),
            bootstrap.get("lineCount")) != (1, "0x0110E680", 327, 14):
        findings.append(Finding("ERROR", "lua-resource-inventory.bootstrap",
                                "embedded bootstrap metadata drifted"))
    prog = resources.get("embedded OnProgFunc chunks", {})
    if prog.get("logicalCount") != 2 or "distinct from" not in prog.get("status", ""):
        findings.append(Finding("ERROR", "lua-resource-inventory.on-prog-func",
                                "OnProgFunc .rdata chunks must remain distinct from core .data anchors"))
    return findings


def check_lua_resource_paths(doc: dict[str, Any]) -> list[Finding]:
    """Keep filename, logical require, and numeric DAT path layers separate."""
    findings: list[Finding] = []
    layer_rows = doc.get("layers", [])
    layers = {row.get("name"): row for row in layer_rows}
    expected_layer_names = {
        "LPB payload wrapper", "physical script filename",
        "logical Lua require path", "numeric resource-id DAT path",
    }
    if len(layer_rows) != 4 or set(layers) != expected_layer_names:
        findings.append(Finding("ERROR", "lua-resource-paths.layers",
                                "expected exactly four unique path layers"))
    if doc.get("sourceSnapshots") != {
        "xivl-client-scripts": "6d0bc47dcf699408e0f3a004057bce9d62138b9b",
        "xivl-decomp": "3f4bcb34a21dd3c3611f3eeafb11743f134d7c64",
    }:
        findings.append(Finding("ERROR", "lua-resource-paths.sources", "source commit pins drifted"))
    wrapper = layers.get("LPB payload wrapper", {})
    if wrapper.get("observedCounts") != {"rlu_0b": 1, "rle_0c": 2670}:
        findings.append(Finding("ERROR", "lua-resource-paths.wrapper", "LPB wrapper counts drifted"))
    if wrapper.get("algorithm", {}).get("decodedMagic") != "1B 4C 75 61 51" or wrapper.get("reversible") is not True:
        findings.append(Finding("ERROR", "lua-resource-paths.wrapper", "LPB byte-transform contract drifted"))
    filename = layers.get("physical script filename", {})
    algorithm = filename.get("algorithm", {})
    if algorithm.get("mappedAlphabet") != "9876543210zyxwvutsrqponmlkjihgfedcba":
        findings.append(Finding("ERROR", "lua-resource-paths.filename", "filename substitution table drifted"))
    if filename.get("retailFunction") is not None or filename.get("reversibleForCanonicalLowercasePaths") is not True:
        findings.append(Finding("ERROR", "lua-resource-paths.filename", "filename cipher boundary drifted"))
    expected_vectors = {
        ("zonemoveprogtest", "kvw5xvo5usv3q5rq"),
        ("man0g0", "x9wj3j"),
        ("chara/player/playerbaseclass.lua", "729s9/uy9l5s/uy9l5s89r57y9rr.lua"),
    }
    vectors = {(row.get("decoded"), row.get("ciphered")) for row in filename.get("knownVectors", [])}
    if vectors != expected_vectors:
        findings.append(Finding("ERROR", "lua-resource-paths.filename", "known cipher vectors drifted"))
    require = layers.get("logical Lua require path", {})
    if require.get("entry", {}).get("function") != "FUN_00D08A10" or require.get("resolver", {}).get("function") != "FUN_00D0CFB0":
        findings.append(Finding("ERROR", "lua-resource-paths.require", "Lua require resolver chain drifted"))
    dat = layers.get("numeric resource-id DAT path", {})
    if (dat.get("function"), dat.get("format"), dat.get("hash")) != (
            "FUN_0044B3A0", "\\data\\%02X\\%02X\\%02X\\%02X.DAT", None):
        findings.append(Finding("ERROR", "lua-resource-paths.dat", "numeric DAT path contract drifted"))
    if dat.get("example") != {"resourceId": "0x12345678", "path": "\\data\\12\\34\\56\\78.DAT"}:
        findings.append(Finding("ERROR", "lua-resource-paths.dat", "numeric DAT path example drifted"))
    required_refs = {
        "tools/decode_lpb.py",
        "xivl-client-scripts:tools/_corpus.py",
        "xivl-decomp:asm/ffxivgame/0090cfb0_FUN_00d0cfb0.s",
        "xivl-decomp:asm/ffxivgame/0004b3a0_FUN_0044b3a0.s",
        "xivl-decomp:docs/resource/sqpack.md",
    }
    if not required_refs.issubset(set(doc.get("sourceRefs", []))):
        findings.append(Finding("ERROR", "lua-resource-paths.sources", "required source references missing"))
    if len(doc.get("rejectedConflations", [])) != 5:
        findings.append(Finding("ERROR", "lua-resource-paths.boundaries", "rejected-conflation fence drifted"))
    return findings


def check_lua_callback_contract(doc: dict[str, Any]) -> list[Finding]:
    """Validate the frozen, script-only callback contract and its claim fence."""
    findings: list[Finding] = []
    if (doc.get("version"), doc.get("generated"), doc.get("gameVersion"), doc.get("extraction")) != (
            1, "2026-08-14", "1.23b", "2012.09.19.0001"):
        findings.append(Finding("ERROR", "lua-callback-contract.metadata", "callback snapshot metadata drifted"))
    expected_totals = {
        "corpusScripts": 2671,
        "contractScriptCount": 88,
        "callbackScriptCount": 73,
        "callbackAssignments": 209,
        "distinctCallbacks": 81,
        "parsedParameterLists": 209,
        "fixedCallbacks": 185,
        "variadicCallbacks": 24,
        "scriptEventHandlerScripts": 15,
        "scriptEventHandlerAssignments": 43,
    }
    if doc.get("totals") != expected_totals:
        findings.append(Finding("ERROR", "lua-callback-contract.totals", "callback totals drifted"))
    if doc.get("scope") != ("Decoded script-declared client callback and script-event contracts. "
                            "Parameter names are decompiler slots, not semantic types. No native registrar, "
                            "xref, packet, or server behavior is claimed."):
        findings.append(Finding("ERROR", "lua-callback-contract.scope", "callback claim fence drifted"))
    rendered_scripts = json.dumps(doc.get("scripts", {}), sort_keys=True, separators=(",", ":"),
                                  ensure_ascii=True).encode("utf-8")
    actual_contract_sha256 = hashlib.sha256(rendered_scripts).hexdigest().upper()
    if (doc.get("contractSha256"), actual_contract_sha256) != (
            "6BB26B1490FF0BA2F7410639C2FD015D07ACD4DF546BA5ABA3AEF03263BDF663",
            "6BB26B1490FF0BA2F7410639C2FD015D07ACD4DF546BA5ABA3AEF03263BDF663"):
        findings.append(Finding("ERROR", "lua-callback-contract.digest", "callback contract table drifted"))
    source = doc.get("sourceSnapshot", {})
    if source != {
            "repository": "XIVLegacy/xivl-client-scripts",
            "commit": "6d0bc47dcf699408e0f3a004057bce9d62138b9b",
            "registry": {
                "path": "lua/registry.json",
                "sha256": "957060C79FCCE34F90B1840251C889EF8EE354F8380000518B1FEB96F65DD78F",
            },
            "scriptManifest": {
                "path": "manifests/scripts.json",
                "sha256": "86798306F71336EE494F12D395DB3B8EA571A21224FBD99E2EF87ECD18C61300",
            },
            "localBodies": "lua/scripts/**/*.lua; required to regenerate, gitignored, and not copied",
    }:
        findings.append(Finding("ERROR", "lua-callback-contract.sources", "callback source snapshot drifted"))
    relationship = doc.get("relationshipToCompleteContract", {})
    if relationship != {
            "status": "narrower_earlier_pass",
            "supersededBy": "manifests/lua_api_contract.json",
            "retainedPurpose": "Compact callback-only view with per-script positional shapes.",
    }:
        findings.append(Finding("ERROR", "lua-callback-contract.relationship",
                                "complete-contract relationship drifted"))
    boundary = doc.get("nativeTraceBoundary", {})
    if boundary != {
            "status": "bounded_sample_succeeded_complete_attribution_blocked",
            "functionalEquivalents": ["DumpStrings.java", "FindCallers.java", "exported asm corpus"],
            "missingCapability": "A reproducible string-name -> string-address -> all data/code references -> registrar/implementation mapping for every callback name.",
            "effect": "The bounded native sample is recorded in lua_api_contract.json. This callback-only manifest does not infer native callback targets.",
    }:
        findings.append(Finding("ERROR", "lua-callback-contract.boundary", "native trace effect drifted"))
    scripts = doc.get("scripts", {})
    if not isinstance(scripts, dict):
        findings.append(Finding("ERROR", "lua-callback-contract.scripts", "scripts must be an object"))
        return findings
    callback_names: set[str] = set()
    callback_count = event_count = fixed_count = variadic_count = 0
    for decoded, script in scripts.items():
        if not isinstance(script, dict):
            findings.append(Finding("ERROR", f"lua-callback-contract.{decoded}", "script row must be an object"))
            continue
        if (not decoded or not script.get("ciphered") or not script.get("class")
                or not isinstance(script.get("lineCount"), int) or script.get("lineCount", 0) < 1
                or not re.fullmatch(r"[0-9A-F]{64}", script.get("scriptSha256", ""))):
            findings.append(Finding("ERROR", f"lua-callback-contract.{decoded}", "script identity is incomplete"))
        callbacks = script.get("callbacks", [])
        event_handlers = script.get("scriptEventHandlers", [])
        if not isinstance(callbacks, list) or not isinstance(event_handlers, list):
            findings.append(Finding("ERROR", f"lua-callback-contract.{decoded}",
                                    "callback collections must be arrays"))
            continue
        for row in callbacks:
            if not isinstance(row, dict):
                findings.append(Finding("ERROR", f"lua-callback-contract.{decoded}",
                                        "callback row must be an object"))
                continue
            callback_count += 1
            callback_names.add(row.get("name", ""))
            fixed_count += not row.get("variadic", False)
            variadic_count += bool(row.get("variadic", False))
            params = row.get("params")
            if (not isinstance(params, list) or not all(isinstance(param, str) and param for param in params)
                    or not row.get("name", "").startswith("_on")
                    or row.get("arity") != sum(param != "..." for param in params)
                    or row.get("variadic") != ("..." in params)
                    or not isinstance(row.get("functionLine"), int)
                    or not isinstance(row.get("sourceLine"), int)
                    or row.get("functionLine", 0) < 1
                    or row.get("sourceLine", 0) <= row.get("functionLine", 0)):
                findings.append(Finding("ERROR", f"lua-callback-contract.{decoded}", "callback shape drifted"))
        for row in event_handlers:
            if not isinstance(row, dict):
                findings.append(Finding("ERROR", f"lua-callback-contract.{decoded}",
                                        "script event row must be an object"))
                continue
            event_count += 1
            params = row.get("params")
            if (row.get("name") not in {
                    "onJobQuestCompleteFirst", "onJobQuestCompleteSecond", "onJobQuestCompleteThird"}
                    or not isinstance(params, list)
                    or row.get("arity") != sum(param != "..." for param in params)
                    or row.get("variadic") != ("..." in params)
                    or not isinstance(row.get("functionLine"), int)
                    or not isinstance(row.get("sourceLine"), int)
                    or row.get("sourceLine", 0) <= row.get("functionLine", 0)):
                findings.append(Finding("ERROR", f"lua-callback-contract.{decoded}", "unexpected script event handler"))
    if (len(scripts), callback_count, len(callback_names), fixed_count, variadic_count, event_count) != (88, 209, 81, 185, 24, 43):
        findings.append(Finding("ERROR", "lua-callback-contract.rows", "row-derived totals drifted"))
    player = scripts.get("chara/player/playerbaseclass", {})
    command = next((row for row in player.get("callbacks", []) if row.get("name") == "_onCommandEvent"), {})
    if (command.get("arity"), command.get("variadic"), command.get("functionLine"), command.get("sourceLine")) != (3, True, 1820, 1881):
        findings.append(Finding("ERROR", "lua-callback-contract.playerbase", "_onCommandEvent contract drifted"))
    if "FUN_" in json.dumps(doc):
        findings.append(Finding("ERROR", "lua-callback-contract.scope", "script-only contract must not claim native functions"))
    if doc.get("sourceRefs") != [
            "xivl-client-scripts:lua/registry.json",
            "xivl-client-scripts:lua/scripts/**/*.lua",
            "xivl-client-scripts:manifests/scripts.json",
            "manifests/lua_api_contract.json"]:
        findings.append(Finding("ERROR", "lua-callback-contract.refs", "callback provenance references drifted"))
    return findings


def check_combat_command_emission(doc: dict[str, Any]) -> list[Finding]:
    """Validate the resolved EventStart owner-ID relationship and boundaries."""
    findings: list[Finding] = []
    relationship = doc.get("commandIdRelationship", {})
    if relationship.get("status") != "resolved_owner_static_actor_identity":
        findings.append(Finding("ERROR", "combat-command.owner-id", "owner-ID relationship is not resolved"))
        return findings
    derivation = relationship.get("derivation", {})
    if derivation != {
            "direction": "serverbound",
            "service": "Map (client decomp attribution)",
            "opcodeHex": "0x012d",
            "framing": "216-byte wire subpacket -> 200-byte retained body -> 16-byte game-message prefix -> 184-byte application payload",
            "ownerOffset": "retained body +0x14 = application payload +0x04",
            "ownerDecode": "little-endian u32",
            "staticActorTest": "(ownerActorId & 0xffff0000) == 0xa0f00000",
            "rowDecode": "ownerActorId & 0x0000ffff",
    }:
        findings.append(Finding("ERROR", "combat-command.derivation", "owner-ID byte derivation drifted"))
    distribution = relationship.get("distribution", {})
    owner_rows = distribution.get("ownerIds", [])
    block_rows = distribution.get("upper16Blocks", [])
    if distribution.get("totalOccurrences") != 126:
        findings.append(Finding("ERROR", "combat-command.distribution", "occurrence total drifted"))
    if (sum(row.get("count", 0) for row in owner_rows) != 126
            or len(owner_rows) != 41
            or sum(row.get("count", 0) for row in block_rows) != 126
            or len(block_rows) != 9):
        findings.append(Finding("ERROR", "combat-command.distribution", "owner-ID distribution does not reconcile"))
    if {row.get("value"): row.get("count") for row in block_rows} != {
            "0x44b0": 2, "0x44b8": 1, "0x44c0": 1, "0x44d8": 9,
            "0x4510": 3, "0x4560": 6, "0x4670": 2, "0x47a0": 2,
            "0xa0f0": 100,
    }:
        findings.append(Finding("ERROR", "combat-command.blocks", "owner upper-16 block distribution drifted"))
    expected_owner_ids = {
        "0x44b00005": 2, "0x44b8000a": 1, "0x44c00012": 1,
        "0x44d80009": 1, "0x44d8000a": 1, "0x44d80026": 2,
        "0x44d8002d": 1, "0x44d8002f": 4, "0x4510000c": 1,
        "0x45100d5b": 2, "0x45600029": 2, "0x45606e22": 2,
        "0x45606e23": 2, "0x46700082": 2, "0x47a00007": 1,
        "0x47a0000c": 1, "0xa0f02ee5": 1, "0xa0f02ee9": 7,
        "0xa0f02eea": 2, "0xa0f02eee": 2, "0xa0f02eef": 3,
        "0xa0f02ef1": 1, "0xa0f05209": 12, "0xa0f0520a": 12,
        "0xa0f055f1": 1, "0xa0f055f3": 1, "0xa0f055f7": 2,
        "0xa0f05e26": 2, "0xa0f05e8b": 1, "0xa0f05e93": 2,
        "0xa0f05e9c": 4, "0xa0f05eed": 3, "0xa0f069dc": 3,
        "0xa0f06a2e": 2, "0xa0f06a36": 12, "0xa0f06a37": 8,
        "0xa0f06a39": 3, "0xa0f06a3e": 3, "0xa0f06a7c": 5,
        "0xa0f06a80": 6, "0xa0f06ad2": 2,
    }
    if {row.get("value"): row.get("count") for row in owner_rows} != expected_owner_ids:
        findings.append(Finding("ERROR", "combat-command.owner-ids", "full owner-ID distribution drifted"))
    retained = distribution.get("retainedSampleCap", {})
    if (retained.get("sampleCount") != 60
            or sum(row.get("count", 0) for row in retained.get("ownerIds", [])) != 60):
        findings.append(Finding("ERROR", "combat-command.retained", "retained sample cap drifted"))
    joins = relationship.get("joins", {})
    expected_join_counts = {
        "eligibleStaticActorSamples": 100,
        "eligibleUniqueOwnerIds": 25,
        "staticActorHits": 100,
        "staticActorMisses": 0,
        "commandPathHits": 100,
        "nonCommandStaticActorHits": 0,
        "gameCommandHits": 88,
        "gameCommandMisses": 12,
    }
    if any(joins.get(key) != value for key, value in expected_join_counts.items()):
        findings.append(Finding("ERROR", "combat-command.joins", "owner-ID join totals drifted"))
    join_rows = joins.get("rows", [])
    if (len(join_rows) != 25
            or sum(row.get("count", 0) for row in join_rows) != 100
            or sum(row.get("count", 0) for row in join_rows if row.get("gameCommandHit")) != 88
            or any(not str(row.get("staticActorClassPath", "")).startswith("/Command/") for row in join_rows)):
        findings.append(Finding("ERROR", "combat-command.join-rows", "owner-ID join rows do not reconcile"))
    expected_join_rows = {
        (owner, owner & 0xFFFF, count, path, game_hit)
        for owner, count, path, game_hit in (
            (0xA0F02EE5, 1, "/Command/Game/BonusPointCommand", True),
            (0xA0F02EE9, 7, "/Command/EquipCommand", True),
            (0xA0F02EEA, 2, "/Command/EquipAbilityCommand", True),
            (0xA0F02EEE, 2, "/Command/Game/Prog/ChocoboRideCommand", True),
            (0xA0F02EEF, 3, "/Command/Game/Prog/ChocoboRideCommand", True),
            (0xA0F02EF1, 1, "/Command/ChangeJobCommand", True),
            (0xA0F05209, 12, "/Command/Game/ActivateCommand", True),
            (0xA0F0520A, 12, "/Command/Game/ActivateCommand", True),
            (0xA0F055F1, 1, "/Command/Game/CraftCommand", True),
            (0xA0F055F3, 1, "/Command/Game/DummyCommand", True),
            (0xA0F055F7, 2, "/Command/Game/DummyCommand", True),
            (0xA0F05E26, 2, "/Command/System/EmoteStandardCommand", False),
            (0xA0F05E8B, 1, "/Command/System/PartyInviteCommand", False),
            (0xA0F05E93, 2, "/Command/System/RequestQuestJournalCommand", False),
            (0xA0F05E9C, 4, "/Command/System/TeleportCommand", False),
            (0xA0F05EED, 3, "/Command/System/PlaceDrivenCommand", False),
            (0xA0F069DC, 3, "/Command/Game/Ability/Ability", True),
            (0xA0F06A2E, 2, "/Command/Game/Ability/Ability", True),
            (0xA0F06A36, 12, "/Command/Game/WeaponSkill/AttackWeaponSkill", True),
            (0xA0F06A37, 8, "/Command/Game/WeaponSkill/AttackWeaponSkill", True),
            (0xA0F06A39, 3, "/Command/Game/WeaponSkill/AttackWeaponSkill", True),
            (0xA0F06A3E, 3, "/Command/Game/WeaponSkill/AttackWeaponSkill", True),
            (0xA0F06A7C, 5, "/Command/Game/Ability/Ability", True),
            (0xA0F06A80, 6, "/Command/Game/Ability/Ability", True),
            (0xA0F06AD2, 2, "/Command/Game/Magic/CureMagic", True),
        )
    }
    actual_join_rows = {
        (int(row.get("ownerActorId", "0"), 16), row.get("low16RowId"),
         row.get("count"), row.get("staticActorClassPath"), row.get("gameCommandHit"))
        for row in join_rows
    }
    if actual_join_rows != expected_join_rows:
        findings.append(Finding("ERROR", "combat-command.join-values", "owner-ID join values drifted"))
    scenarios = relationship.get("scenarioComparison", {})
    combat = scenarios.get("combatExamples", {})
    noncombat = scenarios.get("noncombatExamples", {})
    if (combat.get("sampleCount"), combat.get("staticActorBlockCount"),
            combat.get("outsideStaticActorBlockCount")) != (64, 61, 3):
        findings.append(Finding("ERROR", "combat-command.combat", "combat example distribution drifted"))
    if (noncombat.get("sampleCount"), noncombat.get("staticActorBlockCount"),
            noncombat.get("outsideStaticActorBlockCount")) != (62, 39, 23):
        findings.append(Finding("ERROR", "combat-command.noncombat", "noncombat example distribution drifted"))
    if set(combat.get("captures", [])) != {
            "combat_autoattack.pcapng", "combat_skills.pcapng", "party_battle_leve.pcapng"}:
        findings.append(Finding("ERROR", "combat-command.combat", "combat capture split drifted"))
    event_rows = {
        row.get("eventName"): (
            row.get("count"), row.get("staticActorHits"), row.get("gameCommandHits"),
            row.get("outsideStaticActorBlock"))
        for row in relationship.get("eventNameComparison", [])
    }
    if event_rows != {
            "caution": (3, 0, 0, 3),
            "commandContent": (4, 4, 0, 0),
            "commandDefault": (44, 44, 44, 0),
            "commandForced": (28, 28, 28, 0),
            "commandJudgeMode": (5, 5, 5, 0),
            "commandRequest": (19, 19, 11, 0),
            "exit": (3, 0, 0, 3),
            "noticeEvent": (2, 0, 0, 2),
            "regionChange": (1, 0, 0, 1),
            "talkDefault": (17, 0, 0, 17),
    }:
        findings.append(Finding("ERROR", "combat-command.events", "event-name owner partition drifted"))
    mask = relationship.get("maskWidth", {})
    if (mask.get("verdict"), mask.get("observedMaximumRowId"),
            mask.get("commandStaticActorMaximumRowId"), mask.get("gameCommandMaximumRowId"),
            mask.get("observedOverflowCount"), mask.get("commandStaticActorOverflowCount"),
            mask.get("gameCommandOverflowCount")) != (
            "supports_16_bit_command_static_actor_row_id", 27346, 30101, 30101, 0, 0, 0):
        findings.append(Finding("ERROR", "combat-command.mask", "16-bit command-row boundary drifted"))
    sweep = {row.get("bits"): (row.get("staticActorHits"), row.get("gameCommandHits"))
             for row in mask.get("maskSweep", [])}
    retained_sweep = {
        row.get("bits"): (row.get("staticActorHits"), row.get("gameCommandHits"))
        for row in mask.get("retainedMaskSweep", [])
    }
    if (sweep.get(13), sweep.get(14), sweep.get(15), sweep.get(16), sweep.get(20), sweep.get(21)) != (
            (0, 0), (16, 16), (100, 88), (100, 88), (100, 88), (0, 0)):
        findings.append(Finding("ERROR", "combat-command.mask-sweep", "full mask sweep drifted"))
    if (retained_sweep.get(13), retained_sweep.get(14), retained_sweep.get(15),
            retained_sweep.get(16), retained_sweep.get(20), retained_sweep.get(21)) != (
            (0, 0), (14, 14), (41, 29), (41, 29), (41, 29), (0, 0)):
        findings.append(Finding("ERROR", "combat-command.mask-sweep", "retained mask sweep drifted"))
    script_route = relationship.get("scriptRoute", {})
    if script_route != {
            "status": "command_object_supplied_as_event_owner",
            "evidence": "xivl-client-scripts:lua/scripts/chara/player/playerbaseclass.lua:1823-1840",
            "finding": "PlayerBaseClass._onCommandEvent obtains getCommandId() from A2_2 and passes the same A2_2 command object to _callServerOnCommand. The native bridge preserves an object-owner route; this script fact does not by itself prove the actor-ID packing.",
    }:
        findings.append(Finding("ERROR", "combat-command.script-route", "script owner route drifted"))
    snapshots = relationship.get("sourceSnapshots", {})
    expected_snapshots = {
        "captures": {
            "repository": "XIVLegacy/xivl-captures",
            "commit": "48c7841c947ca07aecccd5fed3db6167b3efbac4",
            "rawCorpusArtifact": "sources/pcap-1.23b/manifest.yaml#members",
            "rawCorpusManifestSha256": "1D281B26CED720E433AA2354BD036B2E932EBEE084DE11CD201F9431C646AFF4",
            "extractorArtifact": "tools/extractors/extract_content_samples.py:73-144",
            "extractorSha256": "3843EDEE0E52FF73B703812AF8355C03A767CCBE052A2F8D6F78CA9391E6A691",
            "retainedSampleArtifact": "derived/payload_samples.json#samples.c2s.0x012d",
            "retainedSampleSha256": "3D08A4ED4407738C02CE13B0FE853B6E8DBA6340930E59DC94734055F8B8DA38",
        },
        "clientData": {
            "repository": "XIVLegacy/xivl-client-data",
            "commit": "566c5dc3ee5e1f036008e6758e8b7bbcf9663ea6",
            "staticActorArtifact": "manifests/staticactor_class_paths.json#records",
            "staticActorSha256": "D612438827E5997422AB6F64A807E567DDF1B953C532E8A319D67B93C53C9DB0",
            "gameCommandArtifact": "csv/gameCommand.csv column 0",
            "gameCommandSha256": "775AA8062AEBC9F394C97CB634B3A75D687FF03063C849B95333A6BCE8032811",
        },
    }
    if snapshots != expected_snapshots:
        findings.append(Finding("ERROR", "combat-command.sources", "source snapshot drifted"))
    capture_boundary = doc.get("captureBoundary", {})
    if (capture_boundary.get("totalOccurrences"), capture_boundary.get("retainedSamples"),
            capture_boundary.get("subpacketSizes"), set(capture_boundary.get("combatExamples", []))) != (
            126, 60, [216], {
                "combat_autoattack.pcapng", "combat_skills.pcapng", "party_battle_leve.pcapng"}):
        findings.append(Finding("ERROR", "combat-command.capture-boundary", "capture boundary drifted"))
    required_refs = {
        "xivl-captures:sources/pcap-1.23b/manifest.yaml#members",
        "xivl-captures:tools/extractors/extract_content_samples.py:73-144",
        "xivl-client-data:manifests/staticactor_class_paths.json#records",
        "xivl-client-data:csv/gameCommand.csv",
        "xivl-client-scripts:lua/scripts/chara/player/playerbaseclass.calls.json",
        "tools/extractors/analyze_event_start_owner_ids.py",
    }
    if not required_refs.issubset(set(doc.get("sourceRefs", []))):
        findings.append(Finding("ERROR", "combat-command.refs", "required evidence references missing"))
    if len(relationship.get("rejectedValues", [])) != 4:
        findings.append(Finding("ERROR", "combat-command.rejections", "imported-value fence drifted"))
    return findings


def check_lua_api_contract(doc: dict[str, Any]) -> list[Finding]:
    """Validate the complete Lua declaration and N-API reference contract."""
    findings: list[Finding] = []
    if (doc.get("version"), doc.get("generated"), doc.get("gameVersion"), doc.get("extraction")) != (
            1, "2026-08-14", "1.23b", "2012.09.19.0001"):
        findings.append(Finding("ERROR", "lua-api-contract.metadata", "API contract metadata drifted"))
    expected_totals = {
        "corpusScripts": 2671,
        "classBearingScripts": 2650,
        "scriptsWithoutClassSignal": 21,
        "scriptsWithMethods": 1492,
        "methodAssignments": 13782,
        "callbackAssignments": 209,
        "scriptEventAssignments": 43,
        "ordinaryMethodAssignments": 13530,
        "napiNames": 433,
        "scriptsWithNapiReferences": 2639,
        "napiApiScriptReferences": 5930,
        "napiReferenceLines": 17049,
    }
    if doc.get("totals") != expected_totals:
        findings.append(Finding("ERROR", "lua-api-contract.totals", "API contract totals drifted"))
    expected_sources = {
        "scripts": {
            "repository": "XIVLegacy/xivl-client-scripts",
            "commit": "6d0bc47dcf699408e0f3a004057bce9d62138b9b",
            "registry": {"path": "lua/registry.json", "sha256": "957060C79FCCE34F90B1840251C889EF8EE354F8380000518B1FEB96F65DD78F"},
            "napiIndex": {"path": "lua/napi_index.json", "sha256": "9E63DDCDA1C3E25DBDEA65082023C4CB23FE950FD53CFC7C57D5B76DCA1234EF"},
            "scriptManifest": {"path": "manifests/scripts.json", "sha256": "86798306F71336EE494F12D395DB3B8EA571A21224FBD99E2EF87ECD18C61300"},
            "localBodies": "lua/scripts/**/*.lua; required to regenerate, gitignored, and not copied",
        },
        "apiCatalog": {
            "path": "manifests/lua_api_index.json",
            "sha256": "25DF1FFFE1EB17376CE5D09E5F55ADD76E9A8FE5D1F56A467A68DD0D881DAA8C",
        },
    }
    if doc.get("sourceSnapshots") != expected_sources:
        findings.append(Finding("ERROR", "lua-api-contract.sources", "API source snapshot drifted"))
    tier_names = [row.get("tier") for row in doc.get("tierCriteria", [])]
    if tier_names != [
            "napi_surface", "script_callback", "script_event_handler", "ordinary_script_method"]:
        findings.append(Finding("ERROR", "lua-api-contract.tiers", "API tier criteria drifted"))

    scripts = doc.get("scriptDeclarations", [])
    if not isinstance(scripts, list) or len(scripts) != 1492:
        findings.append(Finding("ERROR", "lua-api-contract.scripts", "script declaration table drifted"))
        scripts = []
    seen_scripts: set[str] = set()
    method_count = callback_count = event_count = ordinary_count = 0
    for script in scripts:
        decoded = script.get("script")
        if not isinstance(decoded, str) or not decoded or decoded in seen_scripts:
            findings.append(Finding("ERROR", "lua-api-contract.scripts", "script identity is missing or duplicated"))
            continue
        seen_scripts.add(decoded)
        if script.get("receiverReason") not in {"registry_unique_class", "no_class_signal"}:
            findings.append(Finding("ERROR", f"lua-api-contract.{decoded}", "receiver reason is invalid"))
        if (script.get("receiverReason") == "registry_unique_class") != isinstance(script.get("receiverClass"), str):
            findings.append(Finding("ERROR", f"lua-api-contract.{decoded}", "receiver class boundary drifted"))
        collections = [
            ("callbacks", True, False),
            ("scriptEventHandlers", False, True),
            ("ordinaryMethods", False, False),
        ]
        for key, is_callback, is_event in collections:
            rows = script.get(key, [])
            if not isinstance(rows, list):
                findings.append(Finding("ERROR", f"lua-api-contract.{decoded}", f"{key} must be an array"))
                continue
            for row in rows:
                params = row.get("params")
                name = row.get("name", "")
                if (not isinstance(params, list)
                        or row.get("arity") != sum(param != "..." for param in params)
                        or row.get("variadic") != ("..." in params)
                        or row.get("callsiteCount") is not None
                        or not isinstance(row.get("functionLine"), int)
                        or not isinstance(row.get("sourceLine"), int)
                        or row.get("sourceLine", 0) <= row.get("functionLine", 0)):
                    findings.append(Finding("ERROR", f"lua-api-contract.{decoded}.{name}",
                                            "script method shape drifted"))
                if is_callback and not str(name).startswith("_on"):
                    findings.append(Finding("ERROR", f"lua-api-contract.{decoded}.{name}",
                                            "callback tier contains an ordinary method"))
                if is_event and name not in {
                        "onJobQuestCompleteFirst", "onJobQuestCompleteSecond", "onJobQuestCompleteThird"}:
                    findings.append(Finding("ERROR", f"lua-api-contract.{decoded}.{name}",
                                            "script-event tier contains an unexpected name"))
                if not is_callback and not is_event and (
                        str(name).startswith("_on") or name in {
                            "onJobQuestCompleteFirst", "onJobQuestCompleteSecond", "onJobQuestCompleteThird"}):
                    findings.append(Finding("ERROR", f"lua-api-contract.{decoded}.{name}",
                                            "ordinary tier contains a callback"))
            method_count += len(rows)
            callback_count += len(rows) if is_callback else 0
            event_count += len(rows) if is_event else 0
            ordinary_count += len(rows) if not is_callback and not is_event else 0
    if (method_count, callback_count, event_count, ordinary_count) != (13782, 209, 43, 13530):
        findings.append(Finding("ERROR", "lua-api-contract.methods", "row-derived method totals drifted"))

    surfaces = doc.get("napiSurfaces", [])
    if not isinstance(surfaces, list) or len(surfaces) != 433:
        findings.append(Finding("ERROR", "lua-api-contract.napi", "N-API surface table drifted"))
        surfaces = []
    seen_names: set[str] = set()
    reference_lines = 0
    for surface in surfaces:
        name = surface.get("name")
        if not isinstance(name, str) or not name or name in seen_names:
            findings.append(Finding("ERROR", "lua-api-contract.napi", "N-API name is missing or duplicated"))
            continue
        seen_names.add(name)
        if (surface.get("arity") is not None or surface.get("variadic") is not None
                or not surface.get("catalogRefs")):
            findings.append(Finding("ERROR", f"lua-api-contract.napi.{name}",
                                    "N-API unknown-signature or catalog-link boundary drifted"))
        receiver_total = 0
        for receiver in surface.get("receivers", []):
            if receiver.get("arity") is not None or receiver.get("variadic") is not None:
                findings.append(Finding("ERROR", f"lua-api-contract.napi.{name}",
                                        "receiver inferred an unsupported native signature"))
            script_total = sum(row.get("referenceLineCount", 0) for row in receiver.get("scripts", []))
            if script_total != receiver.get("referenceLineCount"):
                findings.append(Finding("ERROR", f"lua-api-contract.napi.{name}",
                                        "receiver reference counts do not reconcile"))
            receiver_total += script_total
        if receiver_total != surface.get("referenceLineCount"):
            findings.append(Finding("ERROR", f"lua-api-contract.napi.{name}",
                                    "surface reference counts do not reconcile"))
        reference_lines += receiver_total
    if reference_lines != 17049:
        findings.append(Finding("ERROR", "lua-api-contract.napi", "N-API reference total drifted"))

    subsystem_expected = {
        "chara/player": (1052, 1620, 68, 0, 1552, 1044, 1749, 180, 3048),
        "director": (299, 412, 10, 0, 402, 299, 375, 31, 413),
        "quest": (629, 6435, 8, 43, 6384, 629, 1593, 74, 7353),
        "command": (165, 498, 7, 0, 491, 164, 475, 164, 1216),
        "widget": (202, 3878, 22, 0, 3856, 200, 1094, 190, 3675),
        "status": (158, 185, 2, 0, 183, 158, 166, 10, 177),
        "group": (26, 113, 43, 0, 70, 24, 142, 29, 362),
        "other": (140, 641, 49, 0, 592, 121, 336, 113, 805),
    }
    actual_subsystems = {
        row.get("name"): (
            row.get("scriptCount"), row.get("methodAssignments"), row.get("callbackAssignments"),
            row.get("scriptEventAssignments"), row.get("ordinaryMethodAssignments"),
            row.get("scriptsWithNapiReferences"), row.get("napiApiScriptReferences"),
            row.get("distinctNapiNames"), row.get("napiReferenceLines"))
        for row in doc.get("subsystems", [])
    }
    if actual_subsystems != subsystem_expected:
        findings.append(Finding("ERROR", "lua-api-contract.subsystems", "subsystem totals drifted"))

    rendered = json.dumps(
        {"scriptDeclarations": doc.get("scriptDeclarations", []),
         "napiSurfaces": doc.get("napiSurfaces", [])},
        sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")
    actual_digest = hashlib.sha256(rendered).hexdigest().upper()
    if doc.get("contractSha256") != actual_digest:
        findings.append(Finding("ERROR", "lua-api-contract.digest", "API contract digest drifted"))
    native = doc.get("nativeAttributionRetest", {})
    if (native.get("status"), native.get("sampleSize"),
            {row.get("name") for row in native.get("directAttributions", [])},
            native.get("sourceSnapshot", {}).get("commit")) != (
            "bounded_sample_succeeded_complete_attribution_blocked", 10,
            {"_globalSave", "_globalTemp", "_memberSave"},
            "3f4bcb34a21dd3c3611f3eeafb11743f134d7c64"):
        findings.append(Finding("ERROR", "lua-api-contract.native", "native retest verdict drifted"))
    expected_native_snapshot = {
        "repository": "XIVLegacy/xivl-decomp",
        "commit": "3f4bcb34a21dd3c3611f3eeafb11743f134d7c64",
        "strings": {
            "path": "config/ffxivgame.strings.json",
            "sha256": "0401A3D88C3F29B53E7820682E551CC8B1A141A12E1300042E415F5BE0D18FF5",
        },
        "dumpStrings": {
            "path": "tools/ghidra_scripts/DumpStrings.java",
            "sha256": "0A70112572773A199912862C5E7AF0EFC63580C2CAF8AD9F586D3935DFE1C3DF",
        },
        "findCallers": {
            "path": "tools/ghidra_scripts/FindCallers.java",
            "sha256": "0D9565C031559228D2C3B5C6F0EC137B622453D397A1A9685A645DBF09B3029C",
        },
    }
    if native.get("sourceSnapshot") != expected_native_snapshot:
        findings.append(Finding("ERROR", "lua-api-contract.native-sources",
                                "native source snapshot drifted"))
    assessment = native.get("existingExporterAssessment", {})
    if assessment.get("missingCapability") != (
            "A reproducible string-name -> string-address -> all data/code references -> "
            "registrar/implementation mapping for every N-API name."):
        findings.append(Finding("ERROR", "lua-api-contract.native-boundary",
                                "native attribution blocker drifted"))
    expected_refs = [
        "xivl-client-scripts:lua/registry.json",
        "xivl-client-scripts:lua/napi_index.json",
        "xivl-client-scripts:lua/scripts/**/*.calls.json",
        "xivl-client-scripts:manifests/scripts.json",
        "manifests/lua_api_index.json",
        "xivl-decomp:config/ffxivgame.strings.json:7892-7894",
        "xivl-decomp:asm/ffxivgame/002da450_FUN_006da450.s:21-23",
        "xivl-decomp:asm/ffxivgame/002da4c0_FUN_006da4c0.s:21-23",
        "xivl-decomp:asm/ffxivgame/002da530_FUN_006da530.s:21-23",
        "xivl-decomp:tools/ghidra_scripts/DumpStrings.java:53-72",
        "xivl-decomp:tools/ghidra_scripts/FindCallers.java:25-47",
    ]
    if doc.get("sourceRefs") != expected_refs:
        findings.append(Finding("ERROR", "lua-api-contract.sourceRefs",
                                "API evidence citations drifted"))
    if len(doc.get("boundaries", [])) != 5:
        findings.append(Finding("ERROR", "lua-api-contract.boundaries", "API claim boundaries drifted"))
    return findings

CONFIDENCE_VALUES: frozenset[str] = frozenset({
    "confirmed",
    "confirmed-pcap-derived",
    "confirmed-script-derived",
    "probable",
    "structural",
    "hypothesis-strong",
    "inferred",
    "candidate",
    "unverified",
    "superseded",
})

KIND_VALUES: frozenset[str] = frozenset({
    "function",
    "global",
    "data",
    "rtti",
    "function-cluster",
    "function_case",
    "function_case_block",
    "function_pair",
    "vtable",
    "class",
    "field",
    "note",
    "finding",
})

PATTERN_VALUES: frozenset[str] = frozenset({
    "A", "B", "C", "D", "E",
    "C2S-Builder", "C2S-Operation", "C2S-Embedded",
    "Control", "Unknown",
})

STATUS_VALUES: frozenset[str] = frozenset({
    "covered_receiver",
    "covered_pattern",
    "covered_pipeline",
    "covered_pipeline_hybrid",
    "covered_pipeline_nullstub",
    "covered_emitter",
    "control",
    "gap",
    "noise",
})

# Evidence-kind vocabulary shared by role refinements and downstream reports.
# live_validated means the retail 1.23b client accepted the behavior in a live
# session. It is deliberately distinct from passive pcap observation.
EVIDENCE_KIND_VALUES: frozenset[str] = frozenset({
    "pcap_observed",
    "pcap_unobserved",
    "live_validated",
})
REVERIFY_METHOD = "live-validation against the retail 1.23b client in a live session"


def err(loc: str, msg: str) -> Finding:
    return Finding("ERROR", loc, msg)


def warn(loc: str, msg: str) -> Finding:
    return Finding("WARNING", loc, msg)


def info(loc: str, msg: str) -> Finding:
    return Finding("INFO", loc, msg)


def _is_canonical_nonscalar_address(addr: str) -> bool:
    return any(p.match(addr) for p in ADDRESS_CANONICAL_NONSCALAR_RES)


def _load_json(path: pathlib.Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


REQUIRED_SYMBOL_KEYS = ("id", "name", "kind", "address", "confidence")
OPTIONAL_SYMBOL_KEYS = ("notes", "sourceRefs", "needsReverify", "reverifyMethod")


def _check_reverify_fields(record: dict[str, Any], loc: str) -> list[Finding]:
    findings: list[Finding] = []
    if "needsReverify" in record and record["needsReverify"] is not True:
        findings.append(err(loc, "'needsReverify' must be true when present"))
    if "reverifyMethod" in record:
        method = record["reverifyMethod"]
        if method != REVERIFY_METHOD:
            findings.append(err(loc, f"'reverifyMethod' must equal {REVERIFY_METHOD!r}"))
        if record.get("needsReverify") is not True:
            findings.append(err(loc, "'reverifyMethod' requires needsReverify=true"))
    if record.get("needsReverify") is True and "reverifyMethod" not in record:
        findings.append(err(loc, "'reverifyMethod' is required when needsReverify is true"))
    return findings


def check_symbols(symbols_doc: Any) -> list[Finding]:
    findings: list[Finding] = []

    if not isinstance(symbols_doc, dict):
        return [err("symbols.json", "top-level value is not a JSON object")]

    if "symbols" not in symbols_doc:
        findings.append(err("symbols.json", "missing required key 'symbols'"))
        return findings
    if not isinstance(symbols_doc["symbols"], list):
        findings.append(err("symbols.json", "'symbols' must be a list"))
        return findings

    if "symbolCount" not in symbols_doc:
        findings.append(err("symbols.json", "missing required key 'symbolCount'"))
    else:
        actual = len(symbols_doc["symbols"])
        declared = symbols_doc["symbolCount"]
        if not isinstance(declared, int):
            findings.append(err("symbols.json:symbolCount",
                                f"must be int, got {type(declared).__name__}"))
        elif declared != actual:
            findings.append(err("symbols.json:symbolCount",
                                f"declared {declared} != len(symbols)={actual}"))

    for top_key in ("version", "gameVersion"):
        if top_key not in symbols_doc:
            findings.append(warn("symbols.json",
                                 f"missing recommended top-level key '{top_key}'"))

    seen_ids: set[str] = set()
    duplicate_ids: list[str] = []
    for idx, sym in enumerate(symbols_doc["symbols"]):
        loc_prefix = f"symbols.json[{idx}]"
        if not isinstance(sym, dict):
            findings.append(err(loc_prefix, "symbol entry is not a JSON object"))
            continue

        sid = sym.get("id", "<no-id>")
        loc = f"symbols.json:{sid}"

        for k in REQUIRED_SYMBOL_KEYS:
            if k not in sym:
                findings.append(err(loc, f"missing required key '{k}'"))

        if "id" in sym:
            if not isinstance(sym["id"], str):
                findings.append(err(loc, "'id' must be a string"))
            elif not BCS_Y_ID_RE.match(sym["id"]):
                findings.append(err(loc, f"id {sym['id']!r} does not match BCS-Y-\\d{{4}}"))
            else:
                if sym["id"] in seen_ids:
                    duplicate_ids.append(sym["id"])
                seen_ids.add(sym["id"])

        if "name" in sym and (not isinstance(sym["name"], str) or not sym["name"].strip()):
            findings.append(err(loc, "'name' must be a non-empty string"))

        if "kind" in sym:
            if not isinstance(sym["kind"], str):
                findings.append(err(loc, "'kind' must be a string"))
            elif sym["kind"] not in KIND_VALUES:
                findings.append(warn(loc,
                                     f"kind {sym['kind']!r} not in known set "
                                     f"({len(KIND_VALUES)} values)"))

        if "address" in sym:
            addr = sym["address"]
            if not isinstance(addr, str):
                findings.append(err(loc, "'address' must be a string"))
            elif addr == ADDRESS_PLACEHOLDER:
                pass
            elif ADDRESS_RE.match(addr):
                pass
            elif _is_canonical_nonscalar_address(addr):
                findings.append(info(loc,
                                     f"canonical non-scalar address form "
                                     f"{addr!r} (multi-VA or VA range)"))
            else:
                findings.append(warn(loc,
                                     f"address {addr!r} does not match "
                                     "0x[0-9a-fA-F]{8}"))

        if "confidence" in sym:
            if not isinstance(sym["confidence"], str):
                findings.append(err(loc, "'confidence' must be a string"))
            elif sym["confidence"] not in CONFIDENCE_VALUES:
                findings.append(err(loc,
                                    f"confidence {sym['confidence']!r} not in "
                                    f"allowed set {sorted(CONFIDENCE_VALUES)}"))

        if "sourceRefs" in sym:
            sr = sym["sourceRefs"]
            if not isinstance(sr, list):
                findings.append(err(loc, "'sourceRefs' must be a list"))
            elif not sr:
                findings.append(warn(loc, "'sourceRefs' is empty"))
            else:
                for i, ref in enumerate(sr):
                    if not isinstance(ref, str):
                        findings.append(err(f"{loc}.sourceRefs[{i}]",
                                            "ref must be a string"))

        if "notes" in sym and not isinstance(sym["notes"], str):
            findings.append(err(loc, "'notes' must be a string when present"))

        findings.extend(_check_reverify_fields(sym, loc))

        extra = set(sym.keys()) - set(REQUIRED_SYMBOL_KEYS) - set(OPTIONAL_SYMBOL_KEYS)
        if extra:
            findings.append(info(loc, f"unknown extra keys: {sorted(extra)}"))

    for did in duplicate_ids:
        findings.append(err(f"symbols.json:{did}", "duplicate id"))

    # Global pass records and address-anchored kinds legitimately permit multiple
    # rows at one address, so only identity-bearing kinds participate here.
    identity_kinds = {"function", "data", "rtti", "class"}
    kind_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for sym in symbols_doc["symbols"]:
        if not isinstance(sym, dict) or not isinstance(sym.get("address"), str):
            continue
        address = sym["address"].lower()
        kind = sym.get("kind")
        if address != "0x00000000" and kind in identity_kinds:
            kind_groups[(address, kind)].append(sym)

    for (_, kind), members in kind_groups.items():
        if len(members) < 2:
            continue

        address = members[0]["address"]
        member_ids = [str(member.get("id", "<no-id>")) for member in members]
        missing_ids: list[str] = []
        for member in members:
            notes = member.get("notes")
            if not isinstance(notes, str):
                notes = ""
            references_sibling = False
            for sibling in members:
                if sibling is member:
                    continue
                sibling_id = sibling.get("id")
                if (isinstance(sibling_id, str)
                        and re.search(rf"\b{re.escape(sibling_id)}\b", notes)):
                    references_sibling = True
                    break
                sibling_name = sibling.get("name")
                if (isinstance(sibling_name, str) and sibling_name
                        and sibling_name in notes):
                    references_sibling = True
                    break
            if not references_sibling:
                missing_ids.append(str(member.get("id", "<no-id>")))

        if not missing_ids:
            continue
        # One-way links make the duplicate discoverable, so keep them INFO;
        # only fully orphaned groups are WARNING.
        if len(missing_ids) == len(members):
            findings.append(warn(
                "symbols.json",
                f"duplicate {kind} address {address}: no member references "
                f"a sibling; members {', '.join(member_ids)}",
            ))
        else:
            findings.append(info(
                "symbols.json",
                f"duplicate {kind} address {address}: missing sibling "
                f"back-references from {', '.join(missing_ids)}",
            ))

    return findings


REQUIRED_STRUCT_KEYS = ("id", "name", "namespace", "size", "confidence",
                        "fields")
OPTIONAL_STRUCT_KEYS = ("notes", "aliases", "sourceRefs", "needsReverify", "reverifyMethod")

REQUIRED_FIELD_KEYS = ("offset", "size", "type", "name")
OPTIONAL_FIELD_KEYS = ("notes", "evidence", "absoluteOffset")


def _check_field_offset(value: Any) -> tuple[str, str] | None:
    """Classify a field offset.

    Returns:
        None                    -- canonical hex offset, no finding.
        ('INFO', reason)        -- recognised non-hex sentinel (n/a,
                                   variable, element+0xNN); advisory only.
        ('WARNING', reason)     -- non-canonical form; suspicious.
        ('ERROR', reason)       -- wrong type (not a string).
    """
    if not isinstance(value, str):
        return ("ERROR", f"must be string, got {type(value).__name__}")
    if OFFSET_HEX_RE.match(value):
        return None
    if any(p.match(value) for p in OFFSET_CANONICAL_NONHEX_RES):
        return ("INFO", "canonical non-hex offset sentinel "
                "(n/a, variable, element+0xNN)")
    return ("WARNING", "not 0x[0-9a-f]+ hex")


def _check_field_size(value: Any) -> tuple[str, str] | None:
    """Classify a size value (field-level or struct-level).

    Returns:
        None                    -- canonical hex/int size, no finding.
        ('INFO', reason)        -- recognised non-hex/int canonical form
                                   (variable / varies / unknown / n/a /
                                   pointer/string / Lua-domain logical
                                   size / composite hex-annotated size /
                                   qualified-bound size); advisory only.
        ('WARNING', reason)     -- non-canonical form; suspicious.
        ('ERROR', reason)       -- wrong type or negative integer.
    """
    if isinstance(value, int):
        if value < 0:
            return ("ERROR", "negative size")
        return None
    if isinstance(value, str):
        if SIZE_HEX_RE.match(value) or SIZE_INT_RE.match(value):
            return None
        if any(p.match(value) for p in SIZE_CANONICAL_NONHEX_RES):
            return ("INFO", "canonical non-hex/int size form "
                    "(logical sentinel, Lua-domain, or hex+annotation)")
        return ("WARNING", "not hex/int numeric")
    return ("ERROR", f"must be string or int, got {type(value).__name__}")


def check_structs(structs_doc: Any) -> list[Finding]:
    findings: list[Finding] = []

    if not isinstance(structs_doc, dict):
        return [err("structs.json", "top-level value is not a JSON object")]

    if "structs" not in structs_doc:
        findings.append(err("structs.json", "missing required key 'structs'"))
        return findings
    if not isinstance(structs_doc["structs"], list):
        findings.append(err("structs.json", "'structs' must be a list"))
        return findings

    if "structCount" not in structs_doc:
        findings.append(err("structs.json", "missing required key 'structCount'"))
    else:
        actual = len(structs_doc["structs"])
        declared = structs_doc["structCount"]
        if not isinstance(declared, int):
            findings.append(err("structs.json:structCount",
                                f"must be int, got {type(declared).__name__}"))
        elif declared != actual:
            findings.append(err("structs.json:structCount",
                                f"declared {declared} != len(structs)={actual}"))

    for top_key in ("version", "gameVersion"):
        if top_key not in structs_doc:
            findings.append(warn("structs.json",
                                 f"missing recommended top-level key '{top_key}'"))

    seen_ids: set[str] = set()
    duplicate_ids: list[str] = []
    for idx, st in enumerate(structs_doc["structs"]):
        loc_prefix = f"structs.json[{idx}]"
        if not isinstance(st, dict):
            findings.append(err(loc_prefix, "struct entry is not a JSON object"))
            continue

        sid = st.get("id", "<no-id>")
        loc = f"structs.json:{sid}"

        for k in REQUIRED_STRUCT_KEYS:
            if k not in st:
                findings.append(err(loc, f"missing required key '{k}'"))

        if "id" in st:
            if not isinstance(st["id"], str):
                findings.append(err(loc, "'id' must be a string"))
            elif not BCS_S_ID_RE.match(st["id"]):
                findings.append(err(loc, f"id {st['id']!r} does not match BCS-S-\\d{{4}}"))
            else:
                if st["id"] in seen_ids:
                    duplicate_ids.append(st["id"])
                seen_ids.add(st["id"])

        for k in ("name", "namespace"):
            if k in st and (not isinstance(st[k], str) or not st[k].strip()):
                findings.append(err(loc, f"'{k}' must be a non-empty string"))

        if "size" in st:
            result = _check_field_size(st["size"])
            if result is not None:
                sev, reason = result
                msg = f"struct size {st['size']!r}: {reason}"
                if sev == "ERROR":
                    findings.append(err(loc, msg))
                elif sev == "INFO":
                    findings.append(info(loc, msg))
                else:
                    findings.append(warn(loc, msg))

        if "confidence" in st:
            if not isinstance(st["confidence"], str):
                findings.append(err(loc, "'confidence' must be a string"))
            elif st["confidence"] not in CONFIDENCE_VALUES:
                findings.append(err(loc,
                                    f"confidence {st['confidence']!r} not in "
                                    f"allowed set {sorted(CONFIDENCE_VALUES)}"))

        if "sourceRefs" in st:
            sr = st["sourceRefs"]
            if not isinstance(sr, list):
                findings.append(err(loc, "'sourceRefs' must be a list"))
            elif not sr:
                findings.append(warn(loc, "'sourceRefs' is empty"))

        if "notes" in st and not isinstance(st["notes"], str):
            findings.append(err(loc, "'notes' must be a string when present"))
        if "aliases" in st and not isinstance(st["aliases"], list):
            findings.append(err(loc, "'aliases' must be a list when present"))

        findings.extend(_check_reverify_fields(st, loc))

        if "fields" in st:
            if not isinstance(st["fields"], list):
                findings.append(err(loc, "'fields' must be a list"))
            else:
                for fidx, f in enumerate(st["fields"]):
                    floc = f"{loc}.fields[{fidx}]"
                    if not isinstance(f, dict):
                        findings.append(err(floc, "field entry is not an object"))
                        continue
                    fname = f.get("name", "<no-name>")
                    floc = f"{loc}.{fname}"
                    for k in REQUIRED_FIELD_KEYS:
                        if k not in f:
                            findings.append(err(floc,
                                                f"field missing required key '{k}'"))
                    if "offset" in f:
                        result = _check_field_offset(f["offset"])
                        if result is not None:
                            sev, reason = result
                            msg = f"offset {f['offset']!r}: {reason}"
                            if sev == "ERROR":
                                findings.append(err(floc, msg))
                            elif sev == "INFO":
                                findings.append(info(floc, msg))
                            else:
                                findings.append(warn(floc, msg))
                    if "size" in f:
                        result = _check_field_size(f["size"])
                        if result is not None:
                            sev, reason = result
                            msg = f"size {f['size']!r}: {reason}"
                            if sev == "ERROR":
                                findings.append(err(floc, msg))
                            elif sev == "INFO":
                                findings.append(info(floc, msg))
                            else:
                                findings.append(warn(floc, msg))
                    if "type" in f and not isinstance(f["type"], str):
                        findings.append(err(floc, "'type' must be a string"))
                    if "name" in f and not isinstance(f["name"], str):
                        findings.append(err(floc, "'name' must be a string"))
                    extra = set(f.keys()) - set(REQUIRED_FIELD_KEYS) - set(OPTIONAL_FIELD_KEYS)
                    if extra:
                        findings.append(info(floc,
                                             f"unknown extra field keys: {sorted(extra)}"))

        extra = set(st.keys()) - set(REQUIRED_STRUCT_KEYS) - set(OPTIONAL_STRUCT_KEYS)
        if extra:
            findings.append(info(loc, f"unknown extra keys: {sorted(extra)}"))

    for did in duplicate_ids:
        findings.append(err(f"structs.json:{did}", "duplicate id"))

    return findings


REQUIRED_MATRIX_TOP = (
    "s2cOpcodeTable", "c2sOpcodeTable", "coverageSummary",
)
RECOMMENDED_MATRIX_TOP = (
    "version", "gameVersion", "patternLegend", "sources",
)

REQUIRED_ROW_KEYS = ("opcode", "opcodeInt", "pcapCount", "pattern",
                     "bcsYIds", "catalogStatus")
# bcsYReceiverNames preserves receiver identity when no BCS-Y constructor entry exists.
OPTIONAL_ROW_KEYS = ("notes", "bcsYReceiverNames")

def check_matrix(matrix_doc: Any) -> list[Finding]:
    findings: list[Finding] = []

    if not isinstance(matrix_doc, dict):
        return [err("matrix", "top-level value is not a JSON object")]

    for k in REQUIRED_MATRIX_TOP:
        if k not in matrix_doc:
            findings.append(err("matrix", f"missing required key '{k}'"))

    for k in RECOMMENDED_MATRIX_TOP:
        if k not in matrix_doc:
            findings.append(warn("matrix", f"missing recommended key '{k}'"))

    cs = matrix_doc.get("coverageSummary")
    if cs is not None and not isinstance(cs, dict):
        findings.append(err("matrix.coverageSummary", "must be an object"))

    for table_key in ("s2cOpcodeTable", "c2sOpcodeTable"):
        table = matrix_doc.get(table_key)
        if table is None:
            continue
        if not isinstance(table, list):
            findings.append(err(f"matrix.{table_key}", "must be a list"))
            continue

        seen_opcodes: dict[str, int] = {}
        for idx, row in enumerate(table):
            rloc = f"matrix.{table_key}[{idx}]"
            if not isinstance(row, dict):
                findings.append(err(rloc, "row is not a JSON object"))
                continue

            op = row.get("opcode", "<no-opcode>")
            rloc = f"matrix.{table_key}:{op}"

            for k in REQUIRED_ROW_KEYS:
                if k not in row:
                    findings.append(err(rloc, f"missing required key '{k}'"))

            if "opcode" in row:
                if not isinstance(row["opcode"], str):
                    findings.append(err(rloc, "'opcode' must be a string"))
                elif not OPCODE_RE.match(row["opcode"]):
                    findings.append(warn(rloc,
                                         f"opcode {row['opcode']!r} not "
                                         "0x[0-9a-f]{4}"))
                else:
                    if row["opcode"] in seen_opcodes:
                        findings.append(err(rloc,
                                            f"duplicate opcode within {table_key} "
                                            f"(prior at index "
                                            f"{seen_opcodes[row['opcode']]})"))
                    else:
                        seen_opcodes[row["opcode"]] = idx

            if "opcode" in row and "opcodeInt" in row:
                opi = row["opcodeInt"]
                if not isinstance(opi, int):
                    findings.append(err(rloc,
                                        f"'opcodeInt' must be int, got "
                                        f"{type(opi).__name__}"))
                else:
                    try:
                        expected = int(row["opcode"], 16)
                        if opi != expected:
                            findings.append(err(rloc,
                                                f"opcodeInt={opi} != "
                                                f"int({row['opcode']!r},16)={expected}"))
                    except (TypeError, ValueError):
                        pass

            if "pcapCount" in row:
                pc = row["pcapCount"]
                if not isinstance(pc, int):
                    findings.append(err(rloc,
                                        f"'pcapCount' must be int, got "
                                        f"{type(pc).__name__}"))
                elif pc < 0:
                    findings.append(err(rloc, f"pcapCount {pc} < 0"))

            if "pattern" in row:
                if not isinstance(row["pattern"], str):
                    findings.append(err(rloc, "'pattern' must be a string"))
                elif row["pattern"] not in PATTERN_VALUES:
                    findings.append(warn(rloc,
                                         f"pattern {row['pattern']!r} not in "
                                         f"allowed set {sorted(PATTERN_VALUES)}"))

            if "catalogStatus" in row:
                if not isinstance(row["catalogStatus"], str):
                    findings.append(err(rloc, "'catalogStatus' must be a string"))
                elif row["catalogStatus"] not in STATUS_VALUES:
                    findings.append(warn(rloc,
                                         f"catalogStatus {row['catalogStatus']!r} "
                                         f"not in allowed set "
                                         f"{sorted(STATUS_VALUES)}"))

            if "bcsYIds" in row:
                bids = row["bcsYIds"]
                if not isinstance(bids, list):
                    findings.append(err(rloc, "'bcsYIds' must be a list"))
                else:
                    for i, b in enumerate(bids):
                        if not isinstance(b, str):
                            findings.append(err(f"{rloc}.bcsYIds[{i}]",
                                                "entry must be a string"))
                        elif not BCS_Y_PREFIX_RE.match(b):
                            findings.append(warn(f"{rloc}.bcsYIds[{i}]",
                                                 f"entry {b!r} does not start "
                                                 "with BCS-Y-\\d{4}"))

            if "bcsYReceiverNames" in row:
                names = row["bcsYReceiverNames"]
                if not isinstance(names, list):
                    findings.append(err(rloc,
                                        "'bcsYReceiverNames' must be a list"))
                else:
                    for i, n in enumerate(names):
                        if not isinstance(n, str):
                            findings.append(err(
                                f"{rloc}.bcsYReceiverNames[{i}]",
                                "entry must be a string"))
                        elif not n.strip():
                            findings.append(err(
                                f"{rloc}.bcsYReceiverNames[{i}]",
                                "entry must be a non-empty string"))

            if "notes" in row and not isinstance(row["notes"], str):
                findings.append(err(rloc, "'notes' must be a string when present"))

            extra = set(row.keys()) - set(REQUIRED_ROW_KEYS) - set(OPTIONAL_ROW_KEYS)
            if extra:
                findings.append(info(rloc, f"unknown extra keys: {sorted(extra)}"))

    return findings


def check_role_refinements(role_doc: Any) -> list[Finding]:
    """Validate role-refinement evidenceKind values against the shared vocabulary."""
    findings: list[Finding] = []
    if not isinstance(role_doc, dict):
        return [err("role_refinements.json", "top-level value is not a JSON object")]
    refinements = role_doc.get("refinements")
    if not isinstance(refinements, list):
        return [err("role_refinements.json", "'refinements' must be a list")]
    for idx, row in enumerate(refinements):
        loc = f"role_refinements.json[{idx}]"
        if not isinstance(row, dict):
            findings.append(err(loc, "refinement is not an object"))
            continue
        kind = row.get("evidenceKind")
        if not isinstance(kind, str):
            findings.append(err(loc, "'evidenceKind' must be a string"))
        elif kind not in EVIDENCE_KIND_VALUES:
            findings.append(err(loc, f"evidenceKind {kind!r} not in allowed set "
                                      f"{sorted(EVIDENCE_KIND_VALUES)}"))
    return findings


# Opcode rows in the coverage tables must remain one-line objects. JSON parsing alone cannot detect this layout contract.

OPCODE_ROW_OPEN_RE = re.compile(r'^\{"opcode"\s*:')
TABLE_OPEN_RES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("s2cOpcodeTable", re.compile(r'^"s2cOpcodeTable"\s*:\s*\[\s*$')),
    ("c2sOpcodeTable", re.compile(r'^"c2sOpcodeTable"\s*:\s*\[\s*$')),
)


def check_matrix_format(matrix_path: pathlib.Path) -> list[Finding]:
    """Verify the matrix preserves the hybrid single-line-opcode-row format.

    Scans the raw file text (not the parsed JSON) and flags any opcode
    row inside s2cOpcodeTable / c2sOpcodeTable that spans more than one
    line. ERROR severity: this is a hard rule, not advisory.

    Triggers on a known failure mode: re-serialising the matrix via
    `json.dump(matrix, indent=2)` expands every row to a 10+ line object
    and silently destroys the single-line convention.
    """
    findings: list[Finding] = []
    try:
        text = matrix_path.read_text(encoding="utf-8")
    except OSError as e:
        return [err("matrix.format", f"failed to read raw text: {e}")]

    lines = text.splitlines()
    in_table: str | None = None
    for lineno, raw_line in enumerate(lines, 1):
        stripped = raw_line.strip()

        if in_table is None:
            for table_name, pat in TABLE_OPEN_RES:
                if pat.match(stripped):
                    in_table = table_name
                    break
            continue

        if stripped in ("]", "],"):
            in_table = None
            continue

        if not stripped:
            continue

        if stripped.startswith("{"):
            if not OPCODE_ROW_OPEN_RE.match(stripped):
                findings.append(err(
                    f"matrix.{in_table}:line{lineno}",
                    f"row does not start with '{{\"opcode\":' "
                    f"(multi-line object opened?): {stripped[:60]!r}"))
                continue
            if not (stripped.endswith("},") or stripped.endswith("}")):
                findings.append(err(
                    f"matrix.{in_table}:line{lineno}",
                    f"opcode row does not end on same line "
                    f"(hybrid single-line format violated): "
                    f"{stripped[:60]!r}"))
            continue

    return findings


def _extract_bcs_y(token: str) -> str | None:
    m = BCS_Y_PREFIX_RE.match(token)
    return m.group(1) if m else None


def check_cross_references(symbols_doc: Any, structs_doc: Any,
                           matrix_doc: Any) -> list[Finding]:
    findings: list[Finding] = []

    if not (isinstance(symbols_doc, dict)
            and isinstance(symbols_doc.get("symbols"), list)):
        return [err("cross", "symbols.json not loadable for cross-ref")]

    known_y_ids: set[str] = {
        s["id"] for s in symbols_doc["symbols"]
        if isinstance(s, dict) and isinstance(s.get("id"), str)
    }

    if isinstance(matrix_doc, dict):
        for table_key in ("s2cOpcodeTable", "c2sOpcodeTable"):
            table = matrix_doc.get(table_key)
            if not isinstance(table, list):
                continue
            for row in table:
                if not isinstance(row, dict):
                    continue
                op = row.get("opcode", "<?>")
                for raw in row.get("bcsYIds", []) or []:
                    if not isinstance(raw, str):
                        continue
                    yid = _extract_bcs_y(raw)
                    if yid is None:
                        continue
                    if yid not in known_y_ids:
                        findings.append(err(
                            f"matrix.{table_key}:{op}",
                            f"references unknown {yid} (token {raw!r})"))

    # Struct notes may contain BCS-Y references that need cross-file validation.
    if isinstance(structs_doc, dict):
        token_re = re.compile(r"\bBCS-Y-\d{4}\b")
        for st in structs_doc.get("structs", []) or []:
            if not isinstance(st, dict):
                continue
            sid = st.get("id", "<?>")
            scan_blobs: list[tuple[str, str]] = []
            if isinstance(st.get("notes"), str):
                scan_blobs.append(("notes", st["notes"]))
            for fld in st.get("fields", []) or []:
                if isinstance(fld, dict) and isinstance(fld.get("notes"), str):
                    scan_blobs.append((f"fields.{fld.get('name','?')}.notes",
                                       fld["notes"]))
                if isinstance(fld, dict) and isinstance(fld.get("evidence"), str):
                    scan_blobs.append((f"fields.{fld.get('name','?')}.evidence",
                                       fld["evidence"]))
            for where, blob in scan_blobs:
                for yid in token_re.findall(blob):
                    if yid not in known_y_ids:
                        findings.append(warn(
                            f"structs.json:{sid}.{where}",
                            f"references unknown {yid}"))

    return findings


@dataclass
class SectionResult:
    name: str
    check_count: int
    findings: list[Finding]


def _summarize(findings: Iterable[Finding]) -> Counter:
    c: Counter = Counter()
    for f in findings:
        c[f.severity] += 1
    return c


def _print_section(section: SectionResult, sample_limit: int = 10) -> None:
    print(f"\n--- {section.name} ---\n")
    summary = _summarize(section.findings)
    print(f"checks executed: {section.check_count}")
    for sev in SEVERITIES:
        print(f"  {sev:8s}: {summary.get(sev, 0)}")

    by_sev: dict[str, list[Finding]] = defaultdict(list)
    for f in section.findings:
        by_sev[f.severity].append(f)

    for sev in SEVERITIES:
        bucket = by_sev.get(sev, [])
        if not bucket:
            continue
        print(f"\n  {sev} findings (showing up to {sample_limit} of {len(bucket)}):")
        for f in bucket[:sample_limit]:
            print(f"    [{f.location}] {f.message}")
        if len(bucket) > sample_limit:
            print(f"    ... {len(bucket) - sample_limit} more {sev} findings suppressed")


SYMBOL_CHECK_COUNT = 12
STRUCT_CHECK_COUNT = 14
MATRIX_CHECK_COUNT = 14
CROSS_CHECK_COUNT = 2
ROLE_CHECK_COUNT = 1
BATTLE_RESULT_CHECK_COUNT = 1
LUA_RESOURCE_INVENTORY_CHECK_COUNT = 1
LUA_RESOURCE_PATH_CHECK_COUNT = 1
def check_gam_hash_names(doc: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    resolved = doc.get("resolved", [])
    unresolved = doc.get("unresolved", [])
    coverage = doc.get("coverage", {})
    if (len(resolved), len(unresolved)) != (263, 0):
        findings.append(Finding("ERROR", "gam-hash.coverage", "resolved/unresolved hash counts drifted"))
    if (coverage.get("distinctHashes"), coverage.get("totalOccurrences"),
            coverage.get("resolvedOccurrences"), coverage.get("unresolvedOccurrences")) != (263, 8918, 8918, 0):
        findings.append(Finding("ERROR", "gam-hash.coverage", "occurrence-weighted coverage drifted"))
    total = 0
    expected_consumers = {
        "playerWork.castCommandClient": ["ActionMenuWidget.updateCastInfo", "PlayerBaseClass.getCastCommand"],
        "playerWork.castEndClient": ["ActionGaugeWidget.update", "PlayerBaseClass.getCastEndTime"],
        "charaWork.battleTemp.castGauge_speed[0]": ["CharaBaseClass.getCastSpeed"],
        "charaWork.battleTemp.castGauge_speed[1]": ["CharaBaseClass.getCastSpeed"],
    }
    for row in resolved:
        expected = int(row.get("idHex", "0"), 16)
        names = row.get("names", [])
        if not names or any(murmur2_backward(name.encode("ascii")) != expected for name in names):
            findings.append(Finding("ERROR", f"gam-hash.{row.get('idHex')}", "exact name hash mismatch"))
        profile = row.get("observedProfile", {})
        if profile.get("occurrences") != row.get("count") or profile.get("widths") != row.get("sizes"):
            findings.append(Finding("ERROR", f"gam-hash.{row.get('idHex')}", "observed profile drifted"))
        if row.get("resolutionEvidence", {}).get("method") != "exact_backward_murmurhash2_seed_0":
            findings.append(Finding("ERROR", f"gam-hash.{row.get('idHex')}", "resolution method missing"))
        widths = {int(key) for key in row.get("sizes", {})}
        expected_type = {frozenset({1}): "u8_bits", frozenset({2}): "u16_le_bits",
                         frozenset({4}): "u32_or_f32_le_bits"}.get(
            frozenset(widths), "opaque_variable_width")
        if row.get("wireValueType") != expected_type:
            findings.append(Finding("ERROR", f"gam-hash.{row.get('idHex')}", "wire value type drifted"))
        consumers = sorted({consumer for name in names for consumer in expected_consumers.get(name, [])})
        if row.get("consumingScriptGetters") != consumers:
            findings.append(Finding("ERROR", f"gam-hash.{row.get('idHex')}", "consumer context drifted"))
        total += row.get("count", 0)
    if total != 8918:
        findings.append(Finding("ERROR", "gam-hash.occurrences", "resolved occurrence sum drifted"))
    profile_source = doc.get("provenance", {}).get("fullCorpusProfile", {})
    if (profile_source.get("commit") != "54a24c87faa4e3cebde808b74d80b6f1bee4b013" or
            not re.fullmatch(r"[0-9a-f]{64}", profile_source.get("sha256", ""))):
        findings.append(Finding("ERROR", "gam-hash.provenance", "full-corpus source pin drifted"))
    if len(doc.get("provenance", {}).get("consumerContextRefs", [])) != 5:
        findings.append(Finding("ERROR", "gam-hash.provenance", "consumer source refs drifted"))
    return findings


LUA_CALLBACK_CONTRACT_CHECK_COUNT = 1
LUA_API_CONTRACT_CHECK_COUNT = 1
CAST_CHANT_PRESENTATION_CHECK_COUNT = 1
COMBAT_COMMAND_EMISSION_CHECK_COUNT = 1
GAM_HASH_NAMES_CHECK_COUNT = 1


def main() -> int:
    try:
        symbols_doc = _load_json(SYMBOLS_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: failed to load {SYMBOLS_PATH}: {e}", file=sys.stderr)
        return 2
    try:
        structs_doc = _load_json(STRUCTS_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: failed to load {STRUCTS_PATH}: {e}", file=sys.stderr)
        return 2
    try:
        matrix_doc = _load_json(MATRIX_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: failed to load {MATRIX_PATH}: {e}", file=sys.stderr)
        return 2
    try:
        role_doc = _load_json(ROLE_REFINEMENTS_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: failed to load {ROLE_REFINEMENTS_PATH}: {e}", file=sys.stderr)
        return 2
    try:
        battle_result_doc = _load_json(BATTLE_RESULT_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: failed to load {BATTLE_RESULT_PATH}: {e}", file=sys.stderr)
        return 2
    try:
        lua_resource_inventory_doc = _load_json(LUA_RESOURCE_INVENTORY_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: failed to load {LUA_RESOURCE_INVENTORY_PATH}: {e}", file=sys.stderr)
        return 2
    try:
        lua_resource_path_doc = _load_json(LUA_RESOURCE_PATH_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: failed to load {LUA_RESOURCE_PATH_PATH}: {e}", file=sys.stderr)
        return 2
    try:
        lua_callback_contract_doc = _load_json(LUA_CALLBACK_CONTRACT_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: failed to load {LUA_CALLBACK_CONTRACT_PATH}: {e}", file=sys.stderr)
        return 2
    try:
        lua_api_contract_doc = _load_json(LUA_API_CONTRACT_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: failed to load {LUA_API_CONTRACT_PATH}: {e}", file=sys.stderr)
        return 2
    try:
        cast_chant_presentation_doc = _load_json(CAST_CHANT_PRESENTATION_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: failed to load {CAST_CHANT_PRESENTATION_PATH}: {e}", file=sys.stderr)
        return 2
    try:
        combat_command_emission_doc = _load_json(COMBAT_COMMAND_EMISSION_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: failed to load {COMBAT_COMMAND_EMISSION_PATH}: {e}", file=sys.stderr)
        return 2
    try:
        gam_hash_names_doc = _load_json(GAM_HASH_NAMES_PATH)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: failed to load {GAM_HASH_NAMES_PATH}: {e}", file=sys.stderr)
        return 2

    print("=" * 72)
    print("CATALOG VALIDATOR REPORT")
    print("=" * 72)
    print(f"symbols.json: symbolCount={symbols_doc.get('symbolCount')} "
          f"len(symbols)={len(symbols_doc.get('symbols', []))}")
    print(f"structs.json: structCount={structs_doc.get('structCount')} "
          f"len(structs)={len(structs_doc.get('structs', []))}")
    print(f"matrix:       s2c rows={len(matrix_doc.get('s2cOpcodeTable', []))} "
          f"c2s rows={len(matrix_doc.get('c2sOpcodeTable', []))}")
    print(f"role refinements: rows={len(role_doc.get('refinements', []))}")

    matrix_findings = check_matrix(matrix_doc) + check_matrix_format(MATRIX_PATH)
    sections: list[SectionResult] = [
        SectionResult("symbols.json", SYMBOL_CHECK_COUNT, check_symbols(symbols_doc)),
        SectionResult("structs.json", STRUCT_CHECK_COUNT, check_structs(structs_doc)),
        SectionResult("coverage matrix", MATRIX_CHECK_COUNT, matrix_findings),
        SectionResult("role refinements", ROLE_CHECK_COUNT,
                      check_role_refinements(role_doc)),
        SectionResult("battle-result fields", BATTLE_RESULT_CHECK_COUNT,
                      check_battle_result_fields(battle_result_doc, structs_doc)),
        SectionResult("preserved Lua resources", LUA_RESOURCE_INVENTORY_CHECK_COUNT,
                      check_lua_resource_inventory(lua_resource_inventory_doc)),
        SectionResult("Lua resource paths", LUA_RESOURCE_PATH_CHECK_COUNT,
                      check_lua_resource_paths(lua_resource_path_doc)),
        SectionResult("Lua callback contract", LUA_CALLBACK_CONTRACT_CHECK_COUNT,
                      check_lua_callback_contract(lua_callback_contract_doc)),
        SectionResult("complete Lua API contract", LUA_API_CONTRACT_CHECK_COUNT,
                      check_lua_api_contract(lua_api_contract_doc)),
        SectionResult("cast and chant presentation", CAST_CHANT_PRESENTATION_CHECK_COUNT,
                      check_cast_chant_presentation(cast_chant_presentation_doc)),
        SectionResult("combat command emission", COMBAT_COMMAND_EMISSION_CHECK_COUNT,
                      check_combat_command_emission(combat_command_emission_doc)),
        SectionResult("property stream hash catalog", GAM_HASH_NAMES_CHECK_COUNT,
                      check_gam_hash_names(gam_hash_names_doc)),
        SectionResult("cross-file references", CROSS_CHECK_COUNT,
                      check_cross_references(symbols_doc, structs_doc, matrix_doc)),
    ]

    for s in sections:
        _print_section(s)

    print("\n" + "=" * 72)
    print("OVERALL SUMMARY")
    print("=" * 72)
    grand = Counter()
    total_checks = 0
    for s in sections:
        total_checks += s.check_count
        for f in s.findings:
            grand[f.severity] += 1
    print(f"total invariants checked: {total_checks}")
    for sev in SEVERITIES:
        print(f"  {sev:8s}: {grand.get(sev, 0)}")

    return 1 if grand.get("ERROR", 0) > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
