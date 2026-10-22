# Nameplate, actor, area, item reference and group native contracts

[`manifests/nameplate_group_native_call_contract.json`](../manifests/nameplate_group_native_call_contract.json)
records the static Lua call contracts of twelve natives. Two belong to the
chara nameplate (`_setNameplate`, `_setNameplateVisible`). Two are actor
identity queries (`_getStaticActorID`, `_isExistActor`). Two belong to the area
object (`_setInstanceRaid`, `_getZoneName`). Three read or bind an item
reference (`_bindSpreadSheetData`, `_countStack`, `_getItemPackageFreeSpace`).
Three belong to groups (`_countMember`, `_isMember`, `_getGroup`). Each row
gives the registration site, the receiver type check, the declared argument and
return lists, the reads, the effects on client state, the failure behavior and
whether the call yields. The contracts describe client marshalling and state,
not nameplate content, actor rules, item data, group membership or server
behavior.

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
call, not that a script reaches it at run time. `_isExistActor` has no class
binding in the index. The class that registers it comes from the switchboard.

## Registration and dispatch

Six classes register the twelve natives, each from the switchboard in slot 2 of
its vftable. The switchboard shape, the skip byte and the single `rel32` caller
of each registrar are the ones recorded for `SpreadSheet` in the
[SpreadSheet contracts](spreadsheet-native-contract.md#registration-and-dispatch).
The order is the position among the registrar calls of the switchboard.

| Class | Switchboard | Vftable | Natives (order) |
| --- | --- | --- | --- |
| `CharaBase` | `0x007574A0` | `0x00FD5CAC` | `_setNameplate` (28), `_setNameplateVisible` (32), `_getGroup` (41), `_getItemPackageFreeSpace` (69) |
| `ActorBase` | `0x00753C30` | `0x00FD4FE4` | `_getStaticActorID` (8) |
| `AreaBase` | `0x00753CF0` | `0x00FD63D4` | `_getZoneName` (2), `_setInstanceRaid` (7) |
| `ItemBase` | `0x00753DD0` | `0x00FD5484` | `_countStack` (4), `_bindSpreadSheetData` (10) |
| `GroupBase` | `0x00757B70` | `0x00FD53CC` | `_countMember` (2), `_isMember` (6) |
| `Global` | `0x007582E0` | `0x00FD60AC` | `_isExistActor` (7) |

`GroupBase` has a second vftable at `0x00FD53AC` whose slot 2 is `0x006DD180`.
The switchboard of its primary vftable is the one that registers the group
natives.

| Native | Registrar | Caller | Callback | Wrapper |
| --- | --- | --- | --- | --- |
| `_setNameplate` | `0x00745230` | `0x007576F3` | `0x006F5F30` | `0x00726510` |
| `_setNameplateVisible` | `0x0072EB30` | `0x00757747` | `0x006E4100` | `0x00726460` |
| `_getStaticActorID` | `0x007498F0` | `0x00753CE3` | `0x006F9690` | `0x00726300` |
| `_isExistActor` | `0x0073C660` | `0x0075837A` | `0x006DCD80` | `0x00726E00` |
| `_setInstanceRaid` | `0x0072E5F0` | `0x00753D8A` | `0x006E3C10` | `0x0072CDF0` |
| `_getZoneName` | `0x00749B90` | `0x00753D21` | `0x006F9700` | `0x0072CD40` |
| `_bindSpreadSheetData` | `0x00743C30` | `0x00753EA9` | `0x006F54A0` | `0x00726670` |
| `_countStack` | `0x0074DE80` | `0x00753E2B` | `0x00701920` | `0x00726670` |
| `_getItemPackageFreeSpace` | `0x007560F0` | `0x00757A50` | `0x00708AC0` | `0x00726510` |
| `_countMember` | `0x0074CC20` | `0x00757BA1` | `0x006FFB90` | `0x007265C0` |
| `_isMember` | `0x0074D160` | `0x00757BF5` | `0x006FFED0` | `0x007265C0` |
| `_getGroup` | `0x00755280` | `0x00757804` | `0x007083F0` | `0x00726460` |

Every registrar builds the return list first and the argument list second and
installs the functor through `0x00CCCAD0` under the name literal with the
adjustment 0. The wrappers `0x00726510`, `0x00726460`, `0x00726300` and
`0x00726670` are recorded in the
[scheduler and item contracts](scheduler-item-native-contract.md#registration-and-dispatch).
Four more wrappers appear. Each constructs the `0x58` byte functor in place and
every holder invoke routine casts the receiver with `0x009DA6CC` from
`LuaControl` to the owner class. A null cast returns false without calling the
callback, and the `0x00D19B70` failure path reports it as in the
[talk contracts](talk-native-contract.md#registration-and-dispatch).

| Wrapper | Owner class | Qualifier | Holder vftable | Invoke | Target type descriptor |
| --- | --- | --- | --- | --- | --- |
| `0x00726E00` | `Global` | const | `0x00FD6138` | `0x00725620` | `0x012C27C0` |
| `0x0072CDF0` | `AreaBase` | non-const | `0x00FD6470` | `0x0072CAF0` | `0x012C2A6C` |
| `0x0072CD40` | `AreaBase` | const | `0x00FD6464` | `0x0072CAF0` | `0x012C2A6C` |
| `0x007265C0` | `GroupBase` | const | `0x00FD5B28` | `0x0071A7F0` | `0x012C07E8` |

The type registry constructor `0x00CC9D60` stores the `StackOperator` vftables
`0x0110DF38`, `0x0110DF60`, `0x0110DF88`, `0x0110DFB0`, `0x0110DFD8`,
`0x0110E000`, `0x0110E028`, `0x0110E050`, `0x0110E078` and `0x0110E0A0` as
entries 0 to 9. Their RTTI names are int, float, bool, `Utf8String`,
`LuaControl*`, `AutoReleaseTentative`, `Nil`, `Table`, `IndividualIndex` and
`Variable`. The argument lists below name entries by that numbering.

Argument indices count internal `ExecuteParameters` cells after the receiver.
The readers are the ones of the widget contracts, `0x005819A0` for an int,
`0x0071BA00` for a bool and `0x0071CE70` for a `Utf8String`. Four readers are
new.

| Reader | Reads |
| --- | --- |
| `0x0071BB80` | A tag 4 control. A null pointer passes. A non-null pointer is cast to `ActorBase`, descriptor `0x01270964`. A failed cast or another tag, `Nil` included, reaches `0x00CCA730`. |
| `0x0071C080` | The same reader with the descriptor `0x012C2308`, which is `SpreadSheet`. |
| `0x0071CD90` | Tests an index against the cell vector and reads a tag 8 `IndividualIndex` through `0x0071C2A0`. The result addresses two dwords. |
| `0x00581AE0` | Tests an index against the cell vector and reads an int through `0x005819A0`. |

Each reader follows a cell vector size test that calls `0x009D22B4` on failure,
the invalid-parameter route of the
[target cursor record](target-cursor-native-contract.md#selection-and-the-failure-path).

## World object

The callbacks reach one client object through `0x00CC7510` on `ExecuteParameters`
`+0x04`. With `R` the address that routine returns, `X` is the dword at `R` and
`Y` the dword at `X +0x04`, the chain of the
[scheduler contracts](scheduler-item-native-contract.md#world-object-and-identity-lookup).
These natives read these fields of `Y`. The roles are `INFERRED` from the
natives that use them and the classes of the objects were not identified.

| Field | Used by |
| --- | --- |
| `Y +0x04` | `_setNameplateVisible`, as the object that resolves the identity. |
| `Y +0xDC` | The listener of `_setNameplate`, through `0x00771C20`. |
| `Y +0xE0` | `_setNameplate`, which hands the listener over through `0x0076FF20`. |
| `Y +0xE4` | `_getGroup`, the group lookup `0x006C4560`. |
| `Y +0x118` | `_bindSpreadSheetData`, the row binding `0x00767120`. |
| `Y +0x12C` | `_bindSpreadSheetData`, the lookup `0x007646D0` of the `0xFF` path. |

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_setNameplate` | `CharaBase` | `int`, `LuaControl*`, `int`, `Variable` | none | no |
| `_setNameplateVisible` | `CharaBase` | `bool` | none | no |
| `_getStaticActorID` | `ActorBase` | none | `int` | no |
| `_isExistActor` | `Global` | `Utf8String` | `bool` | no |
| `_setInstanceRaid` | `AreaBase` | `bool` | none | no |
| `_getZoneName` | `AreaBase` | none | `Utf8String` | no |
| `_bindSpreadSheetData` | `ItemBase` | `LuaControl*` | none | no |
| `_countStack` | `ItemBase` | none | `int` | no |
| `_getItemPackageFreeSpace` | `CharaBase` | `int` | `int` | no |
| `_countMember` | `GroupBase` | none | `int` | no |
| `_isMember` | `GroupBase` | `Which<LuaControl*, IndividualIndex>`, `int` | `bool` | no |
| `_getGroup` | `CharaBase` | `int` | `LuaControl*` or nil | no |

Neither the twelve callbacks nor the helper routines named below call the
yield request `0x00CD2860`.

The list builders are `0x0072B440` for none, `0x00728C20` for an int,
`0x00728B70` for a bool, `0x0072B5B0` for a `Utf8String`, `0x0072C260` for a
`LuaControl*`, `0x0073FEF0` for the four entries of `_setNameplate` and
`0x00743020` for the `Which` and the int of `_isMember`. The manifest rows carry
each name literal, name reference, install call, callback load and list
builder.

## Nameplate natives

`_setNameplate` (`0x006F5F30`) reads a slot number `n`, an actor control and an
int. It then reads the cells from index 3 onward through `0x007702C0`. The list
builder makes the four entries int, `LuaControl*`, int and `Variable`.

The callback first computes `n - 1` (`0x006F5F9C`), so the slot number is
1-based. The record for slot `n` lives in the receiver at
`0x68 + 0x38 * (n - 1)`, which is `0x38 * n + 0x30`. The callback stores the
identity that `0x00CC73B0` returns for the control at record `+0x00` and the
third argument at `+0x04`. It copies the parameter record that
`0x007702C0` built into `+0x08` through `0x004D5900` and a dword and byte copy.
No instruction tests `n` against a capacity. The value 0 addresses receiver
`+0x30`, one record before slot 1, and whether that address is in range was not
traced (`unknown`).

`0x007702C0` visits the cells from index 3 and keeps three tags. A tag 0 cell is
read as an int, a tag 3 cell as a `Utf8String` and a tag 4 cell as a control.
A control goes to virtual slot `0x84` of its vftable through `0x006DBF90`.
Every other tag is skipped without an error.

The callback then allocates a `0x48` byte listener through `0x009D1B35` and
constructs it with `0x00744C10`. The vftable `0x00FD76C8` has the RTTI name
`SetNameplateMessageListener` nested in `CharaBase`. The constructor stores the
engine dword at `+0x04`, the receiver identity at `+0x08`, the actor identity at
`+0x0C`, the int at `+0x10` and `n` at `+0x14`, and copies the parameter record
into `+0x18`.

The callback hands the listener to the object at `Y +0xE0` through `0x0076FF20`.
That routine reads the dword at receiver `+0x60`. A nonzero byte at `+0x59` of
that object calls listener slot 1 (`0x00744E70`) at once and destroys the
listener. A zero byte passes the key, the receiver identity, a zero and the
listener to `0x0076FD80` and does not destroy the listener. Listener slot 1
constructs a `0x10` byte object and calls `0x00771C20` on the object at
`Y +0xDC` with the actor identity, the int and the parameter record.

The base vftable `0x00FD40E4` of the listener has the RTTI name
`GetNameListenerInterface` nested in `DisplayNameResolver`. That the listener
waits for a display name, that the byte at `+0x59` says the name is ready and
that `0x00771C20` shows the nameplate are `INFERRED` from those names. The
bodies of `0x0076FD80` and `0x00771C20`, the capacity of the slot table and the
meaning of the second int were not traced.

`_setNameplateVisible` (`0x006E4100`) reads one bool and calls `0x0075B630` on
the dword at `Y +0x04` with the receiver identity and the bool. The routine
resolves the identity through `0x004D9970` and returns when the identity is
absent. Otherwise it calls virtual slot `0x44` of the object at the chara
`+0xBA0` with the bool. The class of that object was not identified.

## Actor identity natives

`_getStaticActorID` (`0x006F9690`) takes no argument. It loads the receiver
identity from `ExecuteParameters` `+0x0C`, masks it with `0xFFFFF` and pushes the
result as an int. It reads neither the registry nor the receiver pointer, so the
identity `0xC0000000` gives 0. That the low 20 bits are the static actor id is
`INFERRED` from the native name.

`_isExistActor` (`0x006DCD80`) is a thin adapter into the body `0x0078CB90`. It
reads one `Utf8String` and asks the engine name tables three things in turn. The
name must be present, which `0x00CC7200` tests through `0x00CD9C60` and
`0x00CD8870` with the flag 0. The state dword at entry `+0x08` must equal one of
`0x00010008`, `0x00010009` and `0x0001000A`, the three dwords at `0x0130D4FC`,
`0x0130D500` and `0x0130D504` that `0x00CE16C0` compares. The name must then
resolve to a handle through `0x00CC7A00`, and `0x00CC72A0` must find a node whose
byte at `+0x7D` is nonzero. The byte is read without a null test. A failed
question pushes false and success pushes true.

The lookup `0x00CD8870` with the flag 1 calls `0x00CD5320` on the dword at
engine implementation `+0x1CC` after a miss in both tables. That this native
does not reach that branch is `INFERRED`, because the first question has found
the name. The `_getStaticActor` row of the
[boot contracts](boot-native-call-contract.md#contracts) uses the same
`0x00CC72A0` test and reads the byte at `+0x7D` as a flag. The meaning of the
state dwords and the node byte, and the classes behind the engine name tables,
were not traced.

`Global` is the class of the receiverless names, as the
[Global call convention](global-native-contract.md#receiverless-call-convention)
records. Its switchboard registers `_defineClass` and `_defineBaseClass` at
orders 1 and 2 and `_isExistActor` at order 7. The boot contracts record the
`global_u` descriptor with the selector `global` for `_getStaticActor`. The
`global_u` script declares a descriptor with that selector for each of the 15
natives below, `_isExistActor` included. The
[binding map contracts](binding-map-native-contract.md#receiverless-names) record
the descriptors and the key suffix.

| Order | Native | Registrar |
| ---: | --- | --- |
| 1 | `_defineClass` | `0x0073C270` |
| 2 | `_defineBaseClass` | `0x0073C3C0` |
| 3 | `_createActor` | `0x00757350` |
| 4 | `_canCreateActorByName` | `0x00753320` |
| 5 | `_getActorByName` | `0x0073C510` |
| 6 | `_isInstanceOf` | `0x00753470` |
| 7 | `_isExistActor` | `0x0073C660` |
| 8 | `_getStaticActor` | `0x00741A30` |
| 9 | `_getQuestActorForCutSceneReplay` | `0x007535C0` |
| 10 | `_isExistStaticActor` | `0x00741B80` |
| 11 | `_prepareAllCommandStaticActor` | `0x0073C7B0` |
| 12 | `_getUTF8StringLength` | `0x0073C900` |
| 13 | `_getUTF8StringByteLength` | `0x0073CA50` |
| 14 | `_normalizeDisplayName` | `0x00753710` |
| 15 | `_replaceMacroCodeString` | `0x00753860` |

The names are the literals that each registrar installs. The
[boot contracts](boot-native-call-contract.md) and the
[widget contracts](widget-native-call-contract.md) record `_createActor`,
`_getStaticActor` and `_isInstanceOf`. The
[Global native contracts](global-native-contract.md#registration-and-dispatch)
cover orders 4, 5 and 9 to 15. `_defineClass` and `_defineBaseClass` have no
contract yet.

## Area natives

`_setInstanceRaid` (`0x006E3C10`) reads one bool and stores its low byte at the
area object `+0xBB`. It reads no world state. That the byte marks an instance
raid is `INFERRED` from the native name, and its readers were not traced.

`_getZoneName` (`0x006F9700`) takes no argument and pushes the `Utf8String` at
the area object `+0x64` through `0x007487C0`. The writer of that string was not
traced.

## Item reference natives

The two item natives work on the `ItemBase` reference of the
[scheduler and item contracts](scheduler-item-native-contract.md#item-packages).
The reference holds an owner at `+0x64`, a package key at `+0x68`, a slot at
`+0x6C` and a variant byte at `+0x70`.

`_countStack` (`0x00701920`) repeats the lookup of `_getCatalogID`. The variant
byte 1 selects `0x006EE480` and any other value `0x006EE3E0`. The callback pushes
the dword at record `+0x18`. It does not test the lookup result, so an absent
record reads the address `0x00000018`. That the dword is the stack count is
`INFERRED` from the native name. A received item record supplies it from wire
record `+0x08`, as the
[item record builders](scheduler-item-native-contract.md#item-record-builders)
show.

`_bindSpreadSheetData` (`0x006F54A0`) reads a `SpreadSheet` control through
`0x0071C080`. It compares the dword at `ItemBase` `+0x68` with the dword `0xFF`
at `0x00FE0508` and takes one of two paths. Neither path reads the variant byte
and neither tests the lookup result.

| Path | Condition | Record lookup | Recorded in |
| --- | --- | --- | --- |
| `0x006F5380` | key not `0xFF` | `0x006EE480` | the set at package manager `+0x54` |
| `0x006F5400` | key `0xFF` | `0x006EE3E0` | the set of the object that `0x007646D0` returns |

Both paths read the catalog id at record `+0x24` and test it with `0x006DFFC0`.
That routine calls slot 14 of the sheet handle at sheet `+0xB4` for the key
vector and scans it as pairs of a start key and a count. A true result inserts
the id through `0x007213F0` and then calls `0x00767120` on the object at
`Y +0x118` with the engine handle, the id and the sheet. The `0xFF` path first
looks up the dword pair at record `+0x10` and `+0x14` in the object at `Y +0x12C`
and does not test the result. `0x00767120` inserts the sheet into the set at
manager `+0x04` through `0x00781F00`, runs `0x006DECC0` on a new entry and calls
`0x006F0D80`, the row request of the
[SpreadSheet contracts](spreadsheet-native-contract.md#asynchronous-loads). That
the native makes the item row available to the sheet reads is `INFERRED` from
those calls.

`_getItemPackageFreeSpace` (`0x00708AC0`) is a thin adapter into `0x007027E0`.
The body reads a package number, subtracts 1 and finds the package of the
receiver. An absent package pushes 0. Otherwise `0x006E5A90` counts the zero
dwords between record `+0x14` and `+0x18` and the count is pushed. That the zero
dwords are free slots is `INFERRED` from the native name.

Five more natives share these helpers. Their callbacks were traced to the same
depth and are recorded as related rows in the manifest.

| Native | Callback | Behavior |
| --- | --- | --- |
| `_getMaxStack` | `0x00701870` | Pushes the dword at item record `+0x7C`. |
| `_isStackable` | `0x007018C0` | Pushes whether the dword at record `+0x7C` is above 1 by an unsigned compare. |
| `_isEquipping` | `0x00702280` | Looks the package key `0xFE` at `0x00FE050C` up for the slots 0 to `0x22` and pushes whether a nonzero record equals the item record. The slot count is the dword `0x23` at `0x00FE052C`. |
| `_hasItemPackage` | `0x00708B60` | Reads a 1-based package number through `0x00702880` and pushes whether `0x006E5BA0` finds the package. The [item package record](chara-desktop-native-contract.md#item-package-lookup) gives the full contract. |
| `_getExtendedTemporaryGroup` | `0x00708410` | Calls the `_getGroup` helper with the flag 1. |

## Group natives

`_countMember` (`0x006FFB90`) passes the address of receiver `+0x68` to
`0x006C02A0`. The routine loads the pointer there, reads the vector start at
`+0x84` and the end at `+0x88` and returns the byte difference shifted right by
4, or 0 for a null start. The count is pushed as an int.

`_isMember` (`0x006FFED0`) declares a `Which` over `LuaControl*` and
`IndividualIndex` and an int. A tag 4 cell is read through `0x0071BB80`,
converted to an identity through `0x00CC73B0` and looked up with `0x006C3560` on
the address of receiver `+0x68`. A tag 8 cell is read as two dwords. The lookup
uses a handle built from the second dword and, after a negative index with a
nonzero first dword, one built from the first. Any other tag or a negative index
pushes false. A found member pushes true when cell 1 is `Nil`. Otherwise cell 1
is read as an int and the result is whether the index equals that int minus 1.
The marshaller supplies a tag 6 placeholder when Lua omits the second argument,
so the position test is optional. That the index is the position in the member
list is `INFERRED` from the native name. The bodies behind `0x006C3560` were not
traced.

`_getGroup` (`0x007083F0`) is a thin adapter into the helper `0x00701140` with
the flag 0. The helper reads an int and asks the object at `Y +0xE4` for
the group of the receiver identity and the int through `0x006C4560`. A group
that fails the `0x006CB950` test pushes nil through `0x00748920`. Otherwise
`0x006E2240` creates the control through `0x00CC80A0`, or `0x00CC8140` for the
flag 1, with the immediate argument `0x012BFB65`. It casts the control to `GroupBase` and
copies 16 bytes of the group handle to control `+0x68`. The native pushes the
control through `0x00748B30`. The copy goes to the same offset that
`_countMember` and `_isMember` read, which is an `INFERRED` link. The
argument `0x012BFB65` is an unaligned `.data` address, not a hash or an id. The
first 11 bytes there are `01 02 03 0C 5D 08 01 00 00 00 00`. Its role
(`unknown`) and the group manager were not identified.

## Ledger rows

These rows of the unimplemented ledger have a registration, argument list,
return list, receiver check and callback contract: `_setNameplate`,
`_setNameplateVisible`, `_getStaticActorID`, `_isExistActor`, `_setInstanceRaid`,
`_getZoneName`, `_bindSpreadSheetData`, `_countStack`,
`_getItemPackageFreeSpace`, `_countMember`, `_isMember` and `_getGroup`. A client
that implements them still needs the nameplate presentation behind the listener,
the engine name tables, the area string and flag writers, the item and sheet
data and the group manager, which this record does not supply.

## Open

- The display name resolver queue behind `0x0076FD80`, the object behind
  `0x00771C20`, the slot table capacity at the chara record base and the
  meaning of the second int of `_setNameplate`.
- The engine name tables behind `0x00CD8870`, the state dwords and the node
  byte read by `_isExistActor`.
- The writers and readers of the area fields at `+0x64` and `+0xBB`.
- The classes of the world objects at `+0xDC`, `+0xE0`, `+0xE4`, `+0x118` and
  `+0x12C` of `Y`, the group handle class and the role of the `.data` argument `0x012BFB65`.
- Whether the Lua wrappers in `chara/charabaseclass_u`, `area/areabaseclass_u`,
  `item/itembaseclass_u` and `group/groupbaseclass_u` adjust the arguments.
- The process behavior of the invalid-parameter route, the unchecked slot number
  of `_setNameplate` and the lookups that read an address near zero.

The ranked list of the next natives lives in the
[fade, actor and group contracts](fade-actor-group-native-contract.md#open).
They cover `_addItem`, `_getMember`, `_isExistInClientMember`, `_delete` and
`_getCurrentAreaMaster`.

`_setNameplateColor` and `_setNameplateIcon` are bound to `CharaBaseClass`
(`chara/charabaseclass_u`) in the index, with 22 and 23 call sites in one script
each. They are registered at orders 29 and 30 of the `CharaBase` switchboard,
between `_setNameplate` and `_setNameplateVisible`, with the callbacks
`0x006E3E00` and `0x006E3F80`, and they are located only. They stay off the
ranked list because one distinct script ranks below the twentieth row, and they
are carried as related rows. The callback of `_setNameplateIcon` is traced in
the [bazaar appearance contract](bazaar-appearance-contract.md#native-nameplate-consumer).
The callback of `_setNameplateColor` was not traced.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes. The listings behind this
record came from a Capstone 5.0.7 x86-32 decode of the file through its
section table, and the `rel32` caller scan of `.text` described in the
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
| Switchboards and registrars | `0x007574A0,0x00753C30,0x00753CF0,0x00753DD0,0x00757B70,0x007582E0,0x00745230,0x0072EB30,0x007498F0,0x0073C660,0x0072E5F0,0x00749B90,0x00743C30,0x0074DE80,0x007560F0,0x0074CC20,0x0074D160,0x00755280` |
| List builders and wrappers | `0x0072B440,0x00728C20,0x00728B70,0x0072B5B0,0x0072C260,0x0073FEF0,0x00743020,0x00726510,0x00726460,0x00726300,0x00726670,0x00726E00,0x0072CDF0,0x0072CD40,0x007265C0,0x00725620,0x0072CAF0,0x0071A7F0` |
| Callbacks | `0x006F5F30,0x006E4100,0x006F9690,0x006DCD80,0x006E3C10,0x006F9700,0x006F54A0,0x00701920,0x00708AC0,0x006FFB90,0x006FFED0,0x007083F0` |
| Readers and parameter record | `0x0071BB80,0x0071C080,0x0071CD90,0x00581AE0,0x007702C0,0x0071BEB0,0x006DBF90,0x005819A0,0x0071BA00,0x0071CE70` |
| Nameplate listener | `0x00744C10,0x0076FF20,0x00744E70,0x0076FD80,0x00771C20,0x0075B630` |
| Actor name tests | `0x0078CB90,0x00CC7200,0x00CD9C60,0x00CD8870,0x00CE16C0,0x00CC7A00,0x00CC72A0,0x00CD5320` |
| Item and sheet helpers | `0x006EE480,0x006EE3E0,0x006F5380,0x006F5400,0x006DFFC0,0x007213F0,0x00767120,0x007646D0,0x006F0D80,0x007027E0,0x006E5A90,0x00702880,0x006E5BA0` |
| Group helpers | `0x006C02A0,0x006C3560,0x00701140,0x006C4560,0x006CB950,0x006E2240,0x00CC80A0,0x00CC8140,0x00748920,0x00748B30` |
| Related callbacks | `0x00701870,0x007018C0,0x00702280,0x00708B60,0x00708410,0x006E3E00,0x006E3F80` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
