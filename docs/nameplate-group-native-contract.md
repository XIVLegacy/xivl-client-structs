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
`+0x04`. With `R_world` the address that routine returns, `X = [R_world]`,
`Y = [X+0x04]`, `W = [Y]` and `V = [W]`, the chain of the
[scheduler contracts](scheduler-item-native-contract.md#world-object-and-identity-lookup).

The setup call at `0x0057A9E9` constructs an aggregate through `0x00773270`
and stores its result at route state `+0x04` at `0x0057AA1A`. Setup passes that
pointer to `0x007634B0`, which wraps it in a typed `Holder<CoreWork*>` and
retains the holder at the matching ScriptEnv `+0x220`. The selected
`0x00CC7510`/`0x00CD7910` chain reaches that holder. With the matching
initialized context, preserved holder/value and valid lifetime, `Y` is this
CoreWork aggregate. The explicit publication is recorded in
`xivl-decomp:docs/event/player-profile-work-accessors.md`, setup owner join,
and `xivl-decomp:docs/script/worldmaster-message-pool.md#quest-source-and-textmodule-join`.
It is separate from the scheduler contract's `INFERRED` identification of
`V = [[Y]]` as the container. That identification does not identify `Y`.

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

### Client group roles and membership guards

The selector compared with payload `+0x04` has source-qualified client uses.
The separate [GroupBase binding](binding-map-native-contract.md#group-natives)
reads group data `+0x04` through `_getKind`; its kind interpretation remains
inferred from that API. The authored callers below establish selector and
guard conventions, not an authoritative server enumeration. Lua paths are
relative to `xivl-client-scripts:lua/scripts/`.

| Numeric value / domain | Supported role or variant | Membership rule or closest client guard | Source / locator | Confidence / status | Remaining join |
| --- | --- | --- | --- | --- | --- |
| `10001`, Lua selector | `getPlayerParty`; first `getParty` candidate | Calls `_getExtendedTemporaryGroup(self,10001)` without a Lua class cast or membership test. | `chara/charabaseclass.lua:52-79`, `root/proto2` PC 2; `root/proto3` PCs 2-3; `xivl-client-scripts:docs/guildleve-party-continuity.md#party-leader-and-roster-presentation` | Observed caller; player-party convention supported by the authored name and roster consumer. | Exact `PlayerPartyGroup` registration, record writer and server roster. |
| `10002`, Lua selector | `getParty` fallback | Used only when the `10001` result is nil; no additional cast or roster test. | `chara/charabaseclass.lua:63-79`, `root/proto3` PC 7 | Observed fallback; exact class **UNESTABLISHED**. | Numeric-to-class registration/application and authoritative membership. |
| `20002`, community selector | `CompanyGroup.isCurrent`; linkshell command category | Current-group result must be nonnil and equal to `self`. Linkshell command membership/rank guards are separate. | `group/communitygroup/companygroup.lua:334-348`; `xivl-client-scripts:docs/linkshell-party-command-contracts.md#refusals-and-linkshell-operation-meaning` | Observed current-selection equality and published client command role. | Current-selection writer and server enrollment. |
| `30001`, `30006`, `_getKind` results | Selected content init/finalize notifications | Explicit `_isMember(localPlayer)` plus either exact kind permits rows 50011/50012. | `xivl-client-data:docs/party-content-lock-message-rows.md#proven-notification-callers` | Observed local conjunction; individual content categories **UNESTABLISHED**. | Exact kind writer/application and participant policy. |
| `50001`, relation selector | PartyInvite relation exclusion | The published predicate excludes a target already in that relation group; local relation-helper variants are qualified below. | `xivl-client-scripts:docs/linkshell-party-command-contracts.md#refusals-and-linkshell-operation-meaning`; `chara/charabaseclass.lua:185-230` | Observed caller exclusion; relation's human meaning **UNESTABLISHED**. | Relation producer and authoritative roster semantics. |
| `10001` / `0x2711`, incoming `0x017C +0x30` | A separate inbound branch discriminator | `0x006CC620` compares that field with the literal before its conditional path. | `xivl-decomp:docs/net/wire-protocol.md#type-tagged-high-opcode-route` | Observed comparison; header-to-selector binding **UNESTABLISHED**. | Writer/application equating this header field with the selected group data. |

`getContentGroup` and `getRelationGroup` forward a supplied selector to
`_getExtendedTemporaryGroup` without adding a kind check, cast or membership
test (`chara/charabaseclass.lua:96-105,173-182`).
`getCommunityGroup` selects an ordinal from
`_getAllExtendedTemporaryGroup(self,selector)` (`:1642-1652`), while
`getCommunityGroupCurrent` forwards the supplied selector to the current-group
getter (`chara/charabaseclass_cliprog.lua:357-366`). These methods do not define
an accepted kind range. The published
`xivl-client-scripts:docs/guildleve-party-continuity.md#content-group-and-party-are-separate-state`
separately qualifies `charaWork.currentContentGroup`, with zero returning nil.

The native `_isMember` contract above performs local identity lookup with an
optional member-position comparison. The authored `hasRelationGroup` first
asks `_getGroup` for its supplied selector. An omitted subject tests only
group existence. An actor subject requires a nonnil group and invokes
`_isMember(group,subject)`. Other subjects are compared with the roster's
member display names (`chara/charabaseclass.lua:185-230`). Original
`root/proto11` PC 20 at chunk `0xD47` makes the actor call; PC 21 jumps to
PC 24 at `0xD57`, which returns its result. The decompiled expression omits
that visible invocation.

`PartyGroupBaseClass.isPartyLeader(number)` requires a nonnil owner and calls
`_isMember(self,owner,index)`, returning that result. A nonnumeric subject is
compared directly with the owner (`group/partygroup/partygroupbaseclass.lua:34-55`).
Original `root/proto1` PC 12 at `0x245` makes the indexed call; PC 13 jumps
to its result return at PC 16, `0x255`. `CharaBaseClass.isPartyLeader` passes
itself to the player-party helper (`chara/charabaseclass.lua:82-93`). The
separate `getPartyLeader` getter also requires `_isAlive` on its returned
owner (`partygroupbaseclass.lua:14-31`); that is object validity, not leader
election or a server enrollment rule.

Recovered `CompanyGroup.getMemberIndex` rejects a nil or invalid actor and
an empty roster. At each index, successful world/client existence predicates
lead to `_isMember(self,actor,index)`. Otherwise it accepts a nonempty member
display name equal to the actor's display name. It returns the first matching
index, or zero (`group/communitygroup/companygroup.lua:389-461`). That local
identity fallback does not establish the server's membership or collision policy.

Authoritative party, linkshell, content and relation membership remains
**UNESTABLISHED** here. A kind/member record writer or application must bind
these client values and identities to authoritative enrollment. Vector size,
client resolution, casts, owner equality and roster presentation do not supply
that relation. Party request/outcome, refusal and recipient boundaries remain
in `xivl-client-data:docs/party-membership-message-rows.md#request-and-delivery-boundary`
and `xivl-client-data:docs/party-content-lock-message-rows.md`. Notification rows 50011/50012,
Lua log type 32 and content property index 1 retain their separate domains.

These caller observations use extraction `2012.09.19.0001`. The five decoded
members are `chara/charabaseclass.lua`, `chara/charabaseclass_cliprog.lua`,
`group/partygroup/partygroupbaseclass.lua`, `group/partygroup/playerpartygroup.lua`
and `group/communitygroup/companygroup.lua`; their exact identities are owned by
`xivl-client-scripts:manifests/scripts.json` and the archive declaration in
`xivl-client-scripts:manifests/private_lua_corpus.json`. Python 3.12.0 source
inspection established the recovered callers. For the original checks,
`xivl-client-scripts:tools/retail_script.py` unwrapped the LPB resources;
a separate Python 3.12.0 Lua 5.1 chunk reader checked the selected prototype
operands and result paths. Original LPB and decoded-chunk identities for
CharaBaseClass and PartyGroupBaseClass are recorded in
`xivl-client-scripts:docs/guildleve-party-continuity.md#original-inputs-and-tools`.

### Registry getter root and result

Let `O` be the object read from `Y +0xE4` and `R_registry` its first dword.
The thunk `0x006C4560` loads `R_registry` into `ECX` at `0x006C4568` and calls
`0x006C3E50` at `0x006C4572`, forwarding its three formal stack arguments
unchanged. In the getter, those arguments have these direct uses:

| Argument at getter entry | Direct use |
| --- | --- |
| Stack `+0x04` | Caller-supplied output address. |
| Stack `+0x08` | Forwarded unchanged as the second stack argument of `0x006C3B30` at `0x006C3EBC`. |
| Stack `+0x0C` | Pointer whose first dword is compared with the candidate payload dword at `+0x04` (`0x006C3E9B`-`0x006C3EA7`). |

The existing caller contract supplies the identity and int interpretation.
The getter's direct comparison establishes the int input as a dword selector
of payload `+0x04`; it does not assign a group-kind meaning to that field.

The getter saves `R_registry`, reads `H = [R_registry+0x18]`, forms
`C = R_registry+0x14` and reads the initial candidate `N = [H]` (`0x006C3E55`-`0x006C3E6D`). A local pair holds
`C` and `N`. Equality of `N` with the saved `H` takes the zero-result path
(`0x006C3E7E`-`0x006C3E82`). Otherwise the payload is `[N+0x18]`. A selector
mismatch takes the helper path at `0x006C3EC5`. A match calls `0x006C3B30`
with `ECX = payload`, first stack argument `R_registry` and second stack argument equal
to the getter's second argument. Only a nonzero `AL` reaches the selected
result (`0x006C3EC1`-`0x006C3EC3`). The
[existing client-member predicate](fade-actor-group-native-contract.md#group-natives)
describes that callee's identity comparison and resolve/cast test. Its result
is an additional client-side predicate, not proof of server membership.

On selector mismatch or zero `AL`, `0x006C3EC9` calls `0x0067B180` with the
address of the local pair in `ECX`. After normal return the getter reloads
both fields and branches back to its candidate checks (`0x006C3ECE`-
`0x006C3ED6`). The [pair update helper](#pair-update-helper) directly changes
the second field through conditional pointer walks. Candidate/container guards
also call `0x009D22B4`, the existing invalid-parameter route. Their process
effects were not established.

The two result paths directly write these dword lanes of the first argument:

| Output offset | Selected candidate | `N == H` | Store VAs, selected / zero |
| --- | --- | --- | --- |
| `+0x00` | `[N+0x18]` | `0` | `0x006C3EF7` / `0x006C3F14` |
| `+0x04` | No direct write | No direct write | None |
| `+0x08` | `[N+0x10]` | `0` | `0x006C3EFE` / `0x006C3F16` |
| `+0x0C` | `[N+0x14]` | `0` | `0x006C3F01` / `0x006C3F19` |

Both paths return the output address in `EAX` and end with `ret 0x0C`
(`0x006C3F08`, `0x006C3F20`). These argument/result interpretations assume
normal callee return with the caller's stack and nonvolatile-register
conventions preserved. In particular, `0x006C3B30` must remove the two pushed
argument dwords; the getter performs no caller stack correction. The callee's
epilogue was not inspected for this observation. The getter directly writes
twelve bytes across the sixteen-byte handle region copied by the control
builder. It does not directly initialize offset `+0x04`. Callee effects,
aliasing, ownership and reference-count semantics remain unestablished.

These observations came from Python 3.12.0 and Capstone 5.0.7 x86-32 decoding
of the authenticated original PE, VA `0x006C3E50` through `0x006C3F23`
exclusive, RVA `0x002C3E50`, file offset `2899536`. All 211 bytes decoded
contiguously. The range SHA-256 is
`097f2ce7d6a55ad675fa13564368c475b832b2479d253a78bbe130d94c3f9d76`.
The executable identity and section-table method are the ones in
[Binary and method](#binary-and-method). Transitive callee effects are limited
to the cited contracts and the direct helper observation below. Diagnostic
effects and runtime behavior remain unobserved.

#### Pair update helper

For `0x0067B180`, let `I` be entry `ECX`, `C = [I]` and `N = [I+4]`.
At the getter call, `I` addresses the local pair. The helper tests `C` against
zero at `0x0067B183` and calls `0x009D22B4` at `0x0067B188` if it is zero.
If that call returns with the expected stack and saved-register convention,
execution continues without rechecking `C`. The helper does not directly
dereference `C` to find a root or endpoint.

It loads `N` at `0x0067B18D` and tests byte `[N+0x21]`. A nonzero byte
restores `ESI` and tail-jumps to `0x009D22B4` at `0x0067B197`, without a
direct pair store. That target's return behavior, result and indirect effects
were not established. A zero byte selects these direct pointer walks:

| Initial condition | Direct walk and pair update | VAs |
| --- | --- | --- |
| For `Q = [N+8]`, byte `[Q+0x21] == 0` | Form `L = [Q]`. While byte `[L+0x21] == 0`, set `Q = L` and reload `L = [Q]`. Store the last `Q` to `[I+4]`, leaving the first `L` whose flag byte is nonzero in `EAX`. | `0x0067B19C`-`0x0067B1BE` |
| Byte `[Q+0x21] != 0` | Set `A = [N+4]`. While byte `[A+0x21] == 0` and current `[I+4] == [A+8]`, store `A` to `[I+4]` and reload `A = [A+4]`. Store the first `A` with a nonzero flag or an unequal link to `[I+4]`, also leaving it in `EAX`. | `0x0067B1BF`-`0x0067B1E2` |

The only direct non-stack stores are dwords to `[I+4]` at `0x0067B1BA`,
`0x0067B1D0` and `0x0067B1DE`. The second walk performs its intermediate
stores before reading the next `+0x04` link. Neither direct path writes
`[I]`, a separate root or a separate node. Aliasing can make a pair store
affect another object; disjointness was not established. Both direct paths
restore `ESI` and use a plain `ret`. The getter uses the reloaded pair field,
not this helper's `EAX`, as its next candidate.

Treating node `+0x00`, `+0x04` and `+0x08` as left, parent and right links,
and byte `+0x21` as an endpoint flag, gives an `INFERRED` binary tree successor
interpretation. The helper does not compare keys or prove that those links
form a tree. Pointer validity, stable links/flags, finite acyclic paths,
parent/child consistency and compatible endpoints are additional requirements.
Its loops have no iteration cap or cycle check. Arbitrary link arrangements
can loop or return the entry candidate, so strict advancement, key order and
termination are not unconditional results.

The getter ends its search when its candidate equals saved `H`. This helper
neither recovers nor compares `H`, so identifying its flagged endpoints with
that saved pointer remains unproved. Getter exhaustion also requires the walk
sequence to reach `H` and intervening calls to return normally. The existing
selector/predicate can end the search earlier with a selected result. Neither
walk establishes the header/carrier/world pointer association.

The helper observations came from Python 3.12.0 and Capstone 5.0.7 x86-32
decoding of the authenticated original PE, VA `0x0067B180` through
`0x0067B1E3` exclusive, RVA `0x0027B180`, file offset `2601344`. The catalog
extent was 99 bytes, all decoded contiguously. The range SHA-256 is
`aebc319b954f0474763d33eac95aedcf04118dcf7a6bf518b95c81531308764d`.
The binary identity and section-table method are those in
[Binary and method](#binary-and-method). Diagnostic target `0x009D22B4`
effects remain outside this direct helper observation.

#### CoreWork registry pointer publication

For constructor `0x00773270`, let `S` be entry `ESP` and `A6` the physical
dword at `[S+0x18]`. At `0x00773296`, `ESI` captures entry `ECX`. At `0x00773357`,
`EAX` receives the dword at current `ESP+0x3C`; the constructor's saved frame
places that at entry `ESP+0x18`, `A6`. At `0x0077336B`, it stores `EAX`
to `[ESI+0xE4]`. The intervening `0x00773367` store clears the original
input slot to zero after the capture; it does not change captured `EAX`.
The field receives that physical input dword. `A6` is a stack-cell label,
not a recovered source-language parameter ordinal. These stack and receiver
interpretations assume normal returns with the caller's stack/register
conventions preserved and no intervening alias-mediated input change.
The captured dword is copied without a local nonzero test, so zero is copied
by the same store.

With the matching published CoreWork as `Y`, this store supplies
`O = A6`. If that field, object and input value remain valid and
preserved until the getter, its root is `R_registry = [O]`. The direct store
does not identify the pointed-to object's class or prove either `P == O` or
`M == R_registry`. Aliasing, intervening writes and untraced callee effects
remain separate from the direct store observation.

The bounded input trace at call `0x0057A9E9` fixes the physical caller cell.
Let `Q` be `ESP` immediately after `0x0057A9B8` returns. Five
four-byte pushes at `0x0057A9D3`, `0x0057A9D8`, `0x0057A9D9`,
`0x0057A9DA` and `0x0057A9DB` precede the constructor call, with no other
stack adjustment, call or branch in between. Constructor-entry `ESP` is
therefore `Q-0x18`, making `A6 = [Q]`, subject to alias preservation.

That earlier call targets `0x00CC9500`, whose local return at `0x00CC951C`
removes four bytes. Let `B` be caller `ESP` immediately before the call,
after the address push at `0x0057A9B7`. A normal ABI-conforming return gives
`Q = B+4`, so the physical `A6` cell is at caller `ESP` immediately before
that push. The push at `0x0057A99A` reserves this cell. At `0x0057A99D`,
`EAX` captures its address; at `0x0057A9A7`, a four-byte store through `EAX`
writes `EDI` into it. The reservation's original bits are overwritten.

The `EAX` test at `0x0057A938` selects two producers for `EDI`. The zero
arm at `0x0057A94B` clears it. On the nonzero arm, let `G` be that tested
value and `F` the dword loaded from `[ESI+0x18]` at `0x0057A93C`.
The call at `0x0057A942` passes `G` as `ECX`, set at `0x0057A940`, and
pushes `F` at `0x0057A93F` to `0x006BFDA0`. That callee directly writes
the incoming stack dword to receiver `+0` at `0x006BFDA6`, returns the
original receiver in `EAX`, and removes its four-byte input at `0x006BFDA8`.
It has no calls or branches. Thus its normal return has initialized
`[G] = F` and returns `G`.

At `0x0057A947`, `EDI` captures that returned receiver. It is not directly
rewritten before the slot store at `0x0057A9A7`; preservation across the
intervening call assumes the normal nonvolatile-register convention. With
the pending cell preserved, the nonzero path therefore supplies `A6 = G`.
`F` labels the value loaded for this call; incoming `ESI`'s provenance and
the identity of its `+0x18` field remain unestablished. No pointer class or
valid registry object is inferred from these stores.

The wrapper's receiver is loaded from `[ESI]` at `0x0057A9B1`; incoming
`ESI`'s identity is not established. The address formed at `0x0057A9B3`
and pushed at `0x0057A9B7` is `Q+0x44`, distinct from the physical `A6`
cell. The wrapper captures dword `[entry ECX]` at `0x00CC9501` and the
supplied address at `0x00CC9504`. Its call at `0x00CC9513` passes that
address as `ECX` and the captured dword as a pushed input to `0x00CC77E0`.
The wrapper's only direct memory write at `0x00CC950B` clears its own
stack local. The tracked observation in
`xivl-decomp:docs/resource/sqwt-command-parameter-consumer.md#upstream-control-slot-4`
records `0x00CC77E0` writing its supplied pointer to wrapper `+0`.
Applied to this call, that direct initializer writes the captured source
dword to the supplied address. Its other alias effects and cleanup remain
unestablished. The wrapper returns the supplied address in `EAX` at
`0x00CC9518`; reaching its local epilogue normally requires the inner call
to balance its pushed dword.

With the matching initialized `Y` and preserved slot, field and lifetimes,
the nonzero arm supplies `O = A6 = G`. If `G`'s initialized first dword
also remains valid and preserved until the getter, `R_registry = [O] = F`.
The zero arm supplies `O = 0`, with no valid registry dereference asserted.
Neither `G != 0` nor the direct store proves that `F` is nonzero, live or
a valid getter root. `P == O` on the nonzero arm still needs `P == G`;
`M == R_registry` still needs `M == F` at the relevant uses. Those
identities do not follow from pointer shape or these initializers.

These store observations came from Python 3.12.0 and Capstone 5.0.7 x86-32
decoding of authenticated original PE span `0x00773270` through `0x00773654`
exclusive, RVA `0x00373270`, file offset `3617392`. The retained listing's
address/byte-width metadata and the catalog's summed size agreed on one
contiguous 996-byte span, with no excluded gaps. Its SHA-256 is
`e1214281ae864d83749b6b0d081598d0e03a7246209ab3105b8ccb38e197aa6e`.
The executable identity and section-table method are those in
[Binary and method](#binary-and-method).

The producer used the same tools and original PE. Listing address and
byte-width metadata authenticated one span `0x006BFDA0` through `0x006BFDAB`
exclusive, RVA `0x002BFDA0`, file offset `2882976`, with no gaps.
All 11 bytes decoded as four owned instruction units. Its SHA-256 is
`0d9d4797ad8c81da5b9f78b6e3eba5066720c9a41fbd098a5dac1e8581c3c29c`.

The wrapper used the same tools and original PE. Listing address and byte-width
metadata authenticated its single span `0x00CC9500` through
`0x00CC951F` exclusive, RVA `0x008C9500`, file offset `9213184`.
All 31 bytes decoded as 12 owned instruction units, with no gaps. Its
SHA-256 is
`bc41ec9fec00d42348d1b9e776f0d93d6de6fa3aee42407c1af8bc2c5163187e`.

The input trace used the same tool versions and only these caller spans.
Ends are exclusive. The cap starts at `0x0057A869`, inside an instruction;
that one-byte prefix is excluded. The three gaps between the rows are also
excluded. All 379 selected bytes decoded as 119 owned instruction units after
their address/byte-width metadata matched the original PE. No whole-caller
contiguity or transitive callee effects are claimed.

| Start VA | End VA | SHA-256 |
| --- | --- | --- |
| `0x0057A86A` | `0x0057A882` | `77b363e331025ee1d0da22244dda3ea6ba723874bda6aaa749d80d711e1e437b` |
| `0x0057A885` | `0x0057A8CF` | `478a47003ee09e04795d13959749660702e5ae3acce2e0cd4d76237951161a50` |
| `0x0057A8D2` | `0x0057A91C` | `b286f097067079f34ec4e53cc8db24c8052372532a994dfe06389458390979e9` |
| `0x0057A91F` | `0x0057A9EE` | `f5553e39c726c539dc0733db1142b59e51fef7114f7154e3b5f893173e72429e` |

The incoming header's child-record path passes outer carrier `P` to
`0x006D1DC0` with `ECX = headerOwner +0x0C`, with inner pointer `M = [P]`.
That path is recorded in
`xivl-decomp:docs/net/high-017c-object-builder.md#child-record-setup`.
No established pointer binding equates `P` with `O`, or `M` with `R_registry`.
The getter's root offsets, selector test and output lanes do not close that
association. Shared pointer shape or the header's type literal cannot supply
object identity.


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
`0x006E3E00` and `0x006E3F80`. They stay off the ranked list because one
distinct script ranks below the twentieth row, and they are carried as related
rows. Both callbacks are contracted in the
[presentation contracts](presentation-native-contract.md#nameplate-natives) and
the consumer of `_setNameplateIcon` is traced in the
[bazaar appearance contract](bazaar-appearance-contract.md#native-nameplate-consumer).

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
