# Comments and prose

Code, manifests, schemas, and their validators are canonical. Delete
explanatory comments unless they preserve a fact that the use site cannot
carry on its own.

Deletion is the default. Keep a comment only when it records one of these:

- a current invariant enforced by a validator, generator, or check
- a client, wire, layout, RTTI, address, opcode, or decompilation quirk
- an evidence citation or stable `BCS-S`, `BCS-Y`, `FUN_`, or source locator
- a safety constraint that prevents a wrong path, overwrite, or unsafe write
- a CLI, manifest, schema, or regeneration contract not inferable from names
- a generated-output boundary that must remain with its owning generator

Keep evidence identifiers, addresses, RTTI names, offsets, opcodes, and dates
verbatim. They are not shortened for style. Compress other survivors to about
one line at the use site. Move a longer contract to the applicable README,
schema, or policy page and leave a short pointer when one is needed.

Treat Python docstrings, command help, PowerShell help text, schema
descriptions, and workflow step names as runtime or contract text. Tighten
those texts rather than deleting them casually. Treat generated comments and
descriptions as generated output: preserve them, or update the owning
generator and regenerate.

Remove branch-time narration, progress notes, and comments that merely repeat
the next statement. Do not use comments to preserve a maintainer work item in a
consumer-facing source file. When unsure, keep one concise line and flag it in
the review record.

Keep a source locator when it is the only durable link to the evidence:

```python
# Source: manifests/receiver_field_writes.json
```

Keep a safety constraint when the failure mode is not obvious from the code:

```powershell
# Refuse a live sibling path so the promoted source stays reproducible.
```

Delete narration that repeats the operation:

```python
# Load the manifest.
data = load_manifest(path)
```

## Authored public prose

Public prose, meaning the README, CONTRIBUTING, the docs index, and any
page a stranger reads, uses a plain, direct register.

- Avoid over-hyphenation and invented compound modifiers. Established
  technical terms keep their hyphens.
- Use semicolons sparingly, preferring periods, commas, or short lists.
- Cut parenthetical asides. If the aside matters, make it a short sentence
  of its own. If it does not, delete it.
- Short declarative sentences, one idea each. A rule gets one line of
  practical justification, then stops.
- Name the actual hazard or dependency directly: "X relies on Y" or "run X
  before Y". Do not substitute a metaphor for the relationship.

These rules apply to structured data as well as prose. Manifest strings and
keys are public product data: retain technical evidence, provenance,
uncertainty, and conclusions, but remove review summaries, internal task
metadata, prompts, and work-session diary narration.

Internal working docs are out of scope. These rules govern the public tier.
