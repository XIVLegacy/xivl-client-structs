# Retail-input validation

The normal asset-free repository checks remain the merge requirement. The
retail-input workflow is an additional evidence check for one bounded claim. It
proves that a clean Ghidra import of an exact retail executable reproduces a
fixed sanitized observation set; it does not prove runtime behavior or the
complete semantic interpretation of the actor-rebuild transaction.

## Granted pilot

| Item | Grant |
|---|---|
| Public repository | `XIVLegacy/xivl-client-structs` |
| Workflow | `.github/workflows/retail-checks.yml` |
| Check | `actor-rebuild-receiver-field-v1` |
| Input manifest | `manifests/retail_inputs.json` |
| Expected observations | `manifests/retail_actor_rebuild_check.json` |
| Attestation schema | `schemas/retail-evidence-attestation.schema.json` |
| Passing attestation | `manifests/retail_evidence/actor-rebuild-receiver-field-v1.json` |
| Protected environment | `retail-evidence` |
| Private input repository | `XIVLegacy/xivl-private-assets` |

The private repository contains only the canonical `ffxivgame.exe`. The input
manifest pins its repository-relative path, immutable private commit, byte
size, SHA-256, and allowed check. A companion binary, another input class, or
another check requires an explicit manifest amendment and owner review.

## Trust boundary

Credentialed execution is manual `workflow_dispatch` from protected `main`
only. The non-secret preflight rejects any other ref before the credentialed
job starts. The job uses the `retail-evidence` environment, whose deployment
branch rule selects protected branches, currently only `main`; it has no
reviewer requirement. A repository administrator must not bypass the environment
protection rule.

The environment secret is `RETAIL_INPUTS_TOKEN`. It is a fine-grained token
selected only for `XIVLegacy/xivl-private-assets`, with Contents read-only
and a maximum owner-approved lifetime of 366 days. The environment variable
`RETAIL_INPUTS_REPOSITORY` is exactly
`XIVLegacy/xivl-private-assets`. The same token may be stored in another
explicitly granted retail-input lane only when that lane uses this same private
repository and permission scope. Rotation or revocation must update every
sharing environment before another retail run, using the same or narrower
repository and permission scope.

The workflow's `GITHUB_TOKEN` remains Contents read-only and checks out the
public dispatch commit without persisting credentials. The private token is
used only for bounded commit, reachability, and tree metadata resolution plus
one blob download at the manifest-pinned private commit and path. The
downloaded object must match both the declared byte size and SHA-256 before
Ghidra starts.

The current GitHub plan does not provide branch protection for the private
repository. Its `main` branch must not be force-pushed or deleted. The public
manifest's immutable private commit is the authority, and an unreachable commit
fails the check closed.

## Toolchain and retention

The workflow pins Ghidra 12.1.3 archive
`ghidra_12.1.3_PUBLIC_20260817.zip` at SHA-256
`93a5d11a9ad510622acaaf908c556a7b9b764d338e78a7567f3689bf5081fd54`.
It pins the Eclipse Temurin JDK `21.0.12.1+1` x64 Linux HotSpot archive at
SHA-256
`ce79869e1307ed8ee1e2baa86a412b1eb5b75d10a01006d788a6f968bcfaee94`.
Third-party actions use full commit SHAs. The pilot uses no dependency or
Ghidra-project cache.

Only the schema-valid sanitized attestation may be uploaded, as one exact file
with 30-day retention. The input, API response, raw observations, Ghidra
project, imported program, analysis database, private logs, instruction text,
bytes, and decompiled output remain temporary and are deleted on every outcome.
If a failure occurs before a safe attestation exists, no artifact is uploaded.

## Claim boundary

The pilot checks the five target entries BCS-Y-0525, BCS-Y-0588, BCS-Y-0613,
BCS-Y-1019, and BCS-Y-1020. BCS-Y-0280 is supporting context for the two
`actor+0x92` clears in `FUN_004D8860`; it is not a newly promoted target.

The pilot proves exact input and program identity, function ownership, four
direct-call relationships, and four bounded byte-field observations. It does
not prove the full actor-rebuild semantics, runtime behavior, capture
relationships, live-client behavior, or any claim outside the named set.

The actor-rebuild claim predates this workflow. A failed or missing run blocks
describing it as retail-input-CI reproduced and blocks expansion of the check.
It does not revoke previously promoted evidence or block unrelated changes.

For a future claim:

1. Commit the bounded check recipe and expected observation without promoting
   the claim.
2. Merge the recipe to protected `main`.
3. Run the credentialed workflow from `main`.
4. Review and commit the sanitized passing attestation.
5. Promote the claim in a later commit.

## Local verification and response

Local execution requires an explicit path to the approved executable. Verify
the input manifest identity first, create a new temporary Ghidra project, run
`ghidra/VerifyActorRebuild.java` read-only, and pass its structured output to
`tools/verify_retail_actor_rebuild.py`. Never reuse a maintainer project for the
clean-import rehearsal.

On suspected token exposure, cancel the run, revoke the token, delete any
unsafe artifact, inspect workflow and audit logs, and rotate the environment
secret only after the boundary is understood. On suspected byte leakage, also
disable the workflow and preserve no public log excerpt containing the leaked
material.
