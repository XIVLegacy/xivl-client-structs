# Style guide

Repository style covers authored Python, Ghidra Java, PowerShell, manifests,
and documentation. It does not establish client behavior, structure names,
field names, evidence strength, or catalog provenance.

## General

- Prefer existing local patterns once they exist.
- Keep changes scoped to the catalog, extractor, or research tool being
  changed.
- Use small, explicit functions and modules before adding abstractions.
- Follow the [comment policy](ai_agents/comments-and-prose.md) for source
  comments.
- Do not reformat generated catalogs or evidence records for style alone.

### Documentation

The public [documentation policy](ai_agents/README.md#documentation-policy) is
canonical for authored documentation. The
[evidence policy](ai_agents/evidence-and-claims.md) owns claim wording,
citations, confidence, and provenance. Structure and field naming rules live
in [naming.md](naming.md).

## Python

- Use 4 spaces for indentation and no tabs.
- Use `lower_snake_case` for modules, functions, and variables,
  `UpperCamelCase` for classes, and `UPPER_SNAKE_CASE` for constants.
- Group imports as standard library, third-party packages, then local modules.
- Prefer `pathlib.Path` for filesystem paths and explicit text encodings.
- Keep command entry points thin; put reusable work in importable functions.
- Raise or report specific failures instead of using broad exception handlers.
- Add type annotations where they clarify manifest records, addresses, paths,
  or public helper contracts.
- Use Ruff 0.15.21 as the Python formatter and linter. Run `ruff check
  --no-cache tools` and `ruff format --check --no-cache tools` from the
  repository root.

## Ghidra Java

- Use 4 spaces for indentation, no tabs, and braces around control-flow
  bodies.
- Use `UpperCamelCase` for classes and `lowerCamelCase` for methods, fields,
  parameters, and local variables.
- Keep post-scripts read-only unless their documented contract explicitly owns
  a repository output.
- Keep address parsing, program selection, and output formatting explicit.

## PowerShell

- Use approved verb-noun names for functions and 4 spaces for indentation.
- Pass paths as parameters and use literal-path operations for repository
  inputs.
- Set terminating error behavior deliberately at command boundaries.

## Manifests and generated output

- Preserve schema-defined names, identifier formats, field order, and null
  behavior.
- Change canonical manifests and generators through their documented owning
  path; never hand-edit generated products.
- Do not rename evidence-defined symbols or fields to satisfy code style.

## Verification

Use the owning commands in [tools/README.md](../tools/README.md). Formatting is
not a substitute for schema, catalog, generation, or evidence validation.
