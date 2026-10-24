# Nameplate, map marker, look-at, turn, visibility, floating offset and scheduler target native contracts

[`manifests/presentation_native_call_contract.json`](../manifests/presentation_native_call_contract.json)
records the static Lua call contracts of thirteen `CharaBase` native
registrations. Two set the nameplate (`_setNameplateColor`, `_setNameplateIcon`).
One sets the map marker (`_setMapMarker`). Four direct the look-at records of a
chara (`_lookAtCharacter`, `_lookAtPosition`, `_cancelLookAt`,
`_getLookAtCharacter`). Two turn a chara and wait for the turn (`_turnBack`,
`_waitForTurning`). Three set or read the visible flag and the floating offset
(`_setVisible`, `_setFloatingOffset`, `_getFloatingOffset`). One queues a chara
scheduler request against a target chara (`_runCharaSchedulerAgainstTarget`).
Each full row gives the registration site, the receiver type check, the declared
argument and return lists with their tag checks, the Lua pushes of every branch
including an absent receiver, the engine state that the callback reads and
writes, the messages it sends, the failure behavior and whether the call yields.
The contracts describe client marshalling and state, not nameplate content,
marker kinds, look-at timing or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data at
the cited addresses. `MEASURED` is counted by the method named in the fact from
the call-site index of the installed client scripts. `INFERRED` is a name or role
taken from the surrounding instructions or script names that the bytes do not
state. `unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
The listings, the caller scan and the reproduction route are the ones of the
[binding map contracts](binding-map-native-contract.md#binary-and-method). A
second pass re-read the bytes and compared every cited call target, immediate,
vftable cell, data cell and name literal with the claims below. The registrar
shape, the type registry, the cell tags and the invalid-parameter route are the
ones of the [nameplate, actor and group contracts](nameplate-group-native-contract.md)
and the [work binder contracts](work-binder-native-contract.md#binary-and-method).
The chara scheduler queue is the one of the
[scheduler and item contracts](scheduler-item-native-contract.md#chara-scheduler-natives).
`R`, `X`, `Y`, `W` and `V` name the world object chain of the
[scheduler contracts](scheduler-item-native-contract.md#world-object-and-identity-lookup).

The call-site and script counts agree with
`xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. They show that a
script contains a call, not that a script reaches it at run time. The argument
counts, the direct call counts, the return counts, the constants and the
descriptor names come from a local Lua 5.1 bytecode scan of the installed client
scripts, decoded with
[`tools/decode_lpb.py`](../tools/decode_lpb.py). The script sources are not
redistributed and no tracked artifact carries those values, so they are
`INFERRED`.

## Registration

Every native is declared by a `_u` script descriptor named `<name>_inl` in
`chara/charabaseclass_u`. Its prototype returns the selector `self` and the
target `<name>_cpp`, and the scan finds all thirteen descriptors (`INFERRED`). The
order of a native is its position among the 81 rel32 calls of the `CharaBase`
switchboard `0x007574A0`, stored at slot 2 of the vftable `0x00FD5CAC`. Each
registrar has one rel32 caller and each name literal has one referencing
instruction. Each callback address appears once in the image, in its registrar.

| Native | Order | Registrar | Caller | Callback | Wrapper |
| --- | ---: | --- | --- | --- | --- |
| `_setNameplateColor` | 29 | `0x00740FB0` | `0x00757708` | `0x006E3E00` | `0x00726460` |
| `_setNameplateIcon` | 30 | `0x0072E890` | `0x0075771D` | `0x006E3F80` | `0x00726460` |
| `_setFloatingOffset` | 34 | `0x0072EC80` | `0x00757771` | `0x006E4170` | `0x00726460` |
| `_getFloatingOffset` | 35 | `0x0074C1A0` | `0x00757786` | `0x006FA590` | `0x00726460` |
| `_setVisible` | 38 | `0x0072EDD0` | `0x007577C5` | `0x006E41E0` | `0x00726460` |
| `_setMapMarker` | 40 | `0x0072F070` | `0x007577EF` | `0x0071DFD0` | `0x00726510` |
| `_lookAtCharacter` | 50 | `0x0072F5B0` | `0x007578C1` | `0x006E43A0` | `0x00726460` |
| `_lookAtPosition` | 52 | `0x00741100` | `0x007578EB` | `0x006E44B0` | `0x00726460` |
| `_cancelLookAt` | 54 | `0x0072F700` | `0x00757915` | `0x006E16A0` | `0x00726460` |
| `_getLookAtCharacter` | 55 | `0x0074C590` | `0x0075792A` | `0x006FA690` | `0x00726460` |
| `_runCharaSchedulerAgainstTarget` | 58 | `0x0072FAF0` | `0x00757969` | `0x006E49A0` | `0x00726460` |
| `_turnBack` | 62 | `0x00730030` | `0x007579BD` | `0x006E16D0` | `0x00726460` |
| `_waitForTurning` | 63 | `0x00730180` | `0x007579D2` | `0x006E1700` | `0x00726460` |

The wrappers are the `CharaBase` holders `0x00726460`, const, and `0x00726510`,
non-const, recorded in the
[scheduler and item contracts](scheduler-item-native-contract.md). Their invoke
routine `0x0071E1E0` casts the receiver from `LuaControl` (`0x01270B4C`) to
`CharaBase` (`0x012709A4`) and returns without calling the callback when the cast
gives a null pointer. A receiver that is not a `CharaBase` therefore reaches no
callback (`STATIC`). Only `_setMapMarker` uses the non-const holder.

Every registrar builds the return list first and the argument list second. The
list builders select the type registry entries 0 to 4, which are int, float, bool,
`Utf8String` and `LuaControl*`.

| Builder | List |
| --- | --- |
| `0x0072B440` | empty |
| `0x0072B390` | one float |
| `0x00728B70` | one bool |
| `0x0072C260` | one `LuaControl*` |
| `0x0072B660` | three ints |
| `0x00740020` | an int, then four floats |
| `0x0072B920` | a `LuaControl*`, then a float |
| `0x00740130` | four floats |
| `0x0072B730` | an int, then two `Utf8String` values |
| `0x0072BB20` | an int, a `LuaControl*`, then an int |

The argument readers are `0x005819A0` for an int, `0x0071BAC0` for a float,
`0x0071BA00` for a bool and `0x0071CE70` for a `Utf8String`, which read the cell
tags 0, 1, 2 and 3. A mismatched tag reaches `0x00CCA730`. The control reader
`0x0071BC90` reads the cell tag 4. It passes a null pointer, casts a non-null
control from `LuaControl` to `CharaBase` with `0x009DA6CC`, and for a failed cast
or any other tag, `Nil` included, reaches `0x00CCA730` and returns the address of
the static zero holder `0x0134B488`. Each read follows a cell vector size test
that calls `0x009D22B4` on failure, the invalid-parameter route of the
[target cursor record](target-cursor-native-contract.md#selection-and-the-failure-path).
The marshaller `0x00D19A20` fills a position beyond the Lua top with one tag 6
placeholder.

## Receivers and lookups

The callbacks reach one client object through `0x00CC7510` on
`ExecuteParameters` `+0x04`. With `R` the address that routine returns, `X` is the
dword at `R`, `Y` the dword at `X +0x04`, `W` the dword at `Y` and `V` the dword
at `W`. `Z` is the dword at `Y +0x04`. The nameplate pair calls its glue routine
on `Z`. The other callbacks call theirs on `W`.

Every glue routine takes the address of a local that holds the receiver identity
from `ExecuteParameters` `+0x0C` and resolves it through `0x004D9970`. That routine
adds `0x4AC` to its receiver and calls `0x004DE190`, which returns 0 for the
identity `0xC0000000` and otherwise finds the identity in the tree at registry
`+0x38` and returns the dword at node `+0x10`, or 0 when the identity is absent.
The nameplate glue routines `0x0075B570` and `0x0075B5C0` return on a null result. The
other glue routines use the result as `this` without a test, so an absent
receiver reaches a chara routine with a null `this`. Those routines then read or
write at a small address and their run-time effect was not run.

Three natives send a scene record. `0x004D7980` adds `0x15` to a record number,
builds a message through `0x004EC080` with the identity at `this +0x88` and hands
it to virtual slot 3 of the object at `this +0x84`. `0x004D7890`, which the
[Chocobo camera natives](tutorial-control-native-contract.md#chocobo-camera) also
call, builds its message with the type `0x10` or `0x11` and no added offset. The
consumers of these messages were not traced.

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_setNameplateColor` | `CharaBase` | `int`, `float`, `float`, `float`, `float` | none | no |
| `_setNameplateIcon` | `CharaBase` | `int`, `int`, `int` | none | no |
| `_setMapMarker` | `CharaBase` | `int`, `Utf8String`, `Utf8String` | none | no |
| `_lookAtCharacter` | `CharaBase` | `LuaControl*`, `float` | none | no |
| `_lookAtPosition` | `CharaBase` | `float`, `float`, `float`, `float` | none | no |
| `_cancelLookAt` | `CharaBase` | none | none | no |
| `_getLookAtCharacter` | `CharaBase` | none | `LuaControl*` or nil | no |
| `_turnBack` | `CharaBase` | none | none | no |
| `_waitForTurning` | `CharaBase` | none | none | when the turn bit is set |
| `_setVisible` | `CharaBase` | `bool` | none | no |
| `_setFloatingOffset` | `CharaBase` | `float` | none | no |
| `_getFloatingOffset` | `CharaBase` | none | `float` | no |
| `_runCharaSchedulerAgainstTarget` | `CharaBase` | `int`, `LuaControl*`, `int` | none | no |

The return pushers are `0x007489D0` for a float, `0x00748B30` for a control and
`0x00748920` for nil. Only `_waitForTurning` calls the yield request `0x00CD2860`.

## Nameplate natives

`_setNameplateColor` (`0x006E3E00`) reads an int and four floats and passes them
with the receiver identity to `0x0075B570` on `Z`. That routine resolves the
identity, returns on a null result, forms the address `chara +0xBA0` and calls
the routine at vtable offset `+0x08` of that subobject. The subobject is the
NamePlate of the
[Bazaar appearance contract](bazaar-appearance-contract.md#native-nameplate-consumer),
vtable `0x00FCF98C`. Its cell `0x00FCF994` holds `0x006A3AD0`.

`0x006A3AD0` takes a part number `n` and writes the four floats into the record at
`this +0x68 + n * 0x10`. The second Lua argument (index 1) goes to record
`+0x04`, the third (index 2) to `+0x08`, the fourth (index 3) to `+0x0C` and the
fifth (index 4) to `+0x00`. The ordinals count the Lua arguments from 1 and the
indexes count from 0, both without the receiver. No range test precedes the
stores. For `n` equal to 1 the routine returns. For any other `n` it calls
`0x006A3380` with `n` and `0x00938020` on the object that `0x006A3380` returns,
with a copy of the floats, 0 and 1. That the floats are a color with the alpha
stored first is `INFERRED` from the stored order and from the shipped constants,
which lie between 0 and 1 and end in 1 at 19 of 22 sites.

`_setNameplateIcon` (`0x006E3F80`) reads three ints and calls `0x0075B5C0` on
`Z`, which resolves the identity the same way and calls the routine at vtable
offset `+0x0C`. The cell `0x00FCF998` holds `0x006A2C50`. That routine takes the
child control at `this + category * 4 + 0x1C`, sizes it to 36.0, or 64.0 for
category 4, and forwards the three ints to `0x006A2B30`. For an icon id above 0
that routine builds a string of position - 1 separators and the decimal id, hands
it to the category control through `0x0096A010` and stores the id at
`this + category * 4 + 0x30`. For any other id it stores -1 there. The effect on
the player nameplate and the icon table are in
`xivl-decomp:docs/actor/player-nameplate-icons.md`.

The ranges of the part and category numbers, the size of the child control array,
and the bodies of `0x006A3380`, `0x00938020` and `0x0096A010` were not traced.

## Map marker

`_setMapMarker` (`0x0071DFD0`) is a three instruction thunk that jumps through the
dword at receiver vftable offset `+0x94`. The cells hold `0x006EEB00` for the
`CharaBase` vftable `0x00FD5CAC`, the `PlayerBase` vftable `0x00FD5E04` and the
`MyPlayer` vftable `0x00FD785C`, and `0x006F0020` for the `NpcBase` vftable
`0x00FD647C`. A comparison of the first 60 cells of every Lua control vftable with
the `CharaBase` vftable finds only the `PlayerBase`, `MyPlayer` and `NpcBase`
vftables with more than 26 equal cells, so those three are `INFERRED` to be the
classes derived from `CharaBase`.

`0x006EEB00` leaves the marker number at 0 for a `Nil` first cell and otherwise
reads an int. It calls `0x0076D920` on `W` with the receiver identity, the number
and an empty string vector. `0x006F0020` also visits cells 1 and 2, skips a `Nil`
cell, reads any other as a `Utf8String` and appends it to a vector. When the byte
at receiver `+0x5C` is 0 and the vector is not empty, it builds a 0x14 byte
pending object of the number and the vector and stores it at receiver `+0x128`,
freeing a previous one. In every other case it calls `0x0076D920`.

`0x0076D920` resolves the identity without a null test. It stores the low 6 bits
of the number in the dword at `chara +0x270` through `0x00586720`, and copies the
first two strings of the vector to `chara +0x3E4` and `+0x438` through
`0x0058AC90` and `0x00588490`, writing a zero byte at the start of a missing
slot. The chara initialization sets the low 6 bits of `+0x270` to all ones. That
the number is a marker kind and the strings are marker text is `INFERRED` from the
native name. The consumers of those fields and the code that applies a pending
object were not traced.

## Look-at natives

A chara keeps six look-at records of 0x30 bytes at `chara +0x290`. A record sits at
`+0x290 + (slot + 3 * bank) * 0x30` for the slots 0 to 2 and the banks 0 and 1, so
bank 0 starts at `+0x290` and bank 1 at `+0x320`. The chara initialization
constructs the array of 6 elements through `0x009D61D6` and `0x0058F130`. All
three look-at writers use slot 0 and write both banks.

| Record offset | Written by |
| --- | --- |
| `+0x00` word | Flag bits. `_lookAtCharacter` clears bit 0, sets bits 1 and 4 and clears bits 2 and 3. `_lookAtPosition` sets bits 2 and 4 and clears bits 0, 1 and 3. `_cancelLookAt` sets bits 1, 3 and 4 and clears bits 0 and 2. |
| `+0x02` byte | Priority. The two look-at writers store `0xC8` and skip a record whose byte is above it. The cancel stores 0. |
| `+0x03` byte | 0 |
| `+0x04` dword | Target identity. `_lookAtCharacter` stores it, with the own identity at `chara +0x88` replaced by `0xC0000000`. `_cancelLookAt` stores `0xC0000000`. `_lookAtPosition` leaves it. |
| `+0x08` byte | `_lookAtCharacter` stores 0 |
| `+0x18` float | The second Lua argument of `_lookAtCharacter`, the fourth of `_lookAtPosition`, and 1.0 from `0x00F54F70` for the cancel |
| `+0x20`, `+0x24`, `+0x28` floats | The first, second and third Lua argument of `_lookAtPosition` |

`_lookAtCharacter` (`0x006E43A0`) reads a control through `0x0071BC90` and a
float. It converts the control to an identity through `0x00CC73B0`, which passes it
to `0x00CD7A30` and `0x00CC7030`. `0x00CD7A30` returns 0 for a null control and
`0x00CC7030` then loads the dword at `+0x70` of that result, so a null target
control reads a small address. The run-time effect was not run. The callback
then calls `0x0075C580` on `W`. That routine resolves the receiver, calls
`0x00589260` on the chara, and `0x00589260` calls `0x00587F80` with the slot 0, the
priority `0xC8`, the identity, the float and the flag 0. `0x00587F80` calls
`0x00585F60` once for each bank.

`_lookAtPosition` (`0x006E44B0`) reads four floats and calls `0x0075C5F0` on `W`,
which calls `0x00589310` and then `0x00588020` with the slot 0, the priority
`0xC8` and the floats in argument order. `_cancelLookAt` (`0x006E16A0`) calls
`0x0075C560` on `W`, which calls `0x00589240` and then `0x00587EF0` with the slot
0. The tutorial natives `_lookAtPlayerTutorial` and `_cancelLookAtPlayerTutorial`
reach the same workers. That the identity is the character to face, that the
float is a rate or duration and that the three floats are a position are
`INFERRED` from the native names. No consumer of the records was traced.

`_getLookAtCharacter` (`0x006FA690`) does not read these records. It selects an
identity in three steps.

| Step | Source |
| --- | --- |
| 1 | `0x00CC7BE0` tests the work value with the key `0x0BBE`, which is `charaWork.property` in the [work binder contracts](work-binder-native-contract.md), at the element offset 2 for the receiver. A false result skips step 2. |
| 2 | The vtable offset `+0xA0` of the receiver gives an identity. The cells `0x00FD5D4C`, `0x00FD5EA4` and `0x00FD78FC` hold `0x0071E030`, which returns the dword at `0x0130C778`, whose image value is `0xE0000000`. The `NpcBase` cell `0x00FD651C` holds `0x0072D000`, which returns the dword at receiver `+0x154`. The callback ignores a value equal to the dword at `0x0130C778`. |
| 3 | When no identity remains, `0x0075C670` returns the dword at `chara +0x12C`. |

An identity of `0xC0000000` after step 3 pushes nil. Any other identity goes
through `0x00CC7A50` to a control, which `0x009DA6CC` casts to `CharaBase`. A null
result, or a result whose byte at `+0x5C` is 0, pushes nil. Otherwise the callback
pushes the cast pointer through `0x00748B30`. The pushed control is never null.
The writers of `chara +0x12C` and of `NpcBase +0x154` were not traced.

## Turning

`_turnBack` (`0x006E16D0`) calls `0x0075C320` on `W`, which resolves the receiver
and calls `0x00585EC0`. That routine sets bit 1 of the byte at `chara +0x26D` and
sends the record number `0x33` with no payload through `0x004D7980`, so the scene
type is `0x48`.

`_waitForTurning` (`0x006E1700`) calls `0x0075C340` on `W`, which resolves the
receiver and stores the chara pointer, null included, in a slot. It tests the slot
through `0x00758D10`, which jumps to `0x00585250`. That routine returns bit 1 of
the byte at `chara +0x26D`. A clear bit returns from the native with no yield. A
set bit allocates 8 bytes through `0x009D1B35`, constructs a
`WaitForTurningResumeChecker` through `0x006DC040` and requests the yield through
`0x00CD2860` with `ExecuteParameters` `+0x08`. The native pushes no value.

The checker has the vftable `0x00FD50EC` and keeps the chara pointer at `+0x04`.
Slot 0, `0x007187B0`, is the deleting destructor. The poll in slot 1,
`0x006DC0A0`, tests the same bit through `0x00758D10` and stores the dword at
`0x0130CECC` in the result cell while the bit is set and the dword at
`0x01377ECC` otherwise. These are the waiting and done results of the other wait
natives. The push in slot 2, `0x006DC0D0`, is a bare `ret 0xC` that pushes nothing.

Bit 1 of the byte at `chara +0x26D` is set at `0x00585EC0` and `0x00587DF2`. It is
cleared at `0x0058E373`, the case for the event type `0x4A` of the `CharaElement`
dispatcher `0x0058E0C0` in vtable slot 8 (cell `0x00FA7C70`, see
[`manifests/charaelement_slot8_cases.json`](../manifests/charaelement_slot8_cases.json)),
and by the chara initialization at `0x0058B5BC`, which keeps only bit 7. That the
wait ends when the event type `0x4A` reports the turn done is `INFERRED`. The
producer of that event was not traced. Whether `0x00CD2860` polls the checker once
before it suspends was not traced.

## Visibility and floating offset

`_setVisible` (`0x006E41E0`) reads one bool and calls `0x0075C3C0` on `W`, which
resolves the receiver and calls `0x004D7890`. That routine stores the bool byte at
`chara +0x90`, builds a message of type `0x10` for a nonzero byte or `0x11` for zero
with no payload and hands it to virtual slot 3 of the object at `chara +0x84`.
After the call the callback clears the byte at `receiver +0xE0` when it is nonzero.
The receiver there is the `CharaBase` control and not the chara found by
identity. The role of that byte was not traced.

`_setFloatingOffset` (`0x006E4170`) reads one float and calls `0x0075C380` on `W`,
which resolves the receiver and calls `0x00588360`. That routine replaces the
dword at `chara +0xB4` with the float, keeps the other three dwords of the 0x10
bytes at `+0xB0`, and sends them as the payload of the record number `0x26`
through `0x004D7980`, so the scene type is `0x3B`. `_getFloatingOffset`
(`0x006FA590`) calls `0x0075C3A0` on `W`, which resolves the receiver and jumps
to `0x00586740`. That routine loads the float at `chara +0xB4` and the callback
pushes it through `0x007489D0`. That the float is a vertical offset is `INFERRED`
from the native name.

## Scheduler against a target

`_runCharaSchedulerAgainstTarget` (`0x006E49A0`) reads a scheduler int through
`0x005819A0`, reads a target control through `0x0071BC90` and converts it to an
identity through `0x00CC73B0`. A null control reads a small address as in
`_lookAtCharacter`. The callback then tests that the cell vector holds three cells
and that cell 2 has the tag 6. The declared list has three entries, so the
marshaller supplies a placeholder for a missing position. A cell vector of another
size takes the second row of the table even when cell 2 is `Nil`. Whether the
marshaller can yield such a vector was not traced.

| Cell 2 | Call | Word passed on |
| --- | --- | --- |
| Vector size 3 and `Nil` or missing | `0x0075C440` on `W` | 0, through `0x0058CB40` |
| any other size or cell | `0x0075C470` on `W` | the low 16 bits of the int read through `0x005819A0` |

Both routines resolve the receiver through `0x004D9970` without a null test and
reach `0x0058C690` with the scheduler int, the target identity and the word. That
is the routine that `_runCharaScheduler` reaches with the dword at `this +0x88`,
the own identity, in the second position. It zero fills a 0x38 byte record,
stores the arguments and the constants 1 and 1, classifies the int through
`0x00585800` with the default 5, builds an entry through `0x00587370` and appends
it to the container at `this +0xA80` through `0x005901D0`. The native pushes no
value and requests no yield. That the target identity makes the request run
against the target chara is `INFERRED` from the native name. What the queue entry
does when it runs was not traced.

## Script call sites

| Native | Index sites | Scripts | Direct calls |
| --- | ---: | ---: | ---: |
| `_setNameplateColor` | 22 | 1 | 22 |
| `_setNameplateIcon` | 23 | 1 | 23 |
| `_setMapMarker` | 16 | 1 | 16 |
| `_lookAtCharacter` | 6 | 1 | 6 |
| `_lookAtPosition` | 5 | 1 | 5 |
| `_cancelLookAt` | 2 | 2 | 2 |
| `_getLookAtCharacter` | 2 | 2 | 2 |
| `_waitForTurning` | 6 | 3 | 6 |
| `_turnBack` | 2 | 2 | 2 |
| `_setVisible` | 1 | 1 | 1 |
| `_setFloatingOffset` | 1 | 1 | 1 |
| `_getFloatingOffset` | 1 | 1 | 1 |
| `_runCharaSchedulerAgainstTarget` | 9 | 2 | 9 |

The first three columns are `MEASURED` against the call-site index and total 96
sites. The direct call column is the count of method calls that the bytecode scan
resolves (`INFERRED`), and it equals the index count for every native.

The scan also shows these call shapes (`INFERRED`). The nameplate and marker
natives are called only from `judge/depictionjudge`. All 22 `_setNameplateColor`
calls pass five arguments and the part number 1. Of the 23 `_setNameplateIcon`
calls, 22 pass three arguments with the category 1, 2, 3 or 4 at 7, 4, 4 and 7
sites and the position 1, and one takes its arguments from an open result. Of the
16 `_setMapMarker` calls, 14 pass one argument, which is nil at 5 sites, and 2 take
an open result. No site passes a string. `chara/npc/npcbaseclass_event` holds all 6 `_lookAtCharacter` calls, all 5
`_lookAtPosition` calls, 1 `_cancelLookAt` call, 1 `_turnBack` call and 4
`_waitForTurning` calls. `chara/npc/populace/occupancyguide/occupancyguidestandard`
holds the other `_cancelLookAt` and `_turnBack` calls. The other 2
`_waitForTurning` calls are in `judge/harvest/harvestjudge` and
`quest/questbaseclass_common`. All 5 `_lookAtPosition` calls pass the
constant 1 as the fourth argument. Seven of the 9 `_runCharaSchedulerAgainstTarget`
calls come from `chara/npc/debug/populacemenuman`, pass a constant scheduler int
and nil as the third argument. The other 2 come from
`commanddebugger/commanddebuggerdev`. No site passes a non-nil third argument.
`_setVisible` has one call with the constant false. Both floating offset natives
and one `_getLookAtCharacter` call sit in debug console scripts.

## Ledger rows

These rows of the unimplemented ledger now have a registration, argument list,
return list, receiver check and callback contract: `_setNameplateColor`,
`_setNameplateIcon`, `_setMapMarker`, `_lookAtCharacter`, `_lookAtPosition`,
`_cancelLookAt`, `_getLookAtCharacter`, `_turnBack`, `_waitForTurning`,
`_setVisible`, `_setFloatingOffset`, `_getFloatingOffset` and
`_runCharaSchedulerAgainstTarget`. A client that implements them needs the
NamePlate subobject at `chara +0xBA0`, the look-at record banks at `chara +0x290`,
the turning bit at `chara +0x26D` with its clear event, the marker fields at
`chara +0x270`, `+0x3E4` and `+0x438`, and the float at `chara +0xB4`. The values
of those fields come from scripts and the server.

## Open

- The NamePlate record and child control array sizes, the part and category
  numbers that exist, and the bodies of `0x006A3380`, `0x00938020` and
  `0x0096A010`.
- The consumers of the look-at records, the roles of their flag bits and of the
  float at record `+0x18`.
- The consumers of the scene types `0x3B`, `0x48`, `0x10` and `0x11`, the class of
  the object at `chara +0x84`, and the producer of the event type `0x4A`.
- The consumers of `chara +0x270`, `+0x3E4` and `+0x438`, the code that applies a
  pending marker object, and the role of the byte at `NpcBase +0x5C`.
- The writers of `chara +0x12C` and `NpcBase +0x154`, and the meaning of the work
  value at the key `0x0BBE` with the element offset 2.
- The run-time effect of an absent receiver and of a null target control.
- The role of the byte at `receiver +0xE0`.
- Whether `0x00CD2860` polls the checker once before it suspends.
- Whether the marshaller can yield a cell vector of a size other than the declared
  count for `_runCharaSchedulerAgainstTarget`.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes with the route of the
[binding map contracts](binding-map-native-contract.md#reproduction). The script
call shapes come from the `.le.lpb` files of an installed client, decoded by
[`tools/decode_lpb.py`](../tools/decode_lpb.py) and read with a Lua 5.1 bytecode
parser over the `SELF`, `CALL` and `TAILCALL` sites. They are `INFERRED` because
no tracked artifact carries them. The function VAs for `$Addresses` are:

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Registrars | `0x00740FB0,0x0072E890,0x0072EC80,0x0074C1A0,0x0072EDD0,0x0072F070,0x0072F5B0,0x00741100,0x0072F700,0x0074C590,0x0072FAF0,0x00730030,0x00730180` |
| Switchboard and holders | `0x007574A0,0x00726460,0x00726510,0x0071E1E0` |
| Callbacks | `0x006E3E00,0x006E3F80,0x006E4170,0x006FA590,0x006E41E0,0x0071DFD0,0x006E43A0,0x006E44B0,0x006E16A0,0x006FA690,0x006E49A0,0x006E16D0,0x006E1700` |
| List builders and readers | `0x0072B440,0x0072B390,0x00728B70,0x0072C260,0x0072B660,0x00740020,0x0072B920,0x00740130,0x0072B730,0x0072BB20,0x005819A0,0x0071BAC0,0x0071BA00,0x0071CE70,0x0071BC90` |
| Lookup and glue | `0x00CC7510,0x004D9970,0x004DE190,0x0075B570,0x0075B5C0,0x0075C380,0x0075C3A0,0x0075C3C0,0x0075C580,0x0075C5F0,0x0075C560,0x0075C320,0x0075C340,0x0075C440,0x0075C470,0x0075C670` |
| Nameplate | `0x006A3AD0,0x006A2C50,0x006A2B30,0x006A3380,0x00938020` |
| Map marker | `0x006EEB00,0x006F0020,0x0076D920,0x00586720,0x0058AC90,0x00588490,0x00725250,0x007218E0` |
| Look-at | `0x00589260,0x00587F80,0x00585F60,0x00589310,0x00588020,0x00589240,0x00587EF0,0x00CC73B0,0x00CD7A30,0x00CC7030,0x00CC7BE0,0x00CC7A50,0x0071E030,0x0072D000` |
| Turn, wait and visibility | `0x00585EC0,0x00585250,0x00758D10,0x006DC040,0x006DC0A0,0x0058E0C0,0x004D7890,0x004D7980,0x004EC080,0x00588360,0x00586740` |
| Scheduler | `0x0058CB40,0x0058CB60,0x0058C690,0x00585800,0x00587370,0x005901D0` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
