"""Build manifests/ir_catalog.json, the canonical client-structure IR.

The IR is a generated normalization, never a second place to author facts.
`manifests/structs.json` and `manifests/symbols.json` stay authoritative for
everything they already hold; this tool reshapes them into one typed
document that a generator can consume, and `manifests/ir_overlay.json` is
the sole hand-maintained home for the two fields no source catalog records
(type alignment, and the reading of a derived unknown span).

Two rules the code enforces rather than assumes:

1. Nothing is invented. Every size, offset, address, and confidence value is
   carried across verbatim in `raw` beside its parsed form, and an input
   string this tool does not recognise raises instead of degrading to
   "unknown" -- a new catalog convention must be taught to the IR, not
   silently flattened by it.
2. Nothing is promoted or demoted. Confidence is copied. The RTTI
   corroboration flag is descriptive and feeds nothing.
CLI:
  python tools/build_ir.py            # write manifests/ir_catalog.json
  python tools/build_ir.py --check    # rebuild in memory and diff; exit 1 on drift

Pure stdlib.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _symbols_io  # noqa: E402
from hygiene_scan import _classify_ref  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
STRUCTS_PATH = REPO / "manifests" / "structs.json"
OVERLAY_PATH = REPO / "manifests" / "ir_overlay.json"
RTTI_PATH = REPO / "manifests" / "rtti_vftable_index.json"
RTTI_DUMP_PATH = REPO / "manifests" / "rtti_extraction_OUR.txt"
OUT_PATH = REPO / "manifests" / "ir_catalog.json"

# The coverage matrix contributes pcap counts and BCS-Y attribution, not the opcode universe.
RELATIONSHIP_SOURCES = {
    "coverage-matrix": "manifests/pcap_opcode_coverage_matrix.json",
    "receiver-map": "manifests/receiver_opcode_map_inbound.json",
    "operation-map": "manifests/operation_opcode_map_outbound.json",
    "lua-bridge": "manifests/lua_to_opcode.json",
    "c2s-skeleton": "manifests/c2s_bridge_skeleton.json",
    "receiver-field-writes": "manifests/receiver_field_writes.json",
}

IR_VERSION = "1.0"
GAME_VERSION = "1.23b"
GENERATOR_VERSION = 1
SCHEMA_REF = "schemas/ir-v1.schema.json"

# Kinds whose address is expected to be a vftable VA, and so is meaningfully
# checkable against the COL-walk extraction. Every other kind reports
# "not-applicable" rather than a false negative.
VFTABLE_BEARING_KINDS = frozenset({"rtti", "vtable", "class"})

BCS_Y_TOKEN_RE = re.compile(r"\bBCS-Y-\d{4}\b")

HEX_RE = re.compile(r"^0x[0-9a-fA-F]+$")
DEC_RE = re.compile(r"^\d+$")
ANNOTATED_SIZE_RE = re.compile(r"^(0x[0-9a-fA-F]+)[\s(/].+$")
BOUNDED_SIZE_RE = re.compile(
    r"^(at\s+least|approximately|minimum|maximum)\s+(0x[0-9a-fA-F]+)\b.*$")
VARIABLE_ANNOTATED_RE = re.compile(r"^variable\s*\(.+\)$")
LOGICAL_SIZES = frozenset({"pointer/string"})
LUA_LOGICAL_SIZE_RE = re.compile(
    r"^Lua\s+(?:table\s+entry|reference|string|closure|call\s+expression)$")
ELEMENT_OFFSET_RE = re.compile(r"^element\+(0x[0-9a-fA-F]+)$")

SCALAR_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{8}$")
MULTI_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{8}(;0x[0-9a-fA-F]{8})+$")
RANGE_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{8}\.\.0x[0-9a-fA-F]{8}$")
ADDRESS_PLACEHOLDER = "0x00000000"

CITATION_RE = re.compile(r"^([A-Za-z0-9._-]+)@([0-9a-f]{40})(?::(.*))?$")


class BuildError(Exception):
    """An input this tool cannot represent without guessing."""


def parse_size(raw: object, where: str) -> dict:
    if isinstance(raw, bool):
        raise BuildError(f"{where}: size must not be a boolean")
    if isinstance(raw, int):
        if raw < 0:
            raise BuildError(f"{where}: negative size {raw}")
        return {"kind": "exact", "raw": raw, "bytes": raw}
    if not isinstance(raw, str):
        raise BuildError(f"{where}: size must be a string or int, got "
                         f"{type(raw).__name__}")
    text = raw.strip()
    if HEX_RE.match(text):
        return {"kind": "exact", "raw": raw, "bytes": int(text, 16)}
    if DEC_RE.match(text):
        return {"kind": "exact", "raw": raw, "bytes": int(text, 10)}
    m = ANNOTATED_SIZE_RE.match(text)
    if m:
        return {"kind": "annotated", "raw": raw, "bytes": int(m.group(1), 16)}
    m = BOUNDED_SIZE_RE.match(text)
    if m:
        bound = re.sub(r"\s+", "-", m.group(1).lower())
        return {"kind": "bounded", "raw": raw, "bytes": int(m.group(2), 16),
                "bound": bound}
    if text in ("variable", "varies") or VARIABLE_ANNOTATED_RE.match(text):
        return {"kind": "variable", "raw": raw}
    if text in ("unknown", "n/a"):
        return {"kind": "unknown", "raw": raw}
    if text in LOGICAL_SIZES or LUA_LOGICAL_SIZE_RE.match(text):
        return {"kind": "logical", "raw": raw}
    raise BuildError(
        f"{where}: unrecognised size {raw!r}. Teach parse_size() the new "
        "convention rather than letting it fall through to 'unknown'.")


def parse_offset(raw: object, where: str) -> dict:
    if not isinstance(raw, str):
        raise BuildError(f"{where}: offset must be a string, got "
                         f"{type(raw).__name__}")
    text = raw.strip()
    if HEX_RE.match(text):
        return {"kind": "exact", "raw": raw, "bytes": int(text, 16)}
    m = ELEMENT_OFFSET_RE.match(text)
    if m:
        return {"kind": "element-relative", "raw": raw,
                "bytes": int(m.group(1), 16)}
    if text == "variable":
        return {"kind": "variable", "raw": raw}
    if text == "n/a":
        return {"kind": "none", "raw": raw}
    raise BuildError(
        f"{where}: unrecognised offset {raw!r}. Teach parse_offset() the new "
        "convention rather than letting it fall through.")


def parse_address(raw: object, where: str) -> dict:
    if not isinstance(raw, str):
        raise BuildError(f"{where}: address must be a string, got "
                         f"{type(raw).__name__}")
    text = raw.strip()
    if text == ADDRESS_PLACEHOLDER:
        return {"kind": "placeholder", "raw": raw, "values": []}
    if SCALAR_ADDRESS_RE.match(text):
        return {"kind": "scalar", "raw": raw, "values": [text]}
    if MULTI_ADDRESS_RE.match(text):
        return {"kind": "multi", "raw": raw, "values": text.split(";")}
    if RANGE_ADDRESS_RE.match(text):
        return {"kind": "range", "raw": raw, "values": text.split("..")}
    raise BuildError(
        f"{where}: unrecognised address {raw!r}. Extend parse_address() and "
        "validate_catalog.ADDRESS_CANONICAL_NONSCALAR_RES together.")


def parse_namespace(raw: str, where: str) -> dict:
    if not isinstance(raw, str) or not raw.strip():
        raise BuildError(f"{where}: namespace must be a non-empty string")
    text = raw.strip()
    if "::" in text:
        return {"raw": raw, "convention": "cxx", "segments": text.split("::")}
    if "." in text:
        return {"raw": raw, "convention": "dotted", "segments": text.split(".")}
    return {"raw": raw, "convention": "single", "segments": [text]}


def _union(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def derive_layout(fields: list[dict], type_size: dict) -> tuple[dict, list[dict]]:
    """Return (layout, unknown-span members) for one type.

    A span is the complement of the recorded fields inside the type's extent.
    It records that no field claims those bytes -- it is the absence of a
    claim made explicit, which is why deriving it does not promote anything.
    """
    intervals: list[tuple[int, int]] = []
    open_starts: list[int] = []
    for parsed_offset, parsed_size in fields:
        if parsed_offset["kind"] != "exact":
            continue
        start = parsed_offset["bytes"]
        if parsed_size["kind"] == "exact":
            intervals.append((start, start + parsed_size["bytes"]))
        else:
            # An exact offset with unknown width bounds the derived extent.
            open_starts.append(start)

    if not intervals and not open_starts:
        return ({"status": "unmodeled", "coveredBytes": 0, "unknownBytes": 0,
                 "overlapBytes": 0}, [])

    merged = _union(intervals)
    overlap = sum(e - s for s, e in intervals) - sum(e - s for s, e in merged)

    # Only an exact type size declares an extent. An annotated size carries
    # prose that can qualify or vary it ("0x60 (base) / 0x64 (variant)"), so
    # its leading token is not a claim that every byte is accounted for.
    declared = type_size["bytes"] if type_size["kind"] == "exact" else None
    if declared is not None:
        outside = [(start, end) for start, end in intervals if end > declared]
        if outside:
            spans = ", ".join(f"0x{start:X}..0x{end:X}" for start, end in outside)
            raise BuildError(
                f"field extent {spans} exceeds declared type size 0x{declared:X}")
    if declared is not None and not open_starts:
        status, extent, trailing = "modeled", declared, None
    else:
        status, trailing = "partial", "unbounded"
        candidates = [merged[-1][1]] if merged else []
        if open_starts:
            candidates.append(min(open_starts))
        if declared is not None:
            candidates.append(declared)
        extent = min(candidates) if open_starts else max(candidates)

    covered = sum(min(e, extent) - s for s, e in merged if s < extent)

    spans: list[dict] = []
    cursor = 0
    for start, end in merged:
        if start > cursor and cursor < extent:
            gap_end = min(start, extent)
            if gap_end > cursor:
                spans.append((cursor, gap_end - cursor))
        cursor = max(cursor, end)
    if cursor < extent:
        spans.append((cursor, extent - cursor))

    layout = {
        "status": status,
        "coveredBytes": covered,
        "unknownBytes": sum(length for _, length in spans),
        "overlapBytes": overlap,
    }
    if declared is not None:
        layout["declaredBytes"] = declared
    if trailing:
        layout["trailing"] = trailing
    # Key order is fixed by the schema's readable order, not by insertion.
    ordered = {"status": layout["status"]}
    if "declaredBytes" in layout:
        ordered["declaredBytes"] = layout["declaredBytes"]
    ordered["coveredBytes"] = layout["coveredBytes"]
    ordered["unknownBytes"] = layout["unknownBytes"]
    ordered["overlapBytes"] = layout["overlapBytes"]
    if "trailing" in layout:
        ordered["trailing"] = layout["trailing"]
    return ordered, spans


# ---------------------------------------------------------------------------
# Citations
# ---------------------------------------------------------------------------

CATEGORY_TO_RESOLUTION = {
    "citation": "external-immutable",
    "record_label": "maintainer-record",
    "repo_relative": "in-repo-resolved",
    "missing_repo_relative": "in-repo-unresolved",
}


@functools.lru_cache(maxsize=1)
def tracked_paths() -> frozenset[str]:
    """Every path git tracks, forward-slashed.

    Resolution is decided from tracked content rather than from the working
    tree. Asking the filesystem would make a generated artifact depend on
    untracked and gitignored files -- `tools/ghidra/logs/` is gitignored, so
    an author with local decomp logs would generate a different IR than CI
    does from the same catalogs -- and `Path.exists()` is case-insensitive
    on Windows and case-sensitive elsewhere.
    """
    try:
        out = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z"],
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        raise BuildError(
            "cannot list tracked files via git, and the IR's citation "
            f"resolution is defined against tracked content: {e}") from e
    return frozenset(p.decode("utf-8") for p in out.split(b"\0") if p)


def _is_tracked(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized in tracked_paths()


def refuse_unsafe_ref(raw: str, where: str = "sourceRef") -> None:
    """Refuse the two reference forms hygiene_scan gates as defects.

    Applied to overlay references too, which never reach build_citations:
    the overlay is the one hand-maintained file in the IR, so it is exactly
    where a live sibling path would otherwise slip past every gate.
    """
    if re.match(r"^[A-Za-z]:", raw) or raw.startswith("/"):
        raise BuildError(f"{where} {raw!r} is an absolute path")
    if raw.startswith("../") or raw.startswith("..\\"):
        raise BuildError(
            f"{where} {raw!r} is a live_parent_path: a path into another "
            "checkout is a defect hygiene_scan already gates, and the IR must "
            "not launder one into a citation.")


def build_citations(entries: list[tuple[str, list[str]]]) -> tuple[list[dict],
                                                                  dict[str, str]]:
    """Normalize every distinct sourceRef into a citation record.

    EV ids are assigned over the sorted distinct raw strings, so a rebuild
    from identical inputs reproduces them exactly. They are an index into
    this document and deliberately not a citation surface: BCS-Y and BCS-S
    are the stable identifiers other repositories promote against.
    """
    referenced: dict[str, set[str]] = {}
    for owner_id, refs in entries:
        for ref in refs:
            if not ref:
                continue
            referenced.setdefault(ref, set()).add(owner_id)

    citations: list[dict] = []
    by_raw: dict[str, str] = {}
    for index, raw in enumerate(sorted(referenced), start=1):
        refuse_unsafe_ref(raw)
        _status, category = _classify_ref(raw, exists=_is_tracked)
        resolution = CATEGORY_TO_RESOLUTION.get(category)
        if resolution is None:
            raise BuildError(f"sourceRef {raw!r}: unmapped hygiene category "
                             f"{category!r}")
        cid = f"EV-{index:04d}"
        record = {"id": cid, "raw": raw, "category": category,
                  "resolution": resolution}
        m = CITATION_RE.match(raw)
        if m:
            record["repo"] = m.group(1)
            record["commit"] = m.group(2)
            if m.group(3):
                record["path"] = m.group(3)
        else:
            path, _, anchor = raw.partition("#")
            if path:
                record["path"] = path
            if anchor:
                record["anchor"] = anchor
        record["referencedBy"] = sorted(referenced[raw])
        citations.append(record)
        by_raw[raw] = cid
    return citations, by_raw


# ---------------------------------------------------------------------------
# Relationship layer
# ---------------------------------------------------------------------------

OPCODE_HEX_RE = re.compile(r"^0x[0-9a-f]{4}$")


def _opcode_id(direction: str, hex_value: str) -> str:
    if direction not in ("s2c", "c2s"):
        raise BuildError(f"unknown opcode direction {direction!r}")
    if not OPCODE_HEX_RE.match(hex_value):
        raise BuildError(f"opcode {hex_value!r} is not 0x[0-9a-f]{{4}}")
    return f"{direction}:{hex_value}"


class _OpcodeIndex:
    """Union of every opcode any relationship source names.

    Deliberately not matrix-derived. The coverage matrix records what pcap
    capture observed, which is a strict subset: the receiver map alone names
    19 inbound opcodes with no matrix row. Direction is part of the key
    because 12 hex values appear in both matrix tables.
    """

    def __init__(self) -> None:
        self.rows: dict[str, dict] = {}

    def touch(self, direction: str, hex_value: str, source: str) -> dict:
        oid = _opcode_id(direction, hex_value)
        row = self.rows.get(oid)
        if row is None:
            row = {
                "id": oid,
                "direction": direction,
                "hex": hex_value,
                "int": int(hex_value, 16),
                "names": [],
                "receivers": [],
                "operations": [],
                "luaBindings": [],
                "symbols": [],
                "sources": [],
            }
            self.rows[oid] = row
        if source not in row["sources"]:
            row["sources"].append(source)
        return row

    def name(self, row: dict, name: str | None, source: str) -> None:
        """Record a name with its source rather than picking a winner.

        Six c2s opcodes carry disagreeing names across sources, two of them a
        real semantic conflict rather than a placeholder. Collapsing them
        here would silently pick one; the summary counts them instead.
        """
        if not name:
            return
        if not any(n["name"] == name and n["source"] == source
                   for n in row["names"]):
            row["names"].append({"name": name, "source": source})

    @staticmethod
    def add(row: dict, key: str, value: str | None) -> None:
        if value and value not in row[key]:
            row[key].append(value)


def _casts(value: object, where: str) -> list[dict]:
    """Normalize a receiver's cast evidence into a list of {src?, target}.

    The two source catalogs spell it differently: the receiver map uses
    {src, target} with an optional `additional` list of further casts, and
    the field-write catalog uses a bare target name with no source type.
    """
    if value is None:
        return []
    if isinstance(value, str):
        return [{"target": value}]
    if isinstance(value, dict):
        casts = [{k: value[k] for k in ("src", "target") if k in value}]
        for extra in value.get("additional", []):
            casts.append({k: extra[k] for k in ("src", "target") if k in extra})
        if not all(c.get("target") for c in casts):
            raise BuildError(f"{where}: cast evidence with no target")
        return casts
    raise BuildError(f"{where}: cast evidence is a {type(value).__name__}")


def build_relationships(sources: dict[str, dict], known_symbols: set[str]) -> dict:
    index = _OpcodeIndex()
    receivers: list[dict] = []
    operations: list[dict] = []
    lua_bindings: list[dict] = []

    def symbol(row: dict, raw: str | None, where: str) -> None:
        """Attach every BCS-Y id in `raw` to the opcode row.

        Tokens are extracted rather than taken whole: a matrix bcsYIds entry
        can carry a trailing annotation and a c2s-skeleton confirmedBcsy can
        name two ids in one semicolon-joined string.
        """
        if not raw:
            return
        found = BCS_Y_TOKEN_RE.findall(raw)
        if not found:
            raise BuildError(f"{where} cites {raw!r}, which holds no BCS-Y id")
        for bcs_id in found:
            if bcs_id not in known_symbols:
                raise BuildError(f"{where} cites {bcs_id}, which symbols.json "
                                 "does not hold")
            _OpcodeIndex.add(row, "symbols", bcs_id)

    # -- coverage matrix ---------------------------------------------------
    matrix = sources["coverage-matrix"]
    for table, direction in (("s2cOpcodeTable", "s2c"),
                             ("c2sOpcodeTable", "c2s")):
        for entry in matrix[table]:
            row = index.touch(direction, entry["opcode"], "coverage-matrix")
            row["matrix"] = {
                "pattern": entry["pattern"],
                "catalogStatus": entry["catalogStatus"],
                "pcapCount": entry["pcapCount"],
            }
            if entry.get("bcsYReceiverNames"):
                row["matrix"]["receiverNames"] = list(entry["bcsYReceiverNames"])
            for token in entry.get("bcsYIds", []):
                symbol(row, token, f"matrix {entry['opcode']}")

    # -- receiver map ------------------------------------------------------
    receiver_doc = sources["receiver-map"]
    field_writes = {e["receiverName"]: e
                    for e in sources["receiver-field-writes"]["perReceiver"]}
    for bucket, classification in (("inboundReceivers", "inbound"),
                                   ("clientInternalReceivers",
                                    "client-internal")):
        for entry in receiver_doc[bucket]:
            record = {
                "name": entry["name"],
                # Identity is (name, vftable), not name: UserDataReceiver has
                # two rows for its 6-slot and 2-slot vftables sharing one
                # slot1. Dropping the address would make them look duplicated.
                "rttiAddress": entry["rttiRva"],
                "namespace": entry["namespace"],
                "classification": classification,
                "confidence": entry["confidence"],
                "symbolsByRole": {},
                "opcodes": [],
                "sources": ["receiver-map"],
            }
            all_symbols: list[str] = []
            for group, refs in sorted((entry.get("bcsRefs") or {}).items()):
                ids: list[str] = []
                for ref in refs:
                    bcs_id = ref["bcsId"]
                    if bcs_id not in known_symbols:
                        raise BuildError(f"receiver {entry['name']} cites "
                                         f"{bcs_id}, which symbols.json does "
                                         "not hold")
                    if bcs_id not in ids:
                        ids.append(bcs_id)
                    if bcs_id not in all_symbols:
                        all_symbols.append(bcs_id)
                if ids:
                    record["symbolsByRole"][group] = ids
            for opcode in entry["opcodes"]:
                row = index.touch("s2c", opcode["opcodeHex"], "receiver-map")
                index.add(row, "receivers", entry["name"])
                for bcs_id in all_symbols:
                    index.add(row, "symbols", bcs_id)
                if row["id"] not in record["opcodes"]:
                    record["opcodes"].append(row["id"])
            if entry.get("luaCallback"):
                record["luaCallback"] = entry["luaCallback"]
            for key in ("needsReverify", "reverifyMethod"):
                if key in entry:
                    record[key] = entry[key]
            casts = _casts(entry.get("castTarget"), f"receiver {entry['name']}")
            writes = field_writes.get(entry["name"])
            if writes:
                record["sources"].append("receiver-field-writes")
                record["slot1Address"] = writes["slot1Va"]
                record["dispatchKind"] = writes["kind"]
                if writes.get("workers"):
                    record["workerAddresses"] = list(writes["workers"])
                if not casts:
                    casts = _casts(writes.get("castTarget"),
                                   f"field writes {entry['name']}")
            if casts:
                record["casts"] = casts
            receivers.append(record)

    # A receiver known only to the field-write catalog still names an opcode.
    # It carries no namespace and no confidence because that catalog states
    # neither, and guessing one would manufacture an evidence tier.
    for name, writes in field_writes.items():
        if any(r["name"] == name for r in receivers):
            continue
        row = index.touch("s2c", writes["opcodeHex"], "receiver-field-writes")
        index.add(row, "receivers", name)
        record = {
            "name": name,
            "classification": "field-write-only",
            "symbolsByRole": {},
            "opcodes": [row["id"]],
            "sources": ["receiver-field-writes"],
            "slot1Address": writes["slot1Va"],
            "dispatchKind": writes["kind"],
        }
        casts = _casts(writes.get("castTarget"), f"field writes {name}")
        if casts:
            record["casts"] = casts
        if writes.get("workers"):
            record["workerAddresses"] = list(writes["workers"])
        receivers.append(record)

    # -- operation map -----------------------------------------------------
    operation_doc = sources["operation-map"]
    for entry in operation_doc["operationClasses"]:
        record = {"retailClass": entry["retailClass"], "tail": entry["tail"],
                  "symbols": [], "opcodes": [], "sources": ["operation-map"]}
        for ref in entry.get("bcsRefs") or []:
            bcs_id = ref["bcsId"]
            if bcs_id not in known_symbols:
                raise BuildError(f"operation {entry['retailClass']} cites "
                                 f"{bcs_id}, which symbols.json does not hold")
            if bcs_id not in record["symbols"]:
                record["symbols"].append(bcs_id)
        for opcode in entry["opcodes"]:
            if opcode["direction"] != "serverbound":
                raise BuildError(f"operation {entry['retailClass']} carries "
                                 f"direction {opcode['direction']!r}; only "
                                 "serverbound is modeled")
            row = index.touch("c2s", opcode["opcodeHex"], "operation-map")
            index.name(row, opcode.get("name"), "operation-map")
            index.add(row, "operations", entry["retailClass"])
            for bcs_id in record["symbols"]:
                index.add(row, "symbols", bcs_id)
            edge = {"id": row["id"], "confidence": opcode["confidence"]}
            if edge not in record["opcodes"]:
                record["opcodes"].append(edge)
        operations.append(record)
    for entry in operation_doc["serverboundGap"]:
        row = index.touch("c2s", entry["opcodeHex"], "operation-map")
        index.name(row, entry.get("name"), "operation-map")

    # -- c2s bridge skeleton ----------------------------------------------
    # Candidate Lua APIs remain hypotheses and do not become canonical edges.
    for entry in sources["c2s-skeleton"]["rows"]:
        row = index.touch("c2s", entry["opcodeHex"], "c2s-skeleton")
        index.name(row, entry.get("name"), "c2s-skeleton")
        where = f"c2s skeleton {entry['opcodeHex']}"
        confirmed = [{"luaApi": b["luaApi"], "bcsyRef": b.get("bcsyRef")}
                     for b in (entry.get("confirmedBindings") or [])]
        if entry.get("confirmedBinding") and not confirmed:
            # The older scalar form joins several APIs into one string, with
            # its ids joined in the sibling field the same way. Split both
            # rather than emitting a name no source actually states.
            apis = [a.strip() for a in entry["confirmedBinding"].split(";")]
            ids = BCS_Y_TOKEN_RE.findall(entry.get("confirmedBcsy") or "")
            if ids and len(ids) != len(apis):
                raise BuildError(f"{where}: confirmedBinding names "
                                 f"{len(apis)} APIs but confirmedBcsy names "
                                 f"{len(ids)} ids; the pairing is ambiguous")
            confirmed = [{"luaApi": api, "bcsyRef": ids[i] if ids else None}
                         for i, api in enumerate(apis)]
        for binding in confirmed:
            # Keep qualified `Class._method` names separate from bare Lua bridge keys.
            record = {"luaApi": binding["luaApi"]}
            if binding.get("bcsyRef"):
                record["symbols"] = BCS_Y_TOKEN_RE.findall(binding["bcsyRef"])
                symbol(row, binding["bcsyRef"], where)
            if record not in row.setdefault("c2sBindings", []):
                row["c2sBindings"].append(record)

    # -- lua bridge --------------------------------------------------------
    for lua_name, entry in sorted(sources["lua-bridge"]["bindings"].items()):
        record = {
            "luaName": lua_name,
            "symbols": [],
            "opcodes": [],
            # The Lua bridge names a receiver together with the vtable slot
            # the binding was observed dispatching through, so this edge
            # carries the slot the opcode-level receiver list cannot.
            "receivers": [
                {k: ref[k] for k in
                 ("receiverClass", "namespace", "slot", "confidence")
                 if k in ref}
                for ref in (entry.get("receivers") or [])],
        }
        for ref in entry.get("bcsRefs") or []:
            bcs_id = ref["bcsId"]
            if bcs_id not in known_symbols:
                raise BuildError(f"lua binding {lua_name} cites {bcs_id}, "
                                 "which symbols.json does not hold")
            if bcs_id not in record["symbols"]:
                record["symbols"].append(bcs_id)
        for opcode in entry.get("opcodes") or []:
            # Validated, not coerced: an unmodeled direction must stop the
            # build rather than default into c2s.
            direction = {"inbound": "s2c", "outbound": "c2s"}.get(
                opcode["direction"])
            if direction is None:
                raise BuildError(f"lua binding {lua_name} carries direction "
                                 f"{opcode['direction']!r}; only inbound and "
                                 "outbound are modeled")
            row = index.touch(direction, opcode["opcodeHex"], "lua-bridge")
            index.add(row, "luaBindings", lua_name)
            for bcs_id in record["symbols"]:
                index.add(row, "symbols", bcs_id)
            if row["id"] not in record["opcodes"]:
                record["opcodes"].append(row["id"])
        for key, source_key in (("applyChainBindings", "applyChainBindings"),
                                ("indirectBindings", "indirectBindings")):
            if entry.get(source_key):
                record[key] = len(entry[source_key])
        lua_bindings.append(record)

    opcodes = [index.rows[oid] for oid in sorted(index.rows)]
    for row in opcodes:
        for key in ("names", "receivers", "operations", "luaBindings",
                    "symbols", "sources"):
            if key == "names":
                row[key] = sorted(row[key], key=lambda n: (n["source"],
                                                           n["name"]))
            else:
                row[key] = sorted(row[key])
        if "c2sBindings" in row:
            row["c2sBindings"] = sorted(row["c2sBindings"],
                                        key=lambda b: b["luaApi"])
    identities = [(r["name"], r.get("rttiAddress")) for r in receivers]
    if len(identities) != len(set(identities)):
        duplicated = sorted({i for i in identities
                             if identities.count(i) > 1})
        raise BuildError(f"receiver identity (name, vftable) is not unique: "
                         f"{duplicated}")

    conflicts = sum(1 for row in opcodes
                    if len({n["name"] for n in row["names"]}) > 1)
    summary = {
        "opcodes": len(opcodes),
        "s2c": sum(1 for r in opcodes if r["direction"] == "s2c"),
        "c2s": sum(1 for r in opcodes if r["direction"] == "c2s"),
        "withMatrixRow": sum(1 for r in opcodes if "matrix" in r),
        "withReceiver": sum(1 for r in opcodes if r["receivers"]),
        "withOperation": sum(1 for r in opcodes if r["operations"]),
        "withLuaBinding": sum(1 for r in opcodes if r["luaBindings"]),
        "withSymbol": sum(1 for r in opcodes if r["symbols"]),
        "nameConflicts": conflicts,
        "receivers": len(receivers),
        "operations": len(operations),
        "luaBindings": len(lua_bindings),
    }
    return {
        "sources": [{"role": role, "path": path}
                    for role, path in sorted(RELATIONSHIP_SOURCES.items())],
        "summary": summary,
        "opcodes": opcodes,
        "receivers": sorted(receivers, key=lambda r: (r["name"],
                                                      r.get("rttiAddress", ""))),
        "operations": sorted(operations, key=lambda o: o["retailClass"]),
        "luaBindings": lua_bindings,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_vftable_vas(path: Path) -> set[str]:
    """The known vftable VAs, read from the tracked index.

    The raw dump the index reduces is local evidence and absent from most
    checkouts, so the index is what makes addressCorroboration derivable -
    and this build reproducible - for a reader who has no dump. When the
    dump is present the two must agree, or the index is stale.
    """
    with path.open(encoding="utf-8") as f:
        vas = {va.lower() for va in json.load(f)["vftableVAs"]}

    if RTTI_DUMP_PATH.exists():
        import build_rtti_index
        if vas != set(build_rtti_index.read_dump(RTTI_DUMP_PATH)):
            raise BuildError(
                f"{path.name} disagrees with {RTTI_DUMP_PATH.name}; "
                "rerun tools/build_rtti_index.py")
    return vas


def build(symbols_doc: dict | None = None, structs_doc: dict | None = None,
          overlay: dict | None = None,
          relationship_sources: dict[str, dict] | None = None) -> dict:
    """Build the IR document. Arguments override the on-disk inputs.

    The overrides exist so tools/test_ir_gates.py can plant a defect in one
    input and prove the matching gate fires; the CLI always passes none.
    """
    if relationship_sources is None:
        relationship_sources = {}
        for role, rel in RELATIONSHIP_SOURCES.items():
            with (REPO / rel).open(encoding="utf-8") as f:
                relationship_sources[role] = json.load(f)
    if symbols_doc is None:
        symbols_doc = _symbols_io.load_symbols()
    if structs_doc is None:
        with STRUCTS_PATH.open(encoding="utf-8") as f:
            structs_doc = json.load(f)
    if overlay is None:
        with OVERLAY_PATH.open(encoding="utf-8") as f:
            overlay = json.load(f)
    vftable_vas = load_vftable_vas(RTTI_PATH)

    citations, citation_id = build_citations(
        [(s["id"], s.get("sourceRefs", []))
         for s in structs_doc["structs"]]
        + [(s["id"], s.get("sourceRefs", []))
           for s in symbols_doc["symbols"]])

    alignment_overlay = overlay.get("alignment", {})
    span_overlay = overlay.get("unknownSpanAnnotations", {})
    used_span_keys: set[str] = set()

    types: list[dict] = []
    member_count = 0
    span_count = 0
    for st in sorted(structs_doc["structs"], key=lambda s: s["id"]):
        sid = st["id"]
        where = f"structs.json:{sid}"

        prose = [st.get("notes", "")]
        parsed_fields: list[tuple[dict, dict]] = []
        raw_members: list[dict] = []
        for field in st["fields"]:
            floc = f"{where}.{field.get('name', '?')}"
            offset = parse_offset(field["offset"], floc)
            size = parse_size(field["size"], floc)
            parsed_fields.append((offset, size))
            member = {
                "kind": "field",
                "name": field["name"],
                "offset": offset,
                "size": size,
                "type": field["type"],
            }
            if "absoluteOffset" in field:
                member["absoluteOffset"] = field["absoluteOffset"]
            # Fields carry prose evidence rather than sourceRefs, so the
            # optional member-level citation list stays absent until a field
            # actually cites one.
            if "notes" in field:
                member["notes"] = field["notes"]
                prose.append(field["notes"])
            if "evidence" in field:
                member["evidence"] = field["evidence"]
                prose.append(field["evidence"])
            raw_members.append(member)

        type_size = parse_size(st["size"], where)
        layout, spans = derive_layout(parsed_fields, type_size)

        for start, length in spans:
            key = f"{sid}@0x{start:02X}"
            annotation = {"kind": "unmapped"}
            if key in span_overlay:
                used_span_keys.add(key)
                entry = span_overlay[key]
                annotation = {"kind": entry["kind"], "note": entry["note"],
                              "source": "overlay"}
            raw_members.append({
                "kind": "unknown-span",
                "offset": {"kind": "exact", "raw": f"0x{start:02X}",
                           "bytes": start},
                "size": {"kind": "exact", "raw": f"0x{length:02X}",
                         "bytes": length},
                "annotation": annotation,
            })
        span_count += len(spans)

        # Layout order where it exists, catalog order otherwise. Members with
        # no exact offset have no position to sort into, so they follow.
        def _key(item: tuple[int, dict]) -> tuple[int, int, int]:
            index, member = item
            offset = member["offset"]
            if offset["kind"] == "exact":
                return (0, offset["bytes"], index)
            return (1, 0, index)

        members = [m for _, m in sorted(enumerate(raw_members), key=_key)]
        member_count += len(members)

        alignment = {"kind": "unknown",
                     "reason": "no catalog records alignment for this type; "
                               "deriving it from offsets would be inference"}
        if sid in alignment_overlay:
            entry = alignment_overlay[sid]
            alignment = {"kind": "exact", "bytes": entry["bytes"],
                         "reason": entry["reason"], "source": "overlay"}

        record = {
            "id": sid,
            "name": st["name"],
            "namespace": parse_namespace(st["namespace"], where),
        }
        if "aliases" in st:
            record["aliases"] = st["aliases"]
        record.update({
            "confidence": st["confidence"],
            "size": type_size,
            "alignment": alignment,
            "bases": {"status": "deferred", "owner": "C1c"},
            "vtable": {"status": "deferred", "owner": "C1c"},
            "layout": layout,
            "members": members,
            "citations": [citation_id[r] for r in st.get("sourceRefs", []) if r],
        })
        if "notes" in st:
            record["notes"] = st["notes"]
        for key in ("needsReverify", "reverifyMethod"):
            if key in st:
                record[key] = st[key]
        types.append(record)

    unknown_span_keys = set(span_overlay) - used_span_keys
    if unknown_span_keys:
        raise BuildError(
            "ir_overlay.json unknownSpanAnnotations names spans the build does "
            f"not derive: {sorted(unknown_span_keys)}")
    unknown_alignment = set(alignment_overlay) - {t["id"] for t in types}
    if unknown_alignment:
        raise BuildError("ir_overlay.json alignment names unknown types: "
                         f"{sorted(unknown_alignment)}")

    symbols: list[dict] = []
    for sym in sorted(symbols_doc["symbols"], key=lambda s: s["id"]):
        yid = sym["id"]
        address = parse_address(sym["address"], f"symbols.json:{yid}")
        if sym["kind"] not in VFTABLE_BEARING_KINDS or address["kind"] != "scalar":
            corroboration = "not-applicable"
        elif address["values"][0].lower() in vftable_vas:
            corroboration = "matches-rtti-extraction"
        else:
            corroboration = "absent-from-rtti-extraction"

        record = {
            "id": yid,
            "name": sym["name"],
            "kind": sym["kind"],
            "address": address,
            "addressCorroboration": corroboration,
            "confidence": sym["confidence"],
        }
        record["citations"] = [citation_id[r] for r in sym.get("sourceRefs", [])
                               if r]
        if "notes" in sym:
            record["notes"] = sym["notes"]
        for key in ("needsReverify", "reverifyMethod"):
            if key in sym:
                record[key] = sym[key]
        symbols.append(record)

    relationships = build_relationships(
        relationship_sources, {s["id"] for s in symbols_doc["symbols"]})

    inputs = [
        {"path": rel, "sha256": _sha256(REPO / rel)}
        for rel in sorted([
            "manifests/ir_overlay.json",
            "manifests/rtti_vftable_index.json",
            "manifests/structs.json",
            "manifests/symbols.json",
        ] + list(RELATIONSHIP_SOURCES.values()))
    ]

    return {
        "irVersion": IR_VERSION,
        "gameVersion": GAME_VERSION,
        "generator": {"tool": "tools/build_ir.py",
                      "generatorVersion": GENERATOR_VERSION,
                      "schema": SCHEMA_REF},
        "inputs": inputs,
        "dimensions": {
            "namespaces": {"status": "populated",
                           "note": "recorded verbatim and classified; the two "
                                   "conventions are not unified here"},
            "sizes": {"status": "populated",
                      "note": "parsed into exact/annotated/bounded/variable/"
                              "unknown/logical beside the raw value"},
            "offsets": {"status": "populated",
                        "note": "parsed into exact/element-relative/variable/none"},
            "unknownSpans": {"status": "populated",
                             "note": "derived as the complement of the recorded "
                                     "fields inside each type's extent"},
            "confidence": {"status": "populated",
                           "note": "copied from the source catalogs unchanged"},
            "functions": {"status": "populated",
                          "note": "the BCS-Y symbol layer, addresses verbatim"},
            "evidenceRefs": {"status": "populated",
                             "note": "every distinct sourceRef normalized and "
                                     "reverse-indexed, unresolved ones included"},
            "alignment": {"status": "declared-unknown",
                          "note": "no catalog records it; ir_overlay.json is "
                                  "the sole home once evidence exists"},
            "bases": {"status": "deferred", "owner": "C1c",
                      "note": "the facts live in 21 frozen phase snapshots and "
                              "need a per-source adapter each"},
            "vtables": {"status": "deferred", "owner": "C1c",
                        "note": "slot layouts live in the same frozen snapshots"},
            "payloadRelationships": {"status": "populated",
                                     "note": "opcode, receiver, operation and "
                                             "Lua-bridge edges joined from six "
                                             "sources, direction-keyed"},
            "payloadTypeBindings": {"status": "deferred", "owner": "C1c",
                                    "note": "no catalog states a type-to-opcode "
                                            "edge; the available signal is the "
                                            "'<Receiver>Payload' name convention "
                                            "and prose hex, both inference"},
        },
        "counts": {
            "types": len(types),
            "symbols": len(symbols),
            "citations": len(citations),
            "members": member_count,
            "unknownSpans": span_count,
            "opcodes": relationships["summary"]["opcodes"],
        },
        "types": types,
        "symbols": symbols,
        "citations": citations,
        "relationships": relationships,
    }


def serialize(document: dict) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="rebuild and compare against the committed file")
    args = parser.parse_args()

    try:
        document = build()
    except BuildError as e:
        print(f"BUILD ERROR: {e}", file=sys.stderr)
        return 1

    text = serialize(document)

    if args.check:
        if not OUT_PATH.exists():
            print(f"FAIL: {OUT_PATH.name} does not exist", file=sys.stderr)
            return 1
        current = OUT_PATH.read_text(encoding="utf-8")
        if current != text:
            print(f"FAIL: {OUT_PATH.name} is not what tools/build_ir.py "
                  "produces from the current inputs; rerun without --check",
                  file=sys.stderr)
            return 1
        print(f"OK: {OUT_PATH.name} matches a fresh build "
              f"({document['counts']['types']} types, "
              f"{document['counts']['symbols']} symbols, "
              f"{document['counts']['citations']} citations)")
        return 0

    tmp = OUT_PATH.with_name(f"{OUT_PATH.name}.{os.getpid()}.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, OUT_PATH)
    print(f"wrote {OUT_PATH.relative_to(REPO)}: "
          f"{document['counts']['types']} types, "
          f"{document['counts']['symbols']} symbols, "
          f"{document['counts']['members']} members "
          f"({document['counts']['unknownSpans']} unknown spans), "
          f"{document['counts']['citations']} citations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
