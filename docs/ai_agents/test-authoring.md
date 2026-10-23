# Test authoring

Add a test for a demonstrated defect or a distinct supported behavior or
failure. Extend an existing check first. Changed lines, including AI-authored
lines, do not by themselves justify new fixtures or scenarios.

## Choose the smallest boundary

Use a parser, builder, or validator over a small authored catalog or IR document
when it can detect the regression. Use a temporary tree for publication and
preservation failures. Keep real child processes for cross-process exclusion,
CLI routing, or process-output behavior that an in-process call cannot prove.
Do not start Ghidra or a client process for a pure catalog regression.

Reuse small setup helpers in the owning test module. Prefer existing unittest
and standalone contract runners to a new fixture framework. A synthetic fixture
must retain the relationships needed to reach the guard being tested.

## Keep the oracle independent

- Assert literal offsets, sizes, IDs, addresses, confidence values, and expected
  refusals from the supported contract. Do not compute the expected answer with
  the production parser, generator, or constants being checked.
- A generated-output comparison proves agreement, not the source claim.
  Keep independent field and preservation assertions alongside regeneration.
- Plant a defect that reaches the intended invariant and assert that failure.
  An earlier schema, digest, or missing-reference error is insufficient.

The [IR mutation tests](../../tools/test_ir_gates.py) distinguish layout
arithmetic, identifier and confidence preservation, citation safety, overlay
reach, and opcode identity. Preserve their targeted refusals and checks that
other invariants stay quiet where those isolate the defect.

Tests establish repository behavior. Catalog consistency and a synthetic
layout test do not prove retail field semantics or runtime acceptance. Preserve
the [evidence policy](evidence-and-claims.md), including BCS identifiers,
source locators, uncertainty, and the narrower claim of each evidence class.

## Preserve transactions and generated inputs

All symbol readers and writers use the
[shared I/O helpers](../../tools/README.md#shared-helpers). Writers hold
`symbols_transaction()` across read, allocation, and write. Test allocation
and preservation through that boundary rather than a replacement JSON writer.

The [catalog I/O tests](../../tools/test_catalog_io.py) use real writer
processes to check exclusion, sequential IDs, and retained entries. They also
protect failed transactions, timeout behavior, and lock-owner preservation.
Keep those failure paths even when a faster unit test checks ID arithmetic.
Use temporary catalogs and locks rather than mutating the live manifests.

The [bridge tests](../../tools/test_bridge_catalogs.py) distinguish rebuilding
without previous output, missing curated input, row loss, curated-field
preservation, and failed replacement. Retain intended output changes and
unselected data in assertions. Re-parsing a successful write is insufficient.

## Separate integrity from representative integration

Check every relevant catalog row, cross-reference, vendored hash, and generated
relationship when data-wide consistency is the claim. Choose integrated cases
by distinct parser, overlay, publication path, or failure mechanism instead of
rebuilding the complete catalog for each ordinary row.

Load an unchanged baseline once when useful and isolate each mutation with
copies of all mutable ancestors it changes. Preserve a full positive build and
determinism/freshness check. The IR tests compare repeated builds and committed
output; the [checks workflow](../../.github/workflows/checks.yml) separately
checks normal builder freshness. Shared output does not make their entry-point
coverage equivalent.

Before sampling or deduplicating, map retained input/assertion combinations.
Name omitted combinations and lost coverage. Claim equivalent deduplication
only after proving the distinct invariants and failure paths remain covered.
Keep provenance checks under the [vendor contract](../../data/vendor/README.md)
and regeneration under the [manifest contract](../../manifests/README.md).

## Control cost and run the owning checks

For material growth in full builds, catalog scans, subprocesses, or test source,
use representative runtime, build, or source evidence to explain the boundary.
Source size alone does not establish runtime or build cost. Do not invent test
quotas or benchmark every small addition.

Use the [tool guide](../../tools/README.md#commands) and complete applicable
[repository checks](../../.github/workflows/checks.yml) for catalog, tool, or
generated-contract changes. A focused regression check supplements those gates.
Asset-free checks and the [retail-input check](retail-input-validation.md)
establish different claims. Public fixture validation does not reproduce private
source bytes or justify a wider grant. Report checks run and unverified claims.
Prose-only policy changes need source, link, and whitespace verification.
