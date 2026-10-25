# Trophy, achievement list, turn, chat, enmity, group, trading item, map object scale and Chocobo cancel native contracts

[`manifests/trophy_group_native_call_contract.json`](../manifests/trophy_group_native_call_contract.json)
records the static Lua call contracts of 22 natives, which are 23 registrations, on `PlayerBase`, `CharaBase`,
`DirectorBase`, `NpcBase`, `WorldMaster` and `GroupBase`. Three are the trophy natives (`_canGetTrophy`,
`_isAchievedTrophy`, `_achieveTrophy`). Seven read or reset the achievement state (`_countAchievementCategory`,
`_countAchievementItem`, `_getAchievementPoint`, `_getAchievementSheetDataPoint`, `_clearAchievementRateCache`,
`_getAchievementRateList`, `_isDoneAchievementRateList`). Three belong to the local player (`_turn`, `_chat`,
`_haveEnmityCharacters`). Four look up groups (`_getGroupCurrent`, `_getExtendedTemporaryGroupCurrent` and the two
registrations of `_getGroupByDisplayName`). Two build items (`_getTradingItem`, `_createExtendedTemporaryVirtualItem`).
One reads a status bit (`_getGrandOnExtraStat`). The last three are `_updateMemberAndInformation`,
`_setMapObjScale` and `_cancelTransformIntoChocobo`. Each row gives the registration site, the receiver type check, the
declared argument and return lists, the Lua pushes of every branch, the client state that the callback reads or writes,
the messages it sends, failure behavior and whether the call yields. The contracts describe client marshalling and
state. They do not describe achievement, group, item, chat or scene content, or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data at the cited addresses. `MEASURED` is
counted from the call-site index of the installed client scripts. `INFERRED` is a role taken from the surrounding
instructions or scripts that the bytes do not state. `unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned by
[`manifests/retail_inputs.json`](../manifests/retail_inputs.json). The registrar shape, the type registry, the cell tags
and the invalid-parameter route are the ones of the [nameplate, actor and group contracts](nameplate-group-native-contract.md)
and the [work binder contracts](work-binder-native-contract.md#binary-and-method). The `PlayerBase` holders and the thunk
dispatch are the ones of the [player contracts](player-misc-native-contract.md#registration). The world object chain is the
one of the [fade, actor and group contracts](fade-actor-group-native-contract.md#fade-natives).

A script decoded each registrar, callback, vftable cell and string literal from the executable bytes and asserted the
addresses. Callers, stores and loads come from a linear decode of the `.text` section, so virtual and indirect references
are not covered. The results of the constant switches `0x0057ED40`, `0x0070DBB0`, `0x00710490`, `0x007107F0` and
`0x00710BB0` were obtained by evaluating the functions with an interpreter that executes only compare, add, subtract,
negate, subtract with borrow, and, move, zero extend and jump instructions. The facts record counts and shapes. The
switch tables are not copied here.

The call-site and script counts agree with `xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. They show that a
script contains a call, not that a script reaches it at run time. The argument counts, the result counts and the
descriptor constants come from a local Lua 5.1 bytecode scan of the installed client scripts, decoded with
[`tools/decode_lpb.py`](../tools/decode_lpb.py). The script sources are not redistributed and no tracked artifact carries
those values, so they are `INFERRED`.

## Ranking

The ranking covers the natives that `xivl-client-scripts:lua/napi_index.json` binds to a class and whose ledger row in
`bahamut-client:bindings/ledger.toml` at revision `f6e50df28ebcfe7f542a05c23756dac08e26b20b` is unimplemented. It orders
them by the call sites outside the commanddebugger scripts, then by the total index call sites, then by the number of
distinct scripts outside the debug console, then by the class order (`CharaBase`, `NpcBase`, `WorldMaster`, `PlayerBase`, `GroupBase`, `WidgetBase`, `DirectorBase`) and then by the switchboard order. The rank is the
rank among the 28 natives of this record and of the
[widget list and focus record](widget-list-focus-native-contract.md). `_getAllItem`, the 29th unimplemented row, has its
contract in the [debug console record](debug-console-native-contract.md). The script callbacks that begin with `_on` and
the host intrinsics are not natives and are left out.

| Rank | Native | Class | Scripts | Call sites | Index sites | Order |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | `_getGrandOnExtraStat` | `CharaBase` | 1 | 1 | 1 | 18 |
| 6 | `_getExtendedTemporaryGroupCurrent` | `CharaBase` | 1 | 1 | 1 | 49 |
| 7 | `_getTradingItem` | `CharaBase` | 1 | 1 | 1 | 74 |
| 8 | `_createExtendedTemporaryVirtualItem` | `CharaBase` | 1 | 1 | 1 | 77 |
| 9 | `_setMapObjScale` | `NpcBase` | 1 | 1 | 1 | 16 |
| 10 | `_cancelTransformIntoChocobo` | `WorldMaster` | 1 | 1 | 1 | 20 |
| 11 | `_chat` | `PlayerBase` | 1 | 1 | 1 | 26 |
| 12 | `_canGetTrophy` | `PlayerBase` | 1 | 1 | 1 | 44 |
| 13 | `_isAchievedTrophy` | `PlayerBase` | 1 | 1 | 1 | 45 |
| 14 | `_achieveTrophy` | `PlayerBase` | 1 | 1 | 1 | 46 |
| 15 | `_turn` | `PlayerBase` | 1 | 1 | 1 | 47 |
| 16 | `_haveEnmityCharacters` | `PlayerBase` | 1 | 1 | 1 | 58 |
| 17 | `_countAchievementCategory` | `PlayerBase` | 1 | 1 | 1 | 59 |
| 18 | `_countAchievementItem` | `PlayerBase` | 1 | 1 | 1 | 61 |
| 19 | `_getAchievementPoint` | `PlayerBase` | 1 | 1 | 1 | 64 |
| 20 | `_getAchievementSheetDataPoint` | `PlayerBase` | 1 | 1 | 1 | 71 |
| 21 | `_clearAchievementRateCache` | `PlayerBase` | 1 | 1 | 1 | 76 |
| 22 | `_getAchievementRateList` | `PlayerBase` | 1 | 1 | 1 | 78 |
| 23 | `_isDoneAchievementRateList` | `PlayerBase` | 1 | 1 | 1 | 79 |
| 24 | `_updateMemberAndInformation` | `GroupBase` | 1 | 1 | 1 | 16 |
| 27 | `_getGroupCurrent` | `CharaBase` | 0 | 0 | 2 | 48 |
| 28 | `_getGroupByDisplayName` | `CharaBase and DirectorBase` | 0 | 0 | 1 | 46 and 3 |

## Registration

Every native is declared by a `_u` script descriptor named `<name>_inl` whose key is `<name>_cpp`. The scripts that
bind the natives contain both strings (`MEASURED`). That the descriptor declares the native follows the
[binding map contract](binding-map-native-contract.md) and is `INFERRED`. The order of a native is its position among the
rel32 calls of its switchboard. Each registrar has one rel32 caller and each name literal has one referencing instruction.

| Native | Class | Order | Registrar | Caller | Callback | Wrapper |
| --- | --- | --- | --- | --- | --- | --- |
| `_canGetTrophy` | `PlayerBase` | 44 | `0x007339F0` | `0x00754333` | `0x0071E450` | `0x007267D0` |
| `_isAchievedTrophy` | `PlayerBase` | 45 | `0x00729230` | `0x00754348` | `0x0071E460` | `0x007267D0` |
| `_achieveTrophy` | `PlayerBase` | 46 | `0x00733B40` | `0x0075435D` | `0x0071E470` | `0x007267D0` |
| `_turn` | `PlayerBase` | 47 | `0x00733C90` | `0x00754372` | `0x0071E440` | `0x007267D0` |
| `_chat` | `PlayerBase` | 26 | `0x00743D80` | `0x007541B9` | `0x006DE7D0` | `0x007267D0` |
| `_haveEnmityCharacters` | `PlayerBase` | 58 | `0x00734710` | `0x00754459` | `0x0071E500` | `0x007267D0` |
| `_countAchievementCategory` | `PlayerBase` | 59 | `0x00734860` | `0x0075446E` | `0x0071E510` | `0x007267D0` |
| `_countAchievementItem` | `PlayerBase` | 61 | `0x00729620` | `0x00754498` | `0x0071E530` | `0x007267D0` |
| `_getAchievementPoint` | `PlayerBase` | 64 | `0x00729A10` | `0x007544D7` | `0x0071E560` | `0x007267D0` |
| `_getAchievementSheetDataPoint` | `PlayerBase` | 71 | `0x00729F50` | `0x0075456A` | `0x0071E5C0` | `0x007267D0` |
| `_clearAchievementRateCache` | `PlayerBase` | 76 | `0x00734C50` | `0x007545D3` | `0x0071E610` | `0x007267D0` |
| `_getAchievementRateList` | `PlayerBase` | 78 | `0x00734DA0` | `0x007545FD` | `0x0071E630` | `0x007267D0` |
| `_isDoneAchievementRateList` | `PlayerBase` | 79 | `0x0072A730` | `0x00754612` | `0x0071E640` | `0x007267D0` |
| `_getGroupCurrent` | `CharaBase` | 48 | `0x0072F310` | `0x00757897` | `0x0071DFE0` | `0x00726460` |
| `_getExtendedTemporaryGroupCurrent` | `CharaBase` | 49 | `0x0072F460` | `0x007578AC` | `0x0071E000` | `0x00726460` |
| `_getGrandOnExtraStat` | `CharaBase` | 18 | `0x0074B5D0` | `0x00757621` | `0x006FA220` | `0x00726510` |
| `_createExtendedTemporaryVirtualItem` | `CharaBase` | 77 | `0x00756A20` | `0x00757AF8` | `0x00708F00` | `0x00726510` |
| `_getTradingItem` | `CharaBase` | 74 | `0x00756630` | `0x00757AB9` | `0x00708D20` | `0x00726510` |
| `_getGroupByDisplayName` | `CharaBase` | 46 | `0x007557C0` | `0x0075786D` | `0x00708470` | `0x00726460` |
| `_getGroupByDisplayName` | `DirectorBase` | 3 | `0x007570B0` | `0x007582A6` | `0x00709600` | `0x00726D50` |
| `_updateMemberAndInformation` | `GroupBase` | 16 | `0x007306C0` | `0x00757CCB` | `0x006E2130` | `0x007265C0` |
| `_setMapObjScale` | `NpcBase` | 16 | `0x0073F710` | `0x007549A7` | `0x006E66A0` | `0x0072D4B0` |
| `_cancelTransformIntoChocobo` | `WorldMaster` | 20 | `0x0073BBE0` | `0x00754E1B` | `0x006ECA20` | `0x00726CA0` |

The wrappers construct the holders. `0x007267D0` is the const `PlayerBase` holder with the vftable `0x00FD6028`.
`0x00726510` and `0x00726460` are the non-const and const `CharaBase` holders. `0x00726D50` is the const `DirectorBase`
holder, `0x007265C0` the const `GroupBase` holder, `0x0072D4B0` the non-const `NpcBase` holder and `0x00726CA0` the const
`WorldMaster` holder. The invoke routine of each casts the receiver from `LuaControl` (`0x01270B4C`) to the target type
through `0x009DA6CC` and returns without calling the callback for a null cast (`STATIC`).

The list builders are `0x0072B440` for none, `0x00728C20` for an int, `0x00728B70` for a bool, `0x0072C260` for a control,
`0x00583CE0` for two ints, `0x0072B660` for three ints, `0x0073CE40` for three floats and `0x00741EC0` for an int and a
`Which` of a string and an int. `0x00743910` builds a string, a string, a `Which` of a control and a string, and an int.
The cell readers are `0x005819A0` (int), `0x0071BAC0` (float), `0x0071CE70` (`Utf8String`) and `0x0071BC90` (a control
that is cast to `CharaBase`). The return pushers are `0x00584F70` for an int, `0x00748870` for a bool, `0x00748920` for
nil and `0x00748B30` for a control.

## Dispatch of the player natives

Thirteen `PlayerBase` callbacks are thunks that load the receiver vftable and jump through one cell. The `PlayerBase` cell
of each holds `0x00776340`, a bare `ret 4`, except `_chat`, whose cell holds the bare return `0x006DE9F0`. A `PlayerBase`
that is not a `MyPlayer` therefore pushes nothing. The RTTI name of the `MyPlayer` vftable `0x00FD785C` is
`.?AVMyPlayer@Control@Client@Script@Lua@Application@@` and `0x00FD5E04` is the `PlayerBase` vftable (`STATIC`).

| Native | Offset | `PlayerBase` cell | `MyPlayer` cell | `MyPlayer` routine |
| --- | --- | --- | --- | --- |
| `_canGetTrophy` | `0x154` | `0x00FD5F58` | `0x00FD79B0` | `0x007053A0` |
| `_isAchievedTrophy` | `0x158` | `0x00FD5F5C` | `0x00FD79B4` | `0x007053E0` |
| `_achieveTrophy` | `0x15C` | `0x00FD5F60` | `0x00FD79B8` | `0x006E6240` |
| `_turn` | `0x150` | `0x00FD5F54` | `0x00FD79AC` | `0x006E62A0` |
| `_chat` | `0x10C` | `0x00FD5F10` | `0x00FD7968` | `0x006E91F0` |
| `_haveEnmityCharacters` | `0x180` | `0x00FD5F84` | `0x00FD79DC` | `0x00705700` |
| `_countAchievementCategory` | `0x184` | `0x00FD5F88` | `0x00FD79E0` | `0x007057A0` |
| `_countAchievementItem` | `0x18C` | `0x00FD5F90` | `0x00FD79E8` | `0x00705830` |
| `_getAchievementPoint` | `0x198` | `0x00FD5F9C` | `0x00FD79F4` | `0x00705B00` |
| `_getAchievementSheetDataPoint` | `0x1B0` | `0x00FD5FB4` | `0x00FD7A0C` | `0x00705D10` |
| `_clearAchievementRateCache` | `0x1C4` | `0x00FD5FC8` | `0x00FD7A20` | `0x006E3400` |
| `_getAchievementRateList` | `0x1CC` | `0x00FD5FD0` | `0x00FD7A28` | `0x00706160` |
| `_isDoneAchievementRateList` | `0x1D0` | `0x00FD5FD4` | `0x00FD7A2C` | `0x00706260` |

`_getGroupCurrent` and `_getExtendedTemporaryGroupCurrent` call the `CharaBase` cell at offset `0x98` with
`ExecuteParameters` and a flag. The `CharaBase` cell `0x00FD5D44`, the `PlayerBase` cell `0x00FD5E9C` and the `NpcBase`
cell `0x00FD6514` hold `0x00712B40`, a `ret 8`. The `MyPlayer` cell `0x00FD78F4` holds `0x00706A40`.

## Receivers and state objects

`R` is the address that `0x00CC7510` returns for `ExecuteParameters +0x04`. `X` is the dword at `R`, `Y` the dword at
`X +0x04`, `W` the dword at `Y` and `V` the dword at `W`.

`A` is the dword at `MyPlayer +0x114`, the achievement state object of the
[player contracts](player-misc-native-contract.md#object-a). Its bitmap is the 32 dwords at `A +0x00`, the entry vector
is at `A +0x80`, the title set at `A +0x90`, the rate cache map at `A +0x9C` and the point total at `A +0xA8`.

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_canGetTrophy` | `PlayerBase` | none | `bool` | no |
| `_isAchievedTrophy` | `PlayerBase` | `int` | `bool` | no |
| `_achieveTrophy` | `PlayerBase` | `int` | none | no |
| `_countAchievementCategory` | `PlayerBase` | none | `int` | no |
| `_countAchievementItem` | `PlayerBase` | `int` | `int` | no |
| `_getAchievementPoint` | `PlayerBase` | none | `int` | no |
| `_getAchievementSheetDataPoint` | `PlayerBase` | `int` | `int` | no |
| `_clearAchievementRateCache` | `PlayerBase` | none | none | no |
| `_getAchievementRateList` | `PlayerBase` | `int`, `int` | `int`, `int`, `int` | no |
| `_isDoneAchievementRateList` | `PlayerBase` | `int`, `int` | `bool` | no |
| `_turn` | `PlayerBase` | `LuaControl*` | none | no |
| `_chat` | `PlayerBase` | `Utf8String`, `Utf8String`, `Which of control and Utf8String`, `int` | none | no |
| `_haveEnmityCharacters` | `PlayerBase` | none | `bool` | no |
| `_getGroupCurrent` | `CharaBase` | `int` | `LuaControl* or Nil` | no |
| `_getExtendedTemporaryGroupCurrent` | `CharaBase` | `int` | `LuaControl* or Nil` | no |
| `_getGroupByDisplayName` | `CharaBase` | `int`, `Which of Utf8String and int` | `LuaControl* or Nil` | no |
| `_getGroupByDisplayName` | `DirectorBase` | `int`, `Which of Utf8String and int` | `LuaControl* or Nil` | no |
| `_getGrandOnExtraStat` | `CharaBase` | none | `bool` | no |
| `_getTradingItem` | `CharaBase` | `int` | `LuaControl* or Nil` | no |
| `_createExtendedTemporaryVirtualItem` | `CharaBase` | `int`, `int`, `int` | `LuaControl*` | yes |
| `_updateMemberAndInformation` | `GroupBase` | none | none | no |
| `_setMapObjScale` | `NpcBase` | `float`, `float`, `float` | none | no |
| `_cancelTransformIntoChocobo` | `WorldMaster` | `int` | none | no |

Every callback requests no yield except `_createExtendedTemporaryVirtualItem`. Every int reader that finds a mismatched tag
reaches `0x00CCA730`. Every read follows a cell vector size test that calls `0x009D22B4` on failure, the invalid-parameter
route of the [target cursor record](target-cursor-native-contract.md#selection-and-the-failure-path).

## Trophy natives

The three trophy natives do nothing in the 1.23b client. `_canGetTrophy` (`0x007053A0`) resolves `W`, calls `0x0075CD90`
and pushes the `AL` result as a bool. `0x0075CD90` loads `V` and jumps to `0x004D75E0`, whose two instructions are
`xor al,al` and `ret`, so the bool is always false. `_isAchievedTrophy` (`0x007053E0`) reads an int, calls `0x0075CDA0`
and pushes the bool. That routine jumps to `0x004D75F0`, which is `xor al,al` and `ret 4`, so the answer is always false.
`_achieveTrophy` (`0x006E6240`) reads an int and calls `0x0075CDB0`, which jumps to `0x004D7600`, a bare `ret 4`. Nothing
is stored or sent. The only script is `chara/npc/object/bookshelf`, at the lines 221, 264 and 292. A host returns false
for the two queries and ignores the request.

## Achievement point, sheet and category natives

`_countAchievementCategory` (`0x007057A0`) pushes the constant 12. The switch `0x0057ED40` maps 729 ids between `0x65` and
`0x822` to the twelve category numbers 100, 200, 400, 500, 600, 700, 900, 1000, 1200, 1300, 1400 and 1500, the same set as
`_getAchievementCategoryId` in the [player contracts](player-misc-native-contract.md#achievement-state-and-title).

`_countAchievementItem` (`0x00705830`) tests the tag byte of cell 0. A Nil or omitted cell pushes the constant 5.
Otherwise it reads an int and pushes the result of the switch `0x0070DBB0`. The switch answers a count for each of the
twelve category numbers and 0 for every other int. The counts sum to 555. The only script site passes one argument.

`_getAchievementPoint` (`0x00705B00`) pushes the dword at `A +0xA8`. The setter `0x006E1400` stores a nonnegative argument
there. A negative argument zeroes the bitmap dwords at `A +0x00` through `+0x7C`, fills the entry vector contents with
zero bytes through `0x009D2110`, empties the title set through `0x00719D30` and stores 0 as the point total. It does not
touch the rate cache map. `0x006E2DD0` loads `A` and jumps to the setter. Its caller `0x0089C534` is the apply routine
`0x0089C510` of the receiver whose RTTI name is `AchievementPointReceiver` (slot 1 of the vftable `0x010572AC`), which
passes the dword at receiver `+0x04`. The `MyPlayer` slot 30 override `0x006F3420` reaches the setter through `0x0075D3B0`
with the dword at record `+0x44`. `xivl-opcodes:opcodes.json` lists the clientbound `0x019C` record as
`SetAchievementPointsPacket` with the payload length 40 and this retail class name.

`_getAchievementSheetDataPoint` (`0x00705D10`) reads an int, calls `0x006E73D0` and pushes the result. The routine searches
the map at `0x0134B59C` and returns the dword at the found node `+0x10`, or 0. The loader `0x0076A9C0` fills the maps from
the sheet `achievement`, and the map at `0x0134B59C` takes the column 2 of the
[player contracts](player-misc-native-contract.md#achievement-state-and-title). That the column is the point value is
`INFERRED` from the name.

## Achievement rate natives

`_clearAchievementRateCache` (`0x006E3400`) empties the ordered map at `A +0x9C`. It loads the root at the header
`A +0xA0`, calls `0x006D06D0` to erase the nodes, points the header links at the header and stores 0 as the size at
`A +0xA4`. The [achievement rate record](achievement-rate-consumer.md) describes the clientbound `0x019F` writer of the map
and the readers `0x006E3B20` and `0x006E3B90`. After the clear a rate lookup finds no entry.

`_getAchievementRateList` (`0x00706160`) reads an achievement id and a one based step and pushes three ints in this order.
The first is the result of the switch `0x00710490` for the id. The second is the result of the switch `0x00710BB0` for
the id, the zero based step and a Grand Company byte. The third is the constant 1. The Grand Company byte is the sign
extended byte at `MyPlayer +0xED` when `0x0057ED40` maps the id to the category 1500, and 0 otherwise. The two switches
answer for the same 82 ids between `0x6C` and `0x822`. The first returns one of six distinct values. The second returns
a nonzero value for the steps 0 through n - 1 where n is the result of `0x007107F0` for the id, 548 nonzero results in
all, and the id `0x61D` is the one id whose answer depends on the Grand Company byte. The 82 ids are the ids for which
`_countAchievementRateList` answers nonzero. The roles of the three values are `unknown`.

`_isDoneAchievementRateList` (`0x00706260`) subtracts 1 from the step, maps the id to a bitmap bit through `0x0070AB40`
and tests the bit in the bitmap at `A`. A set bit pushes true unless the id is `0x3F2`, `0x3F3` or `0x3F4`. Otherwise
`0x006E3B90` tests the bit `1 shl (step - 1)` of the cached third wire dword and answers false for a missing cache entry.
The [achievement rate record](achievement-rate-consumer.md#list-step-consumer) gives the full body.

## _turn

`_turn` (`0x006E62A0`) reads one control through `0x0071BC90`, which casts it to `CharaBase`. The routine takes the dword
at the control record `+0x70` through `0x00CC73B0` and `0x00CC7030`, with no null test on the record, and calls `0x0075C360`
on `W`. That routine loads `V`, takes the object `Q` from `0x004D72F0`, which is the dword at `V +0x17838`, and jumps to
`0x00589200`. `0x00589200` returns when the dword at `Q +0xF0` is `0xB` or `0xD`. Otherwise it takes the mode 3, or the
mode 4 when the identity equals the dword at `Q +0x88`, and calls `0x00587AC0`. That routine resolves the target actor
through `0x004D9970` on the table at `Q +0x7C`, returns when none is found, computes the angle between the two actor
positions with `0x009DAEBA`, wraps it with pi and 2 pi (`0x00F62F48` and `0x00F62FE0`), stores it at `Q +0xAC` and posts a
`ScenePacket` of type `0x31` and size 8 through `0x004D7980`. The native pushes nothing. That it turns the local player
toward a chara is `INFERRED`. The consumer of the packet and the class of `Q` are `unknown`.

## _chat

`_chat` (`0x006E91F0` on the `MyPlayer`) reads the message text from cell 0 and the mode from cell 1, both through
`0x0071CE70`. It compares the mode with the literals `say`, `shout`, `emote`, `tell` and `group` at `0x00FD4BF0`,
`0x00FD4BF4`, `0x00FD4BFC`, `0x00FD4C04` and `0x00FD4C0C` and calls the sender `0x0075BEF0`, `0x0075BFD0`, `0x0075C0B0`,
`0x0075C190` or `0x0075C1A0`. Any other mode sends nothing. The tell mode reads cell 2 as a string through `0x0071D770`.
The group mode reads cell 2 as a control through `0x0071B9C0` and cell 3 as an int through `0x00581AE0`, subtracts 1,
reads the member through `0x006C0590` and asks the registry at `Y +0xE4` for a word through `0x006C9690`. It sends only
when the word is nonzero. The record layouts are those of the [chat wire contract](../manifests/chat_wire_contract.json)
and the mode dispatch agrees with the [auto-translate record](autotranslate-selection-contract.md#recovered-chat-boundary).
The only script site is `widget/desktopwidget_connector` line 7428.

## _haveEnmityCharacters

`_haveEnmityCharacters` (`0x00705700` on the `MyPlayer`) builds a predicate with the vftable `0x00FD5648` and walks it over
the container at `V +0x4E4` through `0x00764150`. The predicate slot `0x007166D0` resolves each identity, casts the control
to `ActorBase` and requires the byte at control `+0x5C`. It calls the `ActorBase` vftable offset `0x60`. The default
routine `0x0071B1E0` stores the byte 0 and the word `0xFFFF`. The `NpcBase` override `0x006E3530` stores the result of
comparing the local identity with the dword at `NpcBase +0x154` and the word at `+0x158`. A word other than `0xFFFF`
sets the found byte and ends the walk. The native pushes the found byte as a bool. That the word is an enmity entry is
`INFERRED` from the name. Its writer is `unknown`.

## Group natives

`_getGroupCurrent` and `_getExtendedTemporaryGroupCurrent` call the `CharaBase` offset `0x98` with the flag 0 and 1. Only
the `MyPlayer` cell `0x00706A40` acts. It jumps to `0x00701710`, which reads one int, searches the group registry at
`Y +0xE4` through `0x006C20C0` with the number alone, tests the result through `0x006CB950` and pushes nil or the
`GroupBase` control from `0x006E2240`. The lookup of `_getGroup` in the
[nameplate and group record](nameplate-group-native-contract.md#group-natives) uses `0x006C4560`, which also takes the
receiver identity. What the creation mode 1 changes in the control was not traced.

`_getGroupByDisplayName` has two registrations, one on `CharaBase` at order 46 and one on `DirectorBase` at order 3.
Both callbacks call the helper `0x00701430` with the flag 0. The helper reads the tag byte of cell 1. A tag 0 reads an int
and any other tag reads a string. It builds a name key and searches the registry at `Y +0xE4` with `0x006C4580` when cell 0
has the tag 6 and with `0x006C45A0` and the int of cell 0 otherwise. It tests the result and pushes nil or a `GroupBase`
control. The matching rule is `unknown`. The only script site is a string constant in the debug console.

`_updateMemberAndInformation` (`0x006E2130`) copies three dwords of `Y` through `0x0075D460`, reads the group data at
receiver `+0x68` and calls `0x0075E8D0`. That routine writes the code `0x130` and the size `0x20` and four dwords at record
`+0x18`, `+0x1C`, `+0x20` and `+0x24` and sends through `0x004D6D30`. The dwords are the dword at `Y +0x10` (the local
identity of `0x0057AB60`), the dword at `[[receiver +0x68] +0x04]` and the two dwords at receiver `+0x70` and `+0x74`.
`xivl-opcodes:opcodes.json` lists the serverbound `0x0130` record as `UpdateGroupPacket` and
`manifests/c2s_payload_decoding.json` records four `u32` fields. The field meanings are `unknown`.

## _getGrandOnExtraStat

`_getGrandOnExtraStat` (`0x006FA220`) calls `0x006EEC00`, which returns the status record at receiver `+0xDC` and creates
it on first use. It reads the byte at record `+0x10` and pushes bit 0 as a bool. The constructor `0x006EEA80` zeroes
the dwords at `+0x10` and `+0x14`. The record apply `0x006EECD0` stores the dword at chara record `+0x50` there, and its
only caller is `0x006F029C`. The meaning of the bit is `unknown`.

## Item natives

`_createExtendedTemporaryVirtualItem` (`0x00708F00`) builds the helper `0x006DD450` and calls the body `0x00702A20` of
`_createVirtualItem` with the flag 1. `_createVirtualItem` passes 0. The body is in the
[chara world record](chara-world-native-contract.md#virtual-item-creation). The flag becomes the byte at the checker
`+0x20`, which `0x006F6A80` passes to the control builder `0x006E2770`. A zero byte selects `0x00CC80A0`. A nonzero byte
selects `0x00CC81E0` or `0x00CC8140` according to `0x00758EC0`. The native yields on the same path as its sibling.

`_getTradingItem` (`0x00708D20`) builds the same helper and calls the body `0x007025F0` with the flag 0. The body reads a
one based slot, subtracts 1 through `0x0078BCD0` and compares the dword at `ExecuteParameters +0x0C` with the local
identity that `0x0057AB60` returns. For a match it searches the package key `0xFD` (the initialized dword at
`0x00FE0510`) in the package manager of the receiver. Otherwise it searches the key `0xFC` (`0x00FE0514`) in the package
manager of the object at `Y +0x0C`. It pushes nil when the package or the slot record is missing and otherwise builds the
control through `0x006E2770`. The [item record](item-native-contract.md#equipment-and-trade-queries) infers the two keys
to be the two sides of a trade. The object at `Y +0x0C` and the writers of the two packages are `unknown`.

## _setMapObjScale

`_setMapObjScale` (`0x006E66A0`) reads three floats, stores them at `NpcBase +0x148`, `+0x14C` and `+0x150`, stores the
low dword of the time from `0x009D5725` plus 5 at `+0x144` and calls `0x00CC73E0` with the dword 1. The last call edits the
loop list at manager `+0x18C` through `0x00CDAA30` (`INFERRED`). The `NpcBase` vftable offset `0x10` routine `0x006F3110`
posts the scale. When the dword at `+0x144` is nonzero and the time has reached it, the routine calls `0x0075F330` with the
three floats and stores the time plus 1 at `+0x144`, so the post repeats once per second. `0x0075F330` posts a `ScenePacket`
of type `0x23` and size `0x10` holding the three floats and the constant 1.0 at `0x00F54F70`. The constructor `0x006F3650`
zeroes the fields. The consumer of the packet is `unknown`.

## _cancelTransformIntoChocobo

`_cancelTransformIntoChocobo` (`0x006ECA20`) reads one int and builds the control list through `0x00CC88D0`. For the
`WidgetBase` control whose string equals `TargetParameterWidget` at `0x00FD4E84` it builds the strings `Visible`,
`Visibility` and `Window_TargetParameterWidget` and calls `0x0075B810`. The sibling `_transformIntoChocobo` builds `Hidden`
at the same step. The callback then builds the visitor with the vftable `0x00FD590C`, walks `V +0x4E4` through `0x00764150`
and calls `0x0075CDC0` with the result slot. That routine resolves the identity and calls `0x00589D90`, which clears bit 2
of the byte at chara `+0x26D` and posts a `ScenePacket` of type 9 and size 4 with the payload `0xFFFFFFFF`. The sibling posts
its second int instead and then requests a yield. This native requests none. The no match case dereferences a null chara
exactly as the sibling does, as recorded in the [achievement and target record](achievement-target-native-contract.md#chocobo-transform-natives).
The only script site passes 1080101.

## Script call sites

| Native | Index sites | Scripts | Direct calls | Argument counts |
| --- | --- | --- | --- | --- |
| `_canGetTrophy` | 1 | 1 | 1 | 0: 1 |
| `_isAchievedTrophy` | 1 | 1 | 1 | 1: 1 |
| `_achieveTrophy` | 1 | 1 | 1 | 1: 1 |
| `_countAchievementCategory` | 1 | 1 | 1 | 0: 1 |
| `_countAchievementItem` | 1 | 1 | 1 | 1: 1 |
| `_getAchievementPoint` | 1 | 1 | 1 | 0: 1 |
| `_getAchievementSheetDataPoint` | 1 | 1 | 1 | 1: 1 |
| `_clearAchievementRateCache` | 1 | 1 | 1 | 0: 1 |
| `_getAchievementRateList` | 1 | 1 | 1 | 2: 1 |
| `_isDoneAchievementRateList` | 1 | 1 | 1 | 2: 1 |
| `_turn` | 1 | 1 | 1 | 1: 1 |
| `_chat` | 1 | 1 | 1 | 4: 1 |
| `_haveEnmityCharacters` | 1 | 1 | 1 | 0: 1 |
| `_getGroupCurrent` | 2 | 1 | 0 | none |
| `_getExtendedTemporaryGroupCurrent` | 1 | 1 | 1 | 1: 1 |
| `_getGroupByDisplayName` | 1 | 1 | 0 | none |
| `_getGrandOnExtraStat` | 1 | 1 | 1 | 0: 1 |
| `_getTradingItem` | 1 | 1 | 1 | 1: 1 |
| `_createExtendedTemporaryVirtualItem` | 1 | 1 | 1 | 3: 1 |
| `_updateMemberAndInformation` | 1 | 1 | 1 | 0: 1 |
| `_setMapObjScale` | 1 | 1 | 1 | 3: 1 |
| `_cancelTransformIntoChocobo` | 1 | 1 | 1 | 1: 1 |

The counts agree with `xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. The direct call and argument columns
are `INFERRED` from the local bytecode scan. The two `_getGroupCurrent` sites and the `_getGroupByDisplayName` site are
string constants of `commanddebugger/commanddebuggerdev`. `_createExtendedTemporaryVirtualItem` is a tail call that forwards
every result in `chara/charabaseclass_event`, and `_getAchievementPoint` and `_getAchievementRateList` forward every result.

## Host obligations

A host that implements the rows needs these results.

- The trophy queries answer false and the request does nothing.
- `_countAchievementCategory` answers 12 and `_countAchievementItem` answers 5 for an omitted argument and the category
  count otherwise, which needs the twelve counts of the switch `0x0070DBB0`.
- `_getAchievementPoint` answers the point total that the clientbound `0x019C` record sets, and a negative value resets
  the achievement bitmap, the entry vector and the title set.
- `_getAchievementRateList` answers three ints for the 82 ids that have a list. The first two values are an open question.
- `_clearAchievementRateCache` empties the rate cache so that the next progress read takes the request path.
- `_chat` sends the record of the mode and ignores any other mode.
- `_haveEnmityCharacters` answers false until an NPC reports an enmity word other than `0xFFFF`.
- The group lookups answer a group control or nil on the local player only.
- `_getTradingItem` answers an item control or nil by package key `0xFD` or `0xFC`.
- `_updateMemberAndInformation` posts the serverbound `0x0130` record with the four dwords.
- `_setMapObjScale` posts the scale once per second after a delay of 5 seconds.

## Ledger rows

These rows of the unimplemented ledger now have a registration, argument list, return list, receiver check and callback
contract: `_achieveTrophy`, `_canGetTrophy`, `_cancelTransformIntoChocobo`, `_chat`, `_clearAchievementRateCache`,
`_countAchievementCategory`, `_countAchievementItem`, `_createExtendedTemporaryVirtualItem`, `_getAchievementPoint`,
`_getAchievementRateList`, `_getAchievementSheetDataPoint`, `_getExtendedTemporaryGroupCurrent`, `_getGrandOnExtraStat`,
`_getGroupByDisplayName`, `_getGroupCurrent`, `_getTradingItem`, `_haveEnmityCharacters`, `_isAchievedTrophy`,
`_isDoneAchievementRateList`, `_setMapObjScale`, `_turn` and `_updateMemberAndInformation`. The widget rows are in the
[widget list and focus record](widget-list-focus-native-contract.md).

## Open

- The meaning of the three values of `_getAchievementRateList`.
- The writers of `NpcBase +0x154` and `+0x158` and the content of the container at `V +0x4E4`.
- The consumer of the type `0x31` and type `0x23` packets, the class of `Q` and the writers of `Q +0xF0` and
  `NpcBase +0x144`.
- The object at `Y +0x0C` and the writers of the item packages `0xFD` and `0xFC`.
- The matching rule of the group registry for a display name.
- The meaning of the four `u32` fields of the serverbound `0x0130` record and the server reply.
- The meaning of bit 0 of the status record dword at `+0x10`.
- The effect of the creation mode 1 on the item and group controls.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using the procedure in
[`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava). With explicit project and JDK bindings and a
new absolute output path, use:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Registrars | `0x00733B40,0x007339F0,0x00729230,0x00729620,0x00729A10,0x00729F50,0x00734C50,0x00734DA0,0x0072A730,0x00733C90,0x00743D80,0x00734710,0x00734860,0x007306C0,0x00756630,0x00756A20,0x0072F310,0x0072F460,0x007557C0,0x007570B0,0x0074B5D0,0x0073F710,0x0073BBE0` |
| Trophy | `0x007053A0,0x007053E0,0x006E6240,0x0075CD90,0x0075CDA0,0x0075CDB0,0x004D75E0,0x004D75F0,0x004D7600` |
| Achievement | `0x007057A0,0x00705830,0x0070DBB0,0x0057ED40,0x00705B00,0x006E1400,0x006E2DD0,0x0075D3B0,0x0089C510,0x00705D10,0x006E73D0,0x006E3400,0x00706160,0x00710490,0x00710BB0,0x007107F0,0x00706260,0x006E3B90` |
| Turn | `0x006E62A0,0x0071BC90,0x00CC73B0,0x00CC7030,0x0075C360,0x004D72F0,0x00589200,0x00587AC0,0x004D6750` |
| Chat | `0x006E91F0,0x006DE7D0,0x0075BEF0,0x0075BFD0,0x0075C0B0,0x0075C190,0x0075C1A0,0x00763030,0x006C0590,0x006C9690` |
| Enmity | `0x00705700,0x00716600,0x007166D0,0x00764150,0x0071B1E0,0x006E3530,0x004D73A0` |
| Groups | `0x00706A40,0x00701710,0x006C20C0,0x006CB950,0x006E2240,0x00708470,0x00709600,0x00701430,0x006E2130,0x0075D460,0x0075E8D0` |
| Status and items | `0x006FA220,0x006EEC00,0x006EEA80,0x006EECD0,0x00708F00,0x00708D20,0x007025F0,0x00702A20,0x006F6A80,0x006E2770` |
| Map object scale | `0x006E66A0,0x006F3110,0x0075F330,0x009D5725,0x00CC73E0,0x00CDAA30` |
| Chocobo cancel | `0x006ECA20,0x0075CDC0,0x00589D90,0x00589D30,0x00764150` |

The switches `0x0057ED40`, `0x00710490`, `0x007107F0` and `0x00710BB0` jump through tables in `.text`. `0x0070DBB0` is a
compare tree with no indirect jump. Read the compare trees and the table dispatch instructions and do not copy the tables. No decompiled body or ignored export is
a tracked evidence dependency.
