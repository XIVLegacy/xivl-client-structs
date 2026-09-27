"""Check bridge reconstruction and preservation at the curated-input boundary."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_c2s_bridge_skeleton as c2s
from extractors import build_data_dependency_catalog as dependency
from extractors import build_substruct_cross_ref as substruct


def render(document: dict) -> bytes:
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


class BridgeCatalogTests(unittest.TestCase):
    def invoke(self, builder, *arguments: str) -> int:
        with (
            patch.object(sys, "argv", [builder.__file__, *arguments]),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            return builder.main()

    def test_reconstruction_without_previous_output(self) -> None:
        for builder in (c2s, dependency):
            with (
                self.subTest(builder=builder.__name__),
                tempfile.TemporaryDirectory() as raw,
            ):
                expected = builder.OUT_JSON.read_bytes()
                output = Path(raw) / "catalog.json"
                with patch.object(builder, "OUT_JSON", output):
                    self.assertEqual(self.invoke(builder, "--check"), 1)
                    self.assertFalse(output.exists())
                    self.assertEqual(self.invoke(builder), 0)
                    self.assertEqual(output.read_bytes(), expected)
                    self.assertEqual(self.invoke(builder, "--check"), 0)

    def test_check_rejects_same_key_row_loss_without_writing(self) -> None:
        for builder, key in ((c2s, "rows"), (dependency, "confirmedIndirectBindings")):
            with (
                self.subTest(builder=builder.__name__),
                tempfile.TemporaryDirectory() as raw,
            ):
                document = builder.build_catalog()
                document[key].pop()
                output = Path(raw) / "catalog.json"
                original = render(document)
                output.write_bytes(original)
                with patch.object(builder, "OUT_JSON", output):
                    self.assertEqual(self.invoke(builder, "--check"), 1)
                self.assertEqual(output.read_bytes(), original)

    def test_missing_curated_input_preserves_output(self) -> None:
        for builder in (c2s, dependency):
            with (
                self.subTest(builder=builder.__name__),
                tempfile.TemporaryDirectory() as raw,
            ):
                output = Path(raw) / "catalog.json"
                output.write_bytes(b"previous catalog\n")
                with (
                    patch.object(builder, "OUT_JSON", output),
                    patch.object(builder, "CURATED_JSON", Path(raw) / "missing.json"),
                ):
                    self.assertEqual(self.invoke(builder), 1)
                self.assertEqual(output.read_bytes(), b"previous catalog\n")

    def test_candidates_do_not_publish_or_require_curated_input(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "catalog.json"
            output.write_bytes(b"retained catalog\n")
            captured = io.StringIO()
            with (
                patch.object(c2s, "OUT_JSON", output),
                patch.object(c2s, "CURATED_JSON", Path(raw) / "missing.json"),
                patch.object(sys, "argv", [c2s.__file__, "--candidates"]),
                contextlib.redirect_stdout(captured),
            ):
                self.assertEqual(c2s.main(), 0)
            self.assertTrue(json.loads(captured.getvalue())["rows"])
            self.assertEqual(output.read_bytes(), b"retained catalog\n")

    def test_curated_bindings_and_shared_findings_survive(self) -> None:
        original = dependency.build_catalog()
        curated = json.loads(dependency.CURATED_JSON.read_text(encoding="utf-8"))
        entry = copy.deepcopy(curated["confirmedIndirectBindings"][0])
        entry["luaName"] = "_testCuratedBinding"
        entry["sourceRefs"] = ["manifests/test-evidence.json"]
        curated["confirmedIndirectBindings"].append(entry)
        rebuilt = dependency.build_catalog(curated)
        self.assertEqual(rebuilt["confirmedIndirectBindings"][-1], entry)
        self.assertEqual(
            rebuilt["totals"]["confirmedBindings"],
            original["totals"]["confirmedBindings"] + 1,
        )
        self.assertEqual(rebuilt["payloadStructs"], original["payloadStructs"])

        with tempfile.TemporaryDirectory() as raw:
            shared = json.loads(c2s.CURATED_JSON.read_text(encoding="utf-8"))
            shared["outboundFindings"]["expandedReverseBfs"]["sourceRefs"] = [
                "test:evidence"
            ]
            path = Path(raw) / "c2s.json"
            path.write_bytes(render(shared))
            with (
                patch.object(c2s, "CURATED_JSON", path),
                patch.object(dependency, "C2S_CURATED_JSON", path),
            ):
                self.assertEqual(
                    c2s.build_catalog()["expandedReverseBfs"]["sourceRefs"],
                    ["test:evidence"],
                )
                self.assertEqual(
                    dependency.build_catalog()["expandedReverseBfs"]["sourceRefs"],
                    ["test:evidence"],
                )
                self.assertEqual(
                    dependency.build_catalog()["directEmissionMining"],
                    original["directEmissionMining"],
                )

    def test_curated_collisions_and_changed_evidence_source_fail(self) -> None:
        curated = json.loads(dependency.CURATED_JSON.read_text(encoding="utf-8"))
        existing_key = next(iter(dependency.build_catalog()["receiverWriteIndex"]))
        curated["additionalReceiverWriteIndex"][existing_key] = []
        with self.assertRaisesRegex(ValueError, "collide"):
            dependency.build_catalog(curated)
        curated = json.loads(dependency.CURATED_JSON.read_text(encoding="utf-8"))
        curated["recursiveMatchSources"][0]["expectedSource"] = "unrelated"
        with self.assertRaisesRegex(ValueError, "evidence source changed"):
            dependency.build_catalog(curated)

    def test_substruct_writer_updates_curated_input_and_rebuilds(self) -> None:
        curated = json.loads(dependency.CURATED_JSON.read_text(encoding="utf-8"))
        curated["confirmedIndirectBindings"] = [
            row
            for row in curated["confirmedIndirectBindings"]
            if not (
                row["luaName"] == "_getNetStatUser"
                and row.get("writingOpcode") == "0x0145"
            )
        ]
        self.assertLess(
            len(curated["confirmedIndirectBindings"]),
            len(dependency.build_catalog()["confirmedIndirectBindings"]),
        )
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "input.json"
            output = Path(raw) / "catalog.json"
            source.write_bytes(render(curated))
            output.write_bytes(b"not a source of evidence\n")
            with (
                patch.object(dependency, "CURATED_JSON", source),
                patch.object(dependency, "OUT_JSON", output),
            ):
                self.assertEqual(self.invoke(substruct), 0)
                updated = json.loads(source.read_bytes())
                self.assertTrue(
                    any(
                        row["luaName"] == "_getNetStatUser"
                        and row.get("writingOpcode") == "0x0145"
                        for row in updated["confirmedIndirectBindings"]
                    )
                )
                self.assertEqual(updated["payloadFindings"], curated["payloadFindings"])
                self.assertEqual(
                    output.read_bytes(), render(dependency.build_catalog())
                )
                before = source.read_bytes(), output.read_bytes()
                self.assertEqual(self.invoke(substruct), 0)
                self.assertEqual((source.read_bytes(), output.read_bytes()), before)

    def test_citation_normalization_uses_curated_input(self) -> None:
        curated = json.loads(dependency.CURATED_JSON.read_text(encoding="utf-8"))
        curated["metadata"]["source"].append("xivl-opcodes:" + "data/opcodes.json")
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "input.json"
            output = Path(raw) / "catalog.json"
            source.write_bytes(render(curated))
            with (
                patch.object(dependency, "CURATED_JSON", source),
                patch.object(dependency, "OUT_JSON", output),
            ):
                self.assertEqual(self.invoke(dependency, "--normalize-citations"), 0)
                updated = json.loads(source.read_bytes())
                self.assertEqual(
                    updated["metadata"]["source"][-1], "xivl-opcodes:opcodes.json"
                )
                self.assertEqual(updated["payloadFindings"], curated["payloadFindings"])
                self.assertEqual(
                    output.read_bytes(), render(dependency.build_catalog())
                )

    def test_failed_curated_replace_preserves_source(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "input.json"
            source.write_bytes(b"retained curated source\n")
            with (
                patch.object(dependency, "CURATED_JSON", source),
                patch.object(Path, "replace", side_effect=OSError("blocked")),
            ):
                with self.assertRaisesRegex(OSError, "blocked"):
                    dependency.write_curated({"changed": True})
            self.assertEqual(source.read_bytes(), b"retained curated source\n")


if __name__ == "__main__":
    unittest.main()
