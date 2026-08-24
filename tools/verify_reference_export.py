#!/usr/bin/env python3
"""Reject incomplete, truncated, or internally drifting reference exports."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


class VerificationError(ValueError):
    pass


REF_RE = re.compile(
    r"^REF from=(0x[0-9a-f]{8,16}) operand=(-?\d+) type=(\S+) "
    r"source=(\S+) primary=(true|false) owner=.+$"
)
TARGET_RE = re.compile(r"^TARGET ADDRESS: (0x[0-9a-f]{8,16})$")
MATCH_RE = re.compile(
    r"^MATCH: (0x[0-9a-f]{8,16}) section=(\S+) type=(.+) value=(\".*\")$"
)


def _required_number(lines: list[str], prefix: str, minimum: int = 0) -> int:
    matches = [line for line in lines if line.startswith(prefix)]
    if len(matches) != 1:
        raise VerificationError(f"expected one {prefix!r} line")
    try:
        value = int(matches[0][len(prefix):])
    except ValueError as exc:
        raise VerificationError(f"invalid number after {prefix!r}") from exc
    if value < minimum:
        raise VerificationError(f"number after {prefix!r} must be at least {minimum}")
    return value


def _java_string_key(value: str) -> bytes:
    return value.encode("utf-16-be", errors="surrogatepass")


def _reference_groups(lines: list[str]) -> tuple[int, int]:
    group_count = 0
    reference_count = 0
    for index, line in enumerate(lines):
        if not line.startswith("References to target: "):
            continue
        group_count += 1
        try:
            declared = int(line.removeprefix("References to target: "))
        except ValueError as exc:
            raise VerificationError("invalid per-target reference count") from exc

        keys: list[tuple[int, int, str, str, bool]] = []
        cursor = index + 1
        while cursor < len(lines) and lines[cursor].startswith("REF "):
            match = REF_RE.fullmatch(lines[cursor])
            if not match:
                raise VerificationError("malformed REF row")
            keys.append((
                int(match.group(1), 16), int(match.group(2)), match.group(3),
                match.group(4), match.group(5) == "true",
            ))
            cursor += 1
        if len(keys) != declared:
            raise VerificationError("per-target reference count drift")
        if keys != sorted(keys):
            raise VerificationError("reference rows are not deterministic")
        reference_count += len(keys)
    if reference_count != len([line for line in lines if line.startswith("REF ")]):
        raise VerificationError("REF row is not attached to a target")
    return group_count, reference_count


def _verify_address(lines: list[str], summary: str) -> None:
    targets = _required_number(lines, "Targets processed: ", minimum=1)
    target_rows = [line for line in lines if line.startswith("TARGET ADDRESS: ")]
    if len(target_rows) != targets:
        raise VerificationError("address target count drift")
    target_matches = [TARGET_RE.fullmatch(line) for line in target_rows]
    if any(match is None for match in target_matches):
        raise VerificationError("malformed TARGET ADDRESS row")
    addresses = [int(match.group(1), 16) for match in target_matches if match]
    if addresses != sorted(set(addresses)):
        raise VerificationError("address targets are not unique and sorted")

    groups, references = _reference_groups(lines)
    if groups != targets:
        raise VerificationError("address target/reference group drift")
    expected = f"targets={targets} references={references}"
    if summary != expected:
        raise VerificationError("address completion summary drift")


def _verify_string(lines: list[str], summary: str) -> None:
    query_count = _required_number(lines, "String queries: ", minimum=1)
    defined_strings = _required_number(lines, "Defined strings scanned: ")
    query_rows = [line.removeprefix("STRING QUERY: ") for line in lines
                  if line.startswith("STRING QUERY: ")]
    if len(query_rows) != query_count:
        raise VerificationError("string query count drift")
    try:
        queries = [json.loads(row) for row in query_rows]
    except json.JSONDecodeError as exc:
        raise VerificationError("malformed quoted string query") from exc
    if any(not isinstance(query, str) or not query for query in queries):
        raise VerificationError("string queries must be non-empty strings")
    if queries != sorted(set(queries), key=_java_string_key):
        raise VerificationError("string queries are not unique and sorted")

    match_counts = [int(line.removeprefix("Defined-data matches: "))
                    for line in lines if line.startswith("Defined-data matches: ")]
    if len(match_counts) != query_count:
        raise VerificationError("per-query match count drift")
    matches = len([line for line in lines if line.startswith("MATCH: ")])
    if sum(match_counts) != matches:
        raise VerificationError("string match count drift")

    query_match_lists: list[list[int]] = []
    for line in lines:
        if line.startswith("STRING QUERY: "):
            query_match_lists.append([])
        elif line.startswith("MATCH: "):
            match = MATCH_RE.fullmatch(line)
            if not match:
                raise VerificationError("malformed MATCH row")
            try:
                value = json.loads(match.group(4))
            except json.JSONDecodeError as exc:
                raise VerificationError("malformed quoted MATCH value") from exc
            if not isinstance(value, str):
                raise VerificationError("MATCH value must be a string")
            if not query_match_lists:
                raise VerificationError("MATCH row precedes every string query")
            query_match_lists[-1].append(int(match.group(1), 16))
    if len(query_match_lists) != query_count:
        raise VerificationError("could not associate matches with queries")
    if [len(addresses) for addresses in query_match_lists] != match_counts:
        raise VerificationError("per-query string match count drift")
    if any(addresses != sorted(addresses) for addresses in query_match_lists):
        raise VerificationError("string matches are not address-sorted")

    groups, references = _reference_groups(lines)
    if groups != matches:
        raise VerificationError("string match/reference group drift")
    expected = (f"defined_strings={defined_strings} queries={query_count} "
                f"matches={matches} references={references}")
    if summary != expected:
        raise VerificationError("string completion summary drift")


def verify(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "XIVL_REFERENCE_EXPORT_V1":
        raise VerificationError("missing reference export format marker")
    if any(line.startswith("INCOMPLETE:") for line in lines):
        raise VerificationError("reference export is incomplete")

    complete = [line for line in lines if line.startswith("COMPLETE: FindReferences ")]
    if len(complete) != 1 or complete[0] != lines[-1]:
        raise VerificationError("completion marker must be unique and terminal")
    summary = complete[0].removeprefix("COMPLETE: FindReferences ")

    modes = [line.removeprefix("Mode: ") for line in lines
             if line.startswith("Mode: ")]
    if modes == ["ADDRESS"]:
        _verify_address(lines, summary)
    elif modes == ["STRING"]:
        _verify_string(lines, summary)
    else:
        raise VerificationError("mode is missing or invalid")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        verify(args.report)
    except (OSError, VerificationError) as exc:
        parser.error(str(exc))
    print(f"Verified complete reference export: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
