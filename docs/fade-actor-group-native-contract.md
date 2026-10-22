# Widget item, fade, actor, group and background scheduler native contracts

[`manifests/fade_actor_group_native_call_contract.json`](../manifests/fade_actor_group_native_call_contract.json)
records the static Lua call contracts of twelve natives. One adds an item to a
widget list (`_addItem`). Four are screen fade calls (`_fadeIn`, `_fadeOut`,
`_waitForFading`, `_fadeInNowLoadingForNoticeEventJustInArea`). Two belong to
the actor base (`_delete`, `_getCurrentAreaMaster`). Two query a group
(`_getMember`, `_isExistInClientMember`). One reads the grand company of a
player (`_getBelongGrandCompany`). Two start a background scheduler of an NPC
(`_runBgScheduler`, `_runBgSchedulerFromMidstream`). Each row gives the
registration site, the receiver type check, the declared argument and return
lists, the reads, the effects on client state, the failure behavior and
whether the call yields. The contracts describe client marshalling and state,
not fade presentation, group membership, grand company values, scheduler
content or server behavior.

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
per-row `corpusCallSites` records carry the call-site counts from
`xivl-client-scripts:lua/napi_index.json`. They show that a script contains a
call, not that a script reaches it at run time.

## Registration and dispatch

Five classes register the twelve natives, each from the switchboard in slot 2
of its vftable. The switchboard shape, the skip byte and the single `rel32`
caller of each registrar are the ones recorded for `SpreadSheet` in the
[SpreadSheet contracts](spreadsheet-native-contract.md#registration-and-dispatch).
The order is the position among the registrar calls of the switchboard.

| Class | Switchboard | Vftable | Natives (order) |
| --- | --- | --- | --- |
| `WidgetBase` | `0x00754A60` | `0x00FD5A74` | `_addItem` (7) |
| `PlayerBase` | `0x00753F90` | `0x00FD5E04` | `_fadeIn` (18), `_fadeOut` (19), `_waitForFading` (20), `_fadeInAfterWarp` (23), `_fadeInNowLoadingForNoticeEventJustInArea` (25), `_getBelongGrandCompany` (51) |
| `NpcBase` | `0x00754850` | `0x00FD647C` | `_runBgScheduler` (17), `_runBgSchedulerFromMidstream` (18) |
| `ActorBase` | `0x00753C30` | `0x00FD4FE4` | `_getCurrentAreaMaster` (5), `_delete` (7) |
| `GroupBase` | `0x00757B70` | `0x00FD53CC` | `_getMember` (1), `_isExistInClientMember` (4) |

| Native | Registrar | Caller | Callback | Wrapper |
| --- | --- | --- | --- | --- |
| `_addItem` | `0x00741790` | `0x00754AFA` | `0x006EBC10` | `0x00726A90` |
| `_fadeIn` | `0x00731BC0` | `0x00754111` | `0x006DE760` | `0x00726720` |
| `_fadeOut` | `0x00731D10` | `0x00754126` | `0x006DE770` | `0x00726720` |
| `_waitForFading` | `0x00731E60` | `0x0075413B` | `0x006DE780` | `0x007267D0` |
| `_fadeInNowLoadingForNoticeEventJustInArea` | `0x007324F0` | `0x007541A4` | `0x0071E3F0` | `0x00726720` |
| `_delete` | `0x0072E4A0` | `0x00753CCA` | `0x006DF240` | `0x007263B0` |
| `_getCurrentAreaMaster` | `0x007497A0` | `0x00753CA0` | `0x006F9620` | `0x00726300` |
| `_getMember` | `0x0074CAD0` | `0x00757B8C` | `0x006FFAC0` | `0x007265C0` |
| `_isExistInClientMember` | `0x0074CEC0` | `0x00757BCB` | `0x006FFBF0` | `0x007265C0` |
| `_getBelongGrandCompany` | `0x0074F380` | `0x007543C6` | `0x00706CC0` | `0x007267D0` |
| `_runBgScheduler` | `0x00737E30` | `0x007549BC` | `0x006F38D0` | `0x0072D4B0` |
| `_runBgSchedulerFromMidstream` | `0x00737F80` | `0x007549D1` | `0x006F3BA0` | `0x0072D4B0` |

Every registrar builds the return list first and the argument list second and
installs the functor through `0x00CCCAD0` under the name literal with the
adjustment 0. The wrappers `0x00726300` and `0x007265C0` are recorded in the
[scheduler and item contracts](scheduler-item-native-contract.md#registration-and-dispatch)
and the [nameplate and group contracts](nameplate-group-native-contract.md#registration-and-dispatch).
Five more wrappers appear. Each constructs the `0x58` byte functor in place and
every holder invoke routine casts the receiver with `0x009DA6CC` from
`LuaControl` to the owner class. A null cast returns false without calling the
callback, and the `0x00D19B70` failure path reports it as in the
[talk contracts](talk-native-contract.md#registration-and-dispatch).

| Wrapper | Owner class | Qualifier | Holder vftable | Invoke | Target type descriptor |
| --- | --- | --- | --- | --- | --- |
| `0x007263B0` | `ActorBase` | non-const | `0x00FD5B1C` | `0x0071A6D0` | `0x01270964` |
| `0x00726A90` | `WidgetBase` | const | `0x00FD5B64` | `0x0071AD50` | `0x012C1964` |
| `0x007267D0` | `PlayerBase` | const | `0x00FD6028` | `0x0071E7D0` | `0x012BFA48` |
| `0x00726720` | `PlayerBase` | non-const | `0x00FD601C` | `0x0071E7D0` | `0x012BFA48` |
| `0x0072D4B0` | `NpcBase` | non-const | `0x00FD6530` | `0x0072D1B0` | `0x012709E4` |

The readers are the ones of the earlier contracts: `0x005819A0` for an int,
`0x0071BAC0` for a float, `0x0071BA00` for a bool and `0x0071CE70` for a
`Utf8String`. Each reader follows a cell vector size test that calls
`0x009D22B4` on failure, the invalid-parameter route of the
[target cursor record](target-cursor-native-contract.md#selection-and-the-failure-path).

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_addItem` | `WidgetBase` | four `Utf8String` | none | no |
| `_fadeIn` | `PlayerBase` | `float` | none | no |
| `_fadeOut` | `PlayerBase` | `float` | none | no |
| `_waitForFading` | `PlayerBase` | none | none | yes, while a fade runs |
| `_fadeInNowLoadingForNoticeEventJustInArea` | `PlayerBase` | none | none | no |
| `_delete` | `ActorBase` | none | none | no |
| `_getCurrentAreaMaster` | `ActorBase` | none | `LuaControl*` | no |
| `_getMember` | `GroupBase` | `int` | `LuaControl*` | no |
| `_isExistInClientMember` | `GroupBase` | `Which<LuaControl*, IndividualIndex, int>` | `bool` | no |
| `_getBelongGrandCompany` | `PlayerBase` | none | `int` | no |
| `_runBgScheduler` | `NpcBase` | `Utf8String`, `bool` | none | no |
| `_runBgSchedulerFromMidstream` | `NpcBase` | `Utf8String`, `float` | none | no |

Only `_waitForFading` calls the yield request `0x00CD2860`. The list builders
are `0x0072B440` for none, `0x00728C20` for an int, `0x0072B390` for a float,
`0x00728B70` for a bool, `0x0072C260` for a `LuaControl*`, `0x00740570` for the
four strings, `0x00742FA0` for the `Which`, `0x0072D610` and `0x0072D710` for
the scheduler lists. The manifest rows carry each name literal, name
reference, install call, callback load and list builder.

## World object and fade state

The callbacks reach one client object through `0x00CC7510` on
`ExecuteParameters` `+0x04`. With `R` the address that routine returns, `X` is
the dword at `R` and `Y` the dword at `X +0x04`, the chain of the
[scheduler contracts](scheduler-item-native-contract.md#world-object-and-identity-lookup).
These natives read these fields of `Y`.

| Field | Used by |
| --- | --- |
| `Y +0x04` | `_addItem`, as the object whose first dword is the receiver of the identity lookups `0x004D9910` and `0x004D9970`. |
| `Y +0x08` | The fade natives, as the object whose first dword is `V`. |
| `Y +0x0C` | `_getMember`, compared with a member control by `0x006D02D0`. |
| `Y +0x18` | `_getCurrentAreaMaster`, a container of area controls. |

The constructor `0x004DBF40` of `Application::Main::RaptureElementContainer`
(vftable `0x00F912E4`) initializes the identity registry at `+0x4AC`, the log
sink pointer at `+0x660` and the sheet manager pointer at `+0x174F8`. These are
the fields that the scheduler contracts attribute to `V`, so `V` is `INFERRED`
to be that container. The tree at `V +0x17804`, keyed by identity, holds the
objects that `0x004D9910` returns. The dword at `V +0x4CC` is the fade object
`F` that `0x004D7340` returns.

## Widget item

`_addItem` (`0x006EBC10`) declares four `Utf8String` arguments. It reads the
cells 1 to 3 through `0x0071CE70` and then tests the tag of cell 0. A
`Utf8String` cell calls `0x0075B900` with the receiver identity and the four
strings. A `Nil` cell calls `0x0075B8D0` with the identity and the three
strings. Any other tag returns without a call and without an error. Whether
the marshaller admits a `Nil` cell for a declared `Utf8String` was not traced.

Both routines pass the first dword of their receiver, the object at `Y +0x04`,
as the receiver of `0x004D9910`. That lookup returns the object stored under
the identity in the tree at `V +0x17804`, or 0. No instruction tests the
result. `0x0075B8D0` reaches `0x0053AA10` through `0x0053AB60`, which supplies
the static `Utf8String` at `0x01266B10` as the first string.

`0x0053AA10` compares the first string with that static string through
`0x00445D20`. An equal string selects the dword at widget `+0x98`. Any other
string resolves through `0x005353E0`. The routine then calls `0x00538B70`,
`0x00537C60` and `0x00535C80` on the widget, runs `0x0053A970` for each entry
of the set that `0x00535C80` finds, if any, and ends with `0x00539010` on the
widget.
That the static string is the empty string, that `+0x98` is the root element
and that the first string names the target list control are `INFERRED`. The
widget class and the bodies of the called routines were not traced.

## Fade natives

The four fade callbacks are thunks of three instructions. Each loads the vftable
of the receiver and jumps through one slot with the arguments untouched.

| Native | Slot | `PlayerBase` cell | `MyPlayer` cell | `MyPlayer` routine |
| --- | --- | --- | --- | --- |
| `_fadeIn` | `0xEC` | `0x00FD5EF0` | `0x00FD7948` | `0x006E5CE0` |
| `_fadeOut` | `0xF0` | `0x00FD5EF4` | `0x00FD794C` | `0x006E5D50` |
| `_waitForFading` | `0xF4` | `0x00FD5EF8` | `0x00FD7950` | `0x006E3160` |
| `_fadeInAfterWarp` | `0x100` | `0x00FD5F04` | `0x00FD795C` | `0x006E3260` |
| `_fadeInNowLoadingForNoticeEventJustInArea` | `0x108` | `0x00FD5F0C` | `0x00FD7964` | `0x006E32F0` |

The `PlayerBase` slots hold `0x006DE9A0`, `0x006DE9B0`, `0x006DE9C0` and
`0x00776340`, each a bare `ret 4`. `MyPlayer` (vftable `0x00FD785C`) is the
only class whose RTTI base list names `PlayerBase`. It registers nothing, since
its slot 2 holds `0x00776340`. A `PlayerBase` receiver that is not a `MyPlayer`
therefore does nothing for these calls. Whether the Lua class system creates
such receivers for other players was not traced.

`_fadeIn` and `_fadeOut` (`0x006E5CE0`, `0x006E5D50`) read one float, multiply
it by the double `30.0` at `0x00FA7B18` and truncate with the 32 bit
`cvttsd2si`. The result is the frame count. They call `0x0075B490` or
`0x0075B4C0` on the object at `Y +0x08` and store 0 or 1 in the byte at the
receiver `+0x165`. Those routines read `F` through `0x004D7340` and call
`0x005606B0` with four floats and the frame count. The floats are `0.0` four
times for the fade in and `0.0`, `0.0`, `0.0`, `1.0` for the fade out. The
routine sends a 0x14 byte record through `0x004D7980` with record number 0.
`0x004D7980` adds `0x15` to the record number, so the `ScenePacket` carries the
type word `0x15`. The routine then stores the fourth float at `F +0x23C` and a
byte that is set when the signed frame count is above 0 at `F +0x244`. The
scene packet consumer was not traced. Reading the floats as a target colour
and alpha is `INFERRED`.

`_waitForFading` (`0x006E3160`) reads the byte at `F +0x244` through
`0x0075B4F0`. A zero byte returns at once. A nonzero byte builds the four byte
checker `s_FadeResumeChecker` (vftable `0x00FD5628`, poll `0x0071C7B0`) and
requests a yield with it. The poll reads the same byte and stores the waiting
result `0x0130CECC` while it is set and the done result `0x01377ECC` once it
is clear. A fade with a frame count of 0 sets no flag, so the wait returns at
once. `0x0055DA80`, slot 8 of the `GameManagerElement` vftable `0x00FA4AA8`,
clears `+0x244` when its first argument is `0x19` and `+0x245` when it is
`0x1A`. That `F` is a `GameManagerElement` and that a scene message `0x19`
ends the fade are `INFERRED`.

`_fadeInNowLoadingForNoticeEventJustInArea` (`0x006E32F0`) reads no argument.
It loads the dword `0xE0000000` at `0x0130C778` and skips everything when the
dwords at the receiver `+0x128` and `+0x12C` both equal it. Otherwise it calls
`0x0075B510`, which runs `0x004D70B0` with the argument 1, and stores the dword
in both fields. `0x004D70B0` returns when the dword at `V +0x175A4` is null.
Otherwise it calls `0x004D6820` with `-1.0`, 0, 0 and 1 and then `0x0056A7C0`
on that object. The writers of the two receiver fields and the object at
`V +0x175A4` were not traced.

`_fadeInAfterWarp` is a related row of the manifest. Its routine `0x006E3260`
calls `0x0075B500` and `0x0075B300` and stores 1 in the byte at `+0x166`.

## Actor natives

`_delete` (`0x006DF240`) asks the engine whether the receiver identity is
known through `0x00CC7190`, which reaches `0x00D035D0` on the dword at engine
`+0x1C4`. A known identity builds a context object from the Lua thread through
`0x00CD2660` and calls slot `0x70` of the receiver vftable with the engine
handle, the identity address and the context. An unknown identity first calls
`0x00CC7370` with the receiver pointer, which runs `0x00CD7A30` and
`0x00CDAEB0`, and then makes the same slot call.

Slot `0x70` holds `0x00A72A20`, a bare `ret 0xC`, in the vftables of
`ActorBase`, `CharaBase`, `PlayerBase`, `MyPlayer`, `NpcBase`, `GroupBase`,
`ItemBase`, `WorldMaster`, `AreaBase`, `DirectorBase`, `DesktopWidget` and the
other plain controls. It is overridden in `CutScene` (`0x006E19A0`),
`WidgetBase` and `DesktopUtil` (`0x006E3A00`), `SpreadSheet` (`0x006E3730`),
`QuestBase` (`0x006DCFD0`) and `CommandEventRelationActorBase`
(`0x007187B0`). The `SpreadSheet` override passes the identity to `0x0075BEC0`,
which looks it up through `0x004D9910` and calls slot 0 of the found object
with the argument 1. That this slot is the deleting destructor is `INFERRED`.
For the classes with the default slot the call has no effect beyond the engine
calls above. The meaning of those engine calls was not traced.

`_getCurrentAreaMaster` (`0x006F9620`) takes no argument. It adds `0x18` to
`Y`. A zero count at that address `+0x08` pushes a null control through
`0x00748B30`. Otherwise it reads the first node of the container through the
head sentinel at `+0x04` and pushes the control pointer at node `+0x08`. A node
equal to the sentinel reaches `0x009D22B4`. Whether a null control reaches Lua
as nil was not traced, because `0x00748B30` builds the cell through
`0x0073DDD0`.

## Group natives

Both group natives work on the group data pointer at the receiver `+0x68`.

`_getMember` (`0x006FFAC0`) reads an int `n` and calls `0x006C0CF0` with the
index `n - 1`. That routine calls `0x006C0B80`, which returns the address of
the dword `0xE0000000` at `0x0130C778` when the byte at group data `+0xF6` is
zero. Otherwise it indexes the vector of 16 byte entries whose object sits at
`+0x80`, with start at `+0x84` and end at `+0x88`, and calls `0x009D22B4` for
an index at or past the count. An entry with tag byte 3 at `+0x0C` gives the
`0xE0000000` address. Other entries are decoded through `0x006CE230` and
`0x006CF670` or `0x006CF6A0`. The identity is returned only when `0x00CC7A50`
resolves it to a control and `0x006D02D0` accepts that control. That routine
returns true for the control stored at `Y +0x0C` and otherwise the byte at
control `+0x5C`. The callback then resolves the returned identity to a
control through `0x00CC7A50` and pushes it through `0x00748B30`.
`0x00CC7A50` asks `0x00CD80F0` whether the engine knows the identity, calls
`0x00CD81D0` or `0x00CD8160`, and returns the dword at the found node or 0.

`_isExistInClientMember` (`0x006FFBF0`) declares a `Which` over `LuaControl*`,
`IndividualIndex` and an int, built by `0x0073E160` through `0x00728740`. A
tag 4 cell is read through `0x0071BB80`, converted to an identity through
`0x00CC73B0` and passed to `0x006C3E30`. A tag 8 cell pushes false without a
lookup. Every other tag is read as an int through `0x00581AE0`, reduced by 1
and passed to `0x006C3E20`. `0x006C3E20` jumps to `0x006C3AD0`, which indexes
the entry vector at `+0x84` with a bounds test that calls `0x009D22B4` for an
index at or past the count. It then calls `0x006D55C0` on the entry. For an
entry of tag 0 that routine resolves the identity pair through `0x00CC7A50`,
casts the result to `ActorBase` and stores whether the cast succeeded.
`0x006C3B30`, behind `0x006C3E30`, walks the entries for a matching identity
and ends in the same resolve and cast test. The end of the vector gives
false. That the result means the member is registered in the client engine as
an actor follows from the name and from the sibling `_isExistInWorldMember`
and is `INFERRED`. The tag 1 entries and the world variant were not traced.

## Grand company

`_getBelongGrandCompany` (`0x00706CC0`) takes no argument and pushes the
sign-extended byte at `PlayerBase` `+0xED` as an int through `0x00584F70`. It
reads no world state. That the byte is the grand company is `INFERRED` from the
name. Its writers were not traced.

## Background scheduler

Both `NpcBase` natives take a scheduler name and start it on the receiver
chara through the same chain.

`_runBgScheduler` (`0x006F38D0`) reads the name and then an optional bool. A
`Nil` second cell skips the bool. A bool of true replaces the name by its first
three bytes followed by the byte `0x01`. The first four bytes of the resulting
string are the key. The callback creates a `0x0C` byte tree through `0x00726120`
into `NpcBase +0x130` when the dword is null, then calls `0x0075C8E0` with the
receiver identity, the string and the offset 0.

`_runBgSchedulerFromMidstream` (`0x006F3BA0`) reads the name and a float and
multiplies the float by the double `1000.0` at `0x00F91C48`. It truncates with
`fistp` under the truncate rounding control and keeps the low dword of the
64 bit store. It has no bool path and no name rewrite. The rest follows
`_runBgScheduler` with the millisecond count as the offset.

`0x0075C8E0` resolves the receiver through `0x004D9970` and calls `0x00585320`
with the string data pointer and the offset. That routine returns 0 when the
dword at chara `+0xB2C` is null. Otherwise it calls `0x00794690` on that object
with the address of the key and the offset. Afterwards the callback looks the
key up in the tree at `NpcBase +0x130` and inserts a new entry through
`0x00719F70` and `0x006D45A0` when the lookup reaches the end. The callbacks
ignore the result of `0x00585320`. That the object at `+0xB2C` runs
background schedulers and that the tree records the started keys are
`INFERRED`. The `BgSchedulerResumeChecker` (vftable `0x00FD5654`, poll
`0x00716890` on a byte at `+0x04`) belongs to another native and its link to
the tree was not traced.

## Ledger rows

These rows of the unimplemented ledger have a registration, argument list,
return list, receiver check and callback contract: `_addItem`, `_fadeIn`,
`_fadeOut`, `_waitForFading`, `_fadeInNowLoadingForNoticeEventJustInArea`,
`_delete`, `_getCurrentAreaMaster`, `_getMember`, `_isExistInClientMember`,
`_getBelongGrandCompany`, `_runBgScheduler` and `_runBgSchedulerFromMidstream`.
A client that implements them still needs the fade consumer behind scene
packet type `0x15`, the widget methods behind `0x0053AA10`, the group data
class, the grand company writers and the background scheduler runner behind
`0x00794690`, which this record does not supply.

## Open

- The consumer of scene packet type `0x15`, the sender of the message `0x19`,
  the class of `F` and the writers of `MyPlayer +0x128`, `+0x12C` and
  `+0x165`.
- The widget class behind the `V +0x17804` tree and the bodies of `0x00538B70`,
  `0x00537C60`, `0x00535C80`, `0x00539010` and `0x0053A970`.
- The group data class, the entry layouts of tags 1 and 3, and the world
  member variant.
- The engine calls `0x00CD2660`, `0x00CD7A30` and `0x00CDAEB0` of `_delete`.
- The body of `0x00794690` and the meaning of the byte `0x01` in the rewritten
  scheduler name.
- Whether the Lua wrappers in `widget/widgetbaseclass`,
  `chara/player/playerbaseclass`, `actorbaseclass`, `group/groupbaseclass` and
  `chara/npc/npcbaseclass` adjust the arguments.
- The process behavior of the invalid-parameter route for an out-of-range
  member position.

The ranked list of the next natives lives in the
[binding map contracts](binding-map-native-contract.md#open). They cover the
script binding map, `_isAlive`, `_getPos`, `_getDir`, `_getActorMainStat`,
`_isExistInWorldMember`, `_getMemberDisplayName`, `_getPackage`,
`_randomInteger`, `_getDisplayName`, `_getSpecialEventWork`, `_getKind` and
`_unlockPlayerControl`. `_fadeInAfterWarp` stays a related row of this record.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes. The listings behind this
record came from a Capstone 5.0.7 x86-32 decode of the file through its
section table and the `rel32` caller scan of `.text` described in the
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
| Switchboards and registrars | `0x00754A60,0x00753F90,0x00754850,0x00753C30,0x00757B70,0x00741790,0x00731BC0,0x00731D10,0x00731E60,0x007324F0,0x00732250,0x0072E4A0,0x007497A0,0x0074CAD0,0x0074CEC0,0x0074F380,0x00737E30,0x00737F80` |
| Wrappers and list builders | `0x00726A90,0x007267D0,0x00726720,0x007263B0,0x0072D4B0,0x00740570,0x00742FA0,0x0073E160,0x00728740,0x0072D610,0x0072D710,0x0071AD50,0x0071E7D0,0x0072D1B0` |
| Callbacks | `0x006EBC10,0x006DE760,0x006DE770,0x006DE780,0x0071E3F0,0x006DE7B0,0x006DF240,0x006F9620,0x006FFAC0,0x006FFBF0,0x00706CC0,0x006F38D0,0x006F3BA0` |
| Widget item | `0x0075B8D0,0x0075B900,0x004D9910,0x0053AB60,0x0053AA10` |
| Fade | `0x006E5CE0,0x006E5D50,0x006E3160,0x006E3260,0x006E32F0,0x0075B490,0x0075B4C0,0x0075B4F0,0x0075B510,0x004D7340,0x005606B0,0x004D7980,0x0055DA80,0x0055DB00,0x00716460,0x0071C7B0,0x004D70B0` |
| Actor | `0x00CC7190,0x00CD80F0,0x00CD2660,0x00CC7370,0x006E3730,0x0075BEC0,0x006E3A00,0x006E19A0,0x006DCFD0` |
| Group | `0x006C0CF0,0x006C0B80,0x006C3E30,0x006C3E20,0x006C3B30,0x006C3AD0,0x006D55C0,0x006D02D0,0x00CC7A50,0x00748B30` |
| Background scheduler | `0x0075C8E0,0x00585320,0x004D9970,0x00726120,0x00719F70,0x006D45A0,0x00716890` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
