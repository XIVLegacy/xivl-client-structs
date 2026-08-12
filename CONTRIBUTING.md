# Contributing

XIVLegacy Client Structs accepts focused pull requests against `main`. Fork
the repository, create a branch in your fork, and open a pull request. All CI
checks must pass before a change can merge.

## Before contributing

Read the [contribution policy](docs/ai_agents/README.md) and the
[evidence standard](docs/ai_agents/evidence-and-claims.md) before changing a
catalog, manifest, or research claim.

Do not submit retail client binaries, client assets, packet captures,
decompiler project files, credentials, or other private working material.
Derived facts belong in the catalogs with durable citations. The underlying
restricted artifacts do not belong in the repository.

AI-assisted contributions are welcome, but the contributor owns the result.
A contributor who cannot explain their diff in detail, including its evidence
and verification, should not open it.

## Catalog and documentation changes

Keep each change narrow and source-backed. A catalog or manifest change must
carry its evidence where the changed fact lives. Cite at least one applicable
BCS-Y or BCS-S identifier, Ghidra decomp artifact, or capture reference. Pull
request prose alone is not a durable citation.

The doctrine pages under [`docs/ai_agents/`](docs/ai_agents/README.md) are
authoritative for public prose, comments, evidence classes, and claim wording.
Link to those contracts instead of copying them into new documentation.

Follow the generated-output contract in the [tooling guide](tools/README.md)
and the preservation rules in the
[evidence standard](docs/ai_agents/evidence-and-claims.md).

## Verification

The [checks workflow](.github/workflows/checks.yml) is the authoritative list
of CI-covered checks. Run the applicable checks before opening a pull request.
The [verification policy](docs/ai_agents/verification.md) owns the beyond-CI
external-evidence checks and explains what each result proves.

Do not claim client, capture, or decompiler validation unless that track was
actually run and its artifact and result are identified.

## Pull requests

Keep each pull request focused on one catalog slice, documentation batch, or
tooling change. Explain the claim, identify the durable evidence, and describe
the verification performed. Address review with follow-up commits so the
review history remains readable.

## Community

Join the [project Discord](https://discord.gg/PxK5RJYQjm) for questions, design
discussion, and community support. Use the
[issue tracker](https://github.com/XIVLegacy/xivl-client-structs/issues) for
durable corrections and research findings.
