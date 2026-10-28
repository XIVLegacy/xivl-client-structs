# Zone-in, fade, weather, music, notice and calendar native contracts

[`manifests/zone_in_native_call_contract.json`](../manifests/zone_in_native_call_contract.json)
records the static Lua call contracts of fourteen natives. Ten belong to the
player. Five of them are fade and load calls (`_waitForMapLoaded`,
`_fadeInAfterWarp`, `_resetFade`, `_isFading`, `_cancelFading`). Two set the
ambient state (`_setWeather`, `_setMusic`). Three query or end event state
(`_isEventPlaying`, `_cancelNotice`, `_readyInnBed`). Three belong to the world
master and compute calendar values (`_getHydaelynTime`, `_getHydaelynMoon`,
`_getHydaelynHour`). One reads the area type of a private area
(`_getAreaType`). Each row gives the registration site, the receiver type check,
the declared argument and return lists, the reads, the effects on client state,
the failure behavior and whether the call yields. The contracts describe client
marshalling and state, not presentation, calendar naming or server behavior.

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

The native set and the script bindings come from
[`manifests/bulk_napi_classification.json`](../manifests/bulk_napi_classification.json)
and the script metadata. The per-row `corpusCallSites` records carry the
call-site counts from `xivl-client-scripts:lua/napi_index.json`. They show that
a script contains a call, not that a script reaches it at run time.

## Registration and dispatch

Three classes register the fourteen natives, each from the switchboard in slot 2
of its vftable. The switchboard shape, the skip byte and the single `rel32`
caller of each registrar are the ones recorded for `SpreadSheet` in the
[SpreadSheet contracts](spreadsheet-native-contract.md#registration-and-dispatch).
The order is the position among the registrar calls of the switchboard.

| Class | Switchboard | Vftable | Natives (order) |
| --- | --- | --- | --- |
| `PlayerBase` | `0x00753F90` | `0x00FD5E04` | `_cancelNotice` (11), `_isEventPlaying` (15), `_isFading` (21), `_cancelFading` (22), `_fadeInAfterWarp` (23), `_resetFade` (24), `_waitForMapLoaded` (38), `_setMusic` (39), `_setWeather` (40), `_readyInnBed` (94) |
| `WorldMaster` | `0x00754C70` | `0x00FD5864` | `_getHydaelynHour` (6), `_getHydaelynTime` (8), `_getHydaelynMoon` (9) |
| `PrivateAreaBase` | `0x00754E70` | `0x00FD653C` | `_getAreaType` (1) |

| Native | Registrar | Caller | Callback | Wrapper |
| --- | --- | --- | --- | --- |
| `_cancelNotice` | `0x00731290` | `0x0075407E` | `0x006DE6F0` | `0x007267D0` |
| `_isEventPlaying` | `0x007317D0` | `0x007540D2` | `0x006DE730` | `0x007267D0` |
| `_isFading` | `0x00731FB0` | `0x00754150` | `0x006DE790` | `0x007267D0` |
| `_cancelFading` | `0x00732100` | `0x00754165` | `0x006DE7A0` | `0x007267D0` |
| `_fadeInAfterWarp` | `0x00732250` | `0x0075417A` | `0x006DE7B0` | `0x00726720` |
| `_resetFade` | `0x007323A0` | `0x0075418F` | `0x006DE7C0` | `0x00726720` |
| `_waitForMapLoaded` | `0x007334B0` | `0x007542B5` | `0x006DE890` | `0x007267D0` |
| `_setMusic` | `0x00733600` | `0x007542CA` | `0x0071E400` | `0x007267D0` |
| `_setWeather` | `0x00733750` | `0x007542DF` | `0x0071E410` | `0x007267D0` |
| `_readyInnBed` | `0x00735820` | `0x0075474D` | `0x0071E6F0` | `0x00726720` |
| `_getHydaelynHour` | `0x00752B40` | `0x00754CF5` | `0x00707A00` | `0x00726CA0` |
| `_getHydaelynTime` | `0x00752DE0` | `0x00754D1F` | `0x00707AF0` | `0x00726CA0` |
| `_getHydaelynMoon` | `0x00752F30` | `0x00754D34` | `0x00707C00` | `0x00726CA0` |
| `_getAreaType` | `0x00753A40` | `0x00754E84` | `0x00706F20` | `0x0072DB00` |

Every registrar builds the return list first and the argument list second and
installs the functor through `0x00CCCAD0` under the name literal with the
adjustment 0. The wrappers `0x00726720` and `0x007267D0` are recorded in the
[fade contracts](fade-actor-group-native-contract.md#registration-and-dispatch).
Two more wrappers appear. Each constructs the `0x58` byte functor in place and
the holder invoke routine casts the receiver with `0x009DA6CC` from
`LuaControl` to the owner class. A null cast returns false without calling the
callback.

| Wrapper | Owner class | Qualifier | Holder vftable | Invoke | Target type descriptor |
| --- | --- | --- | --- | --- | --- |
| `0x00726CA0` | `WorldMaster` | const | `0x00FD5B70` | `0x0071AE70` | `0x012C1328` |
| `0x0072DB00` | `PrivateAreaBase` | const | `0x00FD65CC` | `0x0072D980` | `0x012C2D90` |

The readers are the ones of the earlier contracts: `0x005819A0` for an int,
`0x0071BA00` for a bool, `0x0071CE70` for a `Utf8String` and `0x0071BC90` for a
chara control. The return pushers are `0x00584F70` for an int, `0x00748870` for
a bool, `0x007487C0` for a `Utf8String` and `0x00748920` for nil. The list
builders are `0x0072B440` for none, `0x00728C20` for an int, `0x00728B70` for a
bool, `0x0072C260` for a `LuaControl*`, `0x0072B5B0` for a `Utf8String`,
`0x00583CE0` for two ints, `0x0072BD30` for a `Utf8String` and an int and
`0x0073DC30` for four ints. Each builder selects its entries through the type
registry of `0x00CCA210`.

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_waitForMapLoaded` | `PlayerBase` | `int` | none | yes, while a flag is set |
| `_fadeInAfterWarp` | `PlayerBase` | none | none | no |
| `_resetFade` | `PlayerBase` | none | none | no |
| `_isFading` | `PlayerBase` | none | `bool` | no |
| `_cancelFading` | `PlayerBase` | none | none | no |
| `_setWeather` | `PlayerBase` | two `int` | none | no |
| `_setMusic` | `PlayerBase` | two `int` | none | no |
| `_isEventPlaying` | `PlayerBase` | `Utf8String` | `bool` | no |
| `_cancelNotice` | `PlayerBase` | `Utf8String`, `int` | none | no |
| `_readyInnBed` | `PlayerBase` | `LuaControl*` | `bool` | no |
| `_getHydaelynTime` | `WorldMaster` | `int` | four `int` | no |
| `_getHydaelynMoon` | `WorldMaster` | `int` | `int` | no |
| `_getHydaelynHour` | `WorldMaster` | `int` | `int` | no |
| `_getAreaType` | `PrivateAreaBase` | none | `Utf8String`, `int` | no |

Only `_waitForMapLoaded` calls the yield request `0x00CD2860`. The manifest
rows carry each name literal, name reference, install call, callback load and
list builder.

## Player thunks and the MyPlayer overrides

The ten `PlayerBase` callbacks are thunks of three instructions. Each loads the
vftable of the receiver and jumps through one slot with the arguments untouched.
The `PlayerBase` cell of every slot holds a bare `ret 4`, either `0x00776340` or
a routine of its own. `MyPlayer` (vftable `0x00FD785C`) is the only class whose RTTI base
list names `PlayerBase`. It registers nothing, since its slot 2 holds
`0x00776340`. A `PlayerBase` receiver that is not a `MyPlayer` therefore does
nothing, and the bool returning natives push no value for it. Whether the Lua
class system creates such receivers for other players was not traced.

| Native | Slot | `PlayerBase` cell | `MyPlayer` cell | `MyPlayer` routine |
| --- | --- | --- | --- | --- |
| `_cancelNotice` | `0xD0` | `0x00FD5ED4` | `0x00FD792C` | `0x006E8F50` |
| `_isEventPlaying` | `0xE0` | `0x00FD5EE4` | `0x00FD793C` | `0x00704DB0` |
| `_isFading` | `0xF8` | `0x00FD5EFC` | `0x00FD7954` | `0x007050F0` |
| `_cancelFading` | `0xFC` | `0x00FD5F00` | `0x00FD7958` | `0x006E3230` |
| `_fadeInAfterWarp` | `0x100` | `0x00FD5F04` | `0x00FD795C` | `0x006E3260` |
| `_resetFade` | `0x104` | `0x00FD5F08` | `0x00FD7960` | `0x006E32A0` |
| `_waitForMapLoaded` | `0x13C` | `0x00FD5F40` | `0x00FD7998` | `0x006E5EB0` |
| `_setMusic` | `0x140` | `0x00FD5F44` | `0x00FD799C` | `0x006E5FD0` |
| `_setWeather` | `0x144` | `0x00FD5F48` | `0x00FD79A0` | `0x006E6070` |
| `_readyInnBed` | `0x1FC` | `0x00FD6000` | `0x00FD7A58` | `0x00706700` |

The routines reach the client through the world chain of the
[scheduler contracts](scheduler-item-native-contract.md#world-object-and-identity-lookup).
With `R` the address that `0x00CC7510` returns for `ExecuteParameters` `+0x04`,
`X` is the dword at `R`, `Y` the dword at `X +0x04` and `W` the dword at `Y`.
`W`, the dword at `Y +0x08` and the dword at `Y +0x04` each address an object
whose first dword is the container `V` of the fade contracts.

| Field | Used by |
| --- | --- |
| `W` | `_setWeather`, `_setMusic` and `_waitForMapLoaded`. |
| `Y +0x08` | The fade natives, as in the fade contracts. |
| `V +0x4CC` | The fade object `F`. |
| `V +0x4E0` | The object whose byte `+0xB9` gates `_waitForMapLoaded` and which receives the weather requests. |
| `V +0x928` | The embedded object that receives the music control `0x004BBB30`. |
| `V +0x17758` | The `RaptureUserControl` of the player control counters. |

## Load and fade

`_waitForMapLoaded` (`0x006E5EB0`) skips a `Nil` cell and otherwise reads an int
and discards it, so the argument has no effect beyond the type check. It calls
`0x0075C820` on `W`. That routine loads `V`, takes the object at `V +0x4E0`
through `0x004D7390` and returns the byte at `+0xB9`. A zero byte returns at
once. A nonzero byte allocates four bytes, builds the `s_MapLoadResumeChecker`
(vftable `0x00FD5638`, poll `0x0071C7F0`) and requests a yield with it. The poll
repeats the byte test and stores the waiting result `0x0130CECC` while the byte
is set and the done result `0x01377ECC` once it is clear. The checker pushes
nothing. That the byte is a map load pending flag is `INFERRED` from the name.
The ordinary MapLayoutElement construction and selected byte writers are
documented in `xivl-decomp:docs/event/airship-scene-sequence.md`, section
`Map loading state and writers`. Transfer-generation identity, terminal
resource failures and connection-loss behavior remain unresolved there.

`_isFading` (`0x007050F0`) pushes the byte at `F +0x244`, the flag that `_fadeIn`
and `_fadeOut` set and `_waitForFading` polls. `_cancelFading` (`0x006E3230`)
reads the same byte and, when it is set, calls `0x0075B490` with the frame count
0. That routine takes `F` from `V +0x4CC` and calls `0x005606B0` with four
`0.0` floats and the frame count, the fade in of `_fadeIn`. A frame count of 0
leaves the flag clear.

`_fadeInAfterWarp` (`0x006E3260`) and `_resetFade` (`0x006E32A0`) work on the
four counters of the `RaptureUserControl` that sits at `V +0x17758`
(vftable `0x00F90F64`). The counters are the dwords at object `+0x18`, `+0x2C`,
`+0x40` and `+0x54`, as in the
[target cursor control](chara-desktop-native-contract.md#target-cursor-control)
record. The channels are the player, the target cursor, the lock-on and the
camera. Slots 1, 4, 7 and 10 add 1 and slots 2, 5, 8 and 11 add -1.

| Native | Calls | Effect |
| --- | --- | --- |
| `_fadeInAfterWarp` | `0x0075B500`, `0x0075B300` | `0x004D6FE0` with two zero arguments, then slots 1, 4, 7 and 10 of the `RaptureUserControl`, and the byte at `MyPlayer +0x166` set to 1. |
| `_resetFade` | `0x0075B490`, `0x0075B510`, `0x0075B330` | The zero frame fade in, the byte at `+0x165` cleared, and, only when the byte at `+0x166` is set, `0x004D70B0` with 1, slots 2, 5, 8 and 11, and the byte at `+0x166` cleared. |

`0x004D6FE0` returns when the dword at `V +0x175A4` is null. Otherwise it calls
`0x0056A5F0` on that object with its two arguments, a virtual call through slot `0x38` of the object embedded at `V +0xB4`,
`0x0091C230` and `0x004D6820` with `0.0`, 0, 0 and 0. Its effects were not
traced. `0x004D70B0` is the routine of
`_fadeInNowLoadingForNoticeEventJustInArea` in the
[fade contracts](fade-actor-group-native-contract.md#fade-natives). That the byte
at `+0x166` records that `_fadeInAfterWarp` raised the counters is `INFERRED`,
because `_resetFade` tests it before it lowers them. Its other writers were not
traced.

## Weather and music

`_setWeather` (`0x006E6070`) and `_setMusic` (`0x006E5FD0`) read two ints. They
keep the low 16 bits of the first with `MOVZX` and the low 8 bits of the second,
resolve the world chain and call a routine on `W`. That routine sign-extends the
word and the byte with `MOVSX`. A script value of 32768 to 65535 therefore
reaches the engine as a negative id, and a second value above 127 as a negative
byte.

`_setWeather` calls `0x0075C910`, which takes the object at `V +0x4E0` and jumps
to `0x0059E700`. That routine builds a 16 byte record from the extended second
value, its sign and `0.0`, leaves dword 3 unwritten, and calls `0x0059E4D0` with
the extended id. An id of
0 skips the sends. A nonzero id copies the record to object `+0x128` through
`0x0059E1F0` and sends it as record number `0x72` with 16 bytes. It stores the id
at `+0x9C` and sends it as record number `0x0C` with 4 bytes. `0x004D7980` adds
`0x15` to the record number, so the scene packet types are `0x87` and `0x21`.
The routine then stores 0 at `+0xA0`, `+0xA4` and `+0xB0` and the byte 0 at
`+0xBB`, whatever the id. The consumers of the scene packets and the ranges of
the two values were not traced.

`_setMusic` calls `0x0075C930`, which takes the object at `V +0x928` through
`0x004D7500` and calls the music control `0x004BBB30` with the song and the
mode. The resource id derivation, the mode branches, the release durations and
the failed load state of that control are recorded in
`xivl-decomp:docs/resource/music-song-table.md`, sections Song values from Lua
and Request path. A reimplementation of the native sign-extends the Lua song
from 16 bits and the Lua mode from 8 bits before it reaches that control.

## Event state

`_isEventPlaying` (`0x00704DB0`) reads the byte at `MyPlayer +0x5C` first. A zero
byte pushes false and the name is not read. A nonzero byte reads a `Utf8String`
and calls `0x00894140` on the object at `MyPlayer +0xF8`. That routine takes
`P` from `this +0x08` and `Q` from `P +0x04`. When the virtual slot `0x18` call
on `Q` with the constant `0x0134C3FF` returns zero and the name at `Q +0x04`
compares equal through `0x00445D20`, it returns whether the byte at `P +0x21` is
nonzero. Otherwise it walks the list whose sentinel pointer is at `this +0x14`
and returns 1 for the first node whose slot `0x18` call with the constant does
not return 1 and whose name compares equal. The end of the list returns 0.

`_cancelNotice` (`0x006E8F50`) reads a `Utf8String` and then tests cell 1. A
`Nil` cell calls `0x00895060` on the same object with the receiver, the string
and the constant `0x012C3F7E`. That routine releases the entry at `this +0x0C`
when its name compares equal and its slot `0x18` call with the constant returns
1, clears the field, and then calls `0x00894800` and `0x008949A0`. Any other
cell is read as an int and its low byte is passed by address to `0x008950D0`.
That routine adds a condition: the byte that `0x00892530` returns must not
exceed the byte, as an unsigned compare, before it releases the entry at
`this +0x0C` or calls `0x00894800` for the entry at `this +0x08`. That the object
at `MyPlayer +0xF8` is the event or notice queue of the player is `INFERRED`
from the pairing of the two natives. The class, the constants and the role of
`0x00892530` were not traced.

`_readyInnBed` (`0x00706700`) tests the byte at `MyPlayer +0x161`. A zero byte
pushes nil through `0x00748920` and reads no argument. A nonzero byte reads a
chara through the cast reader `0x0071BC90`, converts the control to an identity
through `0x00CC73B0` and stores it at `+0x130`. A byte below `0x15` as a signed
value then pushes nil. Otherwise the routine stores the dword at `0x0130C778`,
`0xE0000000`, at `+0x128` and pushes true. The return list declares a bool and
the two nil paths push a nil cell instead. `_fadeInNowLoadingForNoticeEventJustInArea`
tests the same `+0x128` dword. That the byte is a stage of the inn bed sequence
is `INFERRED`. Its writers and the readers of `+0x128` and `+0x130` were not
traced.

## Calendar

The three `WorldMaster` callbacks read one int as an unsigned second count `t`
through `0x005819A0` and read no world state and no clock. The caller supplies
`t`. The arithmetic uses the constant `0xF9A9342D` with the high dword of a
32 bit `MUL` and the 64 bit helpers `0x009D5840` (multiply), `0x009D5880`
(unsigned divide) and `0x009D9AB0` (unsigned remainder).

| Native | Pushes |
| --- | --- |
| `_getHydaelynTime` | Four ints in order: month `((t / 134400) % 12) + 1`, day `((t / 4200) % 32) + 1`, hour `((t * 24) / 4200) % 24` and minute `((t * 1440) / 4200) % 60`. |
| `_getHydaelynHour` | One int, `((t * 24) / 4200) % 24`. |
| `_getHydaelynMoon` | One int, `(((t / 4200) & 0x1F) + 4) / 4`, a value from 1 to 8 that changes every 4 days. |

The month and day divisions are the compiler form of an unsigned division. The
shift of the high dword by 17 and by 12 gives `2^49 / 0xF9A9342D` and
`2^44 / 0xF9A9342D`, and `2^44 / 0xF9A9342D` is 4199.9999998606. A check at the
multiples of 4200 and 134400 and their neighbors across the 32 bit range found
the shifted products equal to `t / 4200` and `t / 134400`. The hour and minute
use the exact products, so the hour is `t / 175` modulo 24. The divisors are
`STATIC`. That `t` is a second count and the results are the in game calendar is
`INFERRED` from the native names. Which clock value a script passes was not
traced.

## Area type

`_getAreaType` (`0x00706F20`) takes no argument. It pushes the `Utf8String`
object at `PrivateAreaBase +0xBC` through `0x007487C0` and then the dword at
`+0x110` increased by 1 through `0x00584F70`. The registrar builds the two entry
return list `0x0072BD30` (registry entries 3 and 0) and the empty argument list.
The `PrivateAreaBase` switchboard `0x00754E70` has the skip byte shape of the
SpreadSheet contracts and holds this single registrar call. That the string is an
area type name and the int an ordinal is `INFERRED`. `_isInn` of the
[chara and desktop contracts](chara-desktop-native-contract.md#area-and-display-name-natives)
reads the `AreaBase` byte at `+0xBA`. The writers of both fields were not traced.

## Ledger rows

These rows of the unimplemented ledger have a registration, argument list,
return list, receiver check and callback contract: `_waitForMapLoaded`,
`_fadeInAfterWarp`, `_resetFade`, `_isFading`, `_cancelFading`, `_setWeather`,
`_setMusic`, `_isEventPlaying`, `_cancelNotice`, `_readyInnBed`,
`_getHydaelynTime`, `_getHydaelynMoon`, `_getHydaelynHour` and `_getAreaType`. A
client that implements them still needs the fade consumer behind scene packet
type `0x15`, the consumers of the weather scene packet types `0x21` and `0x87`,
the object behind `V +0x4E0`, the notice queue behind `MyPlayer +0xF8` and the
writers of the `MyPlayer` fields at `+0x161`, `+0x165` and `+0x166`.

## Open

- The class of the object at `V +0x4E0`, the writers of its byte `+0xB9` and the
  consumers of the weather scene packets.
- The effects of `0x004D6FE0` and the writers and readers of the `MyPlayer`
  bytes at `+0x161`, `+0x165` and `+0x166`.
- The class of the object at `MyPlayer +0xF8`, the constants `0x0134C3FF` and
  `0x012C3F7E` and the role of `0x00892530`.
- The clock value that scripts pass to the calendar natives.
- The writers of the `PrivateAreaBase` fields at `+0xBC` and `+0x110`.
- Whether the yield request `0x00CD2860` polls the checker once before it
  suspends.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes. The listings behind this
record came from a Capstone x86-32 decode of the file through its section table
and the `rel32` caller scan of `.text` described in the
[binary and method](#binary-and-method) section. With explicit project and JDK
bindings and a new absolute output path, the repository route for function
listings is:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Switchboards and registrars | `0x00754E70,0x00754C70,0x00731290,0x007317D0,0x00731FB0,0x00732100,0x00732250,0x007323A0,0x007334B0,0x00733600,0x00733750,0x00735820,0x00752B40,0x00752DE0,0x00752F30,0x00753A40` |
| Wrappers and list builders | `0x00726CA0,0x0072DB00,0x00724E80,0x0072DA30,0x0071AE00,0x0072D910,0x0071AE70,0x0072D980,0x0072BD30,0x0073DC30,0x00583CE0,0x0072B5B0,0x00728C20,0x00728B70,0x0072C260` |
| Thunks and MyPlayer routines | `0x006DE6F0,0x006DE730,0x006DE790,0x006DE7A0,0x006DE7B0,0x006DE7C0,0x006DE890,0x0071E400,0x0071E410,0x0071E6F0,0x006E8F50,0x00704DB0,0x007050F0,0x006E3230,0x006E3260,0x006E32A0,0x006E5EB0,0x006E5FD0,0x006E6070,0x00706700` |
| Load and fade | `0x0075C820,0x004D7390,0x00716530,0x00716590,0x0071C7F0,0x0075B500,0x0075B300,0x0075B330,0x0075B490,0x0075B4F0,0x0075B510,0x004D6FE0,0x004D70B0,0x004D7340,0x004D7580,0x0055DB00,0x005606B0` |
| Control counters | `0x0054B440,0x0054B600,0x0054B620,0x0054B630,0x0054B650,0x0054B660,0x0054B680,0x0054B8C0` |
| Weather and music | `0x0075C910,0x0075C930,0x0059E700,0x0059E4D0,0x0059E1F0,0x004D7500,0x004D7980,0x004BBB30` |
| Event state | `0x00894140,0x00895060,0x008950D0,0x00894800,0x008949A0,0x00892530,0x00445D20,0x0071BC90,0x00CC73B0` |
| Calendar and area | `0x00707A00,0x00707AF0,0x00707C00,0x009D5840,0x009D5880,0x009D9AB0,0x00706F20` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body is a dependency of this record.
