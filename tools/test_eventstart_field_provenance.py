"""Bite proofs for the direct PlayerBase EventStart field and SID-domain contract."""

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
        "0x08": "commandControlBindingSid",
        "0x0c": "secondaryArgument_or_luaTailCrc32",
    }
    for offset, expected in expected_names.items():
        if fields.get(offset, {}).get("name") != expected:
            errors.append(f"combat {offset} name")
        if struct_fields.get(offset, {}).get("name") != expected:
            errors.append(f"BCS-S-0034 {offset} name")

    offset8 = provenance.get("offset0x08", {})
    if offset8.get("classification") != "command_control_binding_sid_domain_token":
        errors.append("+0x08 classification")
    if offset8.get("sourceCategory") != "another source":
        errors.append("+0x08 source category")
    path8 = offset8.get("path", "")
    for token in ("FUN_0070A010", "FUN_00CC73B0", "FUN_00CD7A30", "FUN_00CC7030", "FUN_00895860", "Event::Base+0x08"):
        if token not in path8:
            errors.append(f"+0x08 path missing {token}")
    if "+0x70" not in path8:
        errors.append("+0x08 binding offset")

    writer_domain = offset8.get("writerDomain", {})
    writer = writer_domain.get("writer", "")
    for token in ("FUN_00CE1CC0", "BCS-Y-2162", "+0x70", "unconditionally stores", "FUN_00D03680", "BCS-Y-2167", "Only a successful check", "+0x7e"):
        if token not in writer:
            errors.append(f"+0x70 writer missing {token}")

    expected_callers = {
        "FUN_00CD8210": "BCS-Y-2158",
        "FUN_00CD9360": "BCS-Y-1806",
        "FUN_00CD99F0": "BCS-Y-2159",
        "FUN_00CDAEB0": "BCS-Y-2160",
        "FUN_00CDCBA0": "BCS-Y-1513",
        "FUN_00CDDE20": "BCS-Y-2161",
    }
    callers = writer_domain.get("directCallers", [])
    actual_callers = {item.get("function"): item.get("symbol") for item in callers}
    if actual_callers != expected_callers:
        errors.append("+0x70 direct caller set")
    if any(not item.get("valueOrigin") for item in callers):
        errors.append("+0x70 caller value origin")
    expected_origin_tokens = {
        "FUN_00CD8210": ("source entry +0x70", "FUN_00D03610"),
        "FUN_00CD9360": ("next unused", "FUN_00D038C0"),
        "FUN_00CD99F0": ("runtime SID", "FUN_00D038C0"),
        "FUN_00CDAEB0": ("DAT_0130C778", "BCS-Y-0724"),
        "FUN_00CDCBA0": ("caller-supplied SID", "unchanged"),
        "FUN_00CDDE20": ("0x000fffff", "unchanged full"),
    }
    origins = {item.get("function"): item.get("valueOrigin", "") for item in callers}
    for function, tokens in expected_origin_tokens.items():
        for token in tokens:
            if token not in origins.get(function, ""):
                errors.append(f"+0x70 {function} origin missing {token}")

    allocation = " ".join(writer_domain.get("allocationAndValidation", []))
    for token in (
        "FUN_00D038C0",
        "runtime- and registration-order-dependent",
        "(sid >> 20) & 0x0f",
        "sid & 0xf0f00000",
        "exact SID equality",
    ):
        if token not in allocation:
            errors.append(f"SID domain missing {token}")
    if writer_domain.get("defaultValue") != "DAT_0130C778 = 0xe0000000 null SID sentinel (BCS-Y-0724)":
        errors.append("SID default")
    if writer_domain.get("evidence") != "tools/ghidra/logs/lane2_eventstart-binding-sid-domain.txt":
        errors.append("SID archive locator")

    calibration8 = offset8.get("wireCalibration", {})
    expected_values = {
        "0x24400000": ("0x4024", 2),
        "0x25800000": ("0x8025", 15),
        "0x25c00000": ("0xc025", 1),
        "0x26000000": ("0x0026", 1),
        "0x26800000": ("0x8026", 9),
        "0x26c00000": ("0xc026", 11),
        "0x28800000": ("0x8028", 4),
        "0x2b000000": ("0x002b", 1),
        "0x33800000": ("0x8033", 3),
        "0x3d000000": ("0x003d", 13),
    }
    actual_values = {
        item.get("hostRawDword"): (item.get("networkOrder"), item.get("count"))
        for item in calibration8.get("observedValues", [])
    }
    if actual_values != expected_values or sum(count for _, count in actual_values.values()) != 60:
        errors.append("SID observed domain")
    if calibration8.get("sampleCount") != 60:
        errors.append("SID sample count")
    representation = calibration8.get("representation", "")
    for token in ("without a byte transform", "network-order presentation", "host/raw dwords"):
        if token not in representation:
            errors.append(f"SID representation missing {token}")
    expected_reconciliation = {
        "EmoteStandardCommand: 2 occurrences, SID 0x3d000000",
        "PartyInviteCommand: 1 occurrence, SID 0x26c00000",
        "RequestQuestJournalCommand: 2 occurrences, SID 0x3d000000",
        "TeleportCommand: 4 occurrences, one each at 0x24400000, 0x25800000, 0x26800000, and 0x33800000",
        "PlaceDrivenCommand: 3 occurrences, SID 0x25800000",
    }
    if set(calibration8.get("missingGameCommandReconciliation", [])) != expected_reconciliation:
        errors.append("SID missing-gameCommand reconciliation")
    constraints = calibration8.get("constraints", "")
    for token in ("12 static-owner occurrences", "TeleportCommand uses four SIDs", "neither a stable command-class discriminator nor row-derived data", "not command flags"):
        if token not in constraints:
            errors.append(f"SID reconciliation missing {token}")

    boundary8 = offset8.get("semanticBoundary", "")
    for token in ("runtime Lua control/class SID-domain binding token", "stores it before validation", "registry validity is conditional", "not a stable enum", "flags field", "gameCommand row", "journal ID", "server policy"):
        if token not in boundary8:
            errors.append(f"SID classification missing {token}")

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

    if "SID-domain binding token at entry +0x70" not in journal_fields.get("offset0x08", ""):
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

    def test_binding_writer_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.combat)
        mutated["applicationFieldProvenance"]["offset0x08"]["writerDomain"]["writer"] = "FUN_00CE1CD0 writes +0x74"
        errors = validate_contract(mutated, self.guildleve, self.structs)
        self.assertIn("+0x70 writer missing FUN_00CE1CC0", errors)
        self.assertIn("+0x70 writer missing +0x70", errors)

    def test_binding_caller_set_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.combat)
        mutated["applicationFieldProvenance"]["offset0x08"]["writerDomain"]["directCallers"].pop()
        self.assertIn("+0x70 direct caller set", validate_contract(mutated, self.guildleve, self.structs))

    def test_binding_caller_origin_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.combat)
        callers = mutated["applicationFieldProvenance"]["offset0x08"]["writerDomain"]["directCallers"]
        next(item for item in callers if item["function"] == "FUN_00CDDE20")["valueOrigin"] = "opaque"
        self.assertIn("+0x70 FUN_00CDDE20 origin missing 0x000fffff", validate_contract(mutated, self.guildleve, self.structs))

    def test_sid_allocator_domain_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.combat)
        domain = mutated["applicationFieldProvenance"]["offset0x08"]["writerDomain"]
        domain["allocationAndValidation"] = ["stable enum table"]
        self.assertIn("SID domain missing FUN_00D038C0", validate_contract(mutated, self.guildleve, self.structs))

    def test_sid_observed_value_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.combat)
        observed = mutated["applicationFieldProvenance"]["offset0x08"]["wireCalibration"]["observedValues"]
        observed[0]["hostRawDword"] = "0x24400001"
        self.assertIn("SID observed domain", validate_contract(mutated, self.guildleve, self.structs))

    def test_sid_network_order_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.combat)
        observed = mutated["applicationFieldProvenance"]["offset0x08"]["wireCalibration"]["observedValues"]
        observed[0]["networkOrder"] = "0x2440"
        self.assertIn("SID observed domain", validate_contract(mutated, self.guildleve, self.structs))

    def test_sid_classification_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.combat)
        mutated["applicationFieldProvenance"]["offset0x08"]["classification"] = "stable_enum"
        self.assertIn("+0x08 classification", validate_contract(mutated, self.guildleve, self.structs))

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
