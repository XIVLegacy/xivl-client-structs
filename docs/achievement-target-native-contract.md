# Achievement, target, group, item package, reaction box, Chocobo and cut scene native contracts

[`manifests/achievement_target_native_call_contract.json`](../manifests/achievement_target_native_call_contract.json)
records the static Lua call contracts of fourteen native names that make fifteen
registrations. Two belong to `DesktopWidget` and read or set the target:
`_setTargetNearestCharacter` and `_getLastAttacker`. Four belong to `CharaBase`:
the item package request `_updateItemPackage`, the group getter
`_getExtendedTemporaryGroup`, the status slot reader `_getSubStatStatus` and the
flag reader `_getSystemFlag`. One belongs to `NpcBase`, the reaction box setter
`_setReactionTriggerBox`. `_transformIntoChocobo` is registered under
`WorldMaster` and under `CharaBase`. Five belong to `PlayerBase` and read the
achievement store: `_isDoneAchievement`, `_getAchievementRate`,
`_getAchievementItemId`, `_getAchievementSheetDataTitle` and
`_getAchievementSheetDataItem`. The last belongs to `CutScene`: `_loadCutScene`.
Each row gives the registration site, the receiver type check, the declared
argument and return lists, the Lua pushes of every branch, the reads, the effects
on client state, the failure behavior and whether the call yields. The
contracts describe client marshalling and state, not target selection rules,
group membership, item package contents, achievement values, reaction records or
server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data at
the cited addresses. `MEASURED` is counted or parsed by the method named in the
fact, from the executable or from the call-site index of the installed client
scripts. `INFERRED` is a name or role taken from the surrounding instructions or
script names that the bytes do not state. `unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
The listings, the caller scan and the reproduction route are the ones of the
[binding map contracts](binding-map-native-contract.md#binary-and-method). A
second pass checked that every cited locator begins an instruction of its decoded
function and compared the operands, name literals, vftable cells, jump table
entries, constants and call targets named below with the listings. `R`, `X`, `Y`,
`W` and `V` name the world object chain of the
[fade contracts](fade-actor-group-native-contract.md#fade-natives) and the
[Global contracts](global-native-contract.md#binary-and-method). The registrar
shape, the type registry, the cell tags and the invalid-parameter route are the
ones of the [nameplate, actor and group contracts](nameplate-group-native-contract.md)
and the [work binder contracts](work-binder-native-contract.md#binary-and-method).
The list builders and pushers are the ones of the
[group list and status bit contracts](chara-world-native-contract.md#registration).

The call-site and script counts agree with
`xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. They show that a
script contains a call, not that a script reaches it at run time. The argument
counts, the return counts, the constants and the descriptor selectors come from a
local Lua 5.1 bytecode scan of the installed client scripts, decoded with
[`tools/decode_lpb.py`](../tools/decode_lpb.py). The script sources are not
redistributed and no tracked artifact carries those values, so they are
`INFERRED`.

## Ranking

The ranking covers every native that `xivl-client-scripts:lua/napi_index.json`
lists and that the ledger of the client rewrite still marks unimplemented or a
stub. It orders them by the call sites outside the `commanddebugger` scripts,
then by the total index call sites, then by the number of distinct scripts
outside the debug console, then by the class order `CharaBase`, `NpcBase`,
`WorldMaster`, `DesktopWidget`, `PlayerBase`, `CutScene` and last by the
switchboard order. The ledger is read at the revision named in the manifest. The
selection takes the first fourteen natives that remain after the left out
groups below.

| Rank | Native | Class | Scripts | Call sites |
| ---: | --- | --- | ---: | ---: |
| 1 | `_setTargetNearestCharacter` | `DesktopWidget` | 2 | 8 |
| 2 | `_getExtendedTemporaryGroup` | `CharaBase` | 2 | 7 |
| 3 | `_updateItemPackage` | `CharaBase` | 2 | 7 |
| 4 | `_setReactionTriggerBox` | `NpcBase` | 3 | 6 |
| 5 | `_transformIntoChocobo` | `WorldMaster` | 1 | 4 |
| 6 | `_isDoneAchievement` | `PlayerBase` | 1 | 4 |
| 7 | `_getSubStatStatus` | `CharaBase` | 1 | 3 |
| 8 | `_getLastAttacker` | `DesktopWidget` | 1 | 3 |
| 9 | `_loadCutScene` | `CutScene` | 2 | 2 |
| 10 | `_getSystemFlag` | `CharaBase` | 1 | 2 |
| 11 | `_getAchievementItemId` | `PlayerBase` | 1 | 2 |
| 12 | `_getAchievementSheetDataTitle` | `PlayerBase` | 1 | 2 |
| 13 | `_getAchievementSheetDataItem` | `PlayerBase` | 1 | 2 |
| 14 | `_getAchievementRate` | `PlayerBase` | 1 | 2 |

The left out groups are these.

- `_setListProperty`, `_updateList`, `_removeList`, `_isKeyboardFocused`,
  `_getKeyboardFocusedControl`, `_clearAllList`, `_getListProperty`, `_addList`.
  Widget host natives are outside this slice.
- `_createWidgetInWidgetContainer`, `_deleteCreatingWidgetInWidgetContainer`,
  `_getUserMacroData`, `_getUserMacroIcon`, `_getUserMacroTitle`,
  `_getWidgetFromWidgetContainer`, `_isCreatingWidgetInWidgetContainer`,
  `_isExistWidgetInWidgetContainer`, `_saveUserMacro`, `_setUserMacroData`,
  `_setUserMacroIcon`, `_setUserMacroTitle`, `_waitForItemSearchWidget`. These
  natives hold or query user macros, widget containers or the item search
  widget. They are widget host natives and are outside this slice.
- `_isSpreadSheetExistAttribute`, `_getGroupCurrent`, `_getAllItem`,
  `_getSpreadSheetAllAttribute`, `_getPlayingCutSceneActor`,
  `_getEventPriority`, `_getTimeCost`, `_getCharacterLocation`. Every index site
  is in commanddebugger scripts, or the class is Debug. They are debug console
  natives.
- `_setDir`, `_setPos`, `_setPosDirInn`. The executable holds no registration
  literal of these names, so no registrar exists to read.
- `_getHamletSupplyRanking`, `_countHamletSupplyRanking`.
  [`manifests/hamlet_wire_contract.json`](../manifests/hamlet_wire_contract.json)
  records the ranking getter route in its row 0x01a6.

Natives that already have a contract row in another manifest of this repository
are left out as well, and so are the script callbacks that begin with `_on` and
the host intrinsics of the binding map contract. `_updateItemPackage` and
`_setReactionTriggerBox` have prose records in the
[Bazaar contract](bazaar-native-wire-contract.md#package-and-slot-numbering) and
the [door initialization contract](door-initialization-native-contract.md#reaction-box-arguments).
Those records describe a body or an argument list and give no receiver check, list
declaration or branch table, so the rows here complete them. The `CutScene`
natives `_skip`, `_play` and `_replay` rank below the selection and are recorded
as related rows.

## Registration

Every native but three is declared by a `_u` script descriptor named
`<name>_inl` that returns the selector `self` and the target `<name>_cpp`. The
descriptor tables are `CharaBaseClass` in `chara/charabaseclass_u`,
`NpcBaseClass` in `chara/npc/npcbaseclass_u`, `WorldMaster` in
`world/worldmaster_u`, `DesktopWidget` in `widget/desktopwidget_u` and
`PlayerBaseClass` in `chara/player/playerbaseclass_u` (`INFERRED`). The three
exceptions are `_setTargetNearestCharacter`, which a plain Lua function wraps,
`_loadCutScene`, which an empty plain Lua function replaces, and the `CharaBase`
registration of `_transformIntoChocobo`, which no descriptor targets. The order of
a native is its position among the rel32 calls of its switchboard.

| Native | Class | Switchboard | Order | Registrar | Caller | Callback |
| --- | --- | --- | ---: | --- | --- | --- |
| `_setTargetNearestCharacter` | `DesktopWidget` | `0x00757EA0` | 13 | `0x00739B10` | `0x00757FB8` | `0x006E54E0` |
| `_updateItemPackage` | `CharaBase` | `0x007574A0` | 71 | `0x007302D0` | `0x00757A7A` | `0x006E79D0` |
| `_getExtendedTemporaryGroup` | `CharaBase` | `0x007574A0` | 42 | `0x007553D0` | `0x00757819` | `0x00708410` |
| `_setReactionTriggerBox` | `NpcBase` | `0x00754850` | 21 | `0x007428B0` | `0x00754A10` | `0x006F23F0` |
| `_transformIntoChocobo` | `WorldMaster` | `0x00754C70` | 19 | `0x0073BA90` | `0x00754E06` | `0x006EC5E0` |
| `_transformIntoChocobo` | `CharaBase` | `0x007574A0` | 81 | `0x00730420` | `0x00757B4C` | `0x006DC330` |
| `_isDoneAchievement` | `PlayerBase` | `0x00753F90` | 63 | `0x007298C0` | `0x007544C2` | `0x0071E550` |
| `_getSubStatStatus` | `CharaBase` | `0x007574A0` | 15 | `0x0074B330` | `0x007575E2` | `0x006FA150` |
| `_getLastAttacker` | `DesktopWidget` | `0x00757EA0` | 34 | `0x007520C0` | `0x00758171` | `0x006FE4A0` |
| `_loadCutScene` | `CutScene` | `0x007547D0` | 2 | `0x00736000` | `0x00754801` | `0x006DC550` |
| `_getSystemFlag` | `CharaBase` | `0x007574A0` | 21 | `0x0074B9C0` | `0x00757660` | `0x006FA330` |
| `_getAchievementSheetDataTitle` | `PlayerBase` | `0x00753F90` | 73 | `0x0072A1F0` | `0x00754594` | `0x0071E5E0` |
| `_getAchievementSheetDataItem` | `PlayerBase` | `0x00753F90` | 74 | `0x0072A340` | `0x007545A9` | `0x0071E5F0` |
| `_getAchievementRate` | `PlayerBase` | `0x00753F90` | 75 | `0x0072A490` | `0x007545BE` | `0x0071E600` |
| `_getAchievementItemId` | `PlayerBase` | `0x00753F90` | 62 | `0x00729770` | `0x007544AD` | `0x0071E540` |

The switchboards are `CharaBase` `0x007574A0` at the vftable `0x00FD5CAC`,
`NpcBase` `0x00754850` at `0x00FD647C`, `WorldMaster` `0x00754C70` at
`0x00FD5864`, `DesktopWidget` `0x00757EA0` at `0x00FD5B8C`, `PlayerBase`
`0x00753F90` at `0x00FD5E04` and `CutScene` `0x007547D0` at `0x00FD597C`. Each
switchboard is stored at slot 2 of its vftable. Each of its calls sits behind a
test of the byte at `+0x0E` of the switchboard argument. A nonzero byte adds 1 to
the word at `+0x0C` and skips the registrar. The `CutScene` switchboard registers
`_setFilename` (1), `_loadCutScene` (2), `_play` (3), `_replay` (4) and `_skip` (5).

The holders are the ones of the earlier contracts, with one new entry. The wrapper
`0x00726880` is the `CutScene` non-const holder. It selects an element of `0x58`
bytes of a functor vector, builds the functor with `0x007249A0` and the holder
with `0x0071A9C0`, which stores the vftable `0x00FD5B40` and the member function
pointer. Its invoke routine `0x0071AA30` casts the receiver from `LuaControl`
(`0x01270B4C`) to the type descriptor `0x012C17AC` and returns without calling the
callback for a null cast.

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_setTargetNearestCharacter` | `DesktopWidget` | `int` | none | no |
| `_updateItemPackage` | `CharaBase` | `int` | none | no |
| `_getExtendedTemporaryGroup` | `CharaBase` | `int` | `LuaControl* or Nil` | no |
| `_setReactionTriggerBox` | `NpcBase` | `Utf8String`, `int`, `int`, `Utf8String`, `bool` | none | no |
| `_transformIntoChocobo` | `WorldMaster` | `int`, `int` | none | yes |
| `_transformIntoChocobo` | `CharaBase` | `int` | none | no |
| `_isDoneAchievement` | `PlayerBase` | `int` | `bool` | no |
| `_getSubStatStatus` | `CharaBase` | `int` | `LuaControl* or Nil` | no |
| `_getLastAttacker` | `DesktopWidget` | none | `LuaControl* or Nil` | no |
| `_loadCutScene` | `CutScene` | none | none | no |
| `_getSystemFlag` | `CharaBase` | `int` | `bool` | no |
| `_getAchievementSheetDataTitle` | `PlayerBase` | `int` | `int` | no |
| `_getAchievementSheetDataItem` | `PlayerBase` | `int` | `int` | no |
| `_getAchievementRate` | `PlayerBase` | `int` | `int or Nil`, `int or Nil` | no |
| `_getAchievementItemId` | `PlayerBase` | `int`, `int` | `int or Nil` | no |

The list builders are `0x0072B440` for none, `0x00728C20` for an int,
`0x00728B70` for a bool, `0x0072C260` for a `LuaControl*`, `0x00583CE0` for two
ints, `0x00742010` for the five entries of `_setReactionTriggerBox` and
`0x0072BCA0` for the bool and int of `_play` and `_replay`. The argument readers
are `0x005819A0` for an int, `0x0071CE70` for a `Utf8String` and `0x0071BA00` for a
bool. The pushers are `0x00584F70` for an int, `0x00748870` for a bool,
`0x00748920` for nil and `0x00748B30` for a control. `_transformIntoChocobo` under
`WorldMaster` is the only row that calls the yield request `0x00CD2860`.

## Target natives

`_setTargetNearestCharacter` (`0x006E54E0`) has no `_inl` descriptor, and the
binding map contract lists it among the registered names that no `_cpp` key
targets. `widget/desktopwidget_u` defines a plain Lua function of that name on
`DesktopWidget`. It returns false when `work.targetCursorMask` is true, returns
false when the current target cursor is 1 and the local player has a lock-on
target, and otherwise calls the registered native as
`_setTargetNearestCharacter_cpp` and returns true (`INFERRED`). The seven call
sites in `widget/desktopwidget_connector` call the plain function with the
constants 1 to 4.

The native reads one int and keeps its low byte at receiver `+0x78` for the length
of one call. It takes `Y` and loads the dword at `Y +0x04`. It calls
`0x0075B720` with that dword. The routine reads the first dword of its argument,
takes the object at `+0x4C0` of it through `0x004D7310` and jumps to
`0x005656B0`. That routine answers false when the signed dword at `+0xB8` of the
object is negative. Otherwise it calls `0x005655F0` with the argument 1, passes
a nonzero result and the `+0xB8` dword to `0x00562D30` and answers true. The
callback discards the answer and stores the byte 0 at receiver `+0x78`. A path of
`0x00562D30` builds a record with the dwords `0xCD` and `0x18` and passes it to
`0x004D6D10`. `xivl-opcodes:opcodes.json` names the serverbound opcode `0x00CD`
`SetTargetPacket` (`INFERRED`). The reader of the byte at `+0x78` and the
selection conditions of the two routines were not traced.

`_getLastAttacker` (`0x006FE4A0`) takes no argument. It passes the address of
`Y +0x134` to `0x00CC7A50`, which resolves an identity to a control. A null result
or a zero byte at control `+0x5C` pushes nil. Any other result is pushed through
`0x00748B30`. That the identity is the last attacker is `INFERRED` from the name.

## Group and status natives

`_getExtendedTemporaryGroup` (`0x00708410`) is the sibling of `_getGroup`. Its
callback pushes the flag 1 and calls the helper `0x00701140`, which the
[`_getGroup` callback](nameplate-group-native-contract.md#group-natives) calls with
the flag 0. The helper reads one int and asks the group manager at `Y +0xE4`
through `0x006C4560` for the group of the receiver identity and that int. An
invalid group pushes nil. A valid group goes to `0x006E2240`, which tests the flag
and calls `0x00CC80A0` for 0 or `0x00CC8140` for a nonzero flag. Both are thin
wrappers of the control factory `0x00CD9360` and differ only in the creation mode
dword that they store before the call, 0 and 1. The control is cast to
`GroupBase` and 16 bytes of the group handle are copied to control `+0x68`. What
the creation mode changes in the created control was not traced. The scripts call
the native with the constants 10001 and 10002 or with a variable (`INFERRED`).

`_getSubStatStatus` (`0x006FA150`) reads one int and takes the status record of
the receiver through `0x006EEC00`. The record at receiver `+0xDC` is created on
first use, and its dword vector at `+0x04` holds 20 elements. The callback
subtracts 1 from the low byte of the int, zero extends the result and tests it
against the element count with an unsigned compare. An index at or above the count
calls `0x009D22B4`. A zero element pushes nil. A nonzero element goes to
`0x00748B30`, which builds a cell with the tag 4. The return list builder
`0x0072C260` selects the `LuaControl*` operator, whose push slot `0x00CF9D60` reads
a nonzero dword as a control reference through `0x00CD7A30`, a load of the dword at
`+0x04` of the value. The status effect records describe these slots as u32 status
values, and `0x00707D60` stores a value by index into the same vector. The two
readings were not reconciled, so a client must not assume an int result. The
wrapper in `chara/charabaseclass` loops over `charaWork.statusShownTime`, calls the
native with the loop index and compares the result with nil and with its second
argument (`INFERRED`).

`_getSystemFlag` (`0x006FA330`) reads one int and discards it. It takes the status
record and pushes whether bit 0 of the dword at record `+0x14` is set. A fresh
record answers false. Both script sites pass the constant 1 (`INFERRED`).

## Item package request

`_updateItemPackage` (`0x006E79D0`) reads one Lua package number, subtracts 1 and
sends the serverbound request `0x0131` for the receiver actor. The callback builds
a stack `ItemBase` control with `0x006DD450`, calls `0x006E5AD0` and destroys the
control through `0x006DD4D0`. The receiver register is overwritten before any use,
and `0x006E5AD0` does not read it either. The helper reads cell 0 through
`0x005819A0`, converts it with `0x0078BC90`, takes `Y` and copies the dwords at `Y
+0x00`, `+0x10` and `+0x14` into a local through `0x0075D460`. It then calls
`0x0075EA50` with the local, the address of a local that holds the actor dword at
ExecuteParameters `+0x0C` and the address of the converted package. `0x0075EA50` builds a record
with the dwords `0x131` and `0x18`, the actor dword and the low byte of the
package, and passes it to `0x004D6D30`. No range test exists, so the package 0
becomes the byte `0xFF` and a number above 256 wraps. `xivl-opcodes:opcodes.json`
names the opcode `UpdateItemPackagePacket` with the anchor `FUN_0075EA50`. The
retainer script calls the native with the constants 1, 100 and 8, two times each
(`INFERRED`).

## Reaction box

`_setReactionTriggerBox` (`0x006F23F0`) reads five arguments.

| Index | Operator | Reader | Role |
| ---: | --- | --- | --- |
| 0 | `Utf8String` | `0x0071CE70` | Reaction name. The sites pass in and out (`INFERRED`). |
| 1 | `int` | `0x005819A0` | Layout selector. The low 16 bits select the layout. |
| 2 | `int` | `0x005819A0` | Layout instance selector. |
| 3 | `Utf8String` | `0x0071CE70` | Trigger box name. The sites pass door or tb01 (`INFERRED`). |
| 4 | `bool` | `0x0071BA00` | A cell with the tag 6 reads as false. The sites pass nil or true (`INFERRED`). |

The argument list builder `0x00742010` declares the five entries. A cell 4 whose
tag byte is 6 reads as false without a bool read. The callback appends the
reaction to the container at receiver `+0x12C` through `0x006F0330`. A null
container is allocated with `0x10` bytes, built by `0x006F02C0` and stored through
`0x007219B0`. It then takes `W` and calls `0x0075C800` with the actor dword. Only
when that call answers false does it call `0x0075C7D0` with the layout and instance
ints. The door initialization contract names these two routines as the test for an
existing background attachment and its creation, and gives the meaning of the
layout and instance ints. The scripts pass `in` with a nil flag and `out` with
true, the trigger box `door` at four sites and `tb01` at two (`INFERRED`).

## Chocobo transform natives

The `WorldMaster` registration of `_transformIntoChocobo` (`0x006EC5E0`) reads
two ints and builds the control list through `0x00CC88D0`. For each control that
casts to the `WidgetBase` type descriptor `0x012C1964` it obtains a string through
`0x00CC7560` and compares it with the literal `TargetParameterWidget` at
`0x00FD4E38`. For a match it builds the strings `Hidden`, `Visibility` and
`Window_TargetParameterWidget` and calls `0x0075B810`. The role of that call is
`INFERRED` from the strings to be hiding the target parameter window.

The callback then builds a visitor with the vftable `0x00FD590C`, whose RTTI name
is `s_CharaIterateActorClass`. The visitor keeps the first int at `+0x08` and a
result slot at `+0x0C`. `0x00764150` walks the container at `V +0x4E4` and calls
the visit method `0x007179A0` with each identity. The visit method resolves the
identity to a control through `0x00CC7A50`, casts it to `NpcBase` and requires the
byte at control `+0x5C` to be nonzero. It reads the work value of the key `0x1389`
through `0x00CC7B90`. When the value equals the first int it stores the identity in
the result slot and answers 0, which ends the walk.

`0x0075F3A0` reads the identity from the slot, finds the chara through `0x004D9970`
and calls `0x00589D30` with the second int. The slot starts at 0 and only a
matching visit writes it. When no actor matches, `0x0075F3A0` passes the identity
0 on, and `0x004D9970` jumps to `0x004DE190`, which answers a null chara for the
identity `0xC0000000` and for an identity that is not in its map. Nothing tests
that pointer, and `0x00589D30` executes an AND on the byte at chara `+0x26D` at
`0x00589D35` before it uses the register for anything else. A missing NPC
therefore dereferences the address `0x0000026D` in retail and the yield request is
never reached. The run-time effect was not run. Whether the identity 0 can be a
key of that map was not traced. For a found chara, `0x00589D30` sign extends the
low byte, clears bit 2 of the chara byte at `+0x26D` and calls `0x004D7980` with
the type 9.
`0x0075F3A0` then calls `0x004D7980` with the type `0x17` and stores the chara
pointer in its output local. The callback copies that pointer into a resume checker
of 8 bytes with the vftable `0x00FD5918`, whose RTTI name is
`s_WaitForTransformIntoChocoboResumeChecker`, and requests a yield. The poll of the
checker and the meaning of the work key and of the two event types were not traced.
All four script sites call `worldMaster:_transformIntoChocobo(1080101, x)`
(`INFERRED`).

The `CharaBase` registration of the same name has the callback `0x006DC330`, which
is the single instruction `ret 4`. It declares one int argument and does nothing.
The shipped scripts call the native only on `worldMaster`.
`_cancelTransformIntoChocobo` is the `WorldMaster` sibling at order 20. It is
recorded as a related row.

## Achievement natives

The five achievement natives share one dispatch. Each callback is a thunk of three
instructions that loads the vftable of the receiver, loads one dword of it and
jumps to it.

| Native | Thunk | Slot | PlayerBase cell | MyPlayer cell | MyPlayer routine |
| --- | --- | ---: | --- | --- | --- |
| `_getAchievementItemId` | `0x0071E540` | 100 | `0x00FD5F94` | `0x00FD79EC` | `0x007058D0` |
| `_isDoneAchievement` | `0x0071E550` | 101 | `0x00FD5F98` | `0x00FD79F0` | `0x00705A70` |
| `_getAchievementSheetDataTitle` | `0x0071E5E0` | 110 | `0x00FD5FBC` | `0x00FD7A14` | `0x00705DD0` |
| `_getAchievementSheetDataItem` | `0x0071E5F0` | 111 | `0x00FD5FC0` | `0x00FD7A18` | `0x00705E40` |
| `_getAchievementRate` | `0x0071E600` | 112 | `0x00FD5FC4` | `0x00FD7A1C` | `0x00705EB0` |

The `PlayerBase` vftable `0x00FD5E04` holds `0x00776340` in all five cells. That
routine is the single instruction `ret 4`, so a receiver that does not override a
slot pushes nothing. The `MyPlayer` vftable is `0x00FD785C`. The related rows of the
[player misc manifest](../manifests/player_misc_native_call_contract.json) carry
the same registrars, switchboard orders, vftable offsets and cells for
`_getAchievementItemId`, `_getAchievementSheetDataTitle` and
`_getAchievementSheetDataItem`. The routines read the
achievement store, the pointer at `MyPlayer +0x114`, which the `MyPlayer` override
`0x006F3420` allocates with `0xAC` bytes. Its first member is a bitset of
1024 bits, its dword vector sits at `+0x80` and its map of cached progress counts
sits at `+0x9C`.

`_isDoneAchievement` maps the id to a bit index through `0x0070AB40`. That routine
subtracts 100 and answers 0 for a result above `0x7BE`. Otherwise it jumps through
the table of `0x7BF` cells at `0x0070BCB4`, where each cell loads a constant and
returns it. The table has 740 cells with distinct bit indexes from 1 to 1023 and
1243 cells with 0. An id outside the table range jumps to `0x0070BCB1`, which
returns 0, so that id and every zero cell test bit 0. The routine tests that bit in the bitset and pushes a bool. An
index of `0x400` or more would call `0x006B4AF0`, which throws the message
`invalid bitset<N> position`. No cell returns such an index.

`_getAchievementRate` looks up the maximum M of the id in the map at `0x0134B590`
through `0x006E7370`, which answers 0 for a missing key.

| Case | Pushes |
| --- | --- |
| M is 0 | nil, nil |
| M is 1 and the overall bit is set | 1, 1 |
| M is 1 and the overall bit is clear | 0, 1 |
| M is neither 0 nor 1, the overall bit is set and the id is not 0x3F2, 0x3F3 or 0x3F4 | M, M |
| Otherwise and a cached count of 0 or more exists | the smaller of the count and M by a signed compare, then M |
| Otherwise and the cached count is missing | 0, M after the request below |

The cached count comes from `0x006E3B20` on the achievement store, which answers
-1 for a missing entry. A missing count sends the serverbound request `0x0135`
through `0x0075ECD0`, which `xivl-opcodes:opcodes.json` names
`AchievementRateRequestPacket`. The
[achievement rate consumer contract](achievement-rate-consumer.md) records the
clientbound `0x019F` that fills the cache.

`_getAchievementItemId` tests the tag of cell 0. A nil first cell reads cell 1 as a
1 based position into the dword vector at store `+0x80`. A failed bounds test calls
`0x009D22B4`. A zero element pushes nil and any other element is pushed as an int.
Any other first cell is a category. The routine reads both cells as ints, sets an
extra value of 0 and replaces it for two categories. For 1000 (`0x3E8`) it is the
result of the work accessor `0x00CC7B90` for the work key 100007 (`0x186A7`) with
the index -1. The work binder contract names that key `playerWork.initialTown`. For
1500 (`0x5DC`) it is the sign extended byte at `MyPlayer +0xED`, which the
[player misc contract](player-misc-native-contract.md#grand-company-rank) names
the Grand Company number (`INFERRED`). The routine calls
`0x0070DC60` with the category, the position minus 1 and the extra value and
pushes the returned int. That routine is a compare ladder over the category with
jump tables over the position that returns constants.

`_getAchievementSheetDataTitle` and `_getAchievementSheetDataItem` map the id
through the switches `0x0070F910` and `0x007101E0`, look the result up in the maps
at `0x0134B578` and `0x0134B584` through `0x006E72B0` and `0x006E7310` and push the
dword at node `+0x10`. A key that is not found answers 0. Both switches answer 0
for an id that they do not list. The contents of the switches and maps are client
data and were not decoded here.

## Cut scene natives

`_loadCutScene` (`0x006DC550`) is registered at order 2 of the `CutScene`
switchboard with empty lists. Its callback is the single instruction `ret 4`.
`gamedata/cutscene_u` defines `_loadCutScene` as a plain function that returns at
once, and `gamedata/cutscene_common` calls it with no argument (`INFERRED`).

The related rows record three natives that rank below the selection. `_skip`
sets the byte at receiver `+0xC1` and calls `0x0075B200` on the dword at `Y +0x08`.
`_play` and `_replay` declare a bool and an int as results and one `Variable`
argument. Each clears the byte at receiver `+0xC1`, stores a new object of 16 bytes
at receiver `+0x64` and requests a yield. The
[cut scene contracts](cutscene-native-contract.md) record the three natives in full,
with the resume checker and the two results.

## Script call sites

| Native | Index sites | Scripts | Direct calls | Debug console |
| --- | ---: | ---: | ---: | ---: |
| `_setTargetNearestCharacter` | 8 | 2 | 7 | 0 |
| `_updateItemPackage` | 7 | 2 | 7 | 0 |
| `_getExtendedTemporaryGroup` | 7 | 2 | 7 | 0 |
| `_setReactionTriggerBox` | 6 | 3 | 6 | 0 |
| `_transformIntoChocobo` | 4 | 1 | 4 | 0 |
| `_isDoneAchievement` | 4 | 1 | 4 | 0 |
| `_getSubStatStatus` | 3 | 1 | 3 | 0 |
| `_getLastAttacker` | 3 | 1 | 3 | 0 |
| `_loadCutScene` | 2 | 2 | 1 | 0 |
| `_getSystemFlag` | 2 | 1 | 2 | 0 |
| `_getAchievementSheetDataTitle` | 2 | 1 | 2 | 0 |
| `_getAchievementSheetDataItem` | 2 | 1 | 2 | 0 |
| `_getAchievementRate` | 2 | 1 | 2 | 0 |
| `_getAchievementItemId` | 2 | 1 | 2 | 0 |

The first three columns are `MEASURED` against the call-site index and total 54
sites. The direct call column is the count of method calls that the bytecode scan
resolves. The index counts the `_cpp` call of `_setTargetNearestCharacter` and the
definition key of `_loadCutScene` besides the direct calls. The last column counts
index sites in `commanddebugger` scripts.

The scan shows that every site passes the number of arguments that the registrar
of the registration that scripts reach declares (`INFERRED`). `_play` and
`_replay` pass an open argument list. `_getAchievementRate`, `_play` and `_replay`
take two results, and `_getExtendedTemporaryGroup` and `_getSubStatStatus` have
tail call sites.

## Ledger rows

These rows of the unimplemented ledger now have a registration, argument list,
return list, receiver check and callback contract: `_getAchievementItemId`,
`_getAchievementRate`, `_getAchievementSheetDataItem`,
`_getAchievementSheetDataTitle`, `_getExtendedTemporaryGroup`,
`_getLastAttacker`, `_getSubStatStatus`, `_getSystemFlag`, `_isDoneAchievement`,
`_loadCutScene`, `_setReactionTriggerBox`, `_setTargetNearestCharacter`,
`_transformIntoChocobo`, `_updateItemPackage`. A client that implements them
needs the item package request `0x0131`, the target manager behind the object at
`Y +0x04` and the SetTarget request, the group manager behind `Y +0xE4`, the
status record at `CharaBase +0xDC`, the achievement store behind `MyPlayer
+0x114` with the three sheet maps and the request `0x0135`. `_loadCutScene` and
the `CharaBase` registration of `_transformIntoChocobo` are empty callbacks.

## Next natives

The next natives follow the ranking above by the call sites outside the debug
console, the total index sites and the distinct scripts. Every row after `_skip`
has one site, one script and one index site, so those rows are listed
alphabetically by native name. They carry no class or switchboard order and the
list is a candidate pool, not a selection. The table lists the first twelve
natives that remain after the selected rows and the left out groups.

| Rank | Native | Class | Scripts | Call sites |
| ---: | --- | --- | ---: | ---: |
| 15 | `_skip` | `CutScene` | 1 | 1 |
| 16 | `_achieveTrophy` | `PlayerBase` | 1 | 1 |
| 17 | `_canGetTrophy` | `PlayerBase` | 1 | 1 |
| 18 | `_canRideChocobo` | `AreaBase` | 1 | 1 |
| 19 | `_canStoreItem` | `PlayerBase` | 1 | 1 |
| 20 | `_cancelTransformIntoChocobo` | `WorldMaster` | 1 | 1 |
| 21 | `_chat` | `PlayerBase` | 1 | 1 |
| 22 | `_clearAchievementRateCache` | `PlayerBase` | 1 | 1 |
| 23 | `_countAchievementCategory` | `PlayerBase` | 1 | 1 |
| 24 | `_countAchievementItem` | `PlayerBase` | 1 | 1 |
| 25 | `_countStoredItem` | `PlayerBase` | 1 | 1 |
| 26 | `_createExtendedTemporaryVirtualItem` | `CharaBase` | 1 | 1 |

The manifest rows under `nextTranche` carry the same order.

## Open

- The reader of the byte at `DesktopWidget +0x78`, the selection conditions inside
  `0x005655F0` and `0x00562D30` and the writer of `Y +0x134`.
- What a script receives for a nonzero slot of `_getSubStatStatus`, and the writers
  of the dword at status record `+0x14`.
- The effect of the creation mode of `0x00CD9360` on a group control.
- The reaction record layout, its consumers and the effect of its flag.
- The poll of `s_WaitForTransformIntoChocoboResumeChecker`, the meaning of the
  work key `0x1389` and of the event types 9 and `0x17`, and the effect of the
  hidden widget.
- Whether the identity 0 can be a key of the map that `0x004DE190` searches. A
  `WorldMaster` `_transformIntoChocobo` with no matching NPC dereferences a null
  chara in retail by the instructions, and the run-time effect was not run.
- The writers of the achievement bitset and of the dword vector, the contents of
  the switches and maps and the category numbers of `0x0070DC60` other than 1000
  and 1500.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes with the route of the
[binding map contracts](binding-map-native-contract.md#reproduction). The script
call shapes come from the `.le.lpb` files of an installed client, decoded by
[`tools/decode_lpb.py`](../tools/decode_lpb.py) and read with a Lua 5.1 bytecode
parser over the `SELF` and `TAILCALL` call sites. They are `INFERRED` because no
tracked artifact carries them. The function VAs for `$Addresses` are:

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Registrars | `0x00729770,0x007298C0,0x0072A1F0,0x0072A340,0x0072A490,0x007302D0,0x00730420,0x00736000,0x00736150,0x007362A0,0x00739B10,0x0073BA90,0x0073BBE0,0x007428B0,0x0074B330,0x0074B9C0,0x0074F810,0x007520C0,0x007553D0` |
| Switchboards and holders | `0x007574A0,0x00754850,0x00754C70,0x00757EA0,0x00753F90,0x007547D0,0x00726880,0x007249A0,0x0071A9C0,0x0071AA30` |
| Callbacks and thunks | `0x006DC330,0x006DC550,0x006E54E0,0x006E79D0,0x006EC5E0,0x006ECA20,0x006F11B0,0x006F23F0,0x006FA150,0x006FA330,0x006FB830,0x006FE4A0,0x007058D0,0x00705A70,0x00705DD0,0x00705E40,0x00705EB0,0x00708410,0x0071E540,0x0071E550,0x0071E5E0,0x0071E5F0,0x0071E600` |
| Target and package | `0x0075B720,0x004D7310,0x005656B0,0x005655F0,0x00562D30,0x006E5AD0,0x0075D460,0x0075EA50,0x0078BC90,0x006DD450,0x006DD4D0` |
| Group and status | `0x00701140,0x006E2240,0x00CC80A0,0x00CC8140,0x00CD9360,0x006EEC00,0x006EEA80,0x00707D60,0x00CF9D60,0x00CD7A30,0x00748B30,0x0073DDD0` |
| Reaction box | `0x00742010,0x0072D5B0,0x0072D560,0x006F02C0,0x006F0330,0x0075C800,0x0075C7D0,0x007219B0` |
| Chocobo | `0x00764150,0x007179A0,0x0075F3A0,0x00589D30,0x004D7980,0x004D73A0,0x00CC88D0,0x00CC7560,0x00CC7B90` |
| Achievement | `0x00776340,0x0070AB40,0x006B4AF0,0x0070DC60,0x0070F910,0x007101E0,0x006E72B0,0x006E7310,0x006E7370,0x006E3B20,0x0075ECD0` |
| Cut scene | `0x006E1970,0x0075B200,0x0072BCA0,0x00728AC0` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
