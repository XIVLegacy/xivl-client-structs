# Generic _progFunc native contract

[manifests/progfunc_native_call_contract.json](../manifests/progfunc_native_call_contract.json)
records the generic wrapper representation and its operation-specific limits.

## Metadata

FINAL FANTASY XIV 1.23b, build
`2012.09.19.0001`. The identified `ffxivgame.exe` is `15996808` bytes,
SHA-256 `9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`,
with image base `0x00400000`. These are static client observations.

The observations used bounded read-only ghidra-cli instruction listings and
decompilation from the identified analyzed program. The executable size and
full SHA-256 were verified. Provider summaries matched the executable path,
program name, image base and x86 little-endian 32-bit language. The current
Ghidra FileBytes and loaded-image contents were not freshly compared with
the executable. Addresses are absolute VAs.

The output-table recipe maps VA `0x00D09F90` through the authenticated PE32
section table and reads exactly four little-endian DWORDs. It rechecks the
full executable size and hash before the fixed metadata read. No raw bytes,
retained logs or decompiled bodies are public evidence dependencies.

## Locators

The tracked catalog associates `_progFunc` with registration `0x00CD7920`,
implementation `0x00D09CD0`, and name pointer `0x0130D520`:
`xivl-client-structs:manifests/remaining_templates_attribution.json`,
`templates[regVa=0x00CD7920]`. The catalog relationship is also recorded in
`xivl-client-structs:manifests/lua_to_opcode.json`, `_progFunc`.

## Observations

Registration writes two DWORDs into an eight-byte payload and captures that
payload with implementation `0x00D09CD0`. Invocation selects capture 1 through
index `-0x2713`, then calls payload offset 4 with payload offset 0 and local
marshalling storage. Locators: `0x00CD7931..0x00CD7950`,
`0x00DCE2EF..0x00DCE356`, `0x00D09E19..0x00D09E3B`, and
`0x00DCD93C..0x00DCD95A`.

The input loop examines positions 1 through the smaller of the stack-slot
count and 8. Zero positions still reach dispatch. The local initializer gives
eight input records and four result records internal tag 1. Each 12-byte
record points from offset 4 to its own zero byte at offset 0. Result records
begin at local base `+0x60`. Locators: `0x00D09D3D..0x00D09D6B`,
`0x00D09E0B..0x00D09E19`, and `0x00D09FFC..0x00D0A0C1`.

VM tags and internal marshalling tags are separate domains. The first input
predicate accepts VM tag 3 or a nonzero conversion from `FUN_00DDE8B0`.
The numeric primitive reads a double, or returns zero on conversion failure.
If the first predicate rejects the input, VM tag 1 reaches a conversion that
normalizes its DWORD payload to 0 or 1. Other rejected inputs retain their
initialized record. Locators: `0x00DCDD50..0x00DCDD83`,
`0x00DCDED0..0x00DCDF02`, `0x00CF3700..0x00CF371A`, and
`0x00DCDF50..0x00DCDF76`.

The four-DWORD table at `0x00D09F90` selects these output cases:

| Internal tag | Case | Emitted VM representation |
|---|---|---|
| 0 | `0x00D09E57` | VM tag 1 with normalized 0-or-1 DWORD payload |
| 1 | `0x00D09E72` | VM tag 0 with no payload write |
| 2 | `0x00D09E7D` | VM tag 3 with signed-32 payload converted to double |
| 3 | `0x00D09E96` | VM tag 3 with float32 payload widened to double |

Each supported case advances the stack top by 16 bytes. The verified push
cores are `0x00DCE150..0x00DCE162`, `0x00DCE170..0x00DCE188`, and
`0x00DCE360..0x00DCE37D`. Untouched result defaults therefore emit four
VM-tag-0 slots on the normal path. A tag outside 0 through 3 skips insertion
for that record. The normal native return still declares 4 results:
`0x00D09E47..0x00D09E50`, `0x00D09EB6..0x00D09EBF`, and
`0x00D09F0E..0x00D09F36`.

## Inferences

The inspected wrapper instructions use a captured native dispatch identity.
Those instructions perform neither positional-string operation selection nor
operation-specific closure construction. This statement does not constrain
untraced callees or the bound callback. The capture join remains conditional
on the current closure header permitting capture 1.

## Unknowns

- Semantic VM and internal tag names are unpromoted.
- `FUN_00DDE8B0` coercion grammar, accepted tags, and mutations are untraced.
- `FUN_009D6636`, `FUN_009D6600`, numeric edge cases, and floating-point
  environment behavior remain unverified.
- Concrete callbacks, operation-specific valid arguments/results,
  `FUN_00DD6040` capture-header semantics, and complete exception behavior
  remain unknown.
- Global installation internals, initializer environment, language values,
  host-locale rules, and private decoded Lua are excluded.
- No target execution or live retail, network, or client acceptance was tested.
