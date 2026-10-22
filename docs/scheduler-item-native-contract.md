# Chara scheduler, wait, item and log native contracts

[`manifests/scheduler_item_native_call_contract.json`](../manifests/scheduler_item_native_call_contract.json)
records the static Lua call contracts of ten natives. Three belong to the chara
scheduler (`_runCharaScheduler`, `_waitForCharaSchedulerFinished`,
`_setGroundOn`). One is the timed yield `_wait`. Five read the item packages of
a chara or the fields of an item control (`_getItem`, `_getEquippingItem`,
`_getItemPackageCapacity`, `_getCatalogID`, `_getNameIndex`). One writes a log
line (`_printLog`). Each row gives the registration site, the receiver type
check, the declared argument and return lists, the reads, the effects on client
state, the failure behavior and whether the call yields. The contracts describe
client marshalling and state, not scheduler content, item data, the Lua wrapper
logic or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data
at the cited addresses. `INFERRED` is a name or role taken from the
surrounding instructions that the bytes do not state. `unknown` was not
traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
Addresses are absolute VAs. The instruction listings were decoded directly
from the PE bytes through the section table after the size and hash were
checked. Callers were found by scanning `.text` for `rel32` `call` and `jmp`
instructions, so virtual and indirect callers are not covered.

The native set and the script bindings come from the script metadata. The
per-row `corpusCallSites` lists carry the call-site lines from
`xivl-client-scripts:lua/napi_index.json`. They show that a script contains a
call, not that a script reaches it at run time. `_runCharaScheduler` and
`_wait` list counts only because their line lists are long.

## Registration and dispatch

Five classes register the ten natives, each from the switchboard in slot 2 of
its vftable. The switchboard shape, the skip byte and the single `rel32` caller
of each registrar are the ones recorded for `SpreadSheet` in the
[SpreadSheet contracts](spreadsheet-native-contract.md#registration-and-dispatch).
The order is the position among the registrar calls of the switchboard.

| Class | Switchboard | Vftable | Natives (order) |
| --- | --- | --- | --- |
| `CharaBase` | `0x007574A0` | `0x00FD5CAC` | `_setGroundOn` (39), `_runCharaScheduler` (56), `_waitForCharaSchedulerFinished` (59), `_getItem` (64), `_getEquippingItem` (66), `_getItemPackageCapacity` (68) |
| `ActorBase` | `0x00753C30` | `0x00FD4FE4` | `_wait` (2) |
| `ItemBase` | `0x00753DD0` | `0x00FD5484` | `_getCatalogID` (1), `_getNameIndex` (9) |
| `WorldMaster` | `0x00754C70` | `0x00FD5864` | `_printLog` (4) |
| `Debug` | `0x00757CE0` | `0x00FD51DC` | `_printLog` (1), `_getItem` (19) |

`_getItem` and `_printLog` have a second registration on `Debug`. The script
index lists the `CharaBaseClass` binding for `_getItem` and the `WorldMaster`
binding for `_printLog` and no binding for the `Debug` registrations.

| Native | Registrar | Caller | Callback | Wrapper |
| --- | --- | --- | --- | --- |
| `_runCharaScheduler` | `0x0072F850` | `0x0075793F` | `0x006E48A0` | `0x00726460` |
| `_wait` | `0x0072E0B0` | `0x00753C61` | `0x006DBCB0` | `0x00726300` |
| `_waitForCharaSchedulerFinished` | `0x0072FC40` | `0x0075797E` | `0x006E4B40` | `0x00726460` |
| `_setGroundOn` | `0x0072EF20` | `0x007577DA` | `0x006E4260` | `0x00726460` |
| `_getCatalogID` | `0x0074DA90` | `0x00753DEC` | `0x00701820` | `0x00726670` |
| `_getNameIndex` | `0x0074E510` | `0x00753E94` | `0x00701BF0` | `0x00726670` |
| `_getItem` | `0x00755A60` | `0x007579E7` | `0x007087A0` | `0x00726510` |
| `_getItem` (`Debug`) | `0x00750140` | `0x00757E76` | `0x006FD350` | `0x00726930` |
| `_getEquippingItem` | `0x00755D00` | `0x00757A11` | `0x007088E0` | `0x00726510` |
| `_getItemPackageCapacity` | `0x00755FA0` | `0x00757A3B` | `0x00708A20` | `0x00726510` |
| `_printLog` | `0x0073AD70` | `0x00754CCB` | `0x006EC230` | `0x00726CA0` |
| `_printLog` (`Debug`) | `0x007363F0` | `0x00757CFC` | `0x006E7AB0` | `0x00726930` |

Every registrar builds the return list first and the argument list second and
installs the functor through `0x00CCCAD0` under the name literal with the
adjustment 0. Six wrappers appear. Each constructs the `0x58` byte functor in
place and every holder shares the invoke routine of its class, which casts the
receiver with `0x009DA6CC` from `LuaControl` to the owner class. A null cast
returns false without calling the callback, and the `0x00D19B70` failure path
reports it as in the [talk contracts](talk-native-contract.md#registration-and-dispatch).
The qualifier letter of the holder RTTI name tells const (`BEX`) from non-const
(`AEX`).

| Wrapper | Owner class | Qualifier | Holder vftable | Invoke | Target type descriptor |
| --- | --- | --- | --- | --- | --- |
| `0x00726460` | `CharaBase` | const | `0x00FD5D54` | `0x0071E1E0` | `0x012709A4` |
| `0x00726510` | `CharaBase` | non-const | `0x00FD5D60` | `0x0071E1E0` | `0x012709A4` |
| `0x00726300` | `ActorBase` | const | `0x00FD5B10` | `0x0071A6D0` | `0x01270964` |
| `0x00726670` | `ItemBase` | const | `0x00FD5B34` | `0x0071A910` | `0x012C0864` |
| `0x00726930` | `Debug` | const | `0x00FD5B4C` | `0x0071AB50` | `0x012C0324` |
| `0x00726CA0` | `WorldMaster` | const | `0x00FD5B70` | `0x0071AE70` | `0x012C1328` |

Argument indices count internal `ExecuteParameters` cells after the receiver.
The readers are the ones of the widget contracts, `0x005819A0` for an int,
`0x0071BAC0` for a float, `0x0071BA00` for a bool and `0x0071CE70` for a
`Utf8String`. Each reader follows a cell vector size test that calls
`0x009D22B4` on failure, the invalid-parameter route of the
[target cursor record](target-cursor-native-contract.md#selection-and-the-failure-path).

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_runCharaScheduler` | `CharaBase` | `int` | none | no |
| `_waitForCharaSchedulerFinished` | `CharaBase` | `int` | none | yes |
| `_setGroundOn` | `CharaBase` | `bool` | none | no |
| `_wait` | `ActorBase` | `float` | none | yes |
| `_getItem` | `CharaBase` | `int`, `int` | `LuaControl*` or nil | no |
| `_getItem` | `Debug` | `LuaControl*`, `int`, `int` | `LuaControl*` or nil | no |
| `_getEquippingItem` | `CharaBase` | `int` | `LuaControl*` or nil | no |
| `_getItemPackageCapacity` | `CharaBase` | `int` | `int` | no |
| `_getCatalogID` | `ItemBase` | none | `int` | no |
| `_getNameIndex` | `ItemBase` | none | `int` | no |
| `_printLog` | `WorldMaster`, `Debug` | `Utf8String` | none | no |

The list builders are `0x0072B440` for none, `0x00728C20` for an int,
`0x0072B390` for a float, `0x00728B70` for a bool, `0x0072B5B0` for a
`Utf8String`, `0x00583CE0` for two ints, `0x0072C260` for a `LuaControl*` and
`0x0072C0E0` for the three entries of the `Debug` `_getItem`. The manifest rows
carry each name literal, name reference, install call, callback load and list
builder.

## World object and identity lookup

The callbacks reach one client object through `0x00CC7510` on
`ExecuteParameters` `+0x04`. With `R` the address that routine returns they
read `X = [R]`, `Y = [X + 0x04]`, `W = [Y]` and `V = [W]`. `V` is the object
that the sheet manager chain of the SpreadSheet contracts reaches. It holds
the identity registry at `+0x4AC`, the log sink pointer at `+0x660` and the
sheet manager at `+0x174F8`. The constructor `0x004DBF40` of
`Application::Main::RaptureElementContainer` (vftable `0x00F912E4`) initializes
the same three fields and `MainModule` (vftable `0x00F9142C`) calls it once at
`0x004DC414`, so `V` is `INFERRED` to be that container.

The scheduler natives name their receiver by the identity at
`ExecuteParameters` `+0x0C` and resolve it through `0x004D9970`, which adds
`0x4AC` to its receiver and calls `0x004DE190`. That routine returns 0 for the
identity `0xC0000000` and otherwise finds the identity in the tree at registry
`+0x38` and returns the dword at node `+0x10`, or 0 when the identity is absent.
The glue routines `0x0075C420`, `0x0075C400` and `0x0075C3E0` resolve the
identity and call the chara routine without a null test. A receiver that is
not in the registry therefore reaches the chara routine with a null `this`.
The run-time result of that was not observed.

## Chara scheduler natives

`_runCharaScheduler` (`0x006E48A0`) reads one int and calls `0x0075C420`.
That glue calls `0x0058CAF0`, which reads `this + 0x88` through `0x004D6750` and
calls `0x0058C690` with the int, that dword and a zero. `0x0058C690` zero
fills a `0x38` byte record, stores the arguments, classifies the int through
`0x00585800` with the default 5 and appends a queue entry built by
`0x00587370` to the container at the chara `+0xA80` through `0x005901D0`. The
native never touches the return container and never requests a yield, so the
Lua call returns as soon as the entry is queued.

`0x00585800` returns a category from its first argument or from 7 to `0x11`.
It chooses by comparing fields that `0x00798370` and `0x007982D0` split out of
the identifier and returns the first argument when no case matches. That the
int is a scheduler identifier and that the container is the queue that runs it
is `INFERRED` from the native name and from the wait native below.

`_waitForCharaSchedulerFinished` (`0x006E4B40`) reads the same kind of int. It
resolves the receiver through `0x0075C400`, which stores the chara pointer and
the int in a pair. It allocates a `0x0C` byte checker and constructs it through
`0x006DC0E0`. The vftable is `0x00FD50FC` and its RTTI name
`WaitForCharaSchedulerFinishedResumeChecker` is local to the native. The
checker keeps the chara pointer and the int at `+0x04` and `+0x08`, so it holds
the pointer and not the identity. The native then requests a yield with the
checker and returns.

The checker poll in slot 1 (`0x006DC150`) calls `0x00758CE0`, which calls
`0x0058AB60` on the chara with the int. That routine maps the int to a category
through `0x00585800` with the default 5 and calls `0x00589F60`, which returns 0
for a category outside 1 to `0x19` and otherwise walks the ring of entry
pointers at the chara `+0x878 + category * 0x14`. It returns 1 when an entry has
a dword at `+0x10` equal to the int. A result of 1 stores the dword at
`0x0130CECC` in the result cell and any other result stores the dword at
`0x01377ECC`. The wait ends when the identifier has left its category ring.
That the ring holds the running entries and that the dword at `+0x10` is the
identifier is `INFERRED`. Whether the ring is fed from the queue at `+0xA80`
was not traced.

`_setGroundOn` (`0x006E4260`) reads a bool through `0x0071BA00` and keeps its low
byte. It calls `0x0075C3E0`, which resolves the identity and calls `0x00586750`.
That routine turns the bool into the dword 0 or 1 and calls `0x004D7980` with
the record number `0x12`, the address of the dword and the size 4.
`0x004D7980` builds a `ScenePacket` (RTTI `.?AVScenePacket@Scene@Application@@`,
vftable `0x00F8CC14`) through `0x004EC080` with the identity at `this + 0x88`,
the type word `0x12 + 0x15 = 0x27`, the payload and the size, then calls
virtual slot 3 of the object at `this + 0x84`. After the call the native clears
the byte at the receiver `+0xE1` when it is nonzero. The
[client architecture page](client-architecture.md) lists the same record 0x12 to
scene packet 0x27 path with no server-visible mirror. The consumer of the
scene packet and the role of the byte at `+0xE1` were not traced.

## Yield and resume

`_wait` (`0x006DBCB0`) is a thin callback. It builds an empty adapter, calls the
body `0x0078BED0` with `ExecuteParameters` and does not read the receiver. The
body reads one float through `0x0071BAC0` and converts it with
`cvtss2sd`, a multiply by the double `1000.0` at `0x00F91C48` and the 32 bit
`cvttsd2si eax, xmm0` at `0x0078BF5A`. The `cdq` at `0x0078BF5E` sign extends
the result into the high duration dword, so the duration is a signed 32 bit
millisecond count held in two dwords. A negative float gives a negative
duration. A NaN, an argument of about 2147483.648 seconds (24.855 days) or
more, and an argument below about -2147483.649 seconds make the instruction
return `0x80000000`, so the duration is also negative. It allocates `0x28`
bytes through `0x009D1B35` and constructs the checker through `0x0078B850`,
which stores the duration low and high dwords at `+0x08` and `+0x0C`. A failed
allocation passes a null checker.

The checker vftable is `0x00FE0548` with the RTTI name
`WaitResumeChecker` in an anonymous namespace and the base vftable `0x00FD4F5C`
(`ResumeCheckerInterface`). Slot 0 is `0x0078D980`, slot 1 `0x0078D940` and slot
2 `0x00A72A20`. The constructor runs `0x00D353F0` on the object at `+0x10`,
which stores the result of `WINMM.dll` `timeGetTime` (IAT cell `0x00F3E55C`)
at its `+0x08` and zero at `+0x0C`. For the checker these are the dwords at
`+0x18` and `+0x1C`. The poll in slot 1 (`0x0078D940`) calls `timeGetTime`,
subtracts the stored start as a 64 bit value and compares the result with the
duration, high dword first, with unsigned compares. An elapsed value that is
not below the duration stores the dword at `0x01377ECC` in the result cell. A
smaller value stores the dword at `0x0130CECC`.

Both wait natives end by calling `0x00CD2860` with `ECX` set to the Lua thread
at `ExecuteParameters` `+0x08` and the checker pointer. That routine calls
`0x00CCD390` on the dword at thread `+0x04`. `0x00CCD390` is
`LuaThreadImpl::YieldLua` by the literal at `0x0110E44C`. With the flag byte
zero it compares the byte at its receiver `+0x138` with the byte at
`0x01377FBA` and on a mismatch formats the literal with the line `0x27F` and
calls the diagnostic pair `0x00CF3360` and `0x00CF38A0`. It then stores the
checker at receiver `+0xE8` and destroys a different nonnull previous checker
through slot 0. The state byte at `+0x138` is written by `0x00CD27B0` and
`0x00CD2830`, which the body `0x0078BFC0` of `_restrictYieldFunction` reaches.
The accepted state is 0. `0x00CD27B0` writes 2 only when the state is the
accepted one, so a thread in the restricted state fails the compare.
`0x00CD2830` writes the accepted value only when the state is not the byte 1 at
`0x0130D424`, and otherwise tail-jumps to `0x00CD63F0` (untraced). The state
names are `INFERRED`. `_restrictYieldFunction` is not covered by this record.

The yield is therefore a stored checker and not a call that suspends inside
the native. The functor executor `0x00D19B70` (`Functor::Execute` by the
literal at `0x0110F57C`) calls the holder invoke at `0x00D19D3B`, then tests
`0x00CCD380` at `0x00D19DD7`, which returns whether the dword at `+0xE8` of the
thread implementation is nonzero. A set test takes the branch at `0x00D19DE4`
that calls a virtual slot at `+0x04` of the object at `+0x218` of its second
argument. That argument is `INFERRED` to be the engine object because it also
supplies the member at `+0x1C0` that `YieldLua` reads from the engine at
thread implementation `+0x0C`. A clear test takes the branch at `0x00D19F0A`.
That the first branch is the Lua yield exit follows from the test and was not
traced further.

The resume side is the update loop `0x00CF1B50`, called from `0x00CC98B5`. For
each thread it reaches it calls `0x00CCD4A0` at `0x00CF1CD7`. That routine
stores the dword at `0x0130CED0` in the result cell when the thread has no
checker and otherwise calls checker slot 1. A result equal to the dword at
`0x0130CECC` leaves the thread parked. Any other result resumes it through
`0x00CCF290`, which the client architecture page names
`LuaThreadImpl::Resume`, or through `0x00CCE1C0` when the result equals the
dword at `0x0130CED0`. The loop also stops on a `timeGetTime` budget held in
the word at its receiver `+0x3C`.

| Cell | Value | Stored by |
| --- | ---: | --- |
| `0x01377ECC` | 0 | Checker polls that are done. |
| `0x0130CECC` | 1 | Checker polls that still wait. |
| `0x0130CED0` | 2 | `0x00CCD4A0` for a thread without a checker. |

The values are `STATIC`. The first lies beyond the raw data of `.data`, so 0
is the loader zero fill, and no instruction in `.text` stores to the cells with
an absolute operand. The readings done, waiting and no checker are `INFERRED`
from the branches of the update loop. They agree with the two polls above, in
which an elapsed time reaching the duration and an empty entry ring both
store `0x01377ECC`.

Two consequences follow for a client that implements the waits. A `_wait` thread
always parks at least until the next update loop pass, because the first poll
runs after the native has returned, and a zero duration is done at that poll.
A negative duration, including every NaN or out of range argument, has a high
dword of `0xFFFFFFFF`. The elapsed high dword is the borrow of the 32 bit tick
subtraction, since the stored high dword at `+0x1C` is 0. It stays 0 until
`timeGetTime` wraps below the stored start. The unsigned high compare then
treats a negative duration as larger than the elapsed value, so the poll keeps
reporting waiting. After a tick wrap the elapsed high dword equals the
negative duration's and the low dword compare decides. Both are `INFERRED`
from the compares. Whether the per-thread
timer scheduler `0x00CEF510` that the client architecture page names also acts
on a `_wait` thread was not traced.

## Item packages

The item natives share one package model. `0x006F51A0` returns the package
manager held at owner `+0xD8` and allocates a `0x78` byte manager through
`0x006F5100` when the dword is null. The owner is the `CharaBase` for the three
chara natives and the dword at `ItemBase` `+0x64` for the two `ItemBase`
natives. `0x006E5BA0` is a find on the tree at manager `+0x08` keyed by a dword
and returns the dword at node `+0x10`, the package record, or 0. `0x006EE3E0`
takes the address of a package key and a slot. It finds the package, indexes the
vector at package record `+0x10` through `0x0052F7F0` and reads a slot
descriptor pointer. A null descriptor returns 0. A descriptor with a nonzero
dword at `+0x08` returns that dword. A descriptor with a zero dword at `+0x08`
and neither dword `+0x0C` nor dword `+0x10` equal to -1 repeats the lookup with
the package key at `+0x0C` and the slot at `+0x10`, so a slot can redirect to
another package and slot. Any other descriptor returns 0. `0x006EE480` is the
same routine on the tree at manager `+0x14`.

`0x0052F7F0` is a checked vector index. An index at or beyond the vector size
calls `0x005CF390`, which builds the message `invalid vector<T> subscript`.
The compare at `0x0052F80D..0x0052F811` is unsigned, so the index -1 from a
Lua slot of 0 also throws (`STATIC`). That path is reachable from `_getItem`
and `_getEquippingItem` with a slot of 0 or past the end of the package
vector. The package find itself returns 0 for an absent
key, so an absent package gives nil.

The package and slot arguments are 1-based in Lua. The helpers pass them
through `0x0078BC90` and `0x0078BCD0`, which return their argument minus 1.
`_getEquippingItem` takes only a slot and looks it up in the package whose key
is the dword `0x000000FE` at `0x00FE050C`. The two following dwords at that
address hold `0xFD` and `0xFC`. That the key names the equipment package is
`INFERRED`.

`_getItem` (`0x007087A0`) builds a stack `ItemBase` with `0x006DD450` and calls
the helper `0x00702400` with the receiver and the flag 0. The helper reads the
package and the slot, calls `0x006EE3E0` and pushes nil through `0x00748920`
for a 0 result. Otherwise it calls `0x006E2770` and pushes the control it
returns through `0x00748B30`. The sibling `_getExtendedTemporaryItem` calls the
same helper with the flag 1. `_getEquippingItem` (`0x007088E0`) follows the
same shape through `0x00702510`, with a first lookup of the package that pushes
nil when the package is missing. The `Debug` registration of `_getItem`
(`0x006FD350`) takes the chara as its first argument through `0x0071BC90`, which
casts the control to `CharaBase`, and repeats the same lookup with both numbers
decremented.

`0x006E2770` creates a control and casts it to `ItemBase` with the type
descriptor `0x012C0864`. It stores a dword at `+0x64`, a dword at `+0x68`, a
dword at `+0x6C` and a byte at `+0x70`. These are the four fields that the two
`ItemBase` natives read. The control that `_getItem` returns is therefore a
reference made of the owner, the package key, the slot and a variant byte, and
`_getCatalogID` and `_getNameIndex` look the record up again on every call.
The routines `0x00701820` and `0x00701BF0` are the same except for the field
read. Both load the owner at `+0x64`, the key address `+0x68`, the slot `+0x6C`
and the variant byte `+0x70`, call `0x006F51A0` and choose `0x006EE480` for a
variant byte of 1 or `0x006EE3E0` otherwise. They push the dword at record
`+0x24` and `+0x20`. Neither tests the lookup result, so a result of 0 reads the
address `0x00000024` or `0x00000020`. The reading of those dwords as the catalog
identifier and the name sheet index comes from the native names. The sources of
the dwords are in [Item record builders](#item-record-builders). What the
variant byte selects and the origin of the tree at manager `+0x14` were not
traced.

`_getItemPackageCapacity` (`0x00708A20`) reads the package number, subtracts 1
and calls `0x006E5BA0`. A result of 0 pushes the int 0 and otherwise the dword
at package record `+0x08` is pushed through `0x00584F70`. That the dword is the
slot capacity comes from the native name.

## Item record builders

The record that `0x006EE3E0` returns is an `Item` derived object, because the
fields the item natives read lie in the layout that the `Item` base
constructor `0x006DF580` (vftable `0x00FD5A14`) fills. The item update
execution `0x006F4490` creates one such object per decoded record. It
allocates `0xD0` bytes and constructs them through `0x006EF520`, which forwards
six arguments to `0x006DF580` and then stores the vftable `0x00FD5C68`, RTTI
`ItemBuilder`. `0x0076B760` decodes the `0x70` byte wire record into a `0x58`
byte decoded record. All offsets below are record relative.

| Wire record | Decoded record | Item field | Read by |
| --- | --- | --- | --- |
| `+0x00`, `+0x04` | `+0x00`, `+0x04` | `+0x10`, `+0x14` | The pair collected by the Bazaar serializer. |
| `+0x08` | `+0x08` | `+0x18` | `_countStack` through the nameplate contracts. |
| `+0x1C` | `+0x0C` | `+0x1C` | None of these natives. |
| `+0x0C` | `+0x10` | `+0x24` | `_getCatalogID`. |
| `+0x28`, one byte | `+0x16` | `+0x20`, zero extended | `_getNameIndex`. |

`_getCatalogID` therefore returns the dword at wire record `+0x0C` and
`_getNameIndex` returns the byte at wire record `+0x28`. Neither reads the
eight byte pair at wire `+0x00` and `+0x04`, which the
[Bazaar contract](bazaar-native-wire-contract.md#dealing-fields-read-by-lua)
treats as the item identity pair. That the dword is the catalog identifier and
the byte the name sheet index remains `INFERRED` from the native names. The
helper `0x00702A20` builds an `ItemBuilder` through `0x006EF490` for a native
that reads three ints, and its field sources were not traced. How the built
item reaches the package slot that `0x006EE3E0` returns was not traced.

## Log output

`_printLog` has two registrations that differ only in the class and the kind.
Both read one `Utf8String` at cell 0 through `0x0071CE70` and call `0x0075D4C0`
with the engine handle, a kind, a prefix string, the text and a zero flag. The
`WorldMaster` callback (`0x006EC230`) passes the kind `0x20` and the static
object at `0x01266B10`, whose text pointer addresses a zero byte, so the prefix
is empty. The `Debug` callback (`0x006E7AB0`) passes the kind `0x1F` and a
`Utf8String` built from the literal `<debug>` at `0x00FD46D4`.

`0x0075D4C0` calls `0x004D6D90` on the world object. That routine does nothing
when the dword at world object `+0x660` is null. With a zero flag it calls
`0x004CE760` on that sink with the kind, the prefix and the text. With a nonzero
flag it formats the prefix through `0x0044AB90` first. Neither native uses the
formatted branch.

The sink is a `0x74` byte `Application::Misc::RaptureLogModule` (vftable
`0x00F91434`), allocated at `0x004DC62E`, constructed by `0x004DEE90` and
stored at `V +0x660` by `0x004DC66E`. `0x004CE760` formats the kind word with
the literal `%04X`, concatenates the prefix and the text and passes the
character pointer and the length to virtual slot 7 of the module, `0x00C9AD40`.
That routine appends the text to the container at module `+0x2C`, increments
the count at `+0x10`, increments the dword at `+0x14` when the previous count is at least
`0x4B0` and returns the previous count as an entry id. `0x004CE760` then grows
the vector of 20 byte entries at module `+0x4C` to kind plus 1 entries through
`0x004D56F0`, appends the id to the queue of the entry for the kind through
`0x004571F0` and removes ids from the front of that queue while they are below
the dword that `0x00C9A8C0` returns. That dword is the value at `+0x14`, or -1
when the count at `+0x10` is 0.

Other callers of `0x004D6D90` and `0x0075D4C0` pass the kind 0x20 in
`0x004C3BE0`, `0x00519440` and `0x005614B0`, 0x1F in `0x0075BC90` and
`0x0071C5F0`, 1 in `0x0075BEF0`, 2 in `0x0075BFD0` and 0x19 in `0x0075C0B0`.
`0x0075BC90` builds the literal `<debug>`, `0x0071C5F0` the literal
`<debug>: ` and `0x005614B0` refers to `xtx/_text_ui`, ` 2010 ` and
` 2010, 2011 `. That kind 0x1F carries debug lines and kind 0x20 general system
lines is `INFERRED` from those literals. The names of the kinds and the
consumers of the per-kind queues were not traced.

## Ledger rows

These rows of the unimplemented ledger now have a registration, argument list,
return list, receiver check and callback contract: `_runCharaScheduler`,
`_wait`, `_waitForCharaSchedulerFinished`, `_getCatalogID`, `_getItem`,
`_printLog`, `_getEquippingItem`, `_getItemPackageCapacity`, `_setGroundOn` and
`_getNameIndex`. A client that implements them still needs the scheduler queue
consumers, the item package data from decoded static client data and the sink
behind the log output, which this record does not supply.

## Open

- The consumers of the queue at chara `+0xA80`, how an entry runs, whether the
  ring at `+0x878` is fed from it, and the run-time behavior of a null chara
  after the identity lookup.
- The Lua yield exit behind the branch at `0x00D19DE4`, the body of `0x00CCE1C0`
  and the relation between the update loop and the timer scheduler `0x00CEF510`.
- The control creation in `0x006E2770`, the variant byte at `ItemBase` `+0x70`,
  the tree at manager `+0x14`, the package numbering, the install of a built
  item into its package slot and the `_getExtendedTemporary*` siblings.
- The consumers of the log module queues and the names of the kinds, and the
  consumer of scene packet type `0x27` and of the byte at chara `+0xE1`.
- Whether the Lua wrappers in `chara/charabaseclass_u`, `actorbaseclass_u`,
  `item/itembaseclass_u` and `world/worldmaster_u` adjust the arguments.
- The process behavior of the invalid-parameter route and of the
  `invalid vector<T> subscript` throw.

The ranked list of the next natives lives in the
[fade, actor and group contracts](fade-actor-group-native-contract.md#open).
The [nameplate, actor and group contracts](nameplate-group-native-contract.md)
cover `_countStack`, `_getItemPackageFreeSpace`, `_countMember` and
`_isMember` from the earlier ranking and record `_isEquipping`, `_isStackable`,
`_hasItemPackage` and `_getMaxStack` as related rows.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes. The listings behind this
record came from a Capstone 5.0.7 x86-32 decode of the file through its
section table. With explicit project and JDK bindings and a new absolute
output path, the repository route for function listings is:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Switchboards and registrars | `0x007574A0,0x00753C30,0x00753DD0,0x00754C70,0x00757CE0,0x0072F850,0x0072E0B0,0x0072FC40,0x0072EF20,0x0074DA90,0x0074E510,0x00755A60,0x00750140,0x00755D00,0x00755FA0,0x0073AD70,0x007363F0` |
| List builders and wrappers | `0x0072B440,0x00728C20,0x0072B390,0x00728B70,0x0072B5B0,0x00583CE0,0x0072C260,0x0072C0E0,0x007270B0,0x00726460,0x00726510,0x00726300,0x00726670,0x00726930,0x00726CA0,0x0071E1E0,0x0071A6D0,0x0071A910,0x0071AB50,0x0071AE70` |
| Scheduler callbacks and glue | `0x006E48A0,0x006E4B40,0x006E4260,0x0075C420,0x0075C400,0x0075C3E0,0x004D9970,0x004DE190,0x0058CAF0,0x0058C690,0x00585800,0x00798370,0x0058AB60,0x00589F60,0x00586750,0x004D7980,0x004EC080` |
| Wait and yield | `0x006DBCB0,0x0078BED0,0x0078B850,0x00D353F0,0x0078D940,0x006DC0E0,0x006DC150,0x00758CE0,0x00CD2860,0x00CCD390,0x00CCD380,0x00CCD4A0,0x00CF1B50,0x00D19B70,0x00CD27B0,0x00CD2830,0x0078BFC0` |
| Item callbacks and lookup | `0x007087A0,0x00702400,0x007088E0,0x00702510,0x00708A20,0x00702740,0x00701820,0x00701BF0,0x006FD350,0x006F51A0,0x006E5BA0,0x006EE3E0,0x006EE480,0x0052F7F0,0x005CF390,0x006E2770,0x006DD450,0x0078BC90,0x0078BCD0,0x0071BC90` |
| Log output | `0x006EC230,0x006E7AB0,0x0075D450,0x0075D4C0,0x004D6D90` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
