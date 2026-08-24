#!/usr/bin/env python3
"""Mutation tests for the exhaustive reference export contract."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import verify_reference_export as verifier


REPO = Path(__file__).resolve().parents[1]
JAVA = REPO / "ghidra" / "FindReferences.java"
WRAPPER = REPO / "tools" / "ghidra" / "export-references.ps1"


def complete_report() -> list[str]:
    return [
        "XIVL_REFERENCE_EXPORT_V1",
        "Program: ffxivgame.exe",
        "Mode: STRING",
        "Coverage: every Ghidra-recorded reference to each resolved target",
        "Limit: computed, indirect, dynamic, and unanalyzed references may be absent",
        "String match: EXACT",
        "String queries: 1",
        "Defined strings scanned: 4",
        'STRING QUERY: "a"',
        "Defined-data matches: 1",
        'MATCH: 0x00cdc510 section=.rdata type=string value="a"',
        "References to target: 2",
        "REF from=0x00401000 operand=0 type=DATA source=ANALYSIS primary=false owner=function FUN_00401000 @ 0x00401000",
        "REF from=0x00402000 operand=1 type=READ source=ANALYSIS primary=true owner=function FUN_00402000 @ 0x00402000",
        "COMPLETE: FindReferences defined_strings=4 queries=1 matches=1 references=2",
    ]


def complete_address_report() -> list[str]:
    return [
        "XIVL_REFERENCE_EXPORT_V1",
        "Program: ffxivgame.exe",
        "Mode: ADDRESS",
        "Coverage: every Ghidra-recorded reference to each resolved target",
        "Limit: computed, indirect, dynamic, and unanalyzed references may be absent",
        "Address inputs: 0x00cdc510",
        "Targets processed: 1",
        "TARGET ADDRESS: 0x00cdc510",
        "Target section: .rdata",
        "References to target: 0",
        "COMPLETE: FindReferences targets=1 references=0",
    ]


class ReferenceExportTests(unittest.TestCase):
    def verify(self, lines: list[str]) -> None:
        with tempfile.TemporaryDirectory(prefix="reference-export-test-") as raw:
            path = Path(raw) / "report.txt"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            verifier.verify(path)

    def assert_rejected(self, lines: list[str]) -> None:
        with self.assertRaises(verifier.VerificationError):
            self.verify(lines)

    def test_explicit_short_string_passes(self) -> None:
        self.verify(complete_report())
        source = JAVA.read_text(encoding="utf-8")
        self.assertNotIn("length() < 4", source)
        self.assertNotIn("length() <= 4", source)

    def test_cancellation_and_failure_are_not_complete(self) -> None:
        for status in ("CANCELLED monitor cancelled", "FAILED bad target"):
            lines = complete_report()
            lines[-1] = "INCOMPLETE: " + status
            self.assert_rejected(lines)

    def test_limit_truncation_is_not_complete(self) -> None:
        lines = complete_report()
        lines[-1] = "INCOMPLETE: PARTIAL reference limit exceeded"
        self.assert_rejected(lines)

        lines = complete_report()
        lines[11] = "References to target: 1"
        self.assert_rejected(lines)

    def test_completed_zero_match_is_a_safe_negative(self) -> None:
        lines = complete_report()
        del lines[10:14]
        lines[9] = "Defined-data matches: 0"
        lines[-1] = ("COMPLETE: FindReferences defined_strings=4 queries=1 "
                     "matches=0 references=0")
        self.verify(lines)

    def test_reference_order_and_summary_drift_fail(self) -> None:
        lines = complete_report()
        lines[12], lines[13] = lines[13], lines[12]
        self.assert_rejected(lines)

        lines = complete_report()
        lines[-1] = lines[-1].replace("references=2", "references=3")
        self.assert_rejected(lines)

    def test_malformed_target_and_match_rows_fail(self) -> None:
        lines = complete_address_report()
        lines[7] = "TARGET ADDRESS: -1"
        self.assert_rejected(lines)

        lines = complete_report()
        lines[10] = "MATCH: 0x00cdc510 "
        self.assert_rejected(lines)

    def test_wrapper_forces_read_only_and_verification(self) -> None:
        source = WRAPPER.read_text(encoding="utf-8")
        self.assertIn("-Script FindReferences.java -ReadOnly", source)
        self.assertIn("verify_reference_export.py", source)
        self.assertIn("Output already exists", source)

    def test_exporter_has_bounded_partial_and_atomic_paths(self) -> None:
        source = JAVA.read_text(encoding="utf-8")
        for required in (
            "MAX_TARGETS = 256", "MAX_QUERIES = 256",
            "HARD_MAX_MATCHES = 4096", "HARD_MAX_REFERENCES = 100000",
            "totalMatches == maxMatches", "totalReferences == maxReferences",
            "Status.CANCELLED", "Status.PARTIAL", "Status.FAILED",
            "StandardCopyOption.ATOMIC_MOVE", "monitor.checkCancelled()",
        ):
            self.assertIn(required, source)

    def test_java_utf16_query_order_is_accepted(self) -> None:
        lines = complete_report()
        lines[6] = "String queries: 2"
        lines[8:14] = [
            'STRING QUERY: "\\ud800\\udc00"',
            "Defined-data matches: 0",
            'STRING QUERY: "\\ue000"',
            "Defined-data matches: 0",
        ]
        lines[-1] = ("COMPLETE: FindReferences defined_strings=4 queries=2 "
                     "matches=0 references=0")
        self.verify(lines)

    def test_impossible_export_counts_fail(self) -> None:
        lines = complete_report()
        lines[6] = "String queries: 0"
        self.assert_rejected(lines)
        lines = complete_report()
        lines[7] = "Defined strings scanned: -1"
        self.assert_rejected(lines)


if __name__ == "__main__":
    unittest.main(verbosity=2)
