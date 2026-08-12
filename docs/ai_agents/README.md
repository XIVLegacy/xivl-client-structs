# AI-assisted contributions

This repository is an evidence-backed client structure catalog for Final
Fantasy XIV 1.23b. Machine-readable manifests are the product. Tracked prose
explains the consumer contract or an evidence rule that the manifests cannot
carry by themselves.

## Contribution policy

Keep changes narrow and preserve the catalog's source-backed character. Do not
commit client binaries, assets, database dumps, generated Ghidra project files,
local analysis logs, copied decompiled function bodies, raw credentials, or
live sibling checkout paths. A vendored input is acceptable only with its
`PROVENANCE.json` record and the hash check that owns it.

The [manifest contract](../../manifests/README.md) and
[tools guide](../../tools/README.md) identify generated products and their
owning tools. Hosted CI enforces the catalog and IR checks.

Use [evidence and claims](evidence-and-claims.md) for source classes and claim
boundaries.

## Documentation policy

Tracked documentation is consumer-facing. It describes the current contract,
the evidence standard, and supported research procedures. Dates that belong to
evidence citations remain part of the record.

Untracked maintainer material is outside the public contract. Tracked pages
must not depend on it, link to it, or treat it as evidence. Local paths in
tracked Markdown must resolve inside the repository.

The [comments and prose policy](comments-and-prose.md) owns punctuation,
structure, deletion, and canonical-link guidance for tracked writing.

## Shelf

Read these pages in order:

1. [Evidence and claims](evidence-and-claims.md)
2. [Comments and prose](comments-and-prose.md)
3. [Retail-input validation](retail-input-validation.md)

The [manifest contract](../../manifests/README.md) owns the catalog charter.
The [docs index](../README.md) owns the consumer-facing documentation map, and
the
[tools guide](../../tools/README.md) owns generator and research-command details.
