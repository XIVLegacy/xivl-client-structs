# Evidence and claims

A promoted struct or symbol keeps its source locator, evidence citation,
confidence, and relevant address or RTTI identifier. Citations name the
artifact, function, address, or analysis note that supports the observation.
Dates in source citations remain part of the record. An entry with no
first-party artifact omits `sourceRefs`. An inference is labeled as such and
does not replace a source-backed value. A claim must be no broader than the
artifact that supports it.

## Evidence classes

Use the class that matches the source. Do not promote a generated report or an
agent summary as a stronger class than its inputs.

| Class | Use |
|---|---|
| Direct client or decomp evidence | Client structure, symbol, RTTI, address, and decompilation observations from an identified local artifact and locator. |
| Packet capture evidence | Wire layout, opcode, payload, and state observations supported by the pinned capture-derived inputs under `data/vendor/` and their `PROVENANCE.json`. |
| Script-derived evidence | A value recovered by a named extractor or validator from an identified input. Preserve the source and generator boundary instead of presenting the generated row as independent retail evidence. |
| Repository relationship evidence | Cross-references, bridge maps, receiver maps, and other catalog relationships. These establish an internal relationship unless their row carries a separate client or capture citation. |

## Evidence-kind vocabulary

Machine-readable role refinements use `evidenceKind` to state the observation
boundary. The validator accepts exactly these values:

| Value | Meaning |
|---|---|
| `pcap_observed` | The opcode or payload was observed in the pinned packet-capture corpus. |
| `pcap_unobserved` | The opcode was not observed in that corpus. The row records a bounded absence, not a retail behavior claim. |
| `live_validated` | The retail 1.23b client accepted the behavior in a live session. |

`live_validated` is stronger than a capture observation only for the specific
behavior the client accepted. It does not promote unrelated layout or semantic
claims. The client's acceptance is the evidence. Which server drove the live
session is not.

## Source lanes

For this repository, evidence is the retail client binary, observed wire bytes,
or the retail 1.23b client accepting behavior in a live session. Local Ghidra
analysis supplies client evidence and pinned capture fixtures supply wire
evidence. Repository relationships and external reconstruction agreement supply
context, not retail evidence.

The manifest `confidence` field is a catalog class, not a claim of retail
truth. `tools/validate_catalog.py` owns the allowed values:
`confirmed`, `confirmed-pcap-derived`, `confirmed-script-derived`, `probable`,
`structural`, `hypothesis-strong`, `inferred`, `candidate`, `unverified`, and
`superseded`.

`confirmed` records a promoted observation with supporting evidence.
`confirmed-pcap-derived` and `confirmed-script-derived` retain their narrower
source boundary. `probable`, `hypothesis-strong`, `inferred`, `candidate`, and
`unverified` must not be written as confirmed facts. `structural` describes a
relationship or shape signal, not resolved semantics. `superseded` is
historical and must not be promoted as current evidence.

## Claims and names

Separate client layout or symbol claims from wire observations, repository
relationships, and interpretations. A struct layout does not by itself prove
server behavior. A catalog relationship does not by itself prove retail
behavior. State uncertainty when the version, address, field meaning, or
interpretation is unresolved.

Use the narrowest supported name. Preserve `BCS-S` and `BCS-Y` identifiers,
`FUN_` names, addresses, RTTI identifiers, offsets, opcodes, and source dates
verbatim. Do not replace an uncertain source name with a cleaner guess.

## Numbers in prose

Every figure in authored prose has to carry its sentence's claim. Ask of each
one: is this number the finding, or is it scene-setting?

Evidence-critical figures stay verbatim. Row counts, coverage ratios, per-file
byte sizes and hashes, offsets, and extraction diffs are the claim itself - the
sentence exists to state them. Removing one destroys evidence.

Incidental figures go and the claim stays. When the sentence is about
something else, a count tells the reader nothing they can act on and becomes
stale when another run differs. Keep what was found. Drop the incidental count.

A hedge is the strongest tell. "approximately", "roughly", "about", or a
leading "~" before a figure means the author had already decided the figure
did not matter. Make it exact or cut it. Where an exact source exists, name
that source instead of restating its number in prose.

This governs prose the repository authors. A figure inside a quoted or
transcribed source is source content and stays verbatim, hedge included.

## Citations

A fact promoted from a first-party repository uses:

```text
repository-name:path/to/file
```

Add a stable row, symbol, function, address, or section locator when useful.
When byte identity matters, record a sha256 in the relevant provenance record
(`data/vendor/*/PROVENANCE.json`) rather than in the citation string. Commit
hashes and date pins are not citations: repository histories are rewritten
before publication, and dated "as of" claims rot. First-party revision
identifiers and observation dates remain source metadata.

In-repository `sourceRefs` use paths relative to this repository. Branch
names, working tree paths, and live sibling paths are not citations.

Some retained `sourceRefs` are historical record labels rather than paths:
`mdi-N`, `finding-N`, `ledger:<topic>`, `notes:<topic>`, and the register names
`promotion-register`, `maintainer-ledger`, `open-questions-register`, and
`architectural-findings-register`. They identify a record that carried the
claim when it was promoted and are not resolvable paths.

When evidence conflicts, prefer the most direct source for the target client
version. Record the conflict and uncertainty instead of merging incompatible
values.

## Relationship-specific evidence

A relationship extractor may promote a link only when its mechanism is
supported by a source. Shared naming is not enough. The `_getNetStatUser` and
`_getNetStatSystem` substruct link uses the shared `CharaBase.0xDC.0x10`
write/read chain and the apply-chain evidence from `FUN_006FA980` and
`FUN_006EEC00` in `manifests/receiver_apply_findings_wire_derived.json`, so that
rationale must remain available when the generated relationship catalog is
rebuilt.
