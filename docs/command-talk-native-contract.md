# Command, talk, emote, push and server request native contracts

[`manifests/command_talk_native_call_contract.json`](../manifests/command_talk_native_call_contract.json)
records the static Lua call contracts of 22 natives that start, query, cancel
and request events for the local player and for NPC receivers. Sixteen belong to
`PlayerBase`. They are `_executeCommand`, `_canExecuteCommand`, `_cancelCommand`,
`_isCommandPlaying`, `_countCommandPlaying`, `_executeTalk`, `_canExecuteTalk`,
`_cancelTalk`, `_executeEmote`, `_canExecuteEmote`, `_cancelEmote`,
`_cancelNotice`, `_cancelPush`, `_isPushingOut`, `_callServerOnCommand` and
`_doServerOnCommand`. Six belong to `NpcBase`. They are `_callServerOnTalk`,
`_callServerOnEmote`, `_callServerOnPush`, `_doServerOnTalk`,
`_doServerOnEmote` and `_doServerOnPush`. The
[chara and desktop contracts](chara-desktop-native-contract.md#playerbase-command-dispatch)
hold dispatch rows for `_executeCommand`, `_canExecuteCommand`, `_cancelCommand`
and `_isCommandPlaying`. This record contracts them down to the `MyPlayer`
routines.

Each row gives the registration site, the dispatch to the routine, the declared
argument and return lists, the cell reads, the gates, the effects on client
state, the serverbound record where one is built, the yield behavior and the
corpus call sites. The contracts describe client marshalling and state. They do
not give command names, condition names or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data
at the cited addresses. `MEASURED` is counted by the method named in the fact,
from the call-site index of the installed client scripts or from the retail
capture study that the fact cites. `INFERRED` is a name or role taken from the
surrounding instructions or scripts that the bytes do not state. `unknown` was
not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
The listings, the caller scan and the reproduction route are the ones of the
[binding map contracts](binding-map-native-contract.md#binary-and-method). The
registrar shape, the type registry, the cell tags, the holder adapter and the
invalid-parameter route are the ones of the
[nameplate, actor and group contracts](nameplate-group-native-contract.md) and
the [work binder contracts](work-binder-native-contract.md#binary-and-method).
`R`, `X`, `Y`, `W` and `V` name the world object chain of the
[Global contracts](global-native-contract.md#binary-and-method).

The call-site and chunk counts agree with
`xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. They show that a
script contains a call, not that a script reaches it at run time. The
descriptor strings come from a local scan of the installed `playerbaseclass_u`
and `npcbaseclass_u` chunks, decoded with [`tools/decode_lpb.py`](../tools/decode_lpb.py).
No tracked artifact carries them, so they are `INFERRED`.

## Registration

The `PlayerBase` switchboard is `0x00753F90`, stored at slot 2 of the vftable
`0x00FD5E04`. The `NpcBase` switchboard is `0x00754850`, stored at slot 2 of
the vftable `0x00FD647C`. Each registrar has one `rel32` caller in the
switchboard, recorded in the manifest as `registrarCaller`. Every registrar
builds the return list first and the argument list second and installs the
functor through `0x00CCCAD0` under the name literal.

Every native is declared by a `_u` script descriptor. For the natives of this
record, `playerbaseclass_u` and `npcbaseclass_u` carry a descriptor named
`<name>_inl` and a matching `<name>_cpp` string, with one exception.
`npcbaseclass_u` carries the bare name `_doServerOnTalk` and has no
`_doServerOnTalk_inl` or `_doServerOnTalk_cpp` string. The call-site index
binds the native to no class. Whether the Lua call to that name reaches the
native was not run (`INFERRED`). The Lua side of `_executeEmote`,
`_callServerOnEmote` and `_doServerOnEmote` returns the descriptor strings
`self` and `<name>_cpp`, as
`xivl-client-scripts:docs/winter-is-not-coming-client-contract.md` records.

### PlayerBase

| Native | Order | Registrar | Callback | Wrapper |
| --- | ---: | --- | --- | --- |
| `_executeCommand` | 1 | `0x0073F080` | `0x006DE650` | `0x00726720` |
| `_executeTalk` | 2 | `0x00730960` | `0x006DE660` | `0x00726720` |
| `_executeEmote` | 3 | `0x00730AB0` | `0x006DE670` | `0x00726720` |
| `_callServerOnCommand` | 4 | `0x0073F1D0` | `0x006DE680` | `0x00726720` |
| `_doServerOnCommand` | 5 | `0x0073F320` | `0x006DE690` | `0x007267D0` |
| `_canExecuteCommand` | 6 | `0x00730C00` | `0x006DE6A0` | `0x007267D0` |
| `_canExecuteTalk` | 7 | `0x00730D50` | `0x006DE6B0` | `0x007267D0` |
| `_canExecuteEmote` | 8 | `0x00730EA0` | `0x006DE6C0` | `0x007267D0` |
| `_cancelCommand` | 9 | `0x00730FF0` | `0x006DE6D0` | `0x007267D0` |
| `_cancelTalk` | 10 | `0x00731140` | `0x006DE6E0` | `0x007267D0` |
| `_cancelNotice` | 11 | `0x00731290` | `0x006DE6F0` | `0x007267D0` |
| `_cancelEmote` | 12 | `0x007313E0` | `0x006DE700` | `0x007267D0` |
| `_cancelPush` | 13 | `0x00731530` | `0x006DE710` | `0x007267D0` |
| `_isCommandPlaying` | 16 | `0x00731920` | `0x006DE740` | `0x007267D0` |
| `_countCommandPlaying` | 17 | `0x00731A70` | `0x006DE750` | `0x007267D0` |
| `_isPushingOut` | 57 | `0x007345C0` | `0x0071E4F0` | `0x007267D0` |

The wrappers are `0x00726720` (`PlayerBase`, non-const, holder vftable
`0x00FD601C`) and `0x007267D0` (`PlayerBase`, const, holder vftable
`0x00FD6028`). Both holders share the invoke routine `0x0071E7D0`, which casts
the receiver from `LuaControl` (`0x01270B4C`) to the `PlayerBase` descriptor
`0x012BFA48` and returns without calling the callback for a null cast. The
callbacks are three instruction thunks that load the receiver vftable and jump
through a slot. `_isPushingOut` uses the thunk `0x0071E4F0`. The thunks are
`STATIC`.

### NpcBase

| Native | Order | Registrar | Callback | Wrapper |
| --- | ---: | --- | --- | --- |
| `_callServerOnTalk` | 1 | `0x00736FC0` | `0x006E9520` | `0x0072D400` |
| `_callServerOnEmote` | 2 | `0x00737110` | `0x006E95C0` | `0x0072D400` |
| `_callServerOnPush` | 3 | `0x00737260` | `0x006E9660` | `0x0072D400` |
| `_doServerOnTalk` | 4 | `0x007373B0` | `0x006E9700` | `0x0072D400` |
| `_doServerOnEmote` | 5 | `0x00737500` | `0x006E97A0` | `0x0072D400` |
| `_doServerOnPush` | 6 | `0x00737650` | `0x006E9840` | `0x0072D400` |

The wrapper `0x0072D400` is the const `NpcBase` holder, vftable `0x00FD6524`,
target descriptor `0x012709E4`. The callbacks are direct member functions.

## PlayerBase dispatch

The `PlayerBase` cell of every slot holds a bare `ret 4`. A `PlayerBase`
receiver that is not a `MyPlayer` therefore pushes nothing. The `MyPlayer`
vftable `0x00FD785C` holds the routines.

| Native | Slot | `PlayerBase` cell | `MyPlayer` cell | `MyPlayer` routine |
| --- | ---: | --- | --- | --- |
| `_executeCommand` | `0xA8` | `0x00FD5EAC` | `0x00FD7904` | `0x0070A010` |
| `_executeTalk` | `0xAC` | `0x00FD5EB0` | `0x00FD7908` | `0x00704860` |
| `_executeEmote` | `0xB0` | `0x00FD5EB4` | `0x00FD790C` | `0x00704990` |
| `_callServerOnCommand` | `0xB4` | `0x00FD5EB8` | `0x00FD7910` | `0x006E8B30` |
| `_doServerOnCommand` | `0xB8` | `0x00FD5EBC` | `0x00FD7914` | `0x006E8C90` |
| `_canExecuteCommand` | `0xBC` | `0x00FD5EC0` | `0x00FD7918` | `0x00704AA0` |
| `_canExecuteTalk` | `0xC0` | `0x00FD5EC4` | `0x00FD791C` | `0x00704B60` |
| `_canExecuteEmote` | `0xC4` | `0x00FD5EC8` | `0x00FD7920` | `0x00704C80` |
| `_cancelCommand` | `0xC8` | `0x00FD5ECC` | `0x00FD7924` | `0x006E8D90` |
| `_cancelTalk` | `0xCC` | `0x00FD5ED0` | `0x00FD7928` | `0x006E8E70` |
| `_cancelNotice` | `0xD0` | `0x00FD5ED4` | `0x00FD792C` | `0x006E8F50` |
| `_cancelEmote` | `0xD4` | `0x00FD5ED8` | `0x00FD7930` | `0x006E9030` |
| `_cancelPush` | `0xD8` | `0x00FD5EDC` | `0x00FD7934` | `0x006E9110` |
| `_isCommandPlaying` | `0xE4` | `0x00FD5EE8` | `0x00FD7940` | `0x00704E40` |
| `_countCommandPlaying` | `0xE8` | `0x00FD5EEC` | `0x00FD7944` | `0x00704FA0` |
| `_isPushingOut` | `0x17C` | `0x00FD5F80` | `0x00FD79D8` | `0x00705680` |

The `PlayerBase` cell of slot `0xE8` and of slot `0x17C` is `0x00776340` and
the other cells are the stubs `0x006DE8A0` to `0x006DE990`. The slots `0xDC`
and `0xE0` belong to `_breakCommand` and `_isEventPlaying`, which are not part
of this record.

## Argument cells and list builders

Argument indices count internal `ExecuteParameters` cells after the receiver.
A return list states capacity. A handler may push fewer values. The tag byte
sits at cell `+0x0C`. Tag 0 is an int, 2 a bool, 3 a `Utf8String`, 4 a control
and 6 `Nil`.

| List builder | Declared arguments | Used by |
| --- | --- | --- |
| `0x0073D1E0` | `Utf8String`, `LuaControl*`, `Variable` | `_executeCommand`, `_callServerOnCommand`, `_doServerOnCommand` |
| `0x0072B5B0` | `Utf8String` | `_canExecuteCommand` |
| `0x0072C260` | `LuaControl*` | `_executeTalk`, `_canExecuteTalk` |
| `0x0072C050` | `LuaControl*`, `int` | `_executeEmote`, `_canExecuteEmote` |
| `0x0072BD30` | `Utf8String`, `int` | the five `_cancel` natives |
| `0x0072D810` | `Utf8String`, `LuaControl*` | `_isCommandPlaying`, `_countCommandPlaying` |
| `0x0072B440` | none | `_isPushingOut` and the return list of the natives that push nothing |
| `0x0072C7E0` | `LuaControl*`, `Utf8String` | the six `NpcBase` natives |

The return lists are `0x00728B70` (one bool) for the execute, can-execute,
playing and push-out natives, `0x00728C20` (one int) for
`_countCommandPlaying` and `0x0072B440` (empty) for the rest. The bool pusher is
`0x00748870` and the int pusher is `0x00584F70`.

| Reader | Reads |
| --- | --- |
| `0x0071CE70` | A tag 3 `Utf8String`. |
| `0x005819A0` | A tag 0 int. `0x00581AE0` adds an index test. |
| `0x0071A160` | A tag 4 control cast to `NpcBase`, descriptor `0x012709E4`. `0x0071B980` adds an index test. |
| `0x0071A380` | A tag 4 control cast to `MyPlayer`, descriptor `0x012C19A4`. |
| `0x0071BB80` | A tag 4 control cast to `ActorBase`, descriptor `0x01270964`. `0x0071CCB0` adds an index test. |

A null control pointer passes each control reader and a failed cast or another
tag reaches `0x00CCA730`. A failed cell vector size test calls `0x009D22B4`, the
invalid-parameter route of the
[target cursor record](target-cursor-native-contract.md#selection-and-the-failure-path).
Whether the executor pads a call that omits a declared argument was not run.

## Event state

The callbacks read these fields. The offsets and calls are `STATIC`. The names
current, staged and queued entry are `INFERRED` from the tests that use the
fields.

| Object | Field | Use |
| --- | --- | --- |
| `MyPlayer` | `+0x5C` | Byte. A zero byte makes the can-execute natives and `_isCommandPlaying` push false. |
| `MyPlayer` | `+0xF8` | The policy manager. It is the `ECX` of every dispatcher and canceller. |
| `MyPlayer` | `+0xFC` | The command descriptor vector that `0x0071CA50` searches by name. |
| `MyPlayer` | `+0x128`, `+0x12C` | Dwords compared with the dword at `0x0130C778`, whose image value is `0xE0000000`. This page calls that dword the sentinel. |
| `MyPlayer` | `+0x164` | Byte read by `_isPushingOut`. |
| Manager | `+0x08` | The current entry. |
| Manager | `+0x0C` | A staged entry. |
| Manager | `+0x10`, `+0x14` | The list of queued entries. |
| Manager | `+0x1E` | Byte read by `0x00893320` and by `_executeCommand`. |
| `NpcBase` | `+0x5C`, `+0x5D` | Bytes. The talk and emote routines require `+0x5C` nonzero and `+0x5D` zero. |
| `NpcBase` | `+0xE8`, `+0xF8`, `+0x108` | The talk, emote and push condition vectors. |
| Condition | `+0x04` | `Utf8String` name. |
| Condition | `+0x58` | Byte compared with the byte at `0x012C3F77`, image value 1. |
| Condition | `+0x5C` | Word. In emote conditions `0x0FFF` is a wildcard and any other value is an emote id. |

The condition vftable slots are 5 (`+0x14`), which returns the type byte
address, 6 (`+0x18`), which compares an argument type byte address with the
type byte, 7 (`+0x1C`), which returns 1 for the blocking classes and 0 for the
non-blocking classes, and 8 (`+0x20`), which writes a priority byte to its
argument and returns the argument. The block classes read the byte from the
object (`CommandBlock` at `+0x5C` through `0x008999D0`, `EmoteBlock` at `+0x60`
through `0x00899350`). Both non-block classes share `0x008993C0`, which writes
the run-time global byte at `0x01355296` instead. That byte lies outside the
raw-backed extents of the retained image. The descriptor classes `CommandBlock`
(`0x01056CC4`) and `CommandNonBlock` (`0x01056CF8`) are the command descriptors
held in the vector at `MyPlayer +0xFC`. The emote classes (`0x01056D60` and
`0x01056D94`) are NpcBase emote conditions. Both pairs follow the slot layout
above. The `CommandBlock` priority at `+0x5C` is not the condition word at
`+0x5C`. The roles of the player dwords at `+0x128` and `+0x12C`, the byte at
`+0x164`, the manager byte at `+0x1E` and the entry byte at `+0x21` were not
traced. The state machines `0x00897310` and `0x00896510` are recorded in
`xivl-decomp:docs/input/chara-selection-producers.md`, section "Native command
construction and policy dispatch".

### Event type bytes

Five type bytes tell the event classes apart. The cancel natives pass the
address of one of them and condition slot 5 returns it.

| Kind | Address | Image value | Slot 5 routine | Retail `0x012D` selector |
| --- | --- | ---: | --- | --- |
| command | `0x0134C3FF` | 0 (virtual zero-fill) | `0x00899120` | 0 in 100 of 100 command-named messages |
| talk | `0x012C3F7A` | 1 | `0x00899800` | 1 in 16 of 17 `talkDefault` messages |
| push | `0x012C3F7B` | 2 | `0x008998B0` | 2 in 7 of 7 `caution`, `exit` and `regionChange` messages |
| emote | `0x012C3F7C` | 3 | `0x00899300` | not observed |
| notice | `0x012C3F7E` | 5 | `0x00899630` | 5 in 1 of 2 `noticeEvent` messages |

The image values are `STATIC`. The selector counts are `MEASURED` in
`xivl-captures:studies/c2s-012d-event-start/derived/verdicts.md`, sections "Record
shape" and "Selector by event name". The join between the kind names and the
event names is `INFERRED` from the equal values. The command byte lies in
virtual zero-fill, so `0x0089E0D0` compares a run-time value with it. The study
records no emote trigger, so the selector of an NPC emote start rests on the
static value.

## Eligibility natives

`_canExecuteCommand`, `_canExecuteTalk` and `_canExecuteEmote` push false when
the byte at player `+0x5C` is 0. They run no event slot test.
`_canExecuteCommand` reads a name and looks the descriptor up at player
`+0xFC`. The talk and emote forms read an `NpcBase` target, push false for a
target byte `+0x5C` of 0 or a nonzero byte `+0x5D` and select a condition from
the vector at `+0xE8` or `+0xF8`. A missing condition pushes false.

A condition or descriptor whose slot 7 returns 1 pushes the answer of
`0x00893320` for the priority that slot 8 returns, and any other class pushes
true. `0x00893320` returns false when the manager byte at `+0x1E` is nonzero.
Otherwise it returns false when a current entry exists and the argument
priority does not exceed the priority of that entry, and true in every other
case.

`_canExecuteCommand` dereferences the descriptor that `0x0071CA50` returns
without a test. An unknown name therefore reads through a null pointer and the
run-time result was not observed. The same holds for the `NpcBase` target when
a script passes a null control, because the reader returns the cell slot and
the routine reads byte `+0x5C` of the stored pointer.

The talk scan `0x00720730` walks the vector from the back through `0x0071DF30`
and takes the first element whose byte `+0x58` equals the byte at `0x012C3F77`.
The emote scan `0x00720810` uses `0x0071D1D0` and also requires the word at
`+0x5C` to be `0x0FFF` or equal to the emote id.

## Execution natives

`_executeCommand`, `_executeTalk` and `_executeEmote` push a bool. They start
with a gate on the two event slots at player `+0x128` and `+0x12C`.

| Native | Event slot gate | Package record | Selected object | Dispatcher |
| --- | --- | --- | --- | --- |
| `_executeCommand` | Passes when `+0x128` differs from the sentinel. Otherwise `+0x12C` must equal it. | Key 0 must exist and manager byte `+0x1E` must be 0, only when both slots equal the sentinel | Descriptor by name at player `+0xFC` | `0x00898480` |
| `_executeTalk` | Both slots must equal the sentinel. | Key 0 must exist | Last matching talk condition at target `+0xE8` | `0x008984C0` |
| `_executeEmote` | Both slots must equal the sentinel. | none | Last matching emote condition at target `+0xF8` | `0x008985A0` |

The package record is the lower-bound lookup of the item package manager that
the [chara and desktop contracts](chara-desktop-native-contract.md#item-package-lookup)
record for `_hasItemPackage`. The key is a local that the callback zeroes, so it
names package number 1 under that native's rule. The three dispatchers call
the slot 7 of the descriptor or condition and start `0x00897310` for 1 and
`0x00896510` otherwise. They return the byte of that routine and the native
pushes it.

`_executeCommand` also resolves the command actor in cell 1 to a binding
reference through `0x00CC73B0`. Unless player `+0x128` is the sentinel, the
reference must equal it, and otherwise the native pushes false. It copies the
cells from index 1 into a vector and walks them. A tag 4 cell with a non-null
control is accepted when one of the registry predicates `0x00CC7190` and
`0x00CC70B0` answers true. Otherwise the control needs a nonzero byte `+0x5C`
and a zero byte `+0x5D`, and the native pushes false when it fails.

`_executeTalk` and `_executeEmote` read the target and apply the target byte
tests of the eligibility natives. `_executeEmote` reads the emote id from cell 1
through `0x00581AE0` and passes it to `0x006EDB50`, which keeps the low word.

No execute native requests a yield. Whether the dispatched entry yields is a
property of the state machines.

## Cancel natives

`_cancelCommand`, `_cancelTalk`, `_cancelNotice`, `_cancelEmote` and `_cancelPush`
share one shape. They read a name from cell 0 and test the tag of cell 1. They
pass the address of their type byte and push nothing.

| Native | Type byte | Nil form | Int form |
| --- | --- | --- | --- |
| `_cancelCommand` | `0x0134C3FF` | `0x006E8DFF` | `0x006E8E57` |
| `_cancelTalk` | `0x012C3F7A` | `0x006E8EDF` | `0x006E8F37` |
| `_cancelNotice` | `0x012C3F7E` | `0x006E8FBF` | `0x006E9017` |
| `_cancelEmote` | `0x012C3F7C` | `0x006E909F` | `0x006E90F7` |
| `_cancelPush` | `0x012C3F7B` | `0x006E917F` | `0x006E91D7` |

A Nil cell 1 calls `0x00895060` on the manager at player `+0xF8`. That routine
removes the staged entry at manager `+0x0C` when its name and type match and
then calls `0x00894800` and `0x008949A0` with the player, the name and the type
byte address. Any other cell 1 is read as an int and its low byte reaches
`0x008950D0` as a priority ceiling. That routine removes the staged entry only
when its priority does not exceed the byte, then calls `0x00894800` for the
current entry under the same ceiling. It does not call `0x008949A0`. The effect
on the entries, the Lua callbacks and the server flow was not traced here.

## Playing queries

`_isCommandPlaying` pushes false for a zero byte at player `+0x5C`. It reads a
name and, unless cell 1 is `Nil`, resolves the command actor to a reference
through `0x00CC73B0`. `0x00894200` then tests the current entry for the name and
the command type byte `0x0134C3FF`. A match with the sentinel reference or an
equal reference returns the byte at entry `+0x21`, and a match with another
reference returns false. An absent or non-matching current entry sends the
routine to the list at manager `+0x10`, where the first node with the name and
type returns true for the sentinel or an equal reference and false otherwise.

`_countCommandPlaying` reads the same arguments, has no byte test and pushes the
int that `0x00894370` returns. Its counting rule beyond the first tests was not
traced.

Both natives test the cell count. A vector with fewer than two cells reaches
`0x009D22B4`.

## Push-out query

`_isPushingOut` takes no argument. A nonzero byte at player `+0x164` pushes
true. Otherwise the callback follows the chain `R`, `X`, `Y` and `W` from
`ExecuteParameters` `+0x04` and calls `0x0075C970` with `W` and the value 4. That
routine loads `V` from `W` and tests bit 4 of the byte at `+0x45D` of the object at
`V +0x17838`, as `0x00589750` does for the touch attribute natives of the
[work binder contracts](work-binder-native-contract.md#touch-attributes). The
native therefore reports touch attribute 4. The writers of the byte at player
`+0x164` were not traced.

## Server request natives

### Command requests

`_callServerOnCommand` and `_doServerOnCommand` read a name, a command actor and
the remaining arguments, look the descriptor up at player `+0xFC` and send
through `0x006E2FB0`. That routine serializes the arguments from index 2 and
builds the `0x012D` record that the
[player command wire contract](player-command-wire-contract.md) records.
`_callServerOnCommand` continues with `0x00893380`, `0x00893400` and the yield
request `0x00CD2860` on the Lua thread at `ExecuteParameters` `+0x08`.
`_doServerOnCommand` returns after the send. No instruction tests the
descriptor before `0x006E30BA` reads its vftable.

### NPC event requests

The six `NpcBase` natives read the player from cell 0 through `0x0071A380` and a
name from cell 1. They look the name up in the condition vector of the receiver:
`+0xE8` for talk, `+0xF8` for emote and `+0x108` for push. The `_callServerOn`
forms enter the tail `0x006E5C00`, which calls `0x006E2E40`, takes the block
execution from the manager through `0x00893380` and `0x00893400` and requests the
yield `0x00CD2860` on the thread at `ExecuteParameters` `+0x08`. The `_doServerOn`
forms call `0x006E2E40` directly and return. No instruction tests the condition
before `0x006E2F19` reads its vftable.

`0x006E2E40` builds the record in a zeroed `0x80` byte buffer. It constructs the
typed argument writer `0x0078F790`, which writes the terminator `0x0F` at byte 0.
It never calls the serializer, so the tail is `0F` followed by 127 zero bytes.
The CRC32 of that tail is `0x1DD99EDD` (`MEASURED` with zlib). The routes
`0x0075E1C0`, `0x0089E0D0` and `0x00776760` then write the opcode `0x012D` and
the length `0xC8` and the gate `0x004D6D30` receives the message.

| Application offset | Source |
| --- | --- |
| `+0x00` | Reference of the player control, the first dword of the local that `0x00CC73B0` fills. |
| `+0x04` | Dword at the receiver identity, `ExecuteParameters` `+0x0C`. |
| `+0x08` | Dword at protocol context `+0x08`, copied from object `Y +0x14` by `0x0075D460`. |
| `+0x0C` | CRC32 of the 128 byte tail. |
| `+0x10` | Byte at the type byte address that condition slot 5 returns. |
| `+0x11` | The 32 byte condition name from condition `+0x04`. |
| `+0x31` | The 128 byte tail, `0F` then zeros. |
| `+0xB1` | Seven bytes that this builder does not write. |

The command fallback differs. It serializes its arguments, takes application
`+0x00` from object `Y +0x10` and application `+0x04` from the command binding
reference.

The retail capture study `xivl-captures:studies/c2s-012d-event-start` records
the shape for the retail client. It names application `+0x00` the trigger actor
and `+0x04` the owner actor and records `talkDefault` with selector 1 in 16 of
17 messages. The payload samples of `xivl-captures:derived/payload_samples.json`
(c2s `0x012d`, 60 samples) hold 19 starts whose tail is the empty stream, 14
with selector 1 and 5 with selector 2, and all carry the CRC `0x1DD99EDD` at
application `+0x0C`. Those facts agree with the talk and push
records above. They do not show which condition name the server registered.

`xivl-decomp:docs/event/npc-emote-event-dispatch.md` records the emote
condition constructors and states that the emote entry `_callServerOnEmote`
reaches the same event-request builder.

## Corpus

| Native | Call sites | Chunks | Scripts |
| --- | ---: | ---: | --- |
| `_executeCommand` | 6 | 1 | `chara/player/playerbaseclass` |
| `_executeTalk` | 1 | 1 | `command/system/talkcommand` |
| `_executeEmote` | 1 | 1 | `command/system/emotestandardcommand` |
| `_callServerOnCommand` | 1 | 1 | `chara/player/playerbaseclass` |
| `_doServerOnCommand` | 2 | 2 | `chara/player/playerbaseclass`, `command/debuginputcommand` |
| `_canExecuteCommand` | 1 | 1 | `chara/player/playerbaseclass` |
| `_canExecuteTalk` | 2 | 2 | `command/system/talkcommand`, `commanddebugger/commanddebuggerdev` |
| `_canExecuteEmote` | 0 | 0 | none |
| `_cancelCommand` | 9 | 2 | `chara/player/playerbaseclass`, `commanddebugger/commanddebuggerdev` |
| `_cancelTalk` | 1 | 1 | `commanddebugger/commanddebuggerdev` |
| `_cancelNotice` | 2 | 1 | `commanddebugger/commanddebuggerdev` |
| `_cancelEmote` | 8 | 1 | `commanddebugger/commanddebuggerdev` |
| `_cancelPush` | 1 | 1 | `commanddebugger/commanddebuggerdev` |
| `_isCommandPlaying` | 6 | 2 | `chara/player/playerbaseclass`, `commanddebugger/commanddebuggerdev` |
| `_countCommandPlaying` | 1 | 1 | `commanddebugger/commanddebuggerdev` |
| `_isPushingOut` | 2 | 2 | `chara/player/playerbaseclass`, `command/game/prog/chocoboridecommand` |
| `_callServerOnTalk` | 2 | 1 | `chara/npc/npcbaseclass` |
| `_callServerOnEmote` | 3 | 2 | `chara/npc/mapobj/pray12gods`, `chara/npc/npcbaseclass` |
| `_callServerOnPush` | 1 | 1 | `chara/npc/npcbaseclass` |
| `_doServerOnTalk` | 2 | 2 | `chara/npc/npcbaseclass`, `chara/npc/npcbaseclass_u` |
| `_doServerOnEmote` | 1 | 1 | `chara/npc/npcbaseclass` |
| `_doServerOnPush` | 1 | 1 | `chara/npc/npcbaseclass` |

The script side calls the natives as follows, per tracked documents of
`xivl-client-scripts`. `TalkCommand` calls `_canExecuteTalk(target)` and
`_executeTalk(target)`. `EmoteStandardCommand` calls `_executeEmote(target,
emote)`. `NpcBaseClass._onTalkEvent`, `_onEmoteEvent` and `_onPushEvent` call
`_callServerOnTalk`, `_callServerOnEmote` and `_callServerOnPush` with the
player and the request name, and the matching request hooks call the
`_doServerOn` forms. `_isCommandPlaying` receives the command name and the
command actor. The call-site counts are `MEASURED` and the argument shapes are
the cited documents' reading of the decoded chunks.

## Not traced

- The roles of the player dwords at `+0x128` and `+0x12C`, the player byte at
  `+0x164`, the manager byte at `+0x1E` and the entry byte at `+0x21`, and the
  writers of the `NpcBase` bytes at `+0x5C` and `+0x5D`.
- The state machines `0x00897310` and `0x00896510`, the entry classes and the
  routines `0x00894800`, `0x008949A0`, `0x00894200` and `0x00894370` beyond the
  tests recorded above.
- The run-time result of the descriptor and condition lookups for an unknown
  name and of a null control argument.
- The run-time value of the command type byte at `0x0134C3FF`.
- Whether the Lua call to `_doServerOnTalk` reaches the native.
- Any retail observation of an NPC emote `0x012D` start.
- The natives `_breakCommand`, `_isEventPlaying` and the `NpcBase` break
  natives.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes with the route of the
[binding map contracts](binding-map-native-contract.md#reproduction). The
descriptor strings come from the installed `playerbaseclass_u` and
`npcbaseclass_u` chunks decoded by [`tools/decode_lpb.py`](../tools/decode_lpb.py).
The function VAs for `$Addresses` are:

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Switchboards, registrars and wrappers | `0x00753F90,0x00754850,0x0073F080,0x00730960,0x00730AB0,0x0073F1D0,0x0073F320,0x00730C00,0x00730D50,0x00730EA0,0x00730FF0,0x00731140,0x00731290,0x007313E0,0x00731530,0x00731920,0x00731A70,0x007345C0,0x00736FC0,0x00737110,0x00737260,0x007373B0,0x00737500,0x00737650,0x00726720,0x007267D0,0x0072D400,0x0071E7D0` |
| List builders and readers | `0x0073D1E0,0x0072B5B0,0x0072C260,0x0072C050,0x0072BD30,0x0072D810,0x0072C7E0,0x00728040,0x00727F00,0x0071CE70,0x005819A0,0x00581AE0,0x0071A160,0x0071B980,0x0071A380,0x0071BB80,0x0071CCB0` |
| `MyPlayer` routines | `0x0070A010,0x00704860,0x00704990,0x006E8B30,0x006E8C90,0x00704AA0,0x00704B60,0x00704C80,0x006E8D90,0x006E8E70,0x006E8F50,0x006E9030,0x006E9110,0x00704E40,0x00704FA0,0x00705680,0x0071E4F0` |
| Lookups and gates | `0x0071CA50,0x006EDB30,0x006EDB50,0x00720730,0x00720810,0x0071DF30,0x0071D1D0,0x00893320,0x006F51A0,0x006E5BA0,0x00CC73B0,0x00CC7190,0x00CC70B0` |
| Dispatchers and cancel | `0x00898480,0x008984C0,0x008985A0,0x00895060,0x008950D0,0x00894800,0x00894200,0x00894370` |
| Push-out | `0x0075C970,0x004D72F0,0x00589750` |
| Server requests | `0x006E2FB0,0x006E2E40,0x006E5C00,0x006E9520,0x006E95C0,0x006E9660,0x006E9700,0x006E97A0,0x006E9840,0x00893380,0x00893400,0x00CD2860,0x0075E1C0,0x0089E0D0,0x0089EC30,0x00776760,0x0075D460,0x0078F790` |
| Type bytes | `0x00899120,0x00899800,0x008998B0,0x00899300,0x00899630` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
