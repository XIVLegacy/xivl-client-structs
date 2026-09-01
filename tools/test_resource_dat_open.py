#!/usr/bin/env python3
"""Bite proofs for the bounded Resource DAT missing-file observation."""

from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "manifests" / "resource_dat_open.json"


def validate_contract(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("status") != "successful_open_verified_bounded_missing_file_observed":
        errors.append("manifest status")

    identity = document.get("inputIdentity", {})
    if identity.get("build") != "2012.09.19.0001":
        errors.append("build identity")
    if identity.get("size") != 15_996_808:
        errors.append("executable size")
    if identity.get("sha256") != "9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9":
        errors.append("executable hash")

    companion = document.get("companionEvidence", {})
    if companion.get("exactBuildSignature") != "6A 00 68 ?? ?? ?? ?? 83 C6 04 56 8B CF E8 ?? ?? ?? ??":
        errors.append("exact-build signature")
    if companion.get("patternVa") != "0x00C96972" or companion.get("matchCount") != 1:
        errors.append("signature locator")
    if "cross-build stability remains unresolved" not in companion.get("scope", ""):
        errors.append("signature scope")

    open_boundary = document.get("openBoundary", {})
    arguments = open_boundary.get("secureCrtArguments", {})
    if "relative path data\\2A\\08\\00\\17.DAT" not in arguments.get("path", ""):
        errors.append("relative path boundary")
    stack = open_boundary.get("postCallStack", {})
    if stack.get("callerReturnOffset") != "ESP+0xC4":
        errors.append("caller return offset")
    if stack.get("retryCountOffset") != "ESP+0xD0" or stack.get("observedRetryCount") != 0:
        errors.append("retry count boundary")

    experiment = document.get("missingDatExperiment", {})
    if experiment.get("status") != "bounded_live_observation":
        errors.append("missing-file status")
    expected_scope = (
        "One successful baseline request followed by one separate exact-build "
        "missing-path request with retry count zero and a 15-second post-return "
        "observation window. The no-retry and no-fallback result applies only to "
        "the missing-path request and does not establish global behavior."
    )
    if experiment.get("scope") != expected_scope:
        errors.append("bounded observation scope")

    observation = document.get("method", {}).get("missingFileObservation", {})
    expected_boundary = (
        "one missing-path read-mode request at 0x00453CD5 through the FileThread "
        "post-call site at 0x00C96B6D and return at 0x00C96B73, followed by a "
        "15-second observation window; the successful baseline was a separate request"
    )
    if observation.get("evidenceClass") != "sanitized machine-local live observation report":
        errors.append("dynamic evidence class")
    if observation.get("boundary") != expected_boundary:
        errors.append("dynamic observation boundary")
    if "were not reproduced by the static verification" not in observation.get("artifactBoundary", ""):
        errors.append("dynamic artifact boundary")

    attempt = experiment.get("missingAttempt", {})
    expected_attempt = {
        "path": "data\\2A\\08\\00\\1G.DAT",
        "mode": "rb",
        "callerReturn": "0x00C96984",
        "retryCount": 0,
        "outputFilePointerBeforeCall": "null",
        "secureCrtReturn": 2,
        "threadLastError": 2,
        "outputFilePointerAfterCall": "null",
        "pathRestoredBeforeErrorHandling": True,
    }
    if attempt != expected_attempt:
        errors.append("missing-file attempt")

    downstream = experiment.get("downstream", {})
    expected_downstream = {
        "errorHelper": "FUN_00456960",
        "errorHelperCalls": 1,
        "errorArgument": 2,
        "errorHelperReturn": "0x00453D59",
        "memberReturnAl": 0,
        "memberReturnBoundary": "0x00C96984",
        "fileThreadPostCall": "0x00C96B6D",
        "fileThreadReturn": "0x00C96B73",
        "originalPathRetryBeforeServiceReturn": False,
        "observationWindowSeconds": 15,
        "laterOriginalPathOpenObserved": False,
        "fallbackPathObserved": False,
    }
    if downstream != expected_downstream:
        errors.append("bounded downstream result")

    limits = experiment.get("limits", "")
    for text in (
        "one missing-path request and its 15-second observation window",
        "Successful substituted-path ownership",
        "successful redirected read completion",
        "normal-read closure",
        "identity forwarding",
        "cross-build signature stability",
    ):
        if text not in limits:
            errors.append(f"missing limit: {text}")

    correlation = document.get("resourceIdCorrelation", {})
    if correlation.get("status") != "inferred":
        errors.append("resource-id inference boundary")

    gate = document.get("hookGate", {})
    if gate.get("stableExactBuildSignature") != "SUPPORTED for the pinned executable identity":
        errors.append("signature gate")
    expected_missing_gate = (
        "BOUNDED - for one missing-path request, retry count zero produced errno 2, "
        "a null FILE*, one error-helper call, false member return, and no observed "
        "retry or fallback through the service return and following 15 seconds; "
        "global behavior remains unresolved"
    )
    if gate.get("missingFileFallthrough") != expected_missing_gate:
        errors.append("missing-file gate")
    if gate.get("successfulRedirectSemantics") != "NOT TESTED":
        errors.append("redirect gate")
    if gate.get("originalPathIdentityForwarding") != "NOT TESTED":
        errors.append("identity-forwarding gate")
    serialized = json.dumps(document, ensure_ascii=True, sort_keys=True)
    private_path_pattern = re.compile(
        r"[A-Za-z]:\\\\|/" + r"Users/|/" + r"home/|agent-" + r"islands",
        re.I,
    )
    if private_path_pattern.search(serialized):
        errors.append("private path leak")
    return errors


class ResourceDatOpenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = json.loads(MANIFEST.read_text(encoding="ascii"))

    def test_checked_in_contract_passes(self) -> None:
        self.assertEqual([], validate_contract(self.document))

    def assert_mutation_rejected(self, path: tuple[str, ...], value: object) -> None:
        changed = copy.deepcopy(self.document)
        target = changed
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        self.assertNotEqual([], validate_contract(changed))

    def test_required_missing_file_claims_are_guarded(self) -> None:
        cases = (
            (("missingDatExperiment", "missingAttempt", "retryCount"), 1),
            (("missingDatExperiment", "missingAttempt", "secureCrtReturn"), 0),
            (("missingDatExperiment", "missingAttempt", "outputFilePointerAfterCall"), "non-null"),
            (("missingDatExperiment", "missingAttempt", "pathRestoredBeforeErrorHandling"), False),
            (("missingDatExperiment", "downstream", "errorHelperCalls"), 2),
            (("missingDatExperiment", "downstream", "memberReturnAl"), 1),
            (("missingDatExperiment", "downstream", "laterOriginalPathOpenObserved"), True),
            (("missingDatExperiment", "downstream", "fallbackPathObserved"), True),
        )
        for path, value in cases:
            with self.subTest(path=path):
                self.assert_mutation_rejected(path, value)

    def test_global_fallback_promotion_is_rejected(self) -> None:
        self.assert_mutation_rejected(
            ("missingDatExperiment", "scope"),
            "Missing DAT files never retry or fall back.",
        )

    def test_dynamic_boundary_widening_is_rejected(self) -> None:
        self.assert_mutation_rejected(
            ("method", "missingFileObservation", "boundary"),
            "all missing-path requests",
        )

    def test_bounded_gate_widening_is_rejected(self) -> None:
        self.assert_mutation_rejected(
            ("hookGate", "missingFileFallthrough"),
            "BOUNDED - missing files never retry or fall back",
        )

    def test_resource_id_promotion_is_rejected(self) -> None:
        self.assert_mutation_rejected(("resourceIdCorrelation", "status"), "confirmed")


if __name__ == "__main__":
    unittest.main()
