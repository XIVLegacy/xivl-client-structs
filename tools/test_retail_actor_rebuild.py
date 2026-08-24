#!/usr/bin/env python3
"""Mutation tests for the actor-rebuild retail-input contract."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _schema_check  # noqa: E402
import _symbols_io  # noqa: E402
import verify_retail_actor_rebuild as verifier  # noqa: E402


REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tools" / "fixtures" / "retail_actor_rebuild_observations.json"
CHECK = REPO / "manifests" / "retail_actor_rebuild_check.json"
RETAIL_INPUTS = REPO / "manifests" / "retail_inputs.json"
SCHEMA = REPO / "schemas" / "retail-evidence-attestation.schema.json"
VERIFY = REPO / "tools" / "verify_retail_actor_rebuild.py"
WORKFLOW = REPO / ".github" / "workflows" / "retail-checks.yml"
SHARED_ACTION_SHA = "4920dece45e88fcb14424de1f5c4fdee94ae6d02"
PASSED: list[str] = []
FAILED: list[str] = []


def check(name: str, condition: bool) -> None:
    (PASSED if condition else FAILED).append(name)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, document: object) -> Path:
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return path


def _fails(
    directory: Path,
    observations: dict | None = None,
    expected: dict | None = None,
    retail_inputs: dict | None = None,
    symbols: dict | None = None,
) -> bool:
    observation_path = _write(directory / "observations.json", observations or _load(FIXTURE))
    expected_path = _write(directory / "expected.json", expected or _load(CHECK))
    retail_path = _write(directory / "retail.json", retail_inputs or _load(RETAIL_INPUTS))
    symbols_path = _write(directory / "symbols.json", symbols or _symbols_io.load_symbols())
    try:
        return bool(verifier.verify(observation_path, expected_path, retail_path, symbols_path))
    except (OSError, KeyError, TypeError, ValueError, verifier.VerificationError):
        return True


def _run_cli(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VERIFY), "--input", str(path)],
        cwd=REPO, capture_output=True, text=True, check=False,
    )


def main() -> int:
    baseline = _load(FIXTURE)
    workflow = WORKFLOW.read_text(encoding="utf-8")
    check(
        "shared retail actions are pinned",
        workflow.count(
            f"XIVLegacy/xivl-tools/.github/actions/fetch-retail-input@{SHARED_ACTION_SHA}"
        ) == 1
        and workflow.count(
            f"XIVLegacy/xivl-tools/.github/actions/setup-retail-toolchain@{SHARED_ACTION_SHA}"
        ) == 1
        and workflow.count(
            f"XIVLegacy/xivl-tools/.github/actions/finalize-retail-attestation@{SHARED_ACTION_SHA}"
        ) == 1,
    )
    check(
        "shared fetch locks the local executable grant",
        "commit: aeb52f6dbde95a793ee6d52be28de9f28a885b15" in workflow
        and "path: ffxivgame.exe" in workflow
        and 'size: "15996808"' in workflow
        and "sha256: 9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9" in workflow
        and "token: ${{ secrets.RETAIL_INPUTS_TOKEN }}" in workflow
        and "RETAIL_INPUTS_REPOSITORY" not in workflow,
    )
    check(
        "shared toolchain enables Ghidra",
        "include-ghidra: true" in workflow
        and "https://github.com/adoptium/temurin21-binaries" not in workflow
        and "https://github.com/NationalSecurityAgency/ghidra" not in workflow,
    )
    check(
        "analysis consumes the shared toolchain output",
        'headless="${{ steps.toolchain.outputs.analyze-headless }}"' in workflow
        and "ghidra_12.1.3_PUBLIC" not in workflow,
    )
    check(
        "local verifier remains the analysis and retained boundary",
        workflow.count("tools/verify_retail_actor_rebuild.py") >= 2
        and 'verify_retail_actor_rebuild.py --input "${observations}"' in workflow
        and '"${RUNNER_TEMP}/retail-evidence-private/missing-observations.json"' in workflow,
    )
    check(
        "retained validation follows shared finalization",
        "id: finalize" in workflow
        and "id: retained" in workflow
        and "if: always() && !cancelled() && steps.finalize.outcome == 'success'" in workflow
        and "hashFiles" not in workflow,
    )
    check(
        "artifact upload requires finalization and retention",
        "if: always() && !cancelled() && steps.finalize.outcome == 'success'"
        " && steps.retained.outcome == 'success'" in workflow,
    )
    check(
        "final failure preserves every retail gate",
        "steps.fetch.outcome != 'success' || steps.toolchain.outcome != 'success'"
        " || steps.analysis.outcome != 'success' || steps.finalize.outcome != 'success'"
        " || steps.retained.outcome != 'success'"
        in workflow,
    )
    check(
        "artifact upload relies on shared action defaults",
        "if-no-files-found: error" in workflow
        and "retention-days: 30" in workflow
        and "compression-level:" not in workflow
        and "overwrite:" not in workflow
        and "include-hidden-files:" not in workflow,
    )
    with tempfile.TemporaryDirectory(prefix="retail-actor-rebuild-test-") as raw:
        directory = Path(raw)
        check("canonical fixture passes", not _fails(directory, baseline))

        call_indices = [index for index, row in enumerate(baseline["observations"])
                        if row["kind"] == "call"]
        field_indices = [index for index, row in enumerate(baseline["observations"])
                         if row["kind"] != "call"]
        check("contract has four calls and four fields",
              len(call_indices) == 4 and len(field_indices) == 4)

        for number, index in enumerate(call_indices, start=1):
            mutated = copy.deepcopy(baseline)
            mutated["observations"][index]["target_va"] = "0xDEADBEEF"
            check(f"call target mutation {number} fails", _fails(directory, mutated))

        for number, index in enumerate(field_indices, start=1):
            mutated = copy.deepcopy(baseline)
            mutated["observations"][index]["displacement"] = "0xDEADBEEF"
            check(f"field offset mutation {number} fails", _fails(directory, mutated))
            mutated = copy.deepcopy(baseline)
            mutated["observations"][index]["immediate"] += 1
            check(f"field value mutation {number} fails", _fails(directory, mutated))

        for field, replacement in (
            ("instruction_va", "0xDEADBEEF"),
            ("owner_va", "0xDEADBEEF"),
            ("width", "word"),
        ):
            mutated = copy.deepcopy(baseline)
            mutated["observations"][0][field] = replacement
            check(f"{field} drift fails", _fails(directory, mutated))

        mutated = copy.deepcopy(baseline)
        mutated["observations"].pop()
        check("missing observation fails", _fails(directory, mutated))
        mutated = copy.deepcopy(baseline)
        mutated["observations"].append({
            "kind": "call", "instruction_va": "0x00400000",
            "owner_va": "0x00400000", "target_va": "0x00400000",
        })
        check("extra observation fails", _fails(directory, mutated))
        mutated = copy.deepcopy(baseline)
        mutated["observations"].append(copy.deepcopy(mutated["observations"][0]))
        check("duplicate observation fails", _fails(directory, mutated))
        mutated = copy.deepcopy(baseline)
        del mutated["observations"][0]["immediate"]
        check("malformed observation fails", _fails(directory, mutated))

        expected = _load(CHECK)
        expected["observations"][2]["target_va"] = "0xDEADBEEF"
        check("expected recipe drift fails", _fails(directory, expected=expected))

        symbols = _symbols_io.load_symbols()
        target = next(row for row in symbols["symbols"] if row["id"] == "BCS-Y-0525")
        target["address"] = "0xDEADBEEF"
        check("BCS target address drift fails", _fails(directory, symbols=symbols))
        symbols = _symbols_io.load_symbols()
        target = next(row for row in symbols["symbols"] if row["id"] == "BCS-Y-0525")
        target["kind"] = "global"
        check("BCS target kind drift fails", _fails(directory, symbols=symbols))
        symbols = _symbols_io.load_symbols()
        context = next(row for row in symbols["symbols"] if row["id"] == "BCS-Y-0280")
        context["address"] = "0xDEADBEEF"
        check("supporting context drift fails", _fails(directory, symbols=symbols))

        retail = _load(RETAIL_INPUTS)
        retail["inputs"][0]["allowedChecks"].append("unapproved-check")
        check("retail grant expansion fails", _fails(directory, retail_inputs=retail))

        schema = _schema_check.load_schema(SCHEMA)
        unsupported_schema = _write(
            directory / "unsupported-schema.json",
            {"$schema": "https://json-schema.org/draft/2020-12/schema", "contains": {}},
        )
        try:
            _schema_check.load_schema(unsupported_schema)
        except _schema_check.SchemaError:
            unsupported_rejected = True
        else:
            unsupported_rejected = False
        check("unsupported schema keyword fails closed", unsupported_rejected)
        public_commit = verifier._git_commit()
        check("test checkout has a public commit", public_commit is not None)
        check("git-less checkout has no public commit", verifier._git_commit(directory) is None)
        attestation = verifier.build_attestation("pass", public_commit)
        check("passing attestation satisfies schema", not _schema_check.validate(attestation, schema))
        attestation["observations"] = []
        check("unexpected attestation field fails", bool(_schema_check.validate(attestation, schema)))
        zero_failure = verifier.build_attestation("fail", None)
        check("zero commit is limited to failed attestations",
              zero_failure["publicRepositoryCommit"] == verifier.ZERO_COMMIT
              and not _schema_check.validate(zero_failure, schema)
              and bool(_schema_check.validate(
                  {**zero_failure, "result": {"status": "pass"}}, schema)))
        try:
            verifier.build_attestation("pass", None)
        except verifier.VerificationError:
            missing_commit_rejected = True
        else:
            missing_commit_rejected = False
        check("passing attestation requires a public commit", missing_commit_rejected)

        failed = copy.deepcopy(baseline)
        failed["observations"][0]["immediate"] = 99
        failed_path = _write(directory / "failed.json", failed)
        result = _run_cli(failed_path)
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            output = {}
        check("failure invocation exits nonzero", result.returncode != 0)
        check("failure output is sanitized", set(output) == {
            "schemaVersion", "publicRepositoryCommit", "approvedInputSha256",
            "toolVersions", "check", "result",
        } and output.get("result", {}).get("status") == "fail"
              and "observations" not in result.stdout)

        first = _run_cli(FIXTURE)
        second = _run_cli(FIXTURE)
        check("repeated passing output is byte-identical",
              first.returncode == second.returncode == 0
              and first.stdout.encode() == second.stdout.encode())

    if FAILED:
        print("FAIL: " + "; ".join(FAILED))
        return 1
    print(f"PASS: {len(PASSED)} actor-rebuild verification checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
