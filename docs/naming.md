# Naming

Use source names when they are backed by the 1.23b client, RTTI, exported
symbols, or a documented Ghidra finding.

When a name is inferred, make that visible:

| Case | Rule |
|---|---|
| Known struct | Preserve the source-backed name. |
| Unknown struct | Use `Unknown` plus a stable subsystem hint, such as `UnknownUiNode`. |
| Unknown field | Use `field_0xNN` until a source-backed name exists. |
| Known field | Preserve the source-backed name and offset. |
| Ambiguous type | Use the narrowest safe primitive or pointer type and set the manifest `confidence` field. |

Prefer hex strings for offsets, sizes, addresses, and signature positions.

## Address convention

In `manifests/symbols.json`, the `address` field is the canonical virtual
address (VA), i.e. the in-memory address after image-base relocation that
Ghidra displays and that the `FUN_<va>` naming convention embeds.
The VA equals the relative virtual address (RVA) plus the PE image base
(`0x00400000` for the 1.23b binaries).

For example, the Murmur2 hash function lives at:

- VA `0x00D31490` (what goes in the manifest `address` field, what Ghidra
  displays, and what `FUN_00D31490` embeds)
- RVA `0x00931490` = `VA(0x00D31490) - image base(0x00400000)`

Symbol `name` fields embed the same VA the `address` field carries (e.g.
`CharacterModifyResponseHandler_FUN_00DA79D0`, address `0x00DA79D0`).

Raw RVA and doubly shifted values are invalid in the `address` field.
