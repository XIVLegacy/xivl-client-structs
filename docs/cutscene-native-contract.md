# Cut scene play, replay, skip, pending actor and replay NPC native contracts

[`manifests/cutscene_native_call_contract.json`](../manifests/cutscene_native_call_contract.json)
records the static Lua call contracts of seven natives. Three belong to `CutScene`: `_play`, `_replay` and `_skip`.
One belongs to `WorldMaster`: `_getPendingCutSceneActor`. Three belong to `PlayerBase` and read the cut scene book
record: `_getCutSceneReplaySnpcNickname`, `_getCutSceneReplaySnpcCoordinate` and `_getCutSceneReplaySnpcPersonality`.
Each row gives the registration site, the receiver type check, the declared argument and return lists, the Lua pushes
of every branch, the reads, the effects on client state, the failure behavior and whether the call yields. The
record also gives the split of the open argument list, the resume checker, the completion routine, the slot 5 teardown
routine, the serverbound `0x00CE` record and the obligations of a host that completes a cut scene at once. The
contracts describe client marshalling and state. They do not describe cut scene content, the behavior of the scene
element or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data at the cited addresses. `MEASURED` is
counted from the call-site index, from one retained capture or from the decoded installed client scripts by the method
named in the fact. `INFERRED` is a role taken from the surrounding instructions or scripts that the bytes do not
state. `unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image base `0x00400000`, `15996808` bytes,
SHA-256 `9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned by
[`manifests/retail_inputs.json`](../manifests/retail_inputs.json). The registrar shape, the type registry, the cell
tags, the holders and the yield request are the ones of the
[achievement, target and cut scene contracts](achievement-target-native-contract.md#registration). The world object
chain `R`, `X` and `Y` is the one of the [fade contracts](fade-actor-group-native-contract.md#world-object-and-fade-state).
The `PlayerBase` dispatch through a `MyPlayer` vftable cell and the object `S` at `Y +0x10C` are the ones of the
[player contracts](player-misc-native-contract.md).

A script decoded each registrar, callback, vftable cell and name literal from the executable bytes and asserted the
addresses, and every cited locator begins an instruction of its decoded function. Callers, stores and loads come from
a linear decode of the `.text` section and from dword scans of the image, so virtual and indirect references are not
covered. The `MEASURED` script facts come from `xivl-client-scripts:lua/napi_index.json`. The argument counts, result
counts and call shapes come from the Lua 5.1 bytecode of the installed client scripts, decoded with
[`tools/decode_lpb.py`](../tools/decode_lpb.py). The chunks and the scan are not tracked, so those facts are
`INFERRED`.

## Summary

| Native | Class | Arguments | Returns | Yields | Callback |
| --- | --- | --- | --- | --- | --- |
| `_play` | `CutScene` | `Variable` | `bool`, `int` on resume | yes | `0x006FB830` |
| `_replay` | `CutScene` | `Variable` | `bool`, `int` on resume | yes | `0x006F11B0` |
| `_skip` | `CutScene` | none | none | no | `0x006E1970` |
| `_getPendingCutSceneActor` | `WorldMaster` | none | `LuaControl*` | no | `0x007079C0` |
| `_getCutSceneReplaySnpcNickname` | `PlayerBase` | none | `Utf8String` | no | `0x0071E660` |
| `_getCutSceneReplaySnpcCoordinate` | `PlayerBase` | none | `int` | no | `0x0071E670` |
| `_getCutSceneReplaySnpcPersonality` | `PlayerBase` | none | `int` | no | `0x0071E690` |

## Registration

Every native is declared by a `_u` script descriptor named `<name>_inl` that targets `<name>_cpp`. The descriptor
tables are `gamedata/cutscene_u`, `world/worldmaster_u` and `chara/player/playerbaseclass_u` (`INFERRED`).

| Native | Switchboard | Order | Registrar | Caller | Name literal | Holder |
| --- | --- | ---: | --- | --- | --- | --- |
| `_play` | `CutScene` `0x007547D0` | 3 | `0x0074F810` | `0x00754816` | `0x00FD7F68` | `0x00726880` |
| `_replay` | `CutScene` `0x007547D0` | 4 | `0x00736150` | `0x0075482B` | `0x00FD6DB0` | `0x00726880` |
| `_skip` | `CutScene` `0x007547D0` | 5 | `0x007362A0` | `0x00754844` | `0x00FD6DB8` | `0x00726880` |
| `_getPendingCutSceneActor` | `WorldMaster` `0x00754C70` | 3 | `0x007529F0` | `0x00754CB6` | `0x00FD8264` | `0x00726CA0` |
| `_getCutSceneReplaySnpcNickname` | `PlayerBase` `0x00753F90` | 81 | `0x00734EF0` | `0x0075463C` | `0x00FD6C50` | `0x007267D0` |
| `_getCutSceneReplaySnpcCoordinate` | `PlayerBase` `0x00753F90` | 82 | `0x00735040` | `0x00754651` | `0x00FD6C70` | `0x007267D0` |
| `_getCutSceneReplaySnpcPersonality` | `PlayerBase` `0x00753F90` | 84 | `0x007352E0` | `0x0075467B` | `0x00FD6CB0` | `0x007267D0` |

Order 83 of the `PlayerBase` switchboard is `_getCutSceneReplaySnpcSkin`, whose row is in the
[player contracts](player-misc-native-contract.md).

The `CutScene` holder `0x00726880` and the `WorldMaster` holder `0x00726CA0` cast the receiver from `LuaControl`
(`0x01270B4C`) to `0x012C17AC` or `0x012C1328` through `0x009DA6CC`. A null cast returns false from the invoke routine
(`0x0071AA30`, `0x0071AE70`) and the callback does not run. The list builders are `0x0072BCA0` for the bool and the
int of `_play` and `_replay`, `0x00728AC0` for their `Variable`, `0x0072B440` for none, `0x0072C260` for a
`LuaControl*`, `0x0072B5B0` for a `Utf8String` and `0x00728C20` for an int.

## Object chain

`R` is the address that `0x00CC7510` returns for `ExecuteParameters +0x04`, `X` the dword at `R` and `Y` the dword at
`X +0x04`. `P` is the dword at `Y +0x08` and `V` the first dword of `P`. The fade natives already use `V`. `Z` is the
dword at `V +0x4C8`, which `0x004D7330` returns, and the fade element `F` is the dword at `V +0x4CC`, which
`0x004D7340` returns. `0x004D6D10` loads the dword at `V +0x174EC` and jumps to `0x004E0240`, which ends in
`0x00DAE010`. `Z` is a scene player element by its use here, which is `INFERRED`, since its class name was not read.

## Argument split

`_play` and `_replay` call `0x006EED90`, with the `CutScene` receiver in `ECX`, on the argument object that the dword at
`ExecuteParameters +0x10` points to (`0x006FB88C`, `0x006F120B`) and two empty vectors. The routine reads the cell
vector from the dword at `+0x04` of that object, with begin at `+0x04` and end at `+0x08` of the vector and 16 byte
cells (`0x006EEE08`). It reserves 8 elements of 4 bytes in the first vector and 5 elements of `0x54` bytes in the second. Both
grow on append. It walks the cells from index 0 in three runs.

- A run of bool cells (tag 2) sets bit `i` of one 32 bit mask for a true cell at index `i` and appends the mask once
  as one int element when the run ends.
- A run of int cells (tag 0) appends each int to the first vector.
- A run of `Utf8String` cells (tag 3) appends each string to the second vector.

A cell that does not continue the walk ends it, and the remaining cells are ignored. The walk never appends floats,
Nil or controls. The cut scene replay arguments that the replay owner passes are columns 8 through 15 of a `cutReplay`
row (`xivl-client-scripts:docs/cutscene-replay-skip-contract.md`, section `Inn replay selection`). Which column falls in
which run was not traced.

## CutScene object and resume checker

| Receiver offset | Width | Role |
| --- | --- | --- |
| `+0x64` | dword | The `PlayingResumeChecker` of the pending call, 0 otherwise. The completion stores 0 at `0x006FBC8A` and the slot 5 routine at `0x006FCB2C`. |
| `+0x6C` | string object of `0x54` bytes | The file name that `_setFilename` stores. |
| `+0xC0` | byte | 1 when the last completion carried a false bool. The slot 5 routine clears it at `0x006FCB25`. |
| `+0xC1` | byte | The skip flag. `_skip` sets it, `_play` and `_replay` clear it and the completion reads it. |
| `+0xC2` | byte | Tested by `0x006FB9C0` before it calls the Lua function `_onFinalizeClip`. |

The checker is 16 bytes with the vftable `0x00FD51AC` and the RTTI name
`PlayingResumeChecker@CutScene@Control@Client@Script@Lua@Application`. Its constructor `0x00713030` stores zero at
`+0x04`, a zero byte at `+0x08` and the waiting result, the dword at `0x0130CECC`, at `+0x0C`. The poll in slot 1
(`0x00713090`) copies the dword at `+0x0C` to its output and tests nothing, so the call stays waiting until the
completion routine stores the done result, the dword at `0x01377ECC`. Slot 2 (`0x007491F0`) pushes the bool at `+0x08`
and then the int at `+0x04`. That slot 1 is the poll and slot 2 the result push follows the fade checker and is
`INFERRED`.

## _play

The callback splits the arguments, resolves `R`, `X` and `Y` and loads the dword at `Y +0x0C`. When the dword at that
object `+0x110` is nonzero it calls `0x006F7CD0` on it, frees it through `0x009D1B17` and stores 0. The role of that
object was not traced. The callback then calls `0x0076D610` on `P` with the address of receiver `+0x6C` and the two
vectors. That routine takes `Z` and calls `0x0055FFE0` on it, then posts the serverbound record described below.

`0x0055FFE0` acts only when the dword at `Z +0x98` is 0. It calls `0x004D6820` on the object at `Z +0x7C`, builds a
`0xE8` byte record from the name and the two vectors through `0x00567930`, posts it with record number 0 through
`0x004D7980` and stores 1 at `Z +0x98`. In any other state it returns, the serverbound record is still posted and the
call still yields.

The callback allocates 16 bytes, constructs the checker, stores it at receiver `+0x64`, clears the byte at receiver
`+0xC1` and requests the yield through `0x00CD2860` on `ExecuteParameters +0x08`. No instruction tests whether
receiver `+0x64` already holds a checker. On resume the call returns the bool and the int that the completion
routine stored.

## _replay

`_replay` splits the arguments as `_play` does. It reads no file name, releases no object at `Y +0x0C` and posts no
serverbound record. It calls `0x0076D820` on `P`, which calls `0x00560050` on `Z`. That routine acts only when the
dword at `Z +0x98` is 2. It builds the `0xE8` byte record from the `0x20` byte block at `Z +0xFC` and the two vectors,
posts it with record number 1 and stores 1 at `Z +0x98`. The block takes the place of the file name argument that
`0x0055FFE0` passes to `0x00567930` (compare `0x00560072` with `0x0076D6F7` and `0x0076D701`), so it is a stored name
argument, which is `INFERRED`.

The handler `0x00563D70` calls `0x004D6820` on the object at `Z +0x7C` and returns when the dword at `Z +0x80` is null.
Otherwise it switches on the dword at input record `+0x20` through the table at `0x00563E48`. Case 1 stores 2 at
`Z +0x98`, copies the `0x20` bytes at input record `+0x00` to `Z +0xFC` through `Z +0x11B` and calls `0x00574E50` with 0
and the dword at input record `+0x28`. Cases 0 and 3 call `0x00574E50` with 1 and that dword, store 0 at `Z +0x98` at
`0x00563DD3` and call `0x00563BE0`. Case 2 and the values above 3 store 0 at `Z +0x98` at `0x00563E38`. That the copied
block is the name argument of the last played scene is `INFERRED`. The checker, the flag clear and the yield are those of
`_play`.

## _skip

`_skip` sets the byte at receiver `+0xC1` to 1, resolves `R`, `X` and `Y` and calls `0x0075B200` on `P`. That routine
takes `Z` and jumps to `0x005645F0`, which pushes 3 and calls `0x00563C40`. The latter loops while the dword at
`Z +0xC4` is nonzero, advancing `Z +0xC0` modulo `Z +0xBC` and decrementing `Z +0xC4`, and calls `0x004D6820` on the
object at `Z +0x7C`. When the dword at `Z +0x98` is 1 it stores 3 there, calls `0x00563BE0` and posts a `0x14` byte
fade record on `F` with a frame count of 0, in the shape that the [fade contracts](fade-actor-group-native-contract.md#fade-natives)
give for `_fadeOut`. Every path ends by posting a 4 byte record with record number 2 and the value 3. `_skip` does not
yield and does not resume the pending call. The skip flag only changes the status of the serverbound record that the
completion sends.

## Completion

`0x006FBC50` is a `CutScene` member that takes the handle that `0x00CC7510` accepts, a bool and an int. The only caller
is the thunk `0x008A3910`, which casts its second stack argument from `0x01270964` to the `CutScene` type and passes
its first, third and fourth stack arguments on. The thunk is reached from the `ret 8` invoker `0x0075D950`, whose
address is stored once, at the cell `0x00FDFBB8` of the `LuaActorImpl` vftable `0x00FDFB2C`. No caller of that slot was
identified, so the raiser of the completion is untraced.

In order the routine does this.

1. A true bool calls `0x006FB9C0`, which returns when the byte at receiver `+0xC2` is 0 and otherwise calls the Lua
   function `_onFinalizeClip` through `0x00CC7A90`.
2. It stores `bool == 0` at receiver `+0xC0`.
3. It stores the int at checker `+0x04`, the bool at checker `+0x08` and the done result at checker `+0x0C`, and
   stores 0 at receiver `+0x64`. No instruction tests that the checker exists.
4. It calls `0x00763060` on `Y`, which returns 0 when the dword at `Y +0x20` is 0 and otherwise the byte at `+0xBB` of
   the control at the first node of the list at `Y +0x1C`. It then calls `0x00763DC0` on `P` with the address of
   receiver `+0x6C`, the byte at receiver `+0xC1` and that area byte.

Among the routines read here the completion is the only one that stores a result into the checker. The [slot 5 routine](#slot-5-teardown-routine) can also
clear receiver `+0x64`, but without storing a result.

## Slot 5 teardown routine

The `CutScene` vftable `0x00FD597C` holds the routine `0x006FCAA0` at the cell `0x00FD5990` (slot 5, offset `0x14`),
and no other cell of the image refers to it. Control vftables that do not override the slot hold the base routine
`0x006F6900` there, for example `WorldMaster` `0x00FD5864` at the cell `0x00FD5878`. `0x006FCAA0` is a `ret 8` member
that takes the handle that `0x00CC7510` accepts and one more argument.

It tests the byte at receiver `+0xC0` and then the dword at receiver `+0x64`. When either is nonzero it calls
`0x006FB9C0` with the handle, calls `0x0075B1B0` on `P` with the address of a stack cell filled through `0x0057AB60`
from `Y` (`0x006FCB0F`), clears the byte at `+0xC0` (`0x006FCB25`) and stores 0 at `+0x64` (`0x006FCB2C`). No
instruction on that path stores the done result into the checker or reads the checker, so the pending call is dropped
and not resumed. Every path then calls the base routine `0x006F6900` with the same two arguments and, when the byte at
receiver `+0x5C` is 0, calls `0x0075BE80` on the dword at `Y +0x00`.

The role of slot 5 and its raiser were not traced. Reading the `+0xC0` test as a deferred `_onFinalizeClip`, because a
false completion skips `0x006FB9C0` and this routine runs it later, and reading the slot as a teardown of a cut scene
that still holds a pending call, are `INFERRED` from the writes above only.

## Serverbound record

The opcode `0x00CE` is the serverbound map entry `_0x00CEHandler` of `xivl-opcodes:opcodes.json`, with the builders
`0x00763DC0` and `0x0076D610` and the semantic record `c2s-00ce` of `xivl-opcodes:data/client_opcode_semantics.json`.
Both builders write the code `0xCE` at stack record `+0x00` and the size `0x38` at `+0x04`, and send the record
through `0x004D6D10` with two zero arguments. The status dword is at `+0x18` and the 32 byte name field at `+0x1C`.

| Builder | Caller | Status | Name |
| --- | --- | --- | --- |
| `0x0076D610` | `_play` | 0 | The receiver `+0x6C` string cut to 31 bytes. |
| `0x00763DC0` | completion | 1 when the skip byte is nonzero, otherwise 2 | The same string. |

The four bytes after the name field are not written by either builder. After the send, `0x00763DC0` continues only
when the area byte is nonzero. It then compares floats against a located control, a branch that was not traced.

`xivl-captures:derived/payload_layouts.json`, `layouts.c2s.0x00ce`, records 2 samples of 72 bytes. Body offset 16
(subpacket `+0x20`) takes the values 0 and 2, body offsets 20 through 27 are `com0g105` followed by NUL padding to
body offset 52 (subpacket `+0x24` through `+0x43`), and the 4 bytes at body offset 52 (subpacket `+0x44`) take the
values 1 and 208. These observations match the two builders and are `MEASURED`. The `xivl-captures` scenario
`cutscene-mechanic-book` lists `0x00CE` in `cutscene_book.pcapng` (123,824 bytes), whose payload object is not part of
the public `xivl-captures` tree, so the order of the two samples (status 0 first, then 2) is an observation from that
untracked object only. The meaning of the statuses and the server reaction are not client facts.

## Scene element

`0x004D7980` builds a `ScenePacket` whose type is the record number plus `0x15`. `_play` posts type `0x15`, `_replay`
posts type `0x16` and `_skip` posts type `0x17`. The dword at `Z +0x98` takes the values 0, 1, 2 and 3. The writers of 1
are `0x0055FFBA`, `0x0056003A`, `0x00560091` and `0x005655A4`, the writer of 3 is `0x00563CC6`, the writer of 2 is
`0x00563DE9` and the writers of 0 are `0x00563DD3`, `0x00563E38`, `0x00565A4C` and `0x00565A76`. Idle, playing,
finished and skipping are the `INFERRED` names of 0 through 3. The consumers of the three records were not traced.

## _getPendingCutSceneActor

The callback resolves `R`, `X` and `Y`, loads the dword at `Y +0x104` and calls `0x00765730` on it. That routine runs
the list search `0x00779CA0` from the first node to the end node with the predicate `0x007768D0`, which returns the byte
at element `+0xC0`. It returns the element stored at the found node `+0x08`, or 0. The callback pushes the result
through `0x00748B30` without a test. The completion routine is the only writer of that byte among the `CutScene`
routines read here, apart from the clear at `0x006FCB25` in the slot 5 routine `0x006FCAA0`, so the native returns the
first `CutScene` whose last completion carried a false bool and that the slot 5 routine has not yet cleared. The sibling search `0x007657B0` uses the predicate `0x007768E0`, which tests the dword
at element `+0x64` for nonzero.

The achievement contract records the push slot `0x00CF9D60` as reading a nonzero dword through `0x00CD7A30`, which
returns 0 for a null input. Whether 0 reaches Lua as nil was not traced. The one script site uses the result as the
receiver of `startCutScene` without a nil test (`INFERRED`).

## Replay NPC getters

Each callback loads the receiver vftable and jumps through one slot. The `PlayerBase` cell holds `0x00776340`, a bare
`ret 4`, so a `PlayerBase` that is not a `MyPlayer` pushes nothing. The `MyPlayer` routine reads `S`, the dword at
`Y +0x10C`, with no null test.

| Native | Offset | `PlayerBase` cell | `MyPlayer` cell | `MyPlayer` routine | Reads | Pushes |
| --- | --- | --- | --- | --- | --- | --- |
| `_getCutSceneReplaySnpcNickname` | `0x1D8` | `0x00FD5FDC` | `0x00FD7A34` | `0x007063E0` | `S +0x2C` through `0x0075D290` | the `Utf8String` through `0x007487C0` |
| `_getCutSceneReplaySnpcCoordinate` | `0x1DC` | `0x00FD5FE0` | `0x00FD7A38` | `0x00706410` | word at `S +0x80` through `0x0075D2A0` | sign extended int through `0x00584F70` |
| `_getCutSceneReplaySnpcPersonality` | `0x1E4` | `0x00FD5FE8` | `0x00FD7A40` | `0x00706490` | byte at `S +0x83` through `0x0075D2C0` | sign extended int through `0x00584F70` |

`0x00767370` writes the state at `[ECX+4] +0x10C` from the cut scene book record `0x01A3` through `0x00576140`. The
nickname comes from application bytes 265 through 296, the word at state `+0x80` from application `+4` and the byte at
state `+0x83` from application `+7`
(`xivl-decomp:docs/event/cutscene-replay-state.md`, section `Packed keys`). That `[ECX+4]` is `Y`, so that the written
state is `S`, is `INFERRED` from the shared offset, because the same document states in section
`Incoming state producer` that the owner-pointer equality was not established by these bodies. The roles are
`INFERRED` from the native names. The initial content of `S` before the first record was not traced.

## Script call sites

| Native | Index sites | Scripts | Shape |
| --- | ---: | ---: | --- |
| `_play` | 1 | 1 | `gamedata/cutscene_common` line 1256, the varargs of the enclosing function, two results |
| `_replay` | 1 | 1 | `gamedata/cutscene_common` line 1263, the varargs, two results |
| `_skip` | 2 | 2 | `widget/cutsceneskipwidget` line 65 with no argument and no result, and a debug console site |
| `_getPendingCutSceneActor` | 1 | 1 | `quest/questbaseclass_common` line 54, no argument, one result used as a receiver |
| `_getCutSceneReplaySnpcNickname` | 1 | 1 | `quest/questbaseclass` line 240 |
| `_getCutSceneReplaySnpcCoordinate` | 1 | 1 | `quest/questbaseclass` line 245 |
| `_getCutSceneReplaySnpcPersonality` | 1 | 1 | `quest/questbaseclass` line 255 |

The counts agree with `xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. The shapes are `INFERRED`. The
`_play` site tests its first result against true to choose the path that hides the skip widget. The `_replay` branch
tests the same result and both branches return both results. The three getters are called on the local player from
`QuestBaseClass.getCutSceneReplayData` for the input values -201, -202 and -204.

## Fade-through host

A host that runs the completion routine right after `_play` or `_replay`, with no scene to show, is consistent with the
contracts. The callbacks only yield, and the completion resumes them with a bool and an int.

- `_play` and `_replay`. Store a pending checker, clear the skip byte, yield and resume with the bool true as the first
  result. The second result is an int whose value the client contract does not give. Posting the serverbound `0x00CE`
  record with status 0 at the start and status 2, or 1 after `_skip`, at the end is optional for the call and needed
  for wire parity.
- Slot 5. A host that never runs the routine at `0x006FCAA0` leaves any `+0xC0` byte set. A host that runs it applies
  the `_onFinalizeClip` rule, clears `+0xC0`, drops the checker pointer without a result and calls the base routine.
- `_skip`. Set the skip byte and return. After a completion it has nothing to skip.
- `_getPendingCutSceneActor`. A host that always completes with true never sets the byte at `+0xC0`, so the native
  finds nothing and the one script site would index a nil value. That site is tied to a completion with a false bool.
- The replay getters. Return the stored book fields, with defaults before the first record that the client contract
  does not give.

## Open

- The bool and int that a retail finish, a skip and a failed start pass to the completion, and the raiser of the
  completion through the `LuaActorImpl` slot at `0x00FDFBB8`.
- The server reaction to the statuses of the serverbound `0x00CE` record.
- When the retail flow completes a cut scene with a false bool.
- The initial content of `S` before the first `0x01A3` record.
- The raiser of the slot 5 routine `0x006FCAA0`, the retail condition that makes it run and the role of `0x0075B1B0`.
- The consumers of the three scene records, the writers of the `Z +0x98` states beyond those read here, the area byte
  branch of `0x00763DC0`, the object at `Y +0x0C` and its `+0x110` member, and the writer of the byte at receiver `+0xC2`.

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
| Registrars | `0x0074F810,0x00736150,0x007362A0,0x007529F0,0x00734EF0,0x00735040,0x007352E0` |
| Cut scene natives | `0x006FB830,0x006F11B0,0x006E1970,0x006EED90,0x00713030,0x0076D610,0x0076D820,0x0075B200` |
| Completion | `0x006FBC50,0x006FB9C0,0x00763060,0x00763DC0,0x008A3910,0x0075D950,0x006FCAA0,0x006F6900,0x0075B1B0` |
| Scene element | `0x0055FFE0,0x00560050,0x005645F0,0x00563C40,0x00563D70,0x00574E50,0x004D7980,0x004D6D10,0x004E0240` |
| Pending actor | `0x007079C0,0x00765730,0x00779CA0,0x007768D0,0x007657B0` |
| Replay getters | `0x0071E660,0x0071E670,0x0071E690,0x007063E0,0x00706410,0x00706490,0x00576140,0x00767370` |

The predicates `0x007768D0` and `0x007768E0` are two-instruction routines. Read them as instruction listings from those
addresses. No decompiled body or ignored export is a tracked evidence dependency.
