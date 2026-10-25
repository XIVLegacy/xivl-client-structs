# Grand Company rank, achievement, title, timer, replay quest, hamlet score, Chocobo grade and stored item native contracts

[`manifests/player_misc_native_call_contract.json`](../manifests/player_misc_native_call_contract.json)
records the static Lua call contracts of fourteen `PlayerBase` native registrations. They rank first by script use among the
unimplemented ledger rows that lie outside the command, talk, emote and push family and outside the records that already describe
their bodies. One reads a Grand Company rank (`_getGrandCompanyRank`). Six handle the achievement state, the title and the
achievement sheet (`_setAchievementTitle`, `_countEnableAchievementTitle`, `_getEnableAchievementTitle`, `_countAchievementRateList`,
`_getAchievementCategoryId`, `_getAchievementSheetDataIcon`). Three read the timer and replay state of the world object
(`_getOccupancyContentsTime`, `_getNMRushUpdateTime`, `_getCutSceneReplaySnpcSkin`). One tests a replay quest number
(`_isCompletedCutSceneReplayQuest`). One counts hamlet defense score rows (`_countHamletDefenseScore`). One reads the Chocobo grade
(`_getChocoboRidingGrade`). One reads a stored item (`_getStoredItem`). Each full row gives the registration site, the receiver type
check, the declared argument and return lists with their tag checks, the Lua pushes of every branch, the engine state that the
callback reads and writes, the messages it sends, the failure behavior and whether the call yields. The contracts describe client
marshalling and state. They do not describe achievement, title, timer, replay quest, hamlet score, Chocobo or stored item content,
or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data at the cited addresses. `MEASURED` is counted by the
method named in the fact from the call-site index of the installed client scripts. `INFERRED` is a name or role taken from the
surrounding instructions, script names or neighbouring records that the bytes do not state. `unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned by
[`manifests/retail_inputs.json`](../manifests/retail_inputs.json). The listings, the caller scan and the reproduction route are the
ones of the [binding map contracts](binding-map-native-contract.md#binary-and-method). A second pass re-read the bytes and compared
every cited instruction, operand, vftable cell and data cell with the claims below. The registrar shape, the type registry, the cell
tags and the invalid-parameter route are the ones of the [nameplate, actor and group contracts](nameplate-group-native-contract.md)
and the [work binder contracts](work-binder-native-contract.md#binary-and-method). The `PlayerBase` holders and the world object
chain are the ones of the [fade, actor and group contracts](fade-actor-group-native-contract.md#fade-natives).

The call-site and script counts agree with `xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. They show that a script
contains a call, not that a script reaches it at run time. The argument counts, the direct call counts, the return counts, the
constants and the descriptor names come from a local Lua 5.1 bytecode scan of the installed client scripts, decoded with
[`tools/decode_lpb.py`](../tools/decode_lpb.py). The script sources are not redistributed and no tracked artifact carries those values,
so they are `INFERRED`.

Two callbacks call constant switches, `0x0057CD90` and `0x007107F0`. The switch tables are not copied
here. Their results were obtained by evaluating the functions with an interpreter that executes only their compare, add, subtract,
move, zero-extend and indirect jump instructions, and the facts record the results (the twelve `0x0057CD90` constants and the `0x007107F0` counts), not the tables.

## Ranking

The ranking covers the natives that `xivl-client-scripts:lua/napi_index.json` binds to `PlayerBaseClass` and whose ledger row in
`bahamut-client:bindings/ledger.toml` is unimplemented at bahamut-client revision `dff89145cff58d31664bede866c4de7cc4ac425c`. It orders
them by the number of distinct scripts that contain a call, then by the call-site count and then by the switchboard order. A native
with a contract row, a related record or a ledger candidate entry in any manifest is left out, and so are the natives of the command,
talk, emote and push family and the natives whose body or arguments another record already describes.

| Rank | Native | Class | Scripts | Call sites | Order |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | `_getGrandCompanyRank` | `PlayerBaseClass` | 4 | 9 | 52 |
| 2 | `_getOccupancyContentsTime` | `PlayerBaseClass` | 2 | 17 | 48 |
| 3 | `_isCompletedCutSceneReplayQuest` | `PlayerBaseClass` | 2 | 14 | 80 |
| 4 | `_setAchievementTitle` | `PlayerBaseClass` | 2 | 4 | 66 |
| 5 | `_countEnableAchievementTitle` | `PlayerBaseClass` | 2 | 3 | 67 |
| 6 | `_countAchievementRateList` | `PlayerBaseClass` | 2 | 2 | 77 |
| 7 | `_countHamletDefenseScore` | `PlayerBaseClass` | 2 | 2 | 96 |
| 8 | `_getNMRushUpdateTime` | `PlayerBaseClass` | 2 | 2 | 99 |
| 9 | `_getAchievementCategoryId` | `PlayerBaseClass` | 1 | 6 | 60 |
| 10 | `_getEnableAchievementTitle` | `PlayerBaseClass` | 1 | 4 | 68 |
| 11 | `_getChocoboRidingGrade` | `PlayerBaseClass` | 1 | 3 | 55 |
| 12 | `_getAchievementSheetDataIcon` | `PlayerBaseClass` | 1 | 3 | 72 |
| 13 | `_getCutSceneReplaySnpcSkin` | `PlayerBaseClass` | 1 | 3 | 83 |
| 14 | `_getStoredItem` | `PlayerBaseClass` | 1 | 3 | 88 |

Four natives that the ranking would otherwise select are left out.

| Native | Class | Scripts | Call sites | Reason |
| --- | --- | ---: | ---: | --- |
| `_getAchievementTitle` | `PlayerBaseClass` | 3 | 4 | The ledger row is implemented. The registration and callback are recorded in relatedNatives. |
| `_isDoneAchievement` | `PlayerBaseClass` | 1 | 4 | The overall completion bitmap test is recorded in docs/achievement-rate-consumer.md, section List-step consumer. |
| `_getAchievementRate` | `PlayerBaseClass` | 1 | 2 | The cached count getter is recorded in docs/achievement-rate-consumer.md, section Supported progress-response boundary. |
| `_isDoneAchievementRateList` | `PlayerBaseClass` | 1 | 1 | The list step predicate is recorded in docs/achievement-rate-consumer.md, section List-step consumer. |

The family left to the command contracts is `_callServerOnCommand`, `_canExecuteCommand`, `_canExecuteTalk`, `_cancelCommand`, `_cancelEmote`, `_cancelPush`, `_cancelTalk`, `_countCommandPlaying`, `_doServerOnCommand`, `_executeCommand`, `_executeEmote`, `_executeTalk`, `_isCommandPlaying`, `_isPushingOut`.

## Registration

Every native is declared by a `_u` script descriptor named `<name>_inl` in `chara/player/playerbaseclass_u` whose key is `<name>_cpp`
(`INFERRED`). The order of a native is its position among the rel32 calls of the `PlayerBase` switchboard `0x00753F90`, stored at
slot 2 of the vftable `0x00FD5E04`. The listing follows the branch targets of the switchboard. The `ret 4` at `0x007547B3` is not
its end, and the switchboard holds 99 calls. Each registrar has one rel32 caller and each name literal has one referencing
instruction.

| Native | Order | Registrar | Caller | Callback | Wrapper |
| --- | ---: | --- | --- | --- | --- |
| `_getGrandCompanyRank` | 52 | `0x0074F4D0` | `0x007543DB` | `0x00706CF0` | `0x007267D0` |
| `_getOccupancyContentsTime` | 48 | `0x00729380` | `0x00754387` | `0x0071E480` | `0x007267D0` |
| `_isCompletedCutSceneReplayQuest` | 80 | `0x0072A880` | `0x00754627` | `0x0071E650` | `0x007267D0` |
| `_setAchievementTitle` | 66 | `0x007349B0` | `0x00754501` | `0x0071E570` | `0x00726720` |
| `_countEnableAchievementTitle` | 67 | `0x00734B00` | `0x00754516` | `0x0071E580` | `0x007267D0` |
| `_countAchievementRateList` | 77 | `0x0072A5E0` | `0x007545E8` | `0x0071E620` | `0x007267D0` |
| `_countHamletDefenseScore` | 96 | `0x00735AC0` | `0x00754777` | `0x0071E710` | `0x007267D0` |
| `_getNMRushUpdateTime` | 99 | `0x00735D60` | `0x007547BA` | `0x0071E740` | `0x007267D0` |
| `_getAchievementCategoryId` | 60 | `0x007294D0` | `0x00754483` | `0x0071E520` | `0x007267D0` |
| `_getEnableAchievementTitle` | 68 | `0x00729B60` | `0x0075452B` | `0x0071E590` | `0x007267D0` |
| `_getChocoboRidingGrade` | 55 | `0x00734320` | `0x0075441A` | `0x0071E4D0` | `0x007267D0` |
| `_getAchievementSheetDataIcon` | 72 | `0x0072A0A0` | `0x0075457F` | `0x0071E5D0` | `0x007267D0` |
| `_getCutSceneReplaySnpcSkin` | 83 | `0x00735190` | `0x00754666` | `0x0071E680` | `0x007267D0` |
| `_getStoredItem` | 88 | `0x0072AC70` | `0x007546CF` | `0x0071E6D0` | `0x007267D0` |

The wrappers construct the `PlayerBase` holders. `0x007267D0` makes the const holder with the vftable `0x00FD6028` and
`0x00726720` makes the non-const holder with the vftable `0x00FD601C`. Only `_setAchievementTitle` uses the non-const holder. Both
share the invoke routine `0x0071E7D0`, which casts the receiver from `LuaControl` (`0x01270B4C`) to `PlayerBase` (`0x012BFA48`)
through `0x009DA6CC` and returns without calling the callback when the cast gives a null pointer (`STATIC`).

The list builders are `0x00728C20` for an int, `0x0072B440` for none, `0x00728B70` for a bool and `0x00583CE0` for two ints. The
int reader is `0x005819A0` for the cell tag 0. The return pushers are `0x00584F70` for an int, `0x00748870` for a bool with the cell
tag 2 and `0x00748920` for nil with the cell tag 6. Each pusher appends its cell to the vector at `ExecuteParameters +0x1C`. A
callback that calls no pusher returns no value to Lua.

Thirteen callbacks are thunks that load the receiver vftable and jump through one of its cells. The `PlayerBase` vftable cell of
each holds `0x00776340`, a bare `ret 4`. A `PlayerBase` that is not a `MyPlayer` therefore pushes nothing and the Lua call returns
no value. The RTTI names of the Lua control vftables show `PlayerBase` and `MyPlayer` as the only classes below the holder cast
(`STATIC`). `_getGrandCompanyRank` is a direct member function, so both classes answer it.

| Native | Offset | `PlayerBase` cell | `MyPlayer` cell | `MyPlayer` routine |
| --- | --- | --- | --- | --- |
| `_getOccupancyContentsTime` | `0x160` | `0x00FD5F64` | `0x00FD79BC` | `0x00705450` |
| `_isCompletedCutSceneReplayQuest` | `0x1D4` | `0x00FD5FD8` | `0x00FD7A30` | `0x00706370` |
| `_setAchievementTitle` | `0x19C` | `0x00FD5FA0` | `0x00FD79F8` | `0x006E6360` |
| `_countEnableAchievementTitle` | `0x1A0` | `0x00FD5FA4` | `0x00FD79FC` | `0x00705B30` |
| `_countAchievementRateList` | `0x1C8` | `0x00FD5FCC` | `0x00FD7A24` | `0x00706100` |
| `_countHamletDefenseScore` | `0x204` | `0x00FD6008` | `0x00FD7A60` | `0x00706800` |
| `_getNMRushUpdateTime` | `0x210` | `0x00FD6014` | `0x00FD7A6C` | `0x00706A00` |
| `_getAchievementCategoryId` | `0x188` | `0x00FD5F8C` | `0x00FD79E4` | `0x007057D0` |
| `_getEnableAchievementTitle` | `0x1A4` | `0x00FD5FA8` | `0x00FD7A00` | `0x00705B60` |
| `_getChocoboRidingGrade` | `0x174` | `0x00FD5F78` | `0x00FD79D0` | `0x007055E0` |
| `_getAchievementSheetDataIcon` | `0x1B4` | `0x00FD5FB8` | `0x00FD7A10` | `0x00705D70` |
| `_getCutSceneReplaySnpcSkin` | `0x1E0` | `0x00FD5FE4` | `0x00FD7A3C` | `0x00706450` |
| `_getStoredItem` | `0x1F4` | `0x00FD5FF8` | `0x00FD7A50` | `0x00706620` |

## Receivers and state objects

The thunk routines reach the client object chain of the earlier contracts. `R` is the address that `0x00CC7510` returns for
`ExecuteParameters +0x04`. `X` is the dword at `R` and `Y` is the dword at `X +0x04`.

### Object S

Four routines read the object `S`, the dword at `Y +0x10C`, with no null test. It holds timers and replay state.

| Offset | Content | Readers | Writers |
| --- | --- | --- | --- |
| `+0x04`, `+0x08` | Begin and end of a dword vector | `0x0075F420` | `0x0075F3E0` |
| `+0x10`, `+0x14`, `+0x18`, `+0x1C` | Four scalar timers | `0x0075D220`, `0x0075D240`, `0x0075D260`, `0x0075D280` | `0x0075D210`, `0x0075D230`, `0x0075D250`, `0x0075D270` |
| `+0x20`, `+0x24` | Set of ints and its head node | `0x00764F90` | `0x00767370` |
| `+0x80`, `+0x82`, `+0x83` | A word and two bytes | `0x0075D2A0`, `0x0075D2B0`, `0x0075D2C0` | `0x00767370` |

`0x00578C90` is the writer of the timers. It switches on its first argument. The ids `0x00` to `0x0F` store into the vector with the
id as index, the ids `0x10`, `0x11` and `0x12` store the scalars `+0x10`, `+0x14` and `+0x18`, and the id `0x16` stores `+0x1C`,
through the jump table at `0x00578FDC`. The value is 0 when the second argument is -1 and the sum of the second and third
arguments otherwise. The caller is `0x004DD37D`. `xivl-opcodes:opcodes.json` records the clientbound `0x0193` record for this routine
with the sixteen entry vector and the scalar readers. `0x00767370` rebuilds the set and the three replay bytes from a record, and its
caller chain is the dispatcher case at `0x004DD397` and `0x00576140`. `xivl-opcodes:opcodes.json` lists the clientbound `0x01A3`
record with the same anchor `FUN_00576140`. The class of `S` and its allocation were not traced.

### Object A

Two routines read the object `A`, the dword at `MyPlayer +0x114`, with no null test. The `MyPlayer` constructor `0x006F9140` zeroes
the pointer at `0x006F91BB`. The `MyPlayer` slot 30 override `0x006F3420` allocates `0xAC` bytes at `0x006F359D`, constructs them with
`0x006F2F60` and stores the pointer at `0x006F35F3`, destroying a previous object through `0x006F1030`. The constructor zeroes
the dwords `+0x04` to `+0x7C` and builds a dword vector at `+0x80`, a set of ints at `+0x90` with its element count at `+0x98`, a
map at `+0x9C` and a dword at `+0xA8`. The map at `+0x9C` and the overall bitmap belong to the
[achievement rate record](achievement-rate-consumer.md).

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_getGrandCompanyRank` | `PlayerBase` | `int` | `int` or nothing | no |
| `_getOccupancyContentsTime` | `PlayerBase` | `int` | `int` or nothing | no |
| `_isCompletedCutSceneReplayQuest` | `PlayerBase` | `int` | `bool` or nothing | no |
| `_setAchievementTitle` | `PlayerBase` | `int` | none | no |
| `_countEnableAchievementTitle` | `PlayerBase` | none | `int` or nothing | no |
| `_countAchievementRateList` | `PlayerBase` | `int` | `int` or nothing | no |
| `_countHamletDefenseScore` | `PlayerBase` | none | `int`, nil or nothing | no |
| `_getNMRushUpdateTime` | `PlayerBase` | none | `int` or nothing | no |
| `_getAchievementCategoryId` | `PlayerBase` | `int` | `int` or nothing | no |
| `_getEnableAchievementTitle` | `PlayerBase` | `int` | `int` or nothing | no |
| `_getChocoboRidingGrade` | `PlayerBase` | none | `int`, nil or nothing | no |
| `_getAchievementSheetDataIcon` | `PlayerBase` | `int` | `int` or nothing | no |
| `_getCutSceneReplaySnpcSkin` | `PlayerBase` | none | `int` or nothing | no |
| `_getStoredItem` | `PlayerBase` | `int`, `int` | `int` or nothing | no |

Every callback requests no yield. Every int reader that finds a mismatched tag reaches `0x00CCA730`. Every read follows a cell
vector size test that calls `0x009D22B4` on failure, the invalid-parameter route of the
[target cursor record](target-cursor-native-contract.md#selection-and-the-failure-path).

## Grand Company rank

`_getGrandCompanyRank` (`0x00706CF0`) reads an int through `0x005819A0`. The value 1 pushes the sign extended byte at receiver
`+0xEE`, the value 2 pushes the byte at `+0xEF` and the value 3 pushes the byte at `+0xF0`, each through `0x00584F70`. Any other int
pushes nothing. The `PlayerBase` constructor `0x006ED720` zeroes the bytes `+0xED` to `+0xF1`. The routines at the vftable offset
`+0xA4` take five stack arguments, ignore the first, and store arguments 2 to 5 as bytes at `+0xED`, `+0xEE`, `+0xEF` and `+0xF0`. They are `0x006DEB00` for
`PlayerBase` (cell `0x00FD5EA8`) and `0x006E2DE0` for `MyPlayer` (cell `0x00FD7900`). Two callers pass them four bytes after a pass-through first argument. The call at
`0x00758B3A` in `0x00758B10` passes the record bytes `+0xC2` to `+0xC5`, and `0x006F0220`, the `PlayerBase` override of vftable slot 30,
calls `0x00758B10` at `0x006F0269`. The receiver routine `0x0089CD60` is slot 1 of the vftable `0x01057318`, whose RTTI name is
`GrandCompanyReceiver`. It casts to `PlayerBase`, reads its bytes `+4` to `+7` and calls the same offset. `manifests/data_dependency_catalog.json`
lists it for the clientbound `0x0194` record. That `+0xED` is the Grand Company number of `_getBelongGrandCompany` and the other three
bytes are the ranks of the three companies is `INFERRED` from the native names and the argument range.

## Achievement state and title

`_countEnableAchievementTitle` (`0x00705B30`) pushes the dword at `A +0x98`, the element count of the set at `A +0x90`.
`_getEnableAchievementTitle` (`0x00705B60`) reads an int, adds -1 and calls `0x006E14C0` on `A`. That routine forms an iterator on the
set at `A +0x90` whose node is the leftmost node, steps it forward through `0x00420630` or backward through `0x00580D70`, tests that
the node is not the head node and returns the dword at node `+0x0C`. A step off the set and the end node reach `0x009D22B4`. The
result for a position of 0 or less was read as a backward step from the first node and was not traced. The method `0x006EDEE0` on `A`
fills the set. It sets the bit of an achievement number in the bitmap at `A +0x00`, shifts the eight entry vector at `A +0x84` and
stores the number first when `0x0057CE20` accepts it, and inserts the value that `0x006E72B0` returns for the number into the set
at `0x006EDFDB` when `0x0070F580` accepts it. `0x00704430` calls it at `0x0070446C`, and slot 1 `0x0089C6D0` of the vftable
`0x010572C4`, whose RTTI name is `AchievementIdReceiver`, jumps to `0x00704430`. A second insert at `0x006EDE4B` belongs to a bit
vector loop whose function entry was not identified. That the keys are the title numbers of earned achievements is `INFERRED`.

`_getAchievementCategoryId` (`0x007057D0`) reads an int, subtracts 1 and calls the switch `0x0057CD90`, which compares its
argument with `0xB` unsigned and jumps through the table at `0x0057CDEC`. The indexes 0 to 11 return 100, 200, 400, 500, 600, 700,
900, 1000, 1200, 1300, 1400 and 1500. Every other argument returns 0. The result is pushed as an int and is never nil.

`_countAchievementRateList` (`0x00706100`) reads an int and pushes the result of the switch `0x007107F0`. The switch has four jump
tables and 82 nonzero results between `0x6C` and `0x822`, which take 13 distinct values from 1 to 25. Every other input returns 0.
That the result is the step count that the detail widget iterates follows the
[achievement rate record](achievement-rate-consumer.md#list-step-consumer) and is `INFERRED`.

`_getAchievementSheetDataIcon` (`0x00705D70`) reads an int and calls `0x006E7430`, which finds the key in the map at `0x0134B5A8`
through `0x00A44B00` and returns the dword at node `+0x10`, or 0 when the key is absent. The routine at `0x0076A9C0` loads the
sheet whose name literal is the string `achievement` at `0x00FD8618`. Its loop at `0x0076AE40..0x0076AFAE` calls `0x006F0F70` at
`0x0076AF95` with the row number and the columns 3, 5, 1, 2 and 4. `0x006F0F70` inserts the sixth argument, column 4, into the map at
`0x0134B5A8` when it is positive. The other maps are at `0x0134B578` for column 3, `0x0134B584` for column 5, `0x0134B590` for
column 1 and `0x0134B59C` for column 2. The row range, the load trigger and the column names were not traced.

`_setAchievementTitle` (`0x006E6360`) reads an int through `0x005819A0` and stores it at receiver `+0xE8` at `0x006E63BD`. The
related `_getAchievementTitle` callback `0x00706D70` pushes that dword. The slot 30 override `0x006F0220` stores the record dword
at `+0x48` there too, the constructor zeroes it, and the receiver routine `0x0089C5F0`, slot 1 of the vftable `0x010572B8` with the RTTI
name `AchievementTitleReceiver`, stores its dword `+4` there at `0x0089C611`. `manifests/data_dependency_catalog.json` lists that
receiver for the clientbound `0x019D` record. The native then copies the dwords at `Y +0x00`, `+0x10` and `+0x14` to a local
through `0x0075D460` and calls `0x0075EBA0` with the value. That routine clears a 16 byte buffer, fills its first 15 bytes
with byte i set to `'a'+i` when `rand()` modulo 52 is below 26 and `'A'+i` otherwise (a to o or A to O, the case chosen once per byte), leaves byte 15 zero, builds a checksum of the 16
bytes through `0x00D3AB60` and `0x00D3AAE0`, and builds a record of the type `0x134` and the length `0x28` at `0x0075EC73` and
`0x0075EC7B`. It submits the record through `0x004D6D30` at `0x0075EC90`. The checksum routine `0x00D3A380` is table driven with the
table at `0x01110808`, whose first entries are `0x00000000` and `0x77073096`, the standard CRC-32 table. `0x004D6D30` returns 0 when
the dword at `this +0x174EC` is null and otherwise jumps to the forwarder `0x004E0240`. `xivl-opcodes:opcodes.json` records the
serverbound `0x0134` record as `AchievementTitleRequestPacket` with the anchor `FUN_0075EBA0`. The field order inside the record
comes from that entry, which gives the title value at application `+0x00`, the checksum at `+0x04` and the 16 generated bytes at
`+0x08`. A `PlayerBase` that is not a `MyPlayer` neither stores nor sends.

## Timers and replay state

`_getOccupancyContentsTime` (`0x00705450`) reads an int, subtracts 1 into a signed byte and calls `0x0075F420` on `S`. That routine
compares the index with the element count of the vector unsigned and returns the element. A failed compare calls `0x009D22B4` and
then reads the element anyway. The scripts pass the positions 1 to 16. `_getNMRushUpdateTime` (`0x00706A00`) pushes the dword at
`S +0x1C` through `0x0075D280`. `_getCutSceneReplaySnpcSkin` (`0x00706450`) pushes the sign extended byte at `S +0x82` through
`0x0075D2B0`. `0x00767370` stores that byte from application `+6`.

`_isCompletedCutSceneReplayQuest` (`0x00706370`) reads an int and calls `0x00764F90`, which calls the set find `0x0071C9A0` on
`S +0x20`, reaches `0x009D22B4` for a null or foreign container and returns whether the iterator node differs from the head node.
The result is pushed through the bool pusher. `0x00767370` empties the set and visits 256 bytes from application `+9`. For each set
bit it inserts `0x0001ADB1` plus eight times the byte index plus the bit index, a range of `0x0001ADB1` to `0x0001B5B0`. It also
inserts fixed numbers for the flag bits of the dword at application `+0`, `0x00A91911` to `0x00A91917`, and of the byte at
application `+8`, `0x0001B0E5` to `0x0001B0E8` and `0x00A91918` to `0x00A9191D`. The scripts pass the constants `110019` to `111827`.

## Hamlet defense score

`_countHamletDefenseScore` (`0x00706800`) loads the pointer at `MyPlayer +0x154`. A null pointer pushes nil through `0x00748920`.
Otherwise it pushes the distance between the dwords at object `+0x08` and `+0x04` divided by 12, the division being a
multiplication by `0x2AAAAAAB` at `0x00706836`, or 0 when the dword at `+0x04` is null. The object is the score object of the
[hamlet record](hamlet-wire-contract.md). `0x006F2210` allocates it with 0x1C bytes and its row getter `0x00706870` indexes the same
vector with 12 byte rows. The `MyPlayer` constructor zeroes the pointer at `0x006F9285`.

## Chocobo grade

`_getChocoboRidingGrade` (`0x007055E0`) tests the byte at `MyPlayer +0x15D`. A nonzero byte is zero extended and pushed as an int.
When it is 0 the routine compares the byte at `+0x15F` with 1. Equal pushes the int `0x101` and any other value pushes nil. The
writers are `0x006DE370`, which stores its second argument (the first is unread) at `+0x15D` and 0 at `+0x15F`, and `0x006DE3C0`, which stores 0 at `+0x15D`
and its second argument (the first is unread) at `+0x15F`. The `PlayerBase` record apply `0x00758AA0` calls them in that order at `0x00758AC2` and `0x00758AD2` with
the record bytes `+0xC0` and `+0xC1`, so after the apply `+0x15D` is 0 and `+0x15F` holds the record byte `+0xC1`. The `MyPlayer`
slot 30 override calls `0x00758AA0` at `0x006F347F`. The routine `0x008A2F30` is slot 1 of the vftable `0x01057598`, whose RTTI name is
`ChocoboReceiver`, and calls `0x006DE370` at `0x008A2F63`. The routine `0x008A3100` is slot 1 of the vftable `0x010575B0`, whose RTTI
name is `GoobbueReceiver`, and reaches `0x006DE3C0` through the jump at `0x008A3129`. `manifests/data_dependency_catalog.json` lists
them for the clientbound `0x0198` and `0x01A0` records under `MyPlayer +0x15D` and `+0x15F`. That `+0x15D` is the Chocobo grade and
`+0x15F` is the Goobbue flag is `INFERRED` from the native name and the receiver names. The meaning of `0x101` was not established.

## Stored items

`_getStoredItem` (`0x00706620`) reads two ints through `0x005819A0` and requires at least two cells. It subtracts 1 from each,
indexes the array of 16 byte records between `MyPlayer +0x148` and `+0x14C` with the first, takes the dword vector of that record at
`+0x04` and `+0x08` and pushes the dword at the second index. Each index is compared unsigned against its container size and a
failure reaches `0x009D22B4`. The `MyPlayer` constructor builds the array with four records through `0x0072DEB0` at `0x006F924E`,
each an empty dword vector. The writer is the `MyPlayer` method `0x006EFBD0`. It empties each list, calls `0x007222D0` with `0x23`,
`0x41`, `0x1A` and `4` for the lists 0 to 3, then walks the bits of a byte vector argument. For each set bit it maps the bit index
through `0x00714E40`, a jump table with 130 nonzero results for the indexes 0 to `0x99`, maps the constant to a list number from 0 to 3
through `0x007153D0`, and appends the constant to that list. It calls `0x00720BB0`, a hybrid sort with a threshold of 32 elements,
on each list range at `0x006EFE3A`. The sort direction was not traced. Slot 1 `0x0089CB90` of the vftable `0x01057470`, whose RTTI
name is `EntrustItemReceiver`, casts to `MyPlayer` and calls `0x006EFBD0` at `0x0089CBB4`. `xivl-opcodes:opcodes.json` lists the
clientbound `0x01A5` record as `SetPlayerItemStoragePacket` with `alt_name=EntrustItem` and a `retail_class_name` field ending in `EntrustItemReceiver`.

## Script call sites

| Native | Index sites | Scripts | Direct calls |
| --- | ---: | ---: | ---: |
| `_getGrandCompanyRank` | 9 | 4 | 9 |
| `_getOccupancyContentsTime` | 17 | 2 | 17 |
| `_isCompletedCutSceneReplayQuest` | 14 | 2 | 14 |
| `_setAchievementTitle` | 4 | 2 | 4 |
| `_countEnableAchievementTitle` | 3 | 2 | 3 |
| `_countAchievementRateList` | 2 | 2 | 2 |
| `_countHamletDefenseScore` | 2 | 2 | 2 |
| `_getNMRushUpdateTime` | 2 | 2 | 2 |
| `_getAchievementCategoryId` | 6 | 1 | 6 |
| `_getEnableAchievementTitle` | 4 | 1 | 4 |
| `_getChocoboRidingGrade` | 3 | 1 | 3 |
| `_getAchievementSheetDataIcon` | 3 | 1 | 3 |
| `_getCutSceneReplaySnpcSkin` | 3 | 1 | 3 |
| `_getStoredItem` | 3 | 1 | 3 |

The first three columns are `MEASURED` against the call-site index and total 75 sites. The direct call column is the count of method
calls that the bytecode scan resolves (`INFERRED`), and it equals the index count for every native.

The scan also shows these call shapes (`INFERRED`). `widget/pcmatchingeditwidget` holds 16 of the 17 `_getOccupancyContentsTime`
calls and passes the constants 1 to 16. `quest/questbaseclass` holds 12 of the 14 `_isCompletedCutSceneReplayQuest` calls, which pass
the constants `110019`, `110480`, `111406`, `111427`, `111606`, `111627`, `111806` and `111827`, and all 3 `_getCutSceneReplaySnpcSkin`
calls. All 9 `_getGrandCompanyRank` calls pass one computed argument. `judge/chocobojudge` holds all 3 `_getChocoboRidingGrade`
calls. `widget/achievementlistwidget` holds all 6 `_getAchievementCategoryId` calls and all 3 `_getAchievementSheetDataIcon` calls.
`widget/achievementtitlelistwidget` holds all 4 `_getEnableAchievementTitle` calls and 2 of the 4 `_setAchievementTitle` calls, one of
which passes the constant 0. `widget/ask/itemstoragegetwidget` holds all 3 `_getStoredItem` calls with two computed arguments.
The `_getAchievementTitle` callback ignores a declared int argument and the scripts pass none.

## Ledger rows

These rows of the unimplemented ledger now have a registration, argument list, return list, receiver check and callback contract:
`_getGrandCompanyRank`, `_getOccupancyContentsTime`, `_isCompletedCutSceneReplayQuest`, `_setAchievementTitle`, `_countEnableAchievementTitle`, `_countAchievementRateList`, `_countHamletDefenseScore`, `_getNMRushUpdateTime`, `_getAchievementCategoryId`, `_getEnableAchievementTitle`, `_getChocoboRidingGrade`, `_getAchievementSheetDataIcon`, `_getCutSceneReplaySnpcSkin`, `_getStoredItem`.
A client that implements them needs the distinct `MyPlayer` and `PlayerBase` behavior, the objects `S` and `A`, the hamlet score
object at `+0x154`, the stored item lists at `+0x148`, the Grand Company bytes at `+0xEE` to `+0xF0`, the Chocobo bytes at `+0x15D` and
`+0x15F`, and the achievement sheet maps. The values come from the server records `0x0193`, `0x01A3` and the player record, and
from the installed sheets.

## Not traced

- The class and allocation of `S`, the size of its timer vector and any writer of `S` other than `0x00578C90` and `0x00767370`.
- The application offsets of the fields of the Grand Company, Chocobo and Goobbue receivers and the wire fields behind the record
  bytes `+0xC0` to `+0xC5`.
- The bit vector loop that also inserts into the title set, the predicates `0x0070F580` and `0x0057CE20`, and the result of a backward
  step from the first node of the set.
- The row range and load trigger of the achievement sheet loop and the column names.
- The sort direction of `0x00720BB0` and the meaning of the constants of `0x00714E40`.
- The run-time effect of a null `A`, `S` or hamlet score object.
- The server handling of the record `0x0134` and the accepted title values.
- The meaning of the Chocobo value `0x101`, the flag bits of the cut scene book record and the fixed numbers it inserts.

## Next natives

The next natives follow the ranking above. The table lists the natives that remain after the selected rows and the left out records.
The registration and the `MyPlayer` routine of the first three are recorded in `relatedNatives`.

| Rank | Native | Class | Scripts | Call sites | Why |
| ---: | --- | --- | ---: | ---: | --- |
| 15 | `_getAchievementItemId` | `PlayerBaseClass` | 1 | 2 | Order 62 of the PlayerBase switchboard. The registration and the MyPlayer routine are recorded in relatedNatives. |
| 16 | `_getAchievementSheetDataTitle` | `PlayerBaseClass` | 1 | 2 | Order 73 of the PlayerBase switchboard. The registration and the MyPlayer routine are recorded in relatedNatives. |
| 17 | `_getAchievementSheetDataItem` | `PlayerBaseClass` | 1 | 2 | Order 74 of the PlayerBase switchboard. The registration and the MyPlayer routine are recorded in relatedNatives. |
| 18 | `_canGetTrophy` | `PlayerBaseClass` | 1 | 1 | Order 44 of the PlayerBase switchboard. |
| 19 | `_isAchievedTrophy` | `PlayerBaseClass` | 1 | 1 | Order 45 of the PlayerBase switchboard. |
| 20 | `_achieveTrophy` | `PlayerBaseClass` | 1 | 1 | Order 46 of the PlayerBase switchboard. |
| 21 | `_turn` | `PlayerBaseClass` | 1 | 1 | Order 47 of the PlayerBase switchboard. |
| 22 | `_getNormalBehestTime` | `PlayerBaseClass` | 1 | 1 | Order 49 of the PlayerBase switchboard. |
| 23 | `_getCompanyBehestTime` | `PlayerBaseClass` | 1 | 1 | Order 50 of the PlayerBase switchboard. |
| 24 | `_getWarpRecastTime` | `PlayerBaseClass` | 1 | 1 | Order 53 of the PlayerBase switchboard. |

The manifest rows under `nextTranche` carry the same order.

## Reproduction

Authenticate the program with [`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using the procedure in
[`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava). Then decode listings from the verified PE bytes with the route of
the [binding map contracts](binding-map-native-contract.md#reproduction). The argument counts, the constants and the descriptor names
come from the `.le.lpb` files of an installed client, decoded by [`tools/decode_lpb.py`](../tools/decode_lpb.py) and read with a Lua 5.1
bytecode parser over the `SELF` call sites. They are `INFERRED` because no tracked artifact carries them. The function VAs for
`$Addresses` are:

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Registrars | `0x0074F4D0,0x00729380,0x0072A880,0x007349B0,0x00734B00,0x0072A5E0,0x00735AC0,0x00735D60,0x007294D0,0x00729B60,0x00734320,0x0072A0A0,0x00735190,0x0072AC70` |
| Switchboard and holders | `0x00753F90,0x007267D0,0x00726720,0x007248D0,0x00724800,0x0071E880,0x0071E760,0x0071E7D0` |
| Callbacks | `0x00706CF0,0x0071E480,0x0071E650,0x0071E570,0x0071E580,0x0071E620,0x0071E710,0x0071E740,0x0071E520,0x0071E590,0x0071E4D0,0x0071E5D0,0x0071E680,0x0071E6D0` |
| `MyPlayer` routines | `0x00705450,0x00706370,0x006E6360,0x00705B30,0x00706100,0x00706800,0x00706A00,0x007057D0,0x00705B60,0x007055E0,0x00705D70,0x00706450,0x00706620,0x00706CF0` |
| List builders and pushers | `0x00728C20,0x0072B440,0x00728B70,0x00583CE0,0x005819A0,0x00584F70,0x00748870,0x00748920,0x00584EE0` |
| Object S | `0x0075F420,0x0075F3E0,0x00764F90,0x0071C9A0,0x0075D280,0x0075D270,0x0075D2B0,0x00578C90,0x00767370,0x00576140` |
| Object A and title set | `0x006F3420,0x006F2F60,0x006F1030,0x006E14C0,0x00420630,0x00580D70,0x006F9140,0x006EDEE0,0x00704430,0x0089C6D0,0x0089C5F0` |
| Grand Company bytes | `0x006ED720,0x006DEB00,0x006E2DE0,0x00758B10,0x006F0220,0x0089CD60` |
| Title record | `0x0075D460,0x0075EBA0,0x004D6D30,0x00D3AB60,0x00D3AAE0,0x00D3A380` |
| Switches and sheet maps | `0x0057CD90,0x007107F0,0x006E7430,0x00A44B00,0x006F0F70,0x0076A9C0,0x007101E0,0x0070F910` |
| Hamlet, Chocobo and stored item | `0x006F2210,0x00706870,0x006DE370,0x006DE3C0,0x00758AA0,0x008A2F30,0x008A3100,0x0072DEB0,0x006EFBD0,0x0089CB90,0x00714E40,0x007153D0,0x00720BB0,0x007222D0` |

A callback address may not be a function entry in the analyzed program. Read such a callback as an instruction listing from its
address. Compare every store, compare and call with the address named in the manifest facts. No decompiled body or ignored export
is a tracked evidence dependency.
