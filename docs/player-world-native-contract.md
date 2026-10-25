# Player timer, Chocobo, stored item, hamlet and area ride natives and the _isAlive method

[`manifests/player_world_native_call_contract.json`](../manifests/player_world_native_call_contract.json)
records the static Lua call contracts of thirteen native registrations and of the `_isAlive` method. Nine natives belong to
`PlayerBase`. Three read the timer scalars that the clientbound `0x0193` record writes (`_getNormalBehestTime`,
`_getCompanyBehestTime`, `_getWarpRecastTime`). Two read a Chocobo or Goobbue byte (`_getChocoboGrade`, `_isEnabledGoobbue`).
Two read the stored item lists (`_canStoreItem`, `_countStoredItem`). Two read and consume the hamlet defense score
(`_getHamletDefenseScore`, `_getHamletDefenseScoreAll`). Four natives belong to `AreaBase`. Two read the hamlet supply ranking
(`_countHamletSupplyRanking`, `_getHamletSupplyRanking`). Two compare an area byte (`_canRideChocobo`, `_isWarpRideChocobo`).
`_isAlive` is not a native. It is a script method with two engine surfaces. Each full row gives the registration site, the receiver
type check, the declared argument and return lists with their stack operator types, the Lua pushes of every branch, the client field
that the callback reads with its writers where traced, the failure behavior and whether the call yields. The contracts describe client
marshalling and state. They do not describe timer, Chocobo, Goobbue, stored item, hamlet or area content, or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data at the cited addresses. `MEASURED` is counted by the
method named in the fact from the call-site index of the installed client scripts. `INFERRED` is a name or role taken from the
surrounding instructions, script names or neighbouring records that the bytes do not state. `unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned by
[`manifests/retail_inputs.json`](../manifests/retail_inputs.json). The registrar shape, the type registry, the cell tags and the
invalid-parameter route are the ones of the [nameplate, actor and group contracts](nameplate-group-native-contract.md) and the
[work binder contracts](work-binder-native-contract.md#binary-and-method). The `PlayerBase` holders and the `MyPlayer` thunk
dispatch are the ones of the [player misc contracts](player-misc-native-contract.md#registration). The `AreaBase` holder is the one of
the [chara desktop contracts](chara-desktop-native-contract.md). The registration fields of every row were decoded from the
executable bytes by a script that asserted them. Callers, stores and loads come from a linear decode of the `.text` section, so
virtual and indirect references are not covered.

The call-site and script counts agree with `xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. They show that a script
contains a call, not that a script reaches it at run time. The argument and result use inside the scripts was not decoded.

## Registration

Every native is bound to `PlayerBaseClass` in `chara/player/playerbaseclass_u` or to `AreaBaseClass` in `area/areabaseclass_u`
(`MEASURED`). The order of a native is its position among the rel32 calls of the switchboard of its class: `0x00753F90` for
`PlayerBase` and `0x00753CF0` for `AreaBase`. Each registrar has one rel32 caller and each name literal has one referencing
instruction.

| Native | Class | Order | Registrar | Caller | Callback | Wrapper |
| --- | --- | ---: | --- | --- | --- | --- |
| `_getNormalBehestTime` | `PlayerBase` | 49 | `0x00733DE0` | `0x0075439C` | `0x0071E490` | `0x007267D0` |
| `_getCompanyBehestTime` | `PlayerBase` | 50 | `0x00733F30` | `0x007543B1` | `0x0071E4A0` | `0x007267D0` |
| `_getWarpRecastTime` | `PlayerBase` | 53 | `0x00734080` | `0x007543F0` | `0x0071E4B0` | `0x007267D0` |
| `_getChocoboGrade` | `PlayerBase` | 54 | `0x007341D0` | `0x00754405` | `0x0071E4C0` | `0x007267D0` |
| `_isEnabledGoobbue` | `PlayerBase` | 56 | `0x00734470` | `0x0075442F` | `0x0071E4E0` | `0x007267D0` |
| `_canStoreItem` | `PlayerBase` | 86 | `0x0072A9D0` | `0x007546A5` | `0x0071E6B0` | `0x007267D0` |
| `_countStoredItem` | `PlayerBase` | 87 | `0x0072AB20` | `0x007546BA` | `0x0071E6C0` | `0x007267D0` |
| `_getHamletDefenseScore` | `PlayerBase` | 97 | `0x00735C10` | `0x0075478C` | `0x0071E720` | `0x007267D0` |
| `_getHamletDefenseScoreAll` | `PlayerBase` | 98 | `0x007413A0` | `0x007547A1` | `0x0071E730` | `0x00726720` |
| `_canRideChocobo` | `AreaBase` | 3 | `0x00749CE0` | `0x00753D36` | `0x006F9720` | `0x0072CD40` |
| `_isWarpRideChocobo` | `AreaBase` | 4 | `0x00749E30` | `0x00753D4B` | `0x006F9750` | `0x0072CD40` |
| `_countHamletSupplyRanking` | `AreaBase` | 8 | `0x0074A220` | `0x00753D9F` | `0x006F97C0` | `0x0072CD40` |
| `_getHamletSupplyRanking` | `AreaBase` | 9 | `0x0074A370` | `0x00753DB8` | `0x006F97F0` | `0x0072CD40` |

The wrappers construct the holders. `0x007267D0` makes the const `PlayerBase` holder and `0x00726720` the non-const one. Only
`_getHamletDefenseScoreAll` uses the non-const holder. `0x0072CD40` makes the const `AreaBase` holder, which casts the receiver to the
type descriptor `0x012C2A6C` and calls the member function directly. The `AreaBase` callbacks are therefore direct member functions
and the nine `PlayerBase` callbacks are thunks.

The list builders are `0x0072B440` for none, `0x00728C20` for an int, `0x00728B70` for a bool, `0x00583CE0` for two ints and
`0x0072B660` for three ints. Two builders are new to this record. `0x00740250` makes five ints and `0x007437F0` makes nine entries,
which are int, Utf8String, int, Utf8String and five ints. The int reader is `0x005819A0` for the cell tag 0. The return pushers are
`0x00584F70` for an int, `0x00748870` for a bool, `0x007487C0` for a Utf8String and `0x00748920` for nil. Each pusher appends its
cell to the vector at `ExecuteParameters +0x1C`. A callback that calls no pusher returns no value to Lua.

## Dispatch of the PlayerBase thunks

Each `PlayerBase` callback loads the receiver vftable and jumps through one of its cells. The `PlayerBase` vftable cell of each holds
`0x00776340`, a bare `ret 4`. A `PlayerBase` that is not a `MyPlayer` therefore pushes nothing and the Lua call returns no value
(`STATIC`).

| Native | Offset | `PlayerBase` cell | `MyPlayer` cell | `MyPlayer` routine |
| --- | --- | --- | --- | --- |
| `_getNormalBehestTime` | `0x164` | `0x00FD5F68` | `0x00FD79C0` | `0x007054D0` |
| `_getCompanyBehestTime` | `0x168` | `0x00FD5F6C` | `0x00FD79C4` | `0x00705510` |
| `_getWarpRecastTime` | `0x16C` | `0x00FD5F70` | `0x00FD79C8` | `0x00705550` |
| `_getChocoboGrade` | `0x170` | `0x00FD5F74` | `0x00FD79CC` | `0x00705590` |
| `_isEnabledGoobbue` | `0x178` | `0x00FD5F7C` | `0x00FD79D4` | `0x00705650` |
| `_canStoreItem` | `0x1EC` | `0x00FD5FF0` | `0x00FD7A48` | `0x007064D0` |
| `_countStoredItem` | `0x1F0` | `0x00FD5FF4` | `0x00FD7A4C` | `0x00706580` |
| `_getHamletDefenseScore` | `0x208` | `0x00FD600C` | `0x00FD7A64` | `0x00706870` |
| `_getHamletDefenseScoreAll` | `0x20C` | `0x00FD6010` | `0x00FD7A68` | `0x00706940` |

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_getNormalBehestTime` | `PlayerBase` | none | `int` or nothing | no |
| `_getCompanyBehestTime` | `PlayerBase` | none | `int` or nothing | no |
| `_getWarpRecastTime` | `PlayerBase` | none | `int` or nothing | no |
| `_getChocoboGrade` | `PlayerBase` | none | `int`, nil or nothing | no |
| `_isEnabledGoobbue` | `PlayerBase` | none | `bool` or nothing | no |
| `_canStoreItem` | `PlayerBase` | `int`, `int` | `bool` or nothing | no |
| `_countStoredItem` | `PlayerBase` | `int` | `int` or nothing | no |
| `_getHamletDefenseScore` | `PlayerBase` | `int` | 3 `int` or nothing | no |
| `_getHamletDefenseScoreAll` | `PlayerBase` | none | 5 `int` or nothing | no |
| `_canRideChocobo` | `AreaBase` | none | `bool` | no |
| `_isWarpRideChocobo` | `AreaBase` | none | `bool` | no |
| `_countHamletSupplyRanking` | `AreaBase` | none | `int` | no |
| `_getHamletSupplyRanking` | `AreaBase` | `int` | 9 values, see below | no |

Every callback requests no yield. Every int reader that finds a mismatched tag reaches `0x00CCA730`. Every read follows a cell vector
size test that calls `0x009D22B4` on failure, the invalid-parameter route of the
[target cursor record](target-cursor-native-contract.md#selection-and-the-failure-path).

## Timer scalars

The three timer natives read the object `S`, the dword at `Y +0x10C`, with no null test. `R` is the address that `0x00CC7510`
returns for `ExecuteParameters +0x04`, `X` is the dword at `R` and `Y` is the dword at `X +0x04`. Each pushes one dword as an int.

| Native | Field | Getter | Setter | `0x00578C90` id |
| --- | --- | --- | --- | --- |
| `_getNormalBehestTime` | `S +0x10` | `0x0075D220` | `0x0075D210` | `0x10` |
| `_getCompanyBehestTime` | `S +0x14` | `0x0075D240` | `0x0075D230` | `0x11` |
| `_getWarpRecastTime` | `S +0x18` | `0x0075D260` | `0x0075D250` | `0x12` |

The sibling `S +0x1C` is read by `_getNMRushUpdateTime` in the [player misc contracts](player-misc-native-contract.md#object-s).
The writer `0x00578C90` switches on its first argument through the jump table at `0x00578FDC`. The case for each id calls the
setter above. The stored value is 0 when the second argument is -1 and the sum of the second and third arguments otherwise. The only
rel32 caller is `0x004DD37D`. `xivl-opcodes:opcodes.json` records the clientbound `0x0193` record for this routine and states
that the packet header clock is a whole second clock and that the application values are offsets in that unit. The role as an end
time follows from those notes and the native names and is `INFERRED`. The eligibility, reset and scheduling rules were not
established.

## Chocobo grade and Goobbue flag

`_getChocoboGrade` (`0x00705590`) pushes the byte at `MyPlayer +0x15E` as an int when it is nonzero and nil when it is 0.
`_isEnabledGoobbue` (`0x00705650`) pushes bit 0 of the byte at `MyPlayer +0x160` as a bool. Neither is the field of
`_getChocoboRidingGrade`, which reads `+0x15D` and `+0x15F`.

| Field | Writers | Receiver |
| --- | --- | --- |
| `+0x15E` | `0x006DE3B0`, the slot 30 override `0x006F3420` from record byte `+0xB7`, zero in the constructor at `0x006F92A7` | `ChocoboGradeReceiver`, slot 1 `0x008A3020`, clientbound `0x0197` `SetCurrentMountChocoboPacket` |
| `+0x160` | `0x006F8350`, the slot 30 override from record byte `+0xB8`, zero in the constructor at `0x006F92B3` | `VehicleGradeReceiver`, slot 1 `0x008A31E0`, clientbound `0x01A1` `SetHasGoobbuePacket` |

Both receivers cast to `MyPlayer`, replace the second argument of the worker with the receiver byte `+4` and jump to the worker.
`0x006F8350` stores the byte and, when bit 0 is set, builds the string `_onGetGoobbue` from the literal at `0x00FD4BAC` and passes it to
`0x00CC7A90`. The grade values, the other seven bits of the Goobbue byte, the wire fields and the handler of `_onGetGoobbue` were
not traced.

## Stored item lists

`_countStoredItem` (`0x00706580`) reads a list number, subtracts 1 and indexes the array of 16 byte records at `MyPlayer +0x148`
and `+0x14C`. It pushes the element count of the dword vector of that record, which is 0 when the vector has no storage. An index
outside the array takes the invalid-parameter route. The array is rewritten by `0x006EFBD0`, which `EntrustItemReceiver` reaches for
the clientbound `0x01A5` record, as the [player misc contracts](player-misc-native-contract.md) record for `_getStoredItem`.

`_canStoreItem` (`0x007064D0`) reads a list number and an item number. It starts with false and subtracts 1 from the list number.
`0x00714440` maps the item number to a small index or -1. A negative answer leaves false. Otherwise `0x007153D0` maps the item
number to a list number from 0 to 3 and the result is true when that list equals the decremented list number. Both routines are
compare trees over item numbers. The tables are not copied here and the item sets were not enumerated. The native reads neither
the stored lists nor a list range.

## Hamlet defense score

The score object `S2` is the dword at `MyPlayer +0x154`, written by the clientbound `0x01A8` handler `0x006F2210` as
[`manifests/hamlet_wire_contract.json`](../manifests/hamlet_wire_contract.json) records. Both natives read it with no null test.

`_getHamletDefenseScore` (`0x00706870`) reads a row number, subtracts 1 and indexes the vector of 12 byte rows between the dwords
`S2 +0x04` and `+0x08`. A row outside the vector takes the invalid-parameter route. It pushes the three dwords of the row as ints in
order, which the wire contract names as computed points, mapped category and original factor. It does not change the object.

`_getHamletDefenseScoreAll` (`0x00706940`) pushes five ints in order. They are the dword at `S2 +0x10`, the sign extended byte at
`+0x18`, the product of those two, the dword at `+0x14` and the product plus that dword. It then destroys `S2` through `0x006E8800`,
frees it through `0x009D1B17` and stores 0 at `MyPlayer +0x154`. This is the only native of the record that changes state, so a second
call before a new `0x01A8` record reads a null object. The run-time effect of that read was not run.

## Hamlet supply ranking

The ranking object is the dword at `AreaBase +0x60`, zeroed by the `AreaBase` constructor at `0x006F324A` and allocated by
`0x006F3310` on the first `0x01A6` record. It is 12 bytes. The dword at `+0x04` is the head node of an ordered tree of unique
elements and the dword at `+0x08` is the element count. The refill `0x006EDFF0` erases the old nodes, zeroes the count and inserts
up to 20 converted records through `0x007214B0`.

`_countHamletSupplyRanking` (`0x006F97C0`) pushes the count as an int, or 0 when the pointer is null.

`_getHamletSupplyRanking` (`0x006F97F0`) reads a row number, subtracts 1, steps that many nodes from the first node through
`0x006E58F0` and pushes nine values. The ranking pointer is passed on without a null test. A step that starts on the head node or a
final node that is the head node takes the invalid-parameter route.

| Result | Type | Source |
| ---: | --- | --- |
| 1 | `int` | Node `+0xB8`, wire dword `+0x04`. The widget shows it as points. |
| 2 | `Utf8String` | Node `+0x0C`, wire string `+0x08`. The player name. |
| 3 | `int` | Node `+0xBE`, wire byte `+0x4A`. The Grand Company icon selector. |
| 4 | `Utf8String` or nil | Node `+0x60`, wire string `+0x28`. The linkshell name. |
| 5 | `int` or nil | Node `+0xBC`, wire word `+0x48`, sign extended. The linkshell icon input. |
| 6 | `int` or nil | The int 0. A frame dword zeroed at `0x006F98C3` that `0x006E58F0` is not given. |
| 7 | `int` or nil | The int 0. A frame dword zeroed at `0x006F98C7` that `0x006E58F0` is not given. |
| 8 | `int` or nil | The int 0. A frame dword zeroed at `0x006F98CB` that `0x006E58F0` is not given. |
| 9 | `int` | Node `+0xB4`, wire dword `+0x00`. |

The results 4 to 8 are nil when the node byte `+0xBF` is 0, which `0x006DCB50` sets when the first byte of the linkshell name is
nonzero. The [wire contract](hamlet-wire-contract.md) names the first five results. It does not record the order of the rows.

`0x007214B0` inserts by descent. An element goes left of a node when its points are greater, or the points are equal and its dword
at `+0xB4` is smaller, or both are equal and `0x00446EF0` reports its name as less. The points compare and the `+0xB4` compare
are signed 32-bit, so a wire dword of `0x80000000` or more sorts as negative. The name compare runs `0x00445B70` over the shorter
of the two lengths on sign extended chars and stops at a NUL both strings share. The string length appears to count the
terminator, so a name that is a proper prefix of another sorts as less and is not dropped as a duplicate. Otherwise it goes right, and an element equivalent in all three keys is not inserted. The getter starts at the leftmost node. Row `n` is
therefore the `n`-th element by points descending, then by the wire dword `+0x00` ascending, then by name. It is not the `n`-th wire
record, and the count can be lower than the number of nonzero wire records.

## Area ride bytes

`_canRideChocobo` (`0x006F9720`) pushes whether the byte at `AreaBase +0xB8` equals 1 and `_isWarpRideChocobo` (`0x006F9750`)
whether it equals 2. The byte sits beside the byte `+0xBA` that `_isInn` reads. The constructor zeroes `+0xB8` to `+0xBA`. The only
nonzero stores found are the immediate 1 at `0x006F736A` in `0x006F7340` and at `0x006F7841` in `0x006F7800`. No store of 2 was
found, so the decoded code cannot answer true for `_isWarpRideChocobo`. A block copy, an indirect write or another record layout was
not excluded. The roles of the values were not established.

## _isAlive

`_isAlive` has no registrar. The literal `0x0110F068` has one code reference at `0x00D08658` and the literal `0x0110F204` has one at
`0x00D1110E`. Both lie inside metatable `__index` closures. The call takes no argument, pushes one Lua boolean and does not yield.

| Receiver | Closure | Behavior |
| --- | --- | --- |
| Script instance | `0x00D085B0` | A live instance resolves the key through the class chain. The `ActorBaseClass` function returns true. A released instance resolves `_isAlive` to the global `__lge_isAlive`, which returns false, and every other key to `__lge_returnNil`, which returns nil. |
| `IndividualRef` userdata | `0x00D110B0` | The closure answers only the key `_isAlive`, with the C closure `0x00D11010`. That closure asks the engine through `0x00CE19C0` and pushes the byte as a boolean through `0x00CF3320`. |

The released test is `0x00CE1BB0`. It returns true when the byte at record `+0x7E` is set. It proceeds only when the dword at record
`+0x08` is `0x00010009`. It then casts the object at record `+0x00` to `LuaTentativeControl` and calls virtual slot 3. A false answer
sets `+0x7E` and returns true. The `IndividualRef` path calls slot 4 of the same class with the first dword of the reference. The base
class answers true in both slots. The `GroupBase`, `ItemBase` and `WidgetHandle` vftables hold the bare `ret 8` `0x00712B40` in both
slots.

The `IndividualRef` call pushes two arguments at `0x00CE1A10` and `0x00CE1A15` and reaches slot 4 through the thunk `0x00CCCB20`,
which loads the slot and jumps to it. The `ret 8` balances the pushes and leaves `eax` holding `0x00712B40`, so the low byte is
`0x40`. `0x00CE19C0` returns that byte, `0x00D11010` passes it to `0x00CF3320` and the `setne` in `0x00DCE360` makes it true. An
`IndividualRef` over a `GroupBase`, `ItemBase` or `WidgetHandle` control therefore answers true.

The released test pushes one argument for slot 3 at `0x00CE1C25`. The base routine `0x006D6F80` is `ret 4` and balances it. A
script instance of the kind `0x00010009` over one of the three controls would reach the `ret 8` with one push, leaving `esp` 4
bytes off inside `0x00CE1BB0`, and slot 3 would answer the nonzero `0x40`. Whether such an instance exists is unknown. The classes
that carry the kind `0x00010009`, the engine event that releases an instance and the receiver kind of each call site were not
traced. The call-site index lists 162 sites in 50 scripts.

## Open questions

These are calibration questions that the client evidence cannot settle. The manifest records each with its constraint.

- What sets `AreaBase +0xB8` to 1 or 2.
- What the wire dword `+0x00` of a `0x01A6` record means, since it is the second ordering key.
- What eligibility and reset rules sit behind the three timer endpoints.
- Which wire fields feed the bytes `+0x15E` and `+0x160`.
- Which engine event releases a script instance, and whether any instance of the kind `0x00010009` sits over a group, item or
  widget handle control.
