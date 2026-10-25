# Target cursor native state

[`manifests/target_cursor_native_contract.json`](../manifests/target_cursor_native_contract.json)
records the client state behind the `DesktopWidget` target cursor natives. The
[boot contracts](boot-native-call-contract.md) record the Lua argument and
return types of these natives. This record covers what the workers do to the
cursor state: creation, replacement, selection, the range check, the empty
identity, the `_getTargetCharacter` result test and the side effects of
`_setTargetCursorImage`. The contracts describe client state, not server
behavior.

Each fact carries a tier. `STATIC` is read directly from instructions at the
cited addresses. `MEASURED` is counted from a pinned capture set by the method
named in the fact. `INFERRED` is a name or role taken from the surrounding
instructions that the bytes do not state. `unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
Addresses are absolute VAs. The instruction listings were decoded directly
from the PE bytes through the section table after the size and hash were
checked. Callers were found by scanning the `.text` section for `rel32` `call`
and `jmp` instructions, so virtual and indirect callers are not covered.

## Cursor state

`0x004D7310` returns the dword at `+0x4C0` of its receiver. Each cursor entry
point resolves the state object through it before using the vector or
`+0xB4` and `+0xB8`. `0x0075F060`, `0x0075B6C0`, `0x0075B700` and the other
`0x0075F...` thunks apply it to the dword stored at the start of their
receiver. `0x00777F50` is entered with the state object already in `ecx`.
`0x00562D30` is a method on the state object and is reached after the
resolution in `0x0075B6C0` and `0x0075B700`. The Lua callbacks load the worker receiver by
reading the dword at the address `0x00CC7510` returns, then the dword at
`+0x04` of that value, then the dword at `+0x04` of that value.

| Offset | Role | Tier |
| --- | --- | --- |
| `+0xA4` | Cursor vector. First pointer at `+0xA8`, end pointer at `+0xAC`, 4-byte entries that point at cursor objects. | STATIC |
| `+0xB4` | Current cursor pointer. 0 means none. | STATIC |
| `+0xB8` | Current cursor index. `0xFFFFFFFF` means none. `_getCurrentTargetCursor` pushes it plus 1. | STATIC |

`DesktopWidget +0x68` holds the count that `_initTargetCursors` was given.
No range check in the cursor workers reads it. Each one tests against the
vector size.

The values of `+0xB4` and `+0xB8` before the first `_initTargetCursors` call
are `unknown`. The only stores of the pair in the cursor workers are the reset
sites below, and the construction of the state object was not traced.

## Init

`_initTargetCursors` stores the count at `DesktopWidget +0x68` and jumps to
worker `0x0075EE70`. The worker builds the cursors and then writes
`+0xB4 = 0` and `+0xB8 = 0xFFFFFFFF` at `0x0075EEFA` and `0x0075EF04`. Those
stores run on every call and for every count. A count of 0 or below skips the
loop and still reaches them. After the stores the worker posts an 8-byte event
`{1, 0xC0000000}` through `0x004D7980` and sets a byte at `+0x04` of the
worker receiver. The event consumers were not traced.

The loop allocates `0x24` bytes, constructs the cursor through `0x00564B50` and
stores it at index `i` through `0x00565D30` with the select flag 0. The select
path of `0x00565D30` runs only for a nonzero flag, so init never selects a
cursor. `0x00565D30` grows the vector through `0x007A0A10` only when the size
is at most the index. The size therefore becomes the larger of its old value
and the count and never shrinks. The loop discards the pointer that
`0x00565D30` returns for the replaced entry and calls no release. A second
init with a smaller count replaces entries `0` to `count - 1` and leaves the
higher entries, with their targets, in place.

## Selection and the failure path

`_setCurrentTargetCursor` passes its argument minus 1 to `0x0075F060`, which
jumps to worker `0x00777F50`. The worker tests the signed index.

- A negative index stores `+0xB4 = 0` and `+0xB8 = 0xFFFFFFFF`. A Lua number of
  0 or below selects none.
- A nonnegative index must be below the vector size by an unsigned compare.
  A vector whose first pointer is null fails that test for every index.
- An index in range stores the vector entry at `+0xB4` and the index at
  `+0xB8`. Lua number `n` from 1 up to the vector size selects cursor `n`.

The worker then posts the same `{1, 0xC0000000}` event when the stored `+0xB8`
is nonzero, which includes the none value. It posts nothing while cursor index
0 is selected.

A failed range test calls `0x009D22B4`. That routine calls `0x009D2290` with
five zero arguments. `0x009D2290` loads a handler through the pointer cell at
`0x01363F1C` and jumps to it when one resolves. Otherwise it calls
`0x009DF94A` with argument 2 and then reaches `0x009D2194`, which builds an exception record with code `0xC000000D`, calls
`UnhandledExceptionFilter` and then `TerminateProcess` with that code. The
shape matches the C runtime invalid-parameter routine, an identification
tiered `INFERRED`. Whether the handler cell holds a handler at run time is
`unknown`, and so is the effect of the `0x009DF94A` call, which may select
the terminate mode or report the error before the exception record is built.

The same test and failure call guard every worker that takes a cursor index:

| Worker | Used by |
| --- | --- |
| `0x0075EFC0` | `_setTargetCursorImage` |
| `0x0075F010` | `_setTargetableDistance` |
| `0x00562D30` | `_setTargetCharacter`, through `0x0075B6C0` and `0x0075B700` |
| `0x0075F0E0` | `_getTargetCharacter` |
| `0x00777F50` | `_setCurrentTargetCursor` |

`0x0075B6C0` first resolves the character identity through `0x004D9970` and
does nothing when that returns null. `0x0075F070`, the worker of
`_setAllTargetCursorMask`, loops over the vector size and tests each entry the
same way.

## Fresh cursor and the target result

The constructor `0x00564B50` stores `0xC0000000` at `+0x04` of a cursor, the
empty identity, which is `-0x40000000` as a signed dword. No later store in
the constructor body changes it. `0x0075F0E0` returns the dword at `+0x04` of
the indexed cursor, and `_getTargetCharacter` compares it with `0xC0000000` and
pushes Nil on equality. A cursor that was never given a character therefore
reads Nil.

| Offset | Fresh value | Role | Tier |
| --- | --- | --- | --- |
| `+0x04` | `0xC0000000` | Target identity | STATIC |
| `+0x0C` | 0 | Target object pointer | INFERRED |
| `+0x10` | `50.0` float from `0x00FA3490` | Targetable distance, set by `0x0055EB30` | INFERRED |
| `+0x14` | `0xFFFFFFFF` | Not traced | unknown |
| `+0x18`, `+0x1C` | Child objects of `0xAC` bytes | Presentation children | INFERRED |
| `+0x20` | `0xFFFFFFFF` | Image value, set by `0x005623E0` | INFERRED |

`0x0055E7A0` sets a target. Its receiver is the indexed cursor, which
`0x00562D30` loads from the vector at `0x00562D94` and applies it to at
`0x00562E16` (`STATIC`). `0x0055EB30` is applied to the indexed cursor by
`0x0075F010` at `0x0075F04E` and stores its float at `+0x10`. `0x0055E7A0`
stores `0x004D6750` of the new object, the dword
at its `+0x88`, at `+0x04` and the object at `+0x0C`. A null target stores
`0xC0000000` and 0.

For a non-empty identity `_getTargetCharacter` converts the identity through
`0x00CC9320` and resolves a control through `0x00CC7A50`. A null control pushes
Nil. A control whose byte at `+0x5C` is zero pushes Nil. Any other control is
pushed through `0x00748B30`. The meaning of the `+0x5C` byte and its writers
are `unknown`.

## Mask

`_setAllTargetCursorMask` passes its flag to `0x0075F070`, which calls
`0x00563510` on every non-null vector entry. That routine writes the flag byte
to `+0x8C` of the two child objects at cursor `+0x18` and `+0x1C` and of the
objects held in the globals `0x0133728C` and `0x01337290`, and calls
`0x00562E90` on each. The flag is not kept on the state object. A child
starts with `+0x8C = 0` at `0x0055E97B`, so a cursor's own two children are
unmasked at creation. These facts are `STATIC`.

The two globals are shared. The cursor constructor creates them only while the
refcount at `0x01337288` is 0 (`0x00564CC1`), stores them at `0x00564D04` and
`0x00564D46`, and increments the refcount at `0x00564D50`. The release path at
`0x0055EAC9` decrements it and deletes and nulls both globals when it reaches
0. Between those points every cursor shares one pair of objects, and they keep
the mask flag across later cursor creation. The creation, sharing and
retention of the flag byte on the globals are `STATIC`. A cursor created after
the mask call therefore sees globals that are still flagged while any earlier
cursor survives, and recreated unflagged after the refcount has reached 0.
The `0x00562E90` method reads `+0x8C` of its own receiver at `0x00562EE5`.
Whether a cursor's drawing path consults the globals, and so whether a later
cursor is observably masked, was not traced and is `unknown`. The bytes do not
support reading the mask as not retained by the client. The references to
`0x01337288` were found by scanning, and the callers of the release path were
not traced.

## Image native

`_setTargetCursorImage` has two parts.

The store is `STATIC`. The callback reads two ints and passes argument 0 minus
1 and argument 1 to `0x0075EFC0`. After the range test, `0x005623E0` stores the
image value at cursor `+0x20` and calls `0x00561F10` with it on the objects at
cursor `+0x18` and `+0x1C`.

The cursor-one branch follows the store. The callback continues only when the
zero-based index is 0 and the byte at `DesktopWidget +0x7C` is 0. It builds the
widget identity into a stack slot through `0x00CC73B0` and tests it with
`0x00CC7BE0`, passing the immediate `0x0007A124` and -1. `0x00CC7BE0` returns
false when the `0x00CD8160` lookup is null, the record byte at `+0x7D` is 0 or
the record dword at `+0x14` is 0. Otherwise it calls `0x00CE53D0` on the object
that `0x00CEB490` returns for the object at engine `+0x214` and returns its
result.

Both outcomes then read the identity of cursor 0 through `0x0075F0E0` and fill a
local record through `0x0075D460` from the object Y that the next section
names. The widget identity feeds only the test: it is released through
`0x00CC9330` at `0x006E5131` right after the test, and its slot is later
overwritten with the cursor 0 identity on the passing branch and with the dword
at `0x0130C778` on the failing branch.

- When the test passes and `DesktopWidget +0x70` equals the dword at
  `0x0130C778`, the callback posts a message through `0x0075EB30` with the
  cursor 0 identity as both values and stores that identity through
  `0x00CC9320` at `+0x70`.
- When the test fails and `+0x70` differs from that dword, it posts the message
  with the cursor 0 identity as the first value and the dword as the second
  value, and stores the dword at `+0x70`.
- Otherwise it returns.

The dword at `0x0130C778` holds `0xE0000000` in the image and is referenced at
many call sites. `0x00CC9310` default-constructs an identity by copying it, and
the `DesktopWidget` constructor applies `0x00CC9310` to `+0x70`, so `+0x70`
starts as that value. Reading it as the no cached identity value is `INFERRED`.

### The posted message

`0x0075EB30` reads the dwords at its second and third pointer arguments and
fills a stack record with the code `0xCD` at `+0x00`, the size `0x18` at
`+0x04`, the first dword at `+0x18` and the second dword at `+0x1C`. It sends
the record through `0x004D6D10` with two zero arguments. Its receiver is the
12 byte record that `0x0075D460` fills. The method reads the first dword of that
record, loads the dword that it points at and uses that as the receiver of
`0x004D6D10`.

`0x0075D460` copies the dwords at `+0x00`, `+0x10` and `+0x14` of its receiver to
`+0x00`, `+0x04` and `+0x08` of the record that its argument points at. The
branch applies it to the object that it reads as the dword at `+0x04` of the
dword at the address `0x00CC7510` returns, the object whose dword at `+0x04` is
the worker receiver. `0x0075EB30` reads only the first dword of the record, and
the branch destroys the record through `0x0075AF70`, which only returns. The
routine has 30 direct callers, two of them in this callback. The others were not
traced.

`0x004D6D10` returns false when the dword at `+0x174EC` of its receiver is null
and otherwise jumps to `0x004E0240`. `0x004E0240` loads the dword at `+0x234` of
that object and the dword at `+0x70` of the result, returns false when either is
null, and otherwise calls `0x00DAE010` with the record and a pointer to a local
8 byte copy of its two trailing stack arguments, which `0x0075EB30` passes as 0.
`0x00DAE010` returns false while the state dword at its receiver `+0x8C` is 0
or below. A state of 1 or 2 admits only the code 2 and state 3 admits any code.
It copies size - `0x10` bytes from record `+0x18` to offset `+0x10` of the
packet body it builds and submits that body through `0x00DB06A0`. The `0xCD`
record is therefore copied as an 8 byte application, the outbound framing in the
[search and recruitment record](search-recruitment-wire-contract.md#outbound-framing)
(`STATIC`).

`xivl-opcodes:opcodes.json` names the serverbound opcode `0x00CD`
`SetTargetPacket` with the decompiler anchor `FUN_0075EB30`, and
[`manifests/c2s_payload_decoding.json`](../manifests/c2s_payload_decoding.json)
records its application as two dwords. Reading the record code as that opcode
is `INFERRED`. In [`manifests/c2s_payload_schemas.json`](../manifests/c2s_payload_schemas.json)
the 118 serverbound `0x00CD` samples have the most common value `0xE0` at byte
`+7` and 0 at bytes `+4` to `+6`, each at the fraction 0.805, and `0xC0` at byte
`+3` at the fraction 0.322 (`MEASURED`). Reading these bytes as the dwords
`0xE0000000` and `0xC0000000` is `INFERRED`, because the study records no
dominant u32 value at offset 0 or offset 4. Reading the second dword as the dword
at `0x0130C778` and a first dword as the empty cursor identity is likewise
`INFERRED`. The study does not separate which sender
produced a sample, so it does not show that this branch produced any.

### Widget fields and their writers

The `DesktopWidget` constructor `0x006E0650` sets `+0x68`, `+0x6C`, `+0x74`,
`+0x78`, `+0x7A`, `+0x7B` and `+0x7C` to 0, sets `+0x79` to 1 and initializes
the `+0x70` identity through `0x00CC9310`.

`LuaActorImpl` vftable slots 25 and 26, at `0x00FDFB90` and `0x00FDFB94`, hold
`0x0075D750` and `0x0075D780`. Each takes an index and an identity and calls the
trampoline `0x008A3EA0` or `0x008A3ED0` with the address `LuaActorImpl +0x04`,
the dword at `+0x08` and the two values. The trampolines call the
`DesktopWidget` methods `0x006FE960` and `0x006FEBB0`, whose only direct callers
are `0x008A3EB3` and `0x008A3EE3`. The strings at `0x00FD47D8` and
`0x00FD47EC` are `_onTargetChanged` and `_onTargetDecided`, and the methods pass
strings built from them to `0x00CC7A90`, which
[`manifests/symbols.json`](../manifests/symbols.json) records as the Lua
callback dispatcher. The index and identity producers that call the two slots
were not traced.

Both methods store 1 at `+0x7C` before they build the argument list and store 0
after the dispatcher returns, at `0x006FEA1E` and `0x006FEAE4` in
`0x006FE960` and at `0x006FEC6C` and `0x006FED32` in `0x006FEBB0`. Within
`0x006C0000` to `0x0071FFFF` a linear decode finds no other byte access at
`+0x7C` through a non-stack base besides the constructor store and the read in
the cursor-one branch at `0x006E50F3`. Other ranges were not decoded. Reading the
byte as a guard that keeps a synchronous script handler of the two events from
re-entering the cursor-one branch is `INFERRED`.

Both methods also write `+0x70`: for index 0 after the dispatch, and for any
index when `+0x68` is below index plus 1. After the dispatcher
returns they test the widget through `0x00CC7BE0` with `0x0007A124` at
`0x006FEB1F` and `0x006FED56` when the index is 0. A true result stores the
identity argument through `0x00CC9320` at `+0x70` and a false result stores the
dword at `0x0130C778`. Before the dispatch `0x006FE960` stores that dword at
`+0x70` and returns in two cases. The first is a cursor count at `+0x68` below
index plus 1. The second is an identity other than `0xC0000000` that resolves to
no control, with the index 0. That second case with a nonzero index returns
without a store. `0x006FEBB0` makes the same two checks in the reverse order.
After the dispatch `0x006FE960` also calls `0x00718EF0` on the object at `+0x6C`
with the control host and the resolved control when the control resolved and
`+0x6C` is nonzero. The
[tutorial control record](tutorial-control-native-contract.md) holds
`0x00718EF0`.

## Callers

Each direct call or jump to a worker has one source: `0x0075EE70` from
`0x006E5028`, `0x00777F50` from `0x0075F069`, `0x0075F060` from `0x006E532B` and
`0x00564B50` from `0x0075EECC`. A teardown loop at `0x0075EF40` clears every
entry through `0x00565D30` with a null object. Its only direct caller is
`0x0057828E`, which is not a cursor native.

## Open

- The construction of the state object and the values of `+0xB4` and `+0xB8`
  before the first init.
- The consumers of the `{1, 0xC0000000}` event.
- The meaning of the control byte at `+0x5C`.
- Whether the invalid-parameter handler cell at `0x01363F1C` holds a handler at
  run time.
- The field at cursor `+0x14` and the roles of the children at `+0x18` and
  `+0x1C`.
- The virtual callers of `LuaActorImpl` vftable slots 25 and 26, which reach the
  `DesktopWidget` methods writing `+0x7C`, and the index and identity they pass.
- Whether the `0x0007A124` query returns the value of the work member `mainTargetDecidedFlag` (key 500004), which the
  [stub overload record](stub-overload-native-contract.md#desktopwidget-_settargetcursorimage-cursor-one-branch)
  identifies.
- Whether a cursor's drawing path consults the shared globals at `0x0133728C`
  and `0x01337290`, which decides if a cursor created after a mask call is
  masked.
- The effect of the `0x009DF94A` call with argument 2 on the failure path.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
With explicit project and JDK bindings and a new absolute output path, use:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| State access and init | `0x004D7310,0x0075EE70,0x00564B50,0x00565D30,0x007A0A10,0x0075EF40` |
| Selection and getters | `0x0075F060,0x00777F50,0x0075B690,0x0075B6A0,0x0075F0E0,0x00562D30,0x0075B6C0,0x0075B700` |
| Failure path | `0x009D22B4,0x009D2290,0x009D2194` |
| Cursor and mask | `0x0055E7A0,0x0055EB30,0x005623E0,0x00563510,0x0055E910,0x0075EFC0,0x0075F010,0x0075F070` |
| Image branch | `0x00CC7BE0,0x0075EB30,0x006E0650,0x006FE960,0x006FEBB0,0x0075D460,0x00CC9310,0x004D6D10,0x004E0240,0x00DAE010,0x0075D750,0x0075D780,0x008A3EA0,0x008A3ED0` |
| Callbacks | `0x006E5030,0x006E52E0,0x006E53A0,0x006FD950,0x006FD990` |

The `_initTargetCursors` callback at `0x006E4FD0` is not a function entry in
the analyzed program. Read it as an instruction listing from that address.
Compare each store, compare and call with the address named in the manifest
facts. No decompiled body or ignored export is a tracked evidence dependency.
