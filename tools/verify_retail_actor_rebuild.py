#!/usr/bin/env python3
"""Verify the fixed actor-rebuild retail-input observation contract."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _schema_check  # noqa: E402
import _symbols_io  # noqa: E402


REPO = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO / "tools" / "fixtures" / "retail_actor_rebuild_observations.json"
DEFAULT_CHECK = REPO / "manifests" / "retail_actor_rebuild_check.json"
DEFAULT_RETAIL_INPUTS = REPO / "manifests" / "retail_inputs.json"
DEFAULT_SCHEMA = REPO / "schemas" / "retail-evidence-attestation-v1.schema.json"

CHECK_ID = "actor-rebuild-receiver-field-v1"
INPUT_ID = "ffxivgame-1.23b"
INPUT_FILENAME = "ffxivgame.exe"
INPUT_SIZE = 15996808
INPUT_SHA256 = "9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9"
PRIVATE_REPOSITORY = "XIVLegacy/xivl-private-assets"
PRIVATE_COMMIT = "aeb52f6dbde95a793ee6d52be28de9f28a885b15"
PRIVATE_PATH = "ffxivgame.exe"
SCHEMA_VERSION = 1
TOOL_VERSIONS = {
    "ghidra": "12.1.3",
    "jdk": "21.0.12.1+1",
    "verifier": "1.0",
}

TARGETS: tuple[dict[str, str], ...] = (
    {"bcsId": "BCS-Y-0525", "kind": "function_case", "address": "0x004DC690"},
    {"bcsId": "BCS-Y-0588", "kind": "function", "address": "0x00574780"},
    {"bcsId": "BCS-Y-0613", "kind": "function", "address": "0x00575860"},
    {"bcsId": "BCS-Y-1019", "kind": "function", "address": "0x00774AD0"},
    {"bcsId": "BCS-Y-1020", "kind": "function", "address": "0x00764630"},
)
SUPPORTING_CONTEXT = {
    "bcsId": "BCS-Y-0280", "kind": "function", "address": "0x004D8860"
}
EXPECTED_OBSERVATIONS: tuple[dict[str, Any], ...] = (
    {"kind": "write", "instruction_va": "0x004DCCDD", "owner_va": "0x004DC690", "width": "byte", "displacement": "0x00000092", "immediate": 1},
    {"kind": "compare", "instruction_va": "0x004D8863", "owner_va": "0x004D8860", "width": "byte", "displacement": "0x00000092", "immediate": 0},
    {"kind": "call", "instruction_va": "0x004D88AB", "owner_va": "0x004D8860", "target_va": "0x00575860"},
    {"kind": "write", "instruction_va": "0x004D88B0", "owner_va": "0x004D8860", "width": "byte", "displacement": "0x00000092", "immediate": 0},
    {"kind": "write", "instruction_va": "0x004D88EA", "owner_va": "0x004D8860", "width": "byte", "displacement": "0x00000092", "immediate": 0},
    {"kind": "call", "instruction_va": "0x004D8902", "owner_va": "0x004D8860", "target_va": "0x00574780"},
    {"kind": "call", "instruction_va": "0x005747FB", "owner_va": "0x00574780", "target_va": "0x00774AD0"},
    {"kind": "call", "instruction_va": "0x005758C4", "owner_va": "0x00575860", "target_va": "0x00764630"},
)

ADDRESS_RE = re.compile(r"^0x[0-9A-F]{8}$")
COMMON_KEYS = frozenset({"kind", "instruction_va", "owner_va"})
FIELD_KEYS = COMMON_KEYS | {"width", "displacement", "immediate"}
CALL_KEYS = COMMON_KEYS | {"target_va"}
ROOT_KEYS = frozenset({
    "check", "program", "image_base", "language", "compiler_spec",
    "analysis_complete", "observations", "complete", "completion_marker",
})


class VerificationError(Exception):
    """Malformed input that is safe to report without its contents."""


def _read_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError("JSON input could not be read") from exc


def _fingerprints(rows: Iterable[dict[str, Any]]) -> tuple[str, ...]:
    return tuple(sorted(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows))


def validate_observations(value: Any) -> list[str]:
    if not isinstance(value, list):
        return ["observations are not an array"]
    errors: list[str] = []
    seen: set[str] = set()
    for row in value:
        if not isinstance(row, dict):
            errors.append("observation is not an object")
            continue
        kind = row.get("kind")
        expected_keys = CALL_KEYS if kind == "call" else FIELD_KEYS
        if kind not in {"call", "write", "compare"} or frozenset(row) != expected_keys:
            errors.append("observation shape is invalid")
            continue
        if not all(isinstance(row.get(key), str) and ADDRESS_RE.fullmatch(row[key])
                   for key in ("instruction_va", "owner_va")):
            errors.append("observation address is malformed")
        if kind == "call":
            if not isinstance(row["target_va"], str) or not ADDRESS_RE.fullmatch(row["target_va"]):
                errors.append("call target is malformed")
        elif (row["width"] != "byte"
              or not isinstance(row["displacement"], str)
              or not ADDRESS_RE.fullmatch(row["displacement"])
              or not isinstance(row["immediate"], int)
              or isinstance(row["immediate"], bool)):
            errors.append("field observation is malformed")
        fingerprint = json.dumps(row, sort_keys=True, separators=(",", ":"))
        if fingerprint in seen:
            errors.append("observation is duplicated")
        seen.add(fingerprint)
    return errors


def _check_exact_observations(value: Any, label: str) -> list[str]:
    errors = validate_observations(value)
    if errors:
        return [f"{label} shape is invalid"]
    if _fingerprints(value) != _fingerprints(EXPECTED_OBSERVATIONS):
        return [f"{label} exact set differs"]
    return []


def _catalog_errors(symbols: Any, declared_targets: Any, declared_context: Any) -> list[str]:
    if _fingerprints(declared_targets) != _fingerprints(TARGETS):
        return ["target declarations drifted"]
    if declared_context != SUPPORTING_CONTEXT:
        return ["supporting context declaration drifted"]
    entries = symbols.get("symbols") if isinstance(symbols, dict) else None
    if not isinstance(entries, list):
        return ["symbols catalog is malformed"]
    errors: list[str] = []
    for expected in (*TARGETS, SUPPORTING_CONTEXT):
        matches = [entry for entry in entries
                   if isinstance(entry, dict) and entry.get("id") == expected["bcsId"]]
        if len(matches) != 1:
            errors.append("required BCS entry is not unique")
        elif any(matches[0].get(key) != expected[key] for key in ("kind", "address")):
            errors.append("required BCS entry drifted")
    return errors


def _retail_input_errors(document: Any) -> list[str]:
    expected = {
        "schemaVersion": 1,
        "inputs": [{
            "id": INPUT_ID,
            "filename": INPUT_FILENAME,
            "size": INPUT_SIZE,
            "sha256": INPUT_SHA256,
            "source": {"repository": PRIVATE_REPOSITORY, "commit": PRIVATE_COMMIT, "path": PRIVATE_PATH},
            "allowedChecks": [CHECK_ID],
        }],
    }
    return [] if document == expected else ["retail input grant drifted"]


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO, check=True,
            capture_output=True, text=True,
        )
        commit = result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        commit = "0" * 40
    return commit if re.fullmatch(r"[0-9a-f]{40}", commit) else "0" * 40


def build_attestation(status: str) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "publicRepositoryCommit": _git_commit(),
        "approvedInputSha256": INPUT_SHA256,
        "toolVersions": dict(TOOL_VERSIONS),
        "check": {"id": CHECK_ID, "version": 1},
        "result": {"status": status},
    }


def verify(
    input_path: Path = DEFAULT_INPUT,
    check_path: Path = DEFAULT_CHECK,
    retail_inputs_path: Path = DEFAULT_RETAIL_INPUTS,
    symbols_path: Path = _symbols_io.SYMBOLS_PATH,
) -> list[str]:
    observations = _read_json(input_path)
    check = _read_json(check_path)
    retail_inputs = _read_json(retail_inputs_path)
    symbols = _symbols_io.load_symbols(symbols_path)
    errors = _retail_input_errors(retail_inputs)

    if not isinstance(check, dict):
        errors.append("check manifest is malformed")
        check = {}
    if (check.get("schemaVersion"), check.get("checkId"), check.get("approvedInputId"),
        check.get("approvedInputSha256")) != (SCHEMA_VERSION, CHECK_ID, INPUT_ID, INPUT_SHA256):
        errors.append("check identity drifted")
    if frozenset(check) != frozenset({
        "schemaVersion", "checkId", "approvedInputId", "approvedInputSha256",
        "targets", "supportingContext", "observations",
    }):
        errors.append("check manifest shape drifted")
    errors.extend(_catalog_errors(symbols, check.get("targets"), check.get("supportingContext")))
    errors.extend(_check_exact_observations(check.get("observations"), "expected observations"))

    if not isinstance(observations, dict) or frozenset(observations) != ROOT_KEYS:
        errors.append("observation document shape is invalid")
        observations = {}
    if (
        observations.get("check") != CHECK_ID
        or observations.get("program") != INPUT_FILENAME
        or observations.get("image_base") != "0x00400000"
        or observations.get("language") != "x86:LE:32:default"
        or observations.get("compiler_spec") != "windows"
        or observations.get("analysis_complete") is not True
        or observations.get("complete") is not True
        or observations.get("completion_marker") != "complete"
    ):
        errors.append("observation document identity is invalid")
    errors.extend(_check_exact_observations(observations.get("observations"), "observations"))
    return errors


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, dest="input_path")
    parser.add_argument("--check", type=Path, default=DEFAULT_CHECK, dest="check_path")
    parser.add_argument("--retail-inputs", type=Path, default=DEFAULT_RETAIL_INPUTS)
    parser.add_argument("--symbols", type=Path, default=_symbols_io.SYMBOLS_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        errors = verify(args.input_path, args.check_path, args.retail_inputs, args.symbols)
    except (VerificationError, OSError, KeyError, TypeError, ValueError):
        errors = ["verification input is malformed"]
    attestation = build_attestation("pass" if not errors else "fail")
    try:
        schema = _schema_check.load_schema(DEFAULT_SCHEMA)
        schema_errors = _schema_check.validate(attestation, schema)
    except (OSError, ValueError, _schema_check.SchemaError):
        schema_errors = ["schema unavailable"]
    if schema_errors:
        errors.append("attestation schema rejected output")
        attestation = build_attestation("fail")
    print(json.dumps(attestation, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
