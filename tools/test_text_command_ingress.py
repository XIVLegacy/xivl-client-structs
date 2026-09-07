#!/usr/bin/env python3
"""Bite proofs for the text-command lookup boundary contract."""

from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "manifests" / "text_command_ingress.json"
EXPECTED_HASH = "9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9"
REQUIRED_CANDIDATE_KEYS = {
    "rank", "candidate", "vas", "rvas", "classAndSlot",
    "callingConventionAndPrototype", "signatures", "inputEncoding",
    "inputOwnershipAndLifetime", "expectedInvocationThread",
    "exactOnceBehavior", "consumeForwardMechanism", "cleanupObligations",
    "unsupportedBuildBehavior", "verdict", "evidence",
}


def validate_contract(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("status") != "go_exact_build_lookup_boundary":
        errors.append("manifest status")
    identity = document.get("inputIdentity", {})
    if identity.get("build") != "2012.09.19.0001" or identity.get("size") != 15_996_808:
        errors.append("build identity")
    if identity.get("sha256") != EXPECTED_HASH:
        errors.append("executable hash")

    strongest = document.get("strongestCandidate", {})
    if strongest.get("verdict") != "GO" or "lookup" not in strongest.get("name", ""):
        errors.append("lookup verdict")
    if "0x0056D3C0" not in strongest.get("boundary", "") or \
            "0x0056E6A4" not in strongest.get("boundary", ""):
        errors.append("lookup caller gate")
    candidates = document.get("candidateVerdicts", [])
    if [row.get("rank") for row in candidates] != list(range(1, len(candidates) + 1)):
        errors.append("candidate ranking")
    for row in candidates:
        if not REQUIRED_CANDIDATE_KEYS.issubset(row):
            errors.append(f"candidate fields rank {row.get('rank')}")
    if not candidates or candidates[0].get("vas") != ["0x0056D3C0"]:
        errors.append("lookup address")
    if not candidates or candidates[0].get("verdict") != "GO":
        errors.append("lookup candidate verdict")

    signatures = candidates[0].get("signatures", []) if candidates else []
    if len(signatures) != 1:
        errors.append("lookup signature")
    for signature in signatures:
        tokens = signature.get("pattern", "").split()
        mask = signature.get("mask", "")
        if len(tokens) != len(mask) or set(mask) - {"x", "?"}:
            errors.append(f"signature mask {signature.get('va')}")
        if signature.get("executableSectionMatches") != 1:
            errors.append(f"signature uniqueness {signature.get('va')}")

    contract = document.get("proposedHookContract", {})
    serialized_contract = json.dumps(contract, sort_keys=True)
    for required in ("0x0056E6A4", "original lookup", "return -2", "unique signature"):
        corpus = serialized_contract + json.dumps(candidates[0] if candidates else {})
        if required not in corpus:
            errors.append(f"hook contract: {required}")

    matrix = document.get("requiredRuntimeMatrix", [])
    expected = ["/pos", "ordinary chat", "known retail slash command", "/unknown-command",
                "known retail command with deferred target-selection syntax"]
    if [row.get("input") for row in matrix] != expected:
        errors.append("runtime matrix")
    if not matrix or not matrix[0].get("currentStatus", "").startswith("partial pass 2026-09-07"):
        errors.append("live runtime status")
    if any(row.get("currentStatus") != "not run" for row in matrix[1:]):
        errors.append("runtime status boundary")

    limits = " ".join(document.get("evidenceBoundaries", []))
    for required in ("four preservation rows remain unverified",
                     "Exact character encoding is unresolved",
                     "GO applies only to the exact-build lookup hook"):
        if required not in limits:
            errors.append(f"evidence boundary: {required}")

    serialized = json.dumps(document, ensure_ascii=True, sort_keys=True)
    private_path_pattern = (
        r"[A-Za-z]:\\\\|/Us" + r"ers/|/ho" + r"me/|agent-" + r"islands"
    )
    if re.search(private_path_pattern, serialized, re.I):
        errors.append("private path leak")
    return errors


class TextCommandIngressTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_checked_in_contract_passes(self) -> None:
        self.assertEqual([], validate_contract(self.document))

    def assert_mutation_rejected(self, path: tuple[object, ...], value: object) -> None:
        changed = copy.deepcopy(self.document)
        target = changed
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        self.assertNotEqual([], validate_contract(changed))

    def test_lookup_caller_gate_is_required(self) -> None:
        self.assert_mutation_rejected(
            ("strongestCandidate", "boundary"),
            "Detour 0x0056D3C0 on the exact pinned build.",
        )

    def test_signature_uniqueness_is_guarded(self) -> None:
        self.assert_mutation_rejected(
            ("candidateVerdicts", 0, "signatures", 0, "executableSectionMatches"), 3
        )

    def test_runtime_result_cannot_be_widened(self) -> None:
        self.assert_mutation_rejected(("requiredRuntimeMatrix", 1, "currentStatus"), "passed")

    def test_encoding_claim_cannot_be_widened(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["evidenceBoundaries"] = [
            line for line in changed["evidenceBoundaries"]
            if "Exact character encoding is unresolved" not in line
        ]
        self.assertNotEqual([], validate_contract(changed))


if __name__ == "__main__":
    unittest.main()
