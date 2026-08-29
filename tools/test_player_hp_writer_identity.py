#!/usr/bin/env python3
"""Bite proofs for exact player-HP property hash-to-writer mappings."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from validate_catalog import check_property_stream_hash_catalog


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "manifests" / "property_stream_hash_catalog.json"


def validate(doc: dict) -> list[str]:
    return [finding.message for finding in check_property_stream_hash_catalog(doc)]


class PlayerHpWriterIdentityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_checked_in_contract_passes(self) -> None:
        self.assertEqual([], validate(self.doc))

    def test_hash_to_writer_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.doc)
        row = mutated["playerHpWriterIdentity"]["properties"][2]
        row["writerType"] = "SyncWriterInteger16"
        self.assertIn("hash-to-writer mapping drifted", validate(mutated))

    def test_native_index_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.doc)
        row = mutated["playerHpWriterIdentity"]["properties"][2]
        row["luaIndex"] = 5
        self.assertIn("hash-to-writer mapping drifted", validate(mutated))

    def test_semantic_claim_mutations_are_rejected(self) -> None:
        mutations = (
            ("luaDescriptor", "battleTemp.generalParameter = integer16"),
            ("storageTarget", "fixed CharaBase field at +0x10"),
            ("consumerBoundary", "native Vitality field"),
        )
        for field, value in mutations:
            with self.subTest(field=field):
                mutated = copy.deepcopy(self.doc)
                mutated["playerHpWriterIdentity"]["properties"][2][field] = value
                self.assertIn(
                    "descriptor, storage, or consumer boundary drifted",
                    validate(mutated),
                )

    def test_absent_battle_temp_hpmax_cannot_be_promoted(self) -> None:
        mutated = copy.deepcopy(self.doc)
        row = mutated["playerHpWriterIdentity"]["properties"][3]
        row["cataloged"] = True
        row["writerType"] = "SyncWriterArrayEndianAdjust<short>"
        self.assertIn("hash-to-writer mapping drifted", validate(mutated))

    def test_hp_calibration_path_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.doc)
        correction = mutated["playerHpWriterIdentity"]["calibrationCorrection"]
        correction["path"] = "charaWork.battleTemp.hpMax[0]"
        self.assertIn("HP calibration correction drifted", validate(mutated))

    def test_hp_correction_semantic_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.doc)
        correction = mutated["playerHpWriterIdentity"]["calibrationCorrection"]
        correction["storageTarget"] = "fixed PlayerBase field"
        self.assertIn("HP correction semantic boundary drifted", validate(mutated))

    def test_main_skill_index_chain_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.doc)
        namespace = mutated["playerHpWriterIdentity"]["mainSkillIdentifierNamespace"]
        namespace["nativeReadChain"]["indexConversion"] = (
            "Lua index 1 selects native slot 1"
        )
        self.assertIn("native read or index chain drifted", validate(mutated))

    def test_main_skill_namespace_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.doc)
        namespace = mutated["playerHpWriterIdentity"]["mainSkillIdentifierNamespace"]
        namespace["namespace"]["identifier"] = "job id"
        self.assertIn("identifier or slot namespace drifted", validate(mutated))

    def test_observed_skill_mapping_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.doc)
        namespace = mutated["playerHpWriterIdentity"]["mainSkillIdentifierNamespace"]
        namespace["observedMappings"][0]["className"] = "Marauder"
        self.assertIn("observed skill mapping drifted", validate(mutated))

    def test_api_relationship_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.doc)
        namespace = mutated["playerHpWriterIdentity"]["mainSkillIdentifierNamespace"]
        namespace["scriptRegistration"]["getMainSkill"] = (
            "CharaBaseClass.getMainSkill -> state_mainSkill[1]"
        )
        self.assertIn("API relationship drifted", validate(mutated))

    def test_hp_gate_cannot_be_reinterpreted(self) -> None:
        mutated = copy.deepcopy(self.doc)
        namespace = mutated["playerHpWriterIdentity"]["mainSkillIdentifierNamespace"]
        namespace["calibrationGate"] = "derive an HP formula from the two points"
        self.assertIn("HP calibration gate drifted", validate(mutated))

    def test_main_skill_source_reference_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.doc)
        namespace = mutated["playerHpWriterIdentity"]["mainSkillIdentifierNamespace"]
        namespace["sourceRefs"][0] = "notes:uncited-main-skill"
        self.assertIn("source reference set drifted", validate(mutated))

    def test_main_skill_evidence_record_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.doc)
        runs = mutated["playerHpWriterIdentity"]["evidenceRuns"]
        lane4 = next(run for run in runs if run["id"].startswith("lane4-main-skill-native"))
        lane4["output"] = "tools/ghidra/logs/wrong.txt"
        self.assertTrue(
            any("evidence record drifted" in finding for finding in validate(mutated))
        )


if __name__ == "__main__":
    unittest.main()
