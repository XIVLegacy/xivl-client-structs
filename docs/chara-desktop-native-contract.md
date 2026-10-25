# Item package, main stat mode, target cursor control, inn, display name, NPC filter and command dispatch native contracts

[`manifests/chara_desktop_native_call_contract.json`](../manifests/chara_desktop_native_call_contract.json)
records the static Lua call contracts of eleven native registrations that the
`DesktopWidget` family of scripts and the chara scripts it calls reach, plus the
dispatch of four `PlayerBase` command natives. The eleven natives are
`_hasItemPackage`, `_isActorMainStatMode`, `_lockTargetCursorControl`,
`_unlockTargetCursorControl`, `_isTargetCursorControlEnabled`, `_isInn`,
`_getLocalizedDisplayName`, `_getLocalizedDisplayNameForChat`, `_isTalkable`,
`_isEmotable` and `_isPushable`. The four dispatch rows are `_executeCommand`,
`_canExecuteCommand`, `_cancelCommand` and `_isCommandPlaying`. Each full row
gives the registration site, the receiver type check, the declared argument and
return lists, the reads, the effects on client state, the failure behavior and
whether the call yields. The contracts describe client marshalling and state, not
package numbers, main stat values, display names, inn areas, NPC filter contents,
command names or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data
at the cited addresses. `MEASURED` is counted or parsed by the method named in
the fact, from the executable or from the call-site index of the installed
client scripts. `INFERRED` is a name or role taken from the surrounding
instructions or script names that the bytes do not state. `unknown` was not
traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
The listings, the caller scan and the reproduction route are the ones of the
[binding map contracts](binding-map-native-contract.md#binary-and-method). A
second pass re-read the bytes and compared every cited call target, immediate,
vftable cell, jump table entry and name literal with the claims below.
`V`, `W`, `X`, `Y` and `R` name the world object chain of the
[fade contracts](fade-actor-group-native-contract.md#fade-natives) and the
[Global contracts](global-native-contract.md#binary-and-method). The registrar
shape, the type registry, the cell tags and the invalid-parameter route are the
ones of the [nameplate, actor and group contracts](nameplate-group-native-contract.md)
and the [work binder contracts](work-binder-native-contract.md#binary-and-method).

The call-site and chunk counts agree with
`xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. They show that a
script contains a call, not that a script reaches it at run time. The argument
counts, the constants and the names of the calling functions come from a local
Lua 5.1 bytecode scan of the installed client scripts, decoded with
[`tools/decode_lpb.py`](../tools/decode_lpb.py). The script sources are not
redistributed and no tracked artifact carries those values, so they are
`INFERRED`.

## Registration

Every native is declared by a `_u` script descriptor named `<name>_inl` that
returns the selector `self` and the target `<name>_cpp`. The descriptor tables
are `CharaBaseClass` in `chara/charabaseclass_u`, `DesktopWidget` in
`widget/desktopwidget_u`, `AreaBaseClass` in `area/areabaseclass_u`,
`NpcBaseClass` in `chara/npc/npcbaseclass_u` and `PlayerBaseClass` in
`chara/player/playerbaseclass_u` (`MEASURED`). The order of a native is its
position among the rel32 calls of its switchboard.

| Native | Switchboard | Order | Registrar | Callback | Holder |
| --- | --- | ---: | --- | --- | --- |
| `_hasItemPackage` | `CharaBase` | 70 | `0x00756240` | `0x00708B60` | `0x00726510`, `CharaBase` non-const |
| `_isActorMainStatMode` | `CharaBase` | 36 | `0x0074C2F0` | `0x006FA5D0` | `0x00726460`, `CharaBase` const |
| `_getLocalizedDisplayName` | `CharaBase` | 24 | `0x0074BC60` | `0x006FA3D0` | `0x00726460` |
| `_getLocalizedDisplayNameForChat` | `CharaBase` | 25 | `0x0074BDB0` | `0x006FA3F0` | `0x00726460` |
| `_lockTargetCursorControl` | `DesktopWidget` | 17 | `0x00739C60` | `0x006E1B00` | `0x00726BF0`, `DesktopWidget` const |
| `_unlockTargetCursorControl` | `DesktopWidget` | 18 | `0x00739DB0` | `0x006E1B20` | `0x00726BF0` |
| `_isTargetCursorControlEnabled` | `DesktopWidget` | 19 | `0x007518E0` | `0x006FDDE0` | `0x00726BF0` |
| `_isInn` | `AreaBase` | 6 | `0x0074A0D0` | `0x006F97A0` | `0x0072CD40`, `AreaBase` const |
| `_isTalkable` | `NpcBase` | 11 | `0x007503E0` | `0x00706AA0` | `0x0072D400`, `NpcBase` const |
| `_isEmotable` | `NpcBase` | 12 | `0x00750530` | `0x00706AE0` | `0x0072D400` |
| `_isPushable` | `NpcBase` | 13 | `0x00750680` | `0x00706B20` | `0x0072D400` |
| `_executeCommand` | `PlayerBase` | 1 | `0x0073F080` | `0x006DE650` | `0x00726720`, `PlayerBase` non-const |
| `_canExecuteCommand` | `PlayerBase` | 6 | `0x00730C00` | `0x006DE6A0` | `0x007267D0`, `PlayerBase` const |
| `_cancelCommand` | `PlayerBase` | 9 | `0x00730FF0` | `0x006DE6D0` | `0x007267D0` |
| `_isCommandPlaying` | `PlayerBase` | 16 | `0x00731920` | `0x006DE740` | `0x007267D0` |

The switchboard functions are `0x007574A0` (`CharaBase`), `0x00757EA0`
(`DesktopWidget`), `0x00753CF0` (`AreaBase`), `0x00754850` (`NpcBase`) and
`0x00753F90` (`PlayerBase`), each stored at slot 2 of its class vftable. The
registrar callers and the name literals are in the manifest rows. The holder
invoke routines cast the receiver from `LuaControl` (`0x01270B4C`) to the class
type descriptor and return without calling the callback when the cast gives a
null pointer (`STATIC`: `0x0071B4D7` and `0x0072D1B7` push the `DesktopWidget`
descriptor `0x012C2108` and the `NpcBase` descriptor `0x012709E4`).

## Item package lookup

`_hasItemPackage` (`0x00708B60`) is a thin adapter into the body `0x00702880`,
the sibling of `_getItemPackageFreeSpace` (`0x00708AC0`, body `0x007027E0`) that
the [nameplate contracts](nameplate-group-native-contract.md) record. The adapter
builds a helper object through `0x006DD450`, calls the body and destroys the
helper through `0x006DD4D0`. The body overwrites its `ecx` before reading it, so
the helper takes no part in the result.

The declared lists are one `int` argument and one `bool` return. The body tests
the cell vector size and calls the invalid-parameter route `0x009D22B4` when the
vector is empty. It reads cell 0 through the int reader `0x005819A0`, subtracts 1
through `0x0078BC90` and looks the key up in the package tree of the receiver.

| Step | Instructions | Effect |
| --- | --- | --- |
| Key | `0x007028B6..0x007028CB` | The key is the package number minus 1 with no range test, so the number 0 searches the key `0xFFFFFFFF`. |
| Manager | `0x006F51A0` | Returns the dword at receiver `+0xD8`. A null dword allocates `0x78` bytes through `0x009D1B35`, constructs the manager with `0x006F5100` and stores the pointer at `+0xD8`. The `CharaBase` control constructor stores 0 there at `0x006ECDDE`. |
| Search | `0x006E5BA0` | Searches the tree at manager `+0x08` through `0x0071D420`, a lower-bound walk with unsigned compares that reports the end when the key is below the node found. It returns the dword at node `+0x10`, or 0 for the end. |
| Result | `0x007028D6..0x0070290B` | A nonzero record pointer pushes true and zero pushes false through the bool pusher `0x00748870`. |

The receiver of `0x006F51A0` is the `CharaBase` control and not the chara record
that the identity resolves to. The only state the native writes is the lazy
creation of the manager. It requests no yield. The shipped scripts contain 19
call sites in 13 chunks (`MEASURED`). Each has one argument and six of them pass
the constant 100 (`INFERRED`, local scan). That the key names an item package number and that
the record is the package are `INFERRED` from the native name and the shared
lookup. The writers of the package tree and the numbers that exist for a receiver
were not traced.

## Main stat mode

`_isActorMainStatMode` (`0x006FA5D0`) declares one `int` argument and one `bool`
return. It reads cell 0 as an int, resolves the receiver identity from
`ExecuteParameters` `+0x0C` through `0x0075C1B0` and `0x004D9970` and loads the
dword at chara `+0xF0` through `0x00585400`. That dword is the one that
`_getActorMainStat` returns in the
[binding map contracts](binding-map-native-contract.md). The identity `0xC0000000`
and an absent identity resolve to 0, and no instruction tests the pointer before
the load, so the run-time result for an absent receiver is unknown.

The callback passes the mode and the stat to `0x0078E0E0` as stdcall arguments
and pushes the returned byte as a bool. The routine subtracts 1 from the mode and
sends any result above `0x7F`, as an unsigned compare, to the false exit
`0x0078E12E`. The byte table at `0x0078E1A0` selects one of nine jump targets from
the table at `0x0078E17C`. Its indexes 0, 1, 3, 7, 15, 31, 63 and 127 select cases
0 to 7 and every other index selects the false exit. Only the single bit values
1 to 128 therefore reach a case, and a sum of bits pushes false (`STATIC`).

| Mode | Case routine | Stat values that give true |
| ---: | --- | --- |
| 1 | `0x0078E0FA` | `0x01`, `0x03` |
| 2 | `0x0078E10D` | `0x02`, `0x51` |
| 4 | `0x0078E120` | `0x1E` to `0x20` |
| 8 | `0x0078E133` | `0x32`, `0x33` |
| 16 | `0x0078E141` | `0x46` |
| 32 | `0x0078E14C` | `0x0B`, `0x0D`, `0x0E` through the helper `0x0078E090` |
| 64 | `0x0078E15C` | `0x0C` |
| 128 | `0x0078E167` | `0x0F`, `0x5B` |

The shipped scripts contain 8 call sites in 4 chunks (`MEASURED`). Each has one
argument (`INFERRED`, local scan). `CharaBaseClass.isDeadMode` passes 1 and
`isSitMode` passes 32. `isActiveMode` passes 2, 4, 8 and 16 in turn and returns at
the first true. The talk command passes 2. No shipped script passes 64 or 128. The group names come
from the script helper names and are `INFERRED` for the executable. The writers of
the dword at chara `+0xF0`, the names of the stat values and the roles of modes
64 and 128 were not traced.

## Target cursor control

The three `DesktopWidget` natives share one counter. Each callback reads the
world chain through `0x00CC7510`, loads the dword at `Y +0x08` and calls a glue
routine that loads `V`, calls `0x004D7580`, which adds `0x17758` to `V`, and
tail jumps through a virtual slot of the object at that address. The object is the
`RaptureUserControl` of the
[player control record](binding-map-native-contract.md#player-control), vftable
`0x00F90F64`. Its constructor `0x004DECF0` builds four `0x14` byte records at
object `+0x08` and `0x004DEC70` stores 0 at record `+0x10`. The counters are the
dwords at object `+0x18`, `+0x2C`, `+0x40` and `+0x54`, so each starts at 0
(`STATIC`).

| Native | Glue | Slot | Slot routine | Effect on the dword at `+0x2C` |
| --- | --- | ---: | --- | --- |
| `_lockTargetCursorControl` | `0x0075B270` | 4 | `0x0054B620` | Adds 1 with no bound. |
| `_unlockTargetCursorControl` | `0x0075B290` then `0x0075B280` | 6, 5 | `0x0054B640`, `0x0054B630` | Reads the counter and adds -1 only when it is above 0 as a signed compare. The engine reaches slot 5 directly with no test. |
| `_isTargetCursorControlEnabled` | `0x0075B290` | 6 | `0x0054B640` | Pushes true when the counter equals 0. |

None of the three declares an argument and the first two push nothing. The enabled
native pushes through the bool pusher with the byte from `sete`, so it is true only
for a counter of exactly 0 and a negative counter pushes false. The engine calls
the lock glue directly at `0x0070402D` and the unlock glue at `0x00703A7E`, each
next to the player control glue (`0x00704026` and `0x00703A77`), so the engine and
the Lua natives share the counters. The engine unlock is not guarded. Its glue
`0x0075B280` tail jumps to slot 5, `0x0054B630`, which is an unconditional add of -1
with no test of the counter. Only the Lua native `0x006E1B20` tests the counter
before it decrements, so the rule that the counter falls only when above 0 holds
for the Lua natives and not for the engine, and a negative counter is reachable
(`STATIC`). None of the natives requests a yield.

The shipped scripts contain 12 call sites of each of the lock and unlock natives
in 5 chunks and 1 call site of the enabled native in a debug command chunk
(`MEASURED`). None has an argument (`INFERRED`, local scan).
`PlayerBaseClass._onPreEvent` and `_onPreCommand` call the lock and `_onPostEvent`
and `_onPostCommand` call the unlock. `DesktopWidget.setTutorialMask` calls both.
The opening quest scripts `man0g0`, `man0l0` and `man0u0` contain the remaining
sites. That the counter suppresses target cursor input while above 0 is `INFERRED`
from the native names. The consumers of the counter other than these natives and
the two engine call sites were not traced.

## Area and display name natives

`_isInn` (`0x006F97A0`) takes no argument. It adds `0xBA` to the `AreaBase`
receiver and passes the address to the bool pusher, and `0x00583E30` copies that
byte into a tag 2 cell. The shipped scripts contain 4 call sites in 3 chunks
(`MEASURED`). They are `AreaBaseClass._onInit` and `_onFinalize`,
`CharaBaseClass.getReadyCommand` and the desktop widget connector, none with an
argument (`INFERRED`, local scan). That the byte says the area is an inn is
`INFERRED` from the native name and its writers were not traced.

`_getLocalizedDisplayName` (`0x006FA3D0`) takes no argument and returns one
`Utf8String`. It loads the dword at receiver `+0x60`, adds 4 and passes the address
to the Utf8String pusher `0x007487C0`. The `CharaBase` control constructor stores 0
at `+0x60` (`0x006ECDBA`) and no instruction tests the dword, so the native reads
address 4 until another routine stores a record pointer. The record is the one that
`_getDisplayName` reads in the [binding map contracts](binding-map-native-contract.md),
where a first dword other than -1 selects a result and -1 marks a literal string at
`+0x04`. This native pushes the string at `+0x04` whatever the first dword holds.
The writer of the pointer was not traced.
Eight call sites in 3 chunks exist (`MEASURED`) and two of them pass an argument
that the empty declared list does not read (`INFERRED`, local scan).

`_getLocalizedDisplayNameForChat` (`0x006FA3F0`) takes no argument and returns one
`Utf8String`. When the id dword at the start of the record at receiver `+0x60` is
-1 it pushes the record string like the plain native. Otherwise it reads the
world chain, loads the dword at `Y +0xDC` and calls `0x0075D020` with a result
slot and the id. That routine formats the id into a `0x40` byte buffer with the
format string at `0x00FDF6BC`, which is `<fixed(21,%d)>`, loads the object that
the first dword of the `+0xDC` value addresses and calls its virtual slot 5
(offset `0x14`) with the result string and the buffer. The result string is pushed
through `0x007487C0`. Two call sites exist in the desktop widget connector
(`MEASURED`), in `subTargetDecided` and `convertPronouns`, neither with an
argument (`INFERRED`, local scan). That the macro resolves a chara display name is `INFERRED`. The class
of the object behind slot 5 and the meaning of the macro number 21 were not
traced.

## NpcBase filter natives

`_isTalkable`, `_isEmotable` and `_isPushable` each declare one `LuaControl*`
argument (list builder `0x0072C260`) and one `bool` return. The bytes do not make
the argument optional, as the table below shows. Their
callbacks read the raw cell vector instead of a typed reader and pass the address
of a pointer vector in the receiver and the cell holder at `ExecuteParameters`
`+0x10` to `0x0071DE70`. The vectors are at receiver `+0xE8` (`_isTalkable`),
`+0xF8` (`_isEmotable`) and `+0x108` (`_isPushable`).

| Condition | Result |
| --- | --- |
| The vector holds no 4 byte element. | false, and the cell vector is not read |
| The vector is non-empty and the call supplies no argument cell. | The invalid-parameter route `0x009D22B4` is called at `0x0071DEA3` |
| The first cell has a tag other than 4. | true |
| The first cell has tag 4 and some element has the byte at element `+0x58` equal to the byte at `0x012C3F77`. | true |
| The first cell has tag 4 and no element matches. | false |

The empty-vector exit comes first, so a call with no argument on a receiver whose
vector is empty pushes false, and the same call on a receiver whose vector is
non-empty reaches `0x009D22B4` (`STATIC`). The cell vector counts 16 byte cells.
`0x0071DA00` performs the scan and ignores its argument, so the control in the
cell is never consulted (`STATIC`). The result is pushed through the bool pusher.
The shipped scripts contain 5 call sites of `_isTalkable` in 3 chunks (the desktop
widget connector, the depiction judge and a debug command chunk) and 2 call sites
each of `_isEmotable` and `_isPushable` in a debug command chunk (`MEASURED`). The
`_isTalkable` sites have argument counts 0 (2 sites), 1 (2 sites) and open (1 site),
and each of the other two natives has one site with 0 and one with 1 (`INFERRED`,
local scan). If a script call with no argument leaves the cell vector empty, the
0-argument sites reach `0x009D22B4` on a receiver with a non-empty vector. Whether
the executor adds cells for a declared argument that a call omits, and what the
route does for these callbacks, were not run (`INFERRED`). The writers of the vectors, the class of their
elements, the role of the byte at `+0x58` and the writer of the byte at
`0x012C3F77` were not traced.

## PlayerBase command dispatch

The four callbacks `0x006DE650`, `0x006DE6A0`, `0x006DE6D0` and `0x006DE740` are
three instruction thunks that load the receiver vftable and jump through a slot.
The `PlayerBase` cell of each slot holds a bare `ret 4`, so a `PlayerBase`
receiver that is not a `MyPlayer` pushes nothing (`STATIC`). That the Lua call
then returns no value is `INFERRED` from the empty return container. The
`MyPlayer` vftable `0x00FD785C` holds the routines (`STATIC`).

| Native | Slot | `PlayerBase` cell | `PlayerBase` routine | `MyPlayer` cell | `MyPlayer` routine |
| --- | ---: | --- | --- | --- | --- |
| `_executeCommand` | `0xA8` | `0x00FD5EAC` | `0x006DE8A0` | `0x00FD7904` | `0x0070A010` |
| `_canExecuteCommand` | `0xBC` | `0x00FD5EC0` | `0x006DE8F0` | `0x00FD7918` | `0x00704AA0` |
| `_cancelCommand` | `0xC8` | `0x00FD5ECC` | `0x006DE920` | `0x00FD7924` | `0x006E8D90` |
| `_isCommandPlaying` | `0xE4` | `0x00FD5EE8` | `0x006DE990` | `0x00FD7940` | `0x00704E40` |

`0x00704AA0` and `0x00704E40` push false when the byte at receiver `+0x5C` is 0.
`0x00704AA0` otherwise reads a Utf8String command name, looks it up through
`0x0071CA50` on receiver `+0xFC` and queries the object it finds through virtual
slots 7 and 8. `0x006E8D90` reads a Utf8String from cell 0 and tests whether cell 1
has tag 6. `0x0070A010` compares receiver `+0x128` and `+0x12C` with the dword at
`0x0130C778` and otherwise reads the argument cells. The
[command and talk contracts](command-talk-native-contract.md) trace the four
routines, their gates and the entries they hand to the policy manager.

## Not traced

- The writers of the package tree behind receiver `+0xD8`, the package numbers
  that exist for a receiver and the value of a record under a key.
- The writers of the dword at chara `+0xF0`, the names of the main stat values and
  the roles of the modes 64 and 128 of `_isActorMainStatMode`.
- The run-time result of `_isActorMainStatMode` for an identity that is absent
  from the registry.
- The consumers of the target cursor counter other than the three natives and the
  two engine call sites, and whether a shipped script or the unguarded engine unlock
  can leave the lock and unlock calls unbalanced.
- The writers of the byte at `AreaBase +0xBA`, of the record pointer at
  `CharaBase +0x60` and of the `NpcBase` vectors and the byte at `0x012C3F77`.
- The object behind virtual slot 5 of `_getLocalizedDisplayNameForChat` and the
  meaning of the macro number 21.
- The command objects behind receiver `+0xFC` beyond the first calls recorded in
  the [command and talk contracts](command-talk-native-contract.md).

## Next natives

The next natives by value are ranked by the number of distinct scripts that
contain a call, with the call-site count as the tie break. The selection is by
static script names and switchboard orders. It is not an execution trace and not
the census blocker lists of `bahamut-client`, so a ranked native is not shown to
be reached by `DesktopWidget`, `ActionMenuWidget` or `MapNavigationWidget`
(`_cancelAimCameraTutorial` is a `WorldMaster` native). Natives with a
contract row in any manifest or a wire-level record in a contract page are left
out, and so are the script callbacks that begin with `_on`, the work keys, the
descriptor suffix identifiers and the Lua level helpers `_callFunction`,
`_callSuperClassFunc` and `_assignForChild`. An alias takes the class of its
descriptor.

| Rank | Native | Class | Scripts | Call sites | Why |
| ---: | --- | --- | ---: | ---: | --- |
| 1 | `_cancelAimCameraTutorial` | `WorldMaster` | 5 | 22 | Order 17 of the `WorldMaster` switchboard. |
| 2 | `_cancelLookAtPlayerTutorial` | `WorldMaster` | 5 | 11 | Order 15 of the `WorldMaster` switchboard. |
| 3 | `_commandDebug` | `Debug` | 5 | 8 | Order 7 of the `Debug` switchboard. |
| 4 | `_waitForMapLoaded` | `PlayerBaseClass` | 5 | 8 | Order 38 of the `PlayerBase` switchboard, a candidate yield native. |
| 5 | `_getAllCharacter` | `Debug` | 4 | 17 | Order 5 of the `Debug` switchboard. |
| 6 | `_getAllGroup` | `CharaBaseClass` | 4 | 10 | Order 43 of the `CharaBase` switchboard. |
| 7 | `_getGrandCompanyRank` | `PlayerBaseClass` | 4 | 9 | Order 52 of the `PlayerBase` switchboard. |
| 8 | `_setWeather` | `PlayerBaseClass` | 4 | 8 | Order 40 of the `PlayerBase` switchboard. |
| 9 | `_createVirtualItem` | `CharaBaseClass` | 4 | 6 | Order 76 of the `CharaBase` switchboard. |
| 10 | `_getNetStatUser` | `CharaBaseClass` | 4 | 6 | Order 19 of the `CharaBase` switchboard. |
| 11 | `_getAreaType` | `PrivateAreaBaseClass` | 4 | 5 | Order 1 of the `PrivateAreaBase` switchboard. |
| 12 | `_lockCameraControl` | `PlayerBaseClass` | 3 | 12 | Order 33 of the `PlayerBase` switchboard, next to the lock-on pair. |
| 13 | `_unlockCameraControl` | `PlayerBaseClass` | 3 | 12 | Order 34 of the `PlayerBase` switchboard, next to the lock-on pair. |
| 14 | `_getClassName` | `Debug` | 3 | 11 | Order 3 of the `Debug` switchboard. |
| 15 | `_waitForTargetTutorial` | `DesktopWidget` | 3 | 9 | Order 35 of the `DesktopWidget` switchboard, a candidate yield native. |
| 16 | `_getLowResolutionTime` | `Debug` | 3 | 7 | Order 6 of the `Debug` switchboard. No descriptor of the shipped scripts targets the registered name. |
| 17 | `_waitForCameraTutorial` | `DesktopWidget` | 3 | 6 | Order 36 of the `DesktopWidget` switchboard, a candidate yield native. |
| 18 | `_waitForTurning` | `CharaBaseClass` | 3 | 6 | Order 63 of the `CharaBase` switchboard, a candidate yield native. |
| 19 | `_isTrading` | `ItemBaseClass` | 3 | 5 | Order 18 of the `ItemBase` switchboard. |
| 20 | `_printDebugLog` | `WorldMaster` | 3 | 5 | Order 5 of the `WorldMaster` switchboard. |
| 21 | `_getAchievementTitle` | `PlayerBaseClass` | 3 | 4 | Order 65 of the `PlayerBase` switchboard. |
| 22 | `_isDealing` | `ItemBaseClass` | 3 | 4 | Order 13 of the `ItemBase` switchboard. |

The manifest rows under `nextTranche` carry the same order. This record covers
ranks 2, 3, 10 and 19 of the [Global ranked list](global-native-contract.md) and
ranks 5 and 6 of the [work binder ranked list](work-binder-native-contract.md).

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes with the route of the
[binding map contracts](binding-map-native-contract.md#reproduction). The argument
counts and the constants passed to `_isActorMainStatMode` come from the `.le.lpb`
files of an installed client, decoded by [`tools/decode_lpb.py`](../tools/decode_lpb.py)
and read with a Lua 5.1 bytecode parser over the `SELF` call sites. They are
`INFERRED` because no tracked artifact carries them. The function VAs for `$Addresses`
are:

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Registrars | `0x00756240,0x0074C2F0,0x0074BC60,0x0074BDB0,0x00739C60,0x00739DB0,0x007518E0,0x0074A0D0,0x007503E0,0x00750530,0x00750680,0x0073F080,0x00730C00,0x00730FF0,0x00731920` |
| Switchboards and holders | `0x007574A0,0x00757EA0,0x00753CF0,0x00754850,0x00753F90,0x00726460,0x00726510,0x00726BF0,0x0072CD40,0x0072D400,0x007267D0,0x00726720,0x0071B4D0,0x0072D1B0,0x0071E1E0` |
| Callbacks | `0x00708B60,0x006FA5D0,0x006FA3D0,0x006FA3F0,0x006E1B00,0x006E1B20,0x006FDDE0,0x006F97A0,0x00706AA0,0x00706AE0,0x00706B20,0x006DE650,0x006DE6A0,0x006DE6D0,0x006DE740` |
| Item package | `0x00702880,0x006DD450,0x006DD4D0,0x0078BC90,0x006F51A0,0x006F5100,0x006E5BA0,0x0071D420,0x005819A0` |
| Main stat | `0x0075C1B0,0x004D9970,0x004DE190,0x00585400,0x0078E0E0,0x0078E090` |
| Target cursor | `0x0075B270,0x0075B280,0x0075B290,0x004D7580,0x0054B620,0x0054B630,0x0054B640,0x004DECF0,0x004DEC70` |
| Display name and push | `0x0075D020,0x00583E30,0x00748870,0x007487C0,0x0071DE70,0x0071DA00,0x0072C260` |
| Command dispatch | `0x006DE8A0,0x006DE8F0,0x006DE920,0x006DE990,0x0070A010,0x00704AA0,0x006E8D90,0x00704E40` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
