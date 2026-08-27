"""Bite proofs for the direct PlayerBase EventStart field provenance contract."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_inputs() -> tuple[dict, dict, dict]:
    def read(name: str) -> dict:
        return json.loads((ROOT / "manifests" / name).read_text(encoding="utf-8"))

    return read("combat_command_emission.json"), read("guildleve_lifecycle.json"), read("structs.json")


def validate_contract(combat: dict, guildleve: dict, structs: dict) -> list[str]:
    errors: list[str] = []
    fields = {item["offset"].lower(): item for item in combat["wireLayout"]["fields"]}
    provenance = combat.get("applicationFieldProvenance", {})
    struct = next((item for item in structs["structs"] if item.get("id") == "BCS-S-0034"), None)
    struct_fields = {item["offset"].lower(): item for item in struct["fields"]} if struct else {}
    journal_fields = guildleve.get("journalCommandLuaTail", {}).get("eventStartApplicationFields", {})

    expected_names = {
        "0x08": "contextValue_or_commandControlBindingValue",
        "0x0c": "secondaryArgument_or_luaTailCrc32",
    }
    for offset, expected in expected_names.items():
        if fields.get(offset, {}).get("name") != expected:
            errors.append(f"combat {offset} name")
        if struct_fields.get(offset, {}).get("name") != expected:
            errors.append(f"BCS-S-0034 {offset} name")

    offset8 = provenance.get("offset0x08", {})
    if offset8.get("sourceCategory") != "another source":
        errors.append("+0x08 source category")
    path8 = offset8.get("path", "")
    for token in ("FUN_0070A010", "FUN_00CC73B0", "FUN_00CD7A30", "FUN_00CC7030", "FUN_00895860", "Event::Base+0x08"):
        if token not in path8:
            errors.append(f"+0x08 path missing {token}")
    if "+0x70" not in path8:
        errors.append("+0x08 binding offset")

    offsetc = provenance.get("offset0x0c", {})
    if offsetc.get("sourceCategory") != "runtime arguments after serialization":
        errors.append("+0x0c source category")
    pathc = offsetc.get("path", "")
    for token in ("0x80-byte", "FUN_00D3AB60", "FUN_00D3A380", "FUN_00D3AAE0"):
        if token not in pathc:
            errors.append(f"+0x0c path missing {token}")
    crc_calibration = offsetc.get("wireCalibration", "")
    if "59 of the 60" not in crc_calibration or "invite_join_party.pcapng" not in crc_calibration:
        errors.append("+0x0c producer boundary")

    if "binding entry at +0x70" not in journal_fields.get("offset0x08", ""):
        errors.append("guildleve +0x08 reconciliation")
    crc_text = journal_fields.get("offset0x0c", "")
    if "CRC32" not in crc_text or "128-byte tail" not in crc_text:
        errors.append("guildleve +0x0c reconciliation")
    if provenance.get("evidence") != "tools/ghidra/logs/lane2_eventstart-field-provenance.txt":
        errors.append("archive locator")
    return errors


class EventStartFieldProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.combat, self.guildleve, self.structs = load_inputs()

    def test_repository_contract(self) -> None:
        self.assertEqual([], validate_contract(self.combat, self.guildleve, self.structs))

    def test_binding_source_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.combat)
        mutated["applicationFieldProvenance"]["offset0x08"]["path"] = "gameCommand row"
        self.assertIn("+0x08 path missing FUN_0070A010", validate_contract(mutated, self.guildleve, self.structs))

    def test_crc_length_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.combat)
        mutated["applicationFieldProvenance"]["offset0x0c"]["path"] = mutated["applicationFieldProvenance"]["offset0x0c"]["path"].replace("0x80-byte", "0x40-byte")
        self.assertIn("+0x0c path missing 0x80-byte", validate_contract(mutated, self.guildleve, self.structs))

    def test_struct_name_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.structs)
        struct = next(item for item in mutated["structs"] if item.get("id") == "BCS-S-0034")
        next(item for item in struct["fields"] if item["offset"].lower() == "0x0c")["name"] = "unknown"
        self.assertIn("BCS-S-0034 0x0c name", validate_contract(self.combat, self.guildleve, mutated))


if __name__ == "__main__":
    unittest.main()
