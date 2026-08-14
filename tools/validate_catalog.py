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

import json
import pathlib
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

REPO = pathlib.Path(__file__).resolve().parents[1]
SYMBOLS_PATH = REPO / "manifests" / "symbols.json"
STRUCTS_PATH = REPO / "manifests" / "structs.json"
MATRIX_PATH = REPO / "manifests" / "pcap_opcode_coverage_matrix.json"
ROLE_REFINEMENTS_PATH = REPO / "manifests" / "role_refinements.json"
BATTLE_RESULT_PATH = REPO / "manifests" / "battle_result_field_semantics.json"
LUA_RESOURCE_INVENTORY_PATH = REPO / "manifests" / "preserved_lua_resource_inventory.json"
LUA_RESOURCE_PATH_PATH = REPO / "manifests" / "lua_resource_path_decoding.json"

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


SYMBOL_CHECK_COUNT = 11
STRUCT_CHECK_COUNT = 14
MATRIX_CHECK_COUNT = 14
CROSS_CHECK_COUNT = 2
ROLE_CHECK_COUNT = 1
BATTLE_RESULT_CHECK_COUNT = 1
LUA_RESOURCE_INVENTORY_CHECK_COUNT = 1
LUA_RESOURCE_PATH_CHECK_COUNT = 1


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
