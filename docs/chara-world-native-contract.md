# Group list, virtual item, status bit, spreadsheet container, word table, log and random float native contracts

[`manifests/chara_world_native_call_contract.json`](../manifests/chara_world_native_call_contract.json)
records the static Lua call contracts of thirteen native registrations. Seven
belong to `CharaBase`: the group list `_getAllGroup`, the virtual item builder
`_createVirtualItem`, the status bit readers `_getNetStatUser`,
`_getNetStatSystem` and `_getSubStatBreakage`, and the chara state reads
`_isAccessibleInServer` and `_getGear`. Two belong to `NpcBase` and manage the
item spreadsheet containers (`_preloadItemSpreadSheetContainer` and
`_releaseItemSpreadSheetContainer`). Three belong to `WorldMaster`: the word
table calls `_loadWord` and `_unloadWord` and the log call `_printDebugLog`. One
belongs to `Math`, the float generator `_randomFloat`. Each row gives the
registration site, the receiver type check, the declared argument and return
lists, the reads, the effects on client state, the failure behavior and whether
the call yields. The contracts describe client marshalling and state, not group
kinds, item ids, status bit meanings, sheet names, word table names, log routing
or server behavior.

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
second pass checked that every cited locator begins an instruction of its
decoded function and compared the operands, name literals, vftable cells, RTTI
names, jump table entries, constants and call targets named below with the
listings. `R`, `X`, `Y`, `W` and `V` name the world object chain of the
[fade contracts](fade-actor-group-native-contract.md#fade-natives) and the
[Global contracts](global-native-contract.md#binary-and-method). The registrar
shape, the type registry, the cell tags and the invalid-parameter route are the
ones of the [nameplate, actor and group contracts](nameplate-group-native-contract.md)
and the [work binder contracts](work-binder-native-contract.md#binary-and-method).

The call-site and chunk counts agree with
`xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. They show that a
script contains a call, not that a script reaches it at run time. The argument
counts, the constants and the chunk names of the calling functions come from a
local Lua 5.1 bytecode scan of the installed client scripts, decoded with
[`tools/decode_lpb.py`](../tools/decode_lpb.py). The script sources are not
redistributed and no tracked artifact carries those values, so they are
`INFERRED`.

## Ranking

The ranking covers the natives that `xivl-client-scripts:lua/napi_index.json`
binds to `CharaBaseClass`, `NpcBaseClass`, `WorldMaster`, `AreaBaseClass`,
`PrivateAreaBaseClass` and `Math`. It orders them by the number of distinct
scripts that contain a call, then by the call-site count, then by the class
order just given and then by the switchboard order. A native with a contract
row or a related record in any manifest is left out, and so are the script
callbacks that begin with `_on`, the work keys, the descriptor suffix
identifiers and the Lua level helpers. The look-at and turning, nameplate icon
and color, map marker, floating offset, character presentation (job and
visibility), temporary item and server bridge families are outside this
ranking.

| Rank | Native | Class | Scripts | Call sites |
| ---: | --- | --- | ---: | ---: |
| 1 | `_getAllGroup` | `CharaBaseClass` | 4 | 10 |
| 2 | `_createVirtualItem` | `CharaBaseClass` | 4 | 6 |
| 3 | `_getNetStatUser` | `CharaBaseClass` | 4 | 6 |
| 4 | `_printDebugLog` | `WorldMaster` | 3 | 5 |
| 5 | `_getSubStatBreakage` | `CharaBaseClass` | 3 | 3 |
| 6 | `_preloadItemSpreadSheetContainer` | `NpcBaseClass` | 2 | 8 |
| 7 | `_getNetStatSystem` | `CharaBaseClass` | 2 | 3 |
| 8 | `_isAccessibleInServer` | `CharaBaseClass` | 2 | 3 |
| 9 | `_randomFloat` | `Math` | 2 | 3 |
| 10 | `_getGear` | `CharaBaseClass` | 2 | 2 |
| 11 | `_releaseItemSpreadSheetContainer` | `NpcBaseClass` | 2 | 2 |
| 12 | `_loadWord` | `WorldMaster` | 2 | 2 |
| 13 | `_unloadWord` | `WorldMaster` | 2 | 2 |

Four natives that the ranking would otherwise select already have a record that
describes their body or arguments, so they are left out.

| Native | Class | Scripts | Call sites | Where recorded |
| --- | --- | ---: | ---: | --- |
| `_setReactionTriggerBox` | `NpcBaseClass` | 3 | 6 | [Reaction-box arguments](door-initialization-native-contract.md#reaction-box-arguments) |
| `_updateItemPackage` | `CharaBaseClass` | 2 | 7 | [Package and slot numbering](bazaar-native-wire-contract.md#package-and-slot-numbering) |
| `_countHamletSupplyRanking` | `AreaBaseClass` | 2 | 2 | [Hamlet ranking and score payloads](hamlet-wire-contract.md) |
| `_getHamletSupplyRanking` | `AreaBaseClass` | 2 | 2 | [Hamlet ranking and score payloads](hamlet-wire-contract.md) |

## Registration

Every native is declared by a `_u` script descriptor named `<name>_inl` that
returns the selector `self` and the target `<name>_cpp`. The descriptor tables
are `CharaBaseClass` in `chara/charabaseclass_u`, `NpcBaseClass` in
`chara/npc/npcbaseclass_u`, `WorldMaster` in `world/worldmaster_u` and `Math` in
`system/math_u` (`MEASURED`). The order of a native is its position among the
rel32 calls of its switchboard.

| Class | Switchboard | Vftable | Natives (order) |
| --- | --- | --- | --- |
| `CharaBase` | `0x007574A0` | `0x00FD5CAC` | `_getGear` (6), `_getSubStatBreakage` (12), `_getNetStatUser` (19), `_getNetStatSystem` (20), `_isAccessibleInServer` (22), `_getAllGroup` (43), `_createVirtualItem` (76) |
| `NpcBase` | `0x00754850` | `0x00FD647C` | `_preloadItemSpreadSheetContainer` (22), `_releaseItemSpreadSheetContainer` (23) |
| `WorldMaster` | `0x00754C70` | `0x00FD5864` | `_printDebugLog` (5), `_loadWord` (10), `_unloadWord` (11) |
| `Math` | `0x00740EC0` | `0x00FD559C` | `_randomFloat` (2) |

| Native | Switchboard | Registrar | Caller | Callback | Wrapper |
| --- | --- | --- | --- | --- | --- |
| `_getAllGroup` | `CharaBase` | `0x00755520` | `0x0075782E` | `0x00708430` | `0x00726460` |
| `_createVirtualItem` | `CharaBase` | `0x007568D0` | `0x00757AE3` | `0x00708E60` | `0x00726510` |
| `_getNetStatUser` | `CharaBase` | `0x0074B720` | `0x00757636` | `0x006FA250` | `0x00726510` |
| `_printDebugLog` | `WorldMaster` | `0x0073AEC0` | `0x00754CE0` | `0x006EC2F0` | `0x00726CA0` |
| `_getSubStatBreakage` | `CharaBase` | `0x0074B090` | `0x007575A3` | `0x006FA020` | `0x00726460` |
| `_preloadItemSpreadSheetContainer` | `NpcBase` | `0x0073F860` | `0x00754A25` | `0x006F2620` | `0x0072D4B0` |
| `_getNetStatSystem` | `CharaBase` | `0x0074B870` | `0x0075764B` | `0x006FA2C0` | `0x00726510` |
| `_isAccessibleInServer` | `CharaBase` | `0x0074BB10` | `0x00757675` | `0x006FA3A0` | `0x00726460` |
| `_randomFloat` | `Math` | `0x0073CBA0` | `0x00740EF1` | `0x006DDEE0` | `0x00726F60` |
| `_getGear` | `CharaBase` | `0x0074A8B0` | `0x00757525` | `0x006F9C70` | `0x00726460` |
| `_releaseItemSpreadSheetContainer` | `NpcBase` | `0x00746510` | `0x00754A3A` | `0x006F6480` | `0x0072D4B0` |
| `_loadWord` | `WorldMaster` | `0x0073B010` | `0x00754D49` | `0x006EC380` | `0x00726CA0` |
| `_unloadWord` | `WorldMaster` | `0x0073B160` | `0x00754D5E` | `0x006EC4B0` | `0x00726CA0` |

Every registrar builds the return list first and the argument list second and
installs the functor through `0x00CCCAD0` under the name literal with the
adjustment 0. Each has one rel32 caller in `.text` and no callback has one. The
holder invoke routine casts the receiver with `0x009DA6CC` from `LuaControl` to
the owner class and returns without calling the callback when the cast gives a
null pointer. The wrappers are recorded in the manifest framework.

| Wrapper | Owner class | Qualifier | Target type descriptor |
| --- | --- | --- | --- |
| `0x00726460` | `CharaBase` | const | `0x012709A4` |
| `0x00726510` | `CharaBase` | non-const | `0x012709A4` |
| `0x0072D4B0` | `NpcBase` | non-const | `0x012709E4` |
| `0x00726CA0` | `WorldMaster` | const | `0x012C1328` |
| `0x00726F60` | `Math` | non-const | `0x012C09E8` |

The readers are `0x005819A0` for an int, `0x00581AE0` for an int at an index,
`0x0071BAC0` for a float and `0x0071CE70` for a `Utf8String`. The return
pushers are `0x00584F70` for an int, `0x00748870` for a bool, `0x007489D0` for a
float and `0x00748B30` for a `LuaControl*`. The list builders are `0x0072B440`
for none, `0x00728B70` for a bool, `0x00728C20` for an int, `0x0072B5B0` for a
`Utf8String`, `0x0072BD30` for a `Utf8String` and an int, `0x0072C260` for a
`LuaControl*`, `0x0072B390` for a float, `0x0072C310` for two floats,
`0x0072B660` for three ints, `0x0073D5A0` for a `Utf8String` and three ints and
`0x0072B870` for a `LuaControlArray`. Each builder selects its entries through
the type registry of `0x00CCA210`. The registry constructor `0x00CC9D60` stores
the entries 10 to 13 after the nine entries of the nameplate record. Their RTTI
names are `LuaControlArray`, `LuaManyTentativeControlArray`, `IntegerArray` and
`VariantVectorArray`.

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_getAllGroup` | `CharaBase` | `int` | `LuaControlArray` | no |
| `_createVirtualItem` | `CharaBase` | `int`, `int`, `int` | `LuaControl*` | yes, after a failed first test |
| `_getNetStatUser` | `CharaBase` | `int` | `bool` | no |
| `_printDebugLog` | `WorldMaster` | `Utf8String` | none | no |
| `_getSubStatBreakage` | `CharaBase` | `int` | `bool` | no |
| `_preloadItemSpreadSheetContainer` | `NpcBase` | `Utf8String`, `int`, `int`, `int` | none | yes, always |
| `_getNetStatSystem` | `CharaBase` | `int` | `bool` | no |
| `_isAccessibleInServer` | `CharaBase` | none | `bool` | no |
| `_randomFloat` | `Math` | `float`, `float` | `float` | no |
| `_getGear` | `CharaBase` | none | `int` | no |
| `_releaseItemSpreadSheetContainer` | `NpcBase` | none | none | no |
| `_loadWord` | `WorldMaster` | `Utf8String`, `int` | none | no |
| `_unloadWord` | `WorldMaster` | `Utf8String`, `int` | none | no |

Only `_createVirtualItem` and `_preloadItemSpreadSheetContainer` call the yield
request `0x00CD2860`. The manifest rows carry each name literal, name reference,
install call, callback load and list builder.

## Group list

`_getAllGroup` (`0x00708430`) passes the `ExecuteParameters` pointer and the
flag 0 to the helper `0x00701250` and never reads its receiver. The helper takes
`R`, `X` and `Y` from the world chain and the dword at `Y +0xE4`, the pointer
to the object whose first dword is the group registry. The group lookup of
`_getGroup` in the
[nameplate and group contracts](nameplate-group-native-contract.md#group-natives)
uses the same object. The tag of cell 0 selects the lookup.

| Cell 0 | Call | Result |
| --- | --- | --- |
| Tag 6, an omitted argument | `0x006C5840` with the identity address `ExecuteParameters +0x0C` | The groups of the identity. |
| Tag 0 | The int through `0x00581AE0`, then `0x006C5850` with the identity address and the int address | The same groups with the dword at group record `+0x04` equal to the int. |
| Any other tag | None | An empty result. |

Both thunks load the dword at their `ecx` as the registry and jump to
`0x006C46F0` or `0x006C47B0`. The routines reserve the result vector to the count
at registry `+0x1C` through `0x006D4860`, with `0x10` byte elements. They walk the
list headed by the registry dword at `+0x18` and call `0x006C3B30` on the group
record at node `+0x18` with the registry and the identity address. A nonzero
result appends an element built from the dwords at node `+0x10`, `+0x14` and
`+0x18`. The int variant first compares the dword at group record `+0x04` with
the int. The helper pushes the element count through `0x00584F70`, then calls
`0x006E2240` for every element and pushes the control through `0x00748B30`.
`0x006E2240` is the control creation of the `_getGroup` record. It creates the
control through `0x00CC80A0` for the flag 0, casts it to `GroupBase` and copies 16 bytes
of the element to control `+0x68`. The return list is one `LuaControlArray`. Its
push slot `0x00CFA1D0` reads the count cell and that many control cells and
builds one Lua table. The count is always pushed first, so an empty result is an
empty table and the nil branch for a first cell of tag 6 is not taken.

The shipped scripts contain 10 call sites in 4 chunks (`MEASURED`). Three pass no
argument, six pass one argument and one passes an argument list that ends in a
call or vararg. Three of the one argument sites pass the constant 20002
(`INFERRED`, local scan). The
[client group roles and membership guards](nameplate-group-native-contract.md#client-group-roles-and-membership-guards)
qualify the numeric callers and local predicates. The registry contents,
group-record writers, authoritative membership and the element layout that
`0x006D5F80` appends remain unestablished.

## Virtual item creation

`_createVirtualItem` (`0x00708E60`) builds the inert helper `0x006DD450` and
calls the body `0x00702A20`, as `_hasItemPackage` does in the
[chara and desktop contracts](chara-desktop-native-contract.md#item-package-lookup).
The body reads three ints. Cell 0 and cell 2 are read with no default and cell 1
stores the value 1 when its tag is 6. A short vector reaches `0x009D22B4`.

| Step | Instructions | Effect |
| --- | --- | --- |
| Package key | `0x00702B32` | The key is the dword at `0x00FE0508`, which holds `0xFF` in the file. The equipping key of `_isEquipping` is the dword `0xFE` at `0x00FE050C`. |
| Manager | `0x006F51A0`, `0x006E5BA0` | The lazy item package manager at receiver `+0xD8` is searched for the key. |
| New record | `0x00702B69..0x00702BF7` | A missing record allocates `0x24` bytes, is constructed by `0x006EF0D0` and registered by `0x006F19D0`. |
| Item object | `0x00702C05..0x00702C9E` | `0x00758E00` on `Y +0x128`, `0x0076B4C0` on `Y +0x12C` with the Lua thread, then `0xD0` bytes constructed by `0x006EF490`. |
| Checker | `0x006E0440` | A `CreateClientItemResumeChecker` is built on the stack. |
| First test | `0x006F6A80` | A result of 1 pushes the dword at checker `+0x18` as a control. |
| Yield | `0x006E0550`, `0x00CD2860` | Otherwise the fields move to a heap checker and the native requests a yield with it. |

The checker class has the vftable `0x00FD5958` over the base `0x00FD4F5C`, whose
RTTI names are `CreateClientItemResumeChecker` and
`ResumeCheckerInterface`. The constructor `0x006E0440` stores its four arguments
at `+0x0C`, `+0x10`, `+0x14` and `+0x1C`, its byte argument at `+0x20`, clears
`+0x18` and `+0x21` and builds a `0x10` byte member at `+0x08`. `0x006F6A80`
tests the byte at `+0x21`. A zero byte calls `0x006E2D30` on the dword at
`+0x08`, stores the result in the byte and, on success, stores the result of
`0x006E2770` at `+0x18`. It returns 1 only when the byte is 1 and `0x006ED9E0` on
the dword at `+0x0C` returns 1. The return of the Lua call after a resumed yield
was not traced.

The shipped scripts contain 6 call sites in 4 chunks (`MEASURED`). Every site
passes three arguments, five pass the constant 1 as the second and four pass the
constant 1 as the third (`INFERRED`, local scan). The first int being an item id,
the second a quantity and the third a further item parameter is `INFERRED` from
the native name, the default and the call sites. The mapping of the three ints
into the item object and the package record was not traced.

## Status bit natives

`_getNetStatUser`, `_getNetStatSystem` and `_getSubStatBreakage` read one int and
push whether one bit of a status dword is set.

| Native | Source dword | Bit tested | Out of range |
| --- | --- | --- | --- |
| `_getNetStatUser` | Status record `+0x10` of `CharaBase +0xDC` | The int plus 7, taken modulo 32 | Wraps, no test. |
| `_getNetStatSystem` | The same dword | The int plus 15, taken modulo 32 | Wraps, no test. |
| `_getSubStatBreakage` | Chara `+0xF8` of the identity | 8 minus the int, for 1 to 8 | Pushes false. |

The two net stat natives call `0x006EEC00` on the receiver. It returns the dword
at receiver `+0xDC` and, when that dword is null, allocates `0x1C` bytes,
constructs a record with `0x006EEA80` and stores the pointer. The constructor
zeroes the dwords at `+0x04` through `+0x14` and the byte at `+0x18` and
reserves and resizes the dword vector at `+0x04` to `0x14` elements through
`0x007222D0` and `0x00722DA0`, so a fresh record holds 0 at `+0x10`. The native
creates the record on the first read. The callbacks load the dword at `+0x10`,
shift it right with the `cl` register, which masks the count to 5 bits, and push
whether the low bit equals 1. The
[status effect findings](../manifests/status_effect_findings.json) record the
same dword as the packed word whose bits 8 to 15 are the NetStatUser facet with
the index equal to the bit position minus 7 and whose bits 16 to 18 are the
NetStatSystem facet with the index equal to the bit position minus 15. That
record is a repository relationship. The natives do not enforce the ranges 1 to
8 and 1 to 3.

`_getSubStatBreakage` copies the identity at `ExecuteParameters +0x0C` and passes
its address to `0x0075C1D0` on `W`. That routine loads `V`, searches the identity
registry at `V +0x4AC` through `0x004D9970` and returns the dword at `+0xF8` of
the found chara through `0x00585410`. The int minus 1, as an unsigned compare
against 7, indexes the jump table at `0x006FA0D4`. Its cells select the right
shifts 7, 6, 5, 4, 3, 2, 1 and 0 and the result is the low bit after the shift. An
int outside 1 to 8 leaves the value 0 and pushes false. The same status effect
findings record lists kind 1 as bit 7 and kind 8 as bit 0 for the breakage
facet, which agrees. That record names the status word as a second Lua argument,
while the callback reads one int and takes the word from chara `+0xF8`. The
record also places the breakage bits in a status dword of the `CharaBase +0xDC`
substruct, while the callback reads the dword at `+0xF8` of the chara that the
identity registry at `V +0x4AC` returns. The relationship between the two
locations was not traced. No
instruction tests the registry result before the load, so the run time result for
an identity that is absent from the registry is unknown.

The shipped scripts contain 6 call sites of `_getNetStatUser` in 4 chunks, 3 of
`_getNetStatSystem` in 2 chunks and 3 of `_getSubStatBreakage` in 3 chunks
(`MEASURED`). Every site passes one argument. The net stat sites pass the
constants 1 and 2 and the breakage sites pass a variable (`INFERRED`, local
scan). The writers of the status record, of the dword at chara `+0xF8` and the
names of the bits were not traced here.

## Chara state reads

`_isAccessibleInServer` (`0x006FA3A0`) takes no argument. It compares the byte at
receiver `+0x5D` with 0 and pushes the `sete` result through `0x00748870`. The
byte being 0 is the true result. `_getGear` (`0x006F9C70`) takes no argument. It
passes the identity address to `0x0075C2E0` on `W`, which searches the identity
registry as above and returns the word at `+0x210` of the found chara. The
callback zero extends the word and pushes it as an int through `0x00584F70`. No
instruction tests the registry result before the load, so the result for an
absent identity is unknown. Neither native requests a yield.

`_isAccessibleInServer` has 3 call sites in 2 chunks and `_getGear` has 2 call
sites in 2 chunks (`MEASURED`), none with an argument (`INFERRED`, local scan).
That the byte is a server reachability flag and the word a gear state is
`INFERRED` from the native names. The writers of both fields were not traced.

## Spreadsheet containers

`_preloadItemSpreadSheetContainer` (`0x006F2620`) declares a `Utf8String` and
three ints and returns nothing. It reads the name from cell 0 and the ints from
cells 1, 2 and 3. It builds the five names `itemDataSheet`, `equipmentSheet`,
`weaponSheet`, `armorSheet` and `accessorySheet` and resolves each through
`0x00CC7A20` on the world handle, casting the result from `LuaControl` to the
`SpreadSheet` type descriptor `0x012C2308`. The five controls fill a vector. The
callback then takes the sheet manager pointer that `0x004D74C0` returns for
`V +0x174F8` and calls its virtual slot 1 with the name from cell 0. The
returned pointer, the three ints, the vector and the address of receiver
`+0x134` go to `0x007258C0`, which constructs a `0x40` byte
`s_PreloadResumeChecker` with the vftable `0x00FD6150`. It stores the pointer at
`+0x04`, the ints at `+0x08`, `+0x0C` and `+0x10`, a copy of the vector at `+0x14`
and the receiver address at `+0x24`. The callback requests a yield with the
checker through `0x00CD2860` and tests nothing first.

`_releaseItemSpreadSheetContainer` (`0x006F6480`) declares no argument and no
return. It resolves the same five sheet controls and walks the dword vector
between receiver `+0x138` and `+0x13C`. For each value it calls `0x006DFFC0` on
each sheet and, for a nonzero result, `0x006F63A0` on that sheet with the world
handle and the value. That routine works on the list at sheet `+0xB8` and the
container at sheet `+0xC4`. The callback then erases the whole vector. It requests
no yield.

The shipped scripts contain 8 call sites of the preload in 2 chunks and 2 call
sites of the release in 2 chunks, all in `populacecompanyshop` and
`populacecompanysupply` (`MEASURED`). Every preload site passes four arguments.
Four pass `gcSealShopItem`, the constant 0 and two table lookups. Four pass
`itemGcExSupply`, the constant 0 and the pairs 1001 and 1029, 2001 and 2018, 3001
and 3018, and 4001 and 4014 (`INFERRED`, local scan). The first int being a mode
and the last two the first and last row of a range is `INFERRED` from those
constants. That the vector at receiver `+0x138` holds the containers that the
preload registered is `INFERRED` from the shared offset. The class of the sheet
manager, its slot 1 answer, the checker poll and the predicate `0x006DFFC0` were
not traced.

## Word tables

`_loadWord` (`0x006EC380`) and `_unloadWord` (`0x006EC4B0`) read a `Utf8String`
from cell 0 and an int from cell 1 and return nothing. Each builds a `Utf8String`
from the literal `xtx/` (`0x00FD4E28` and `0x00FD4E30`) and calls `0x0044AB90`
with a result string, that prefix and the name. The routine copies, appends and
copies again, so the result is the prefix followed by the name, which is
`INFERRED` from the call shape. The callback then calls `0x0075CD00` or
`0x0075CD40` on `W` with the path and the int.

| Native | Routine | Table call | Slot call |
| --- | --- | --- | --- |
| `_loadWord` | `0x0075CD00` | `0x0056D990` on the object at `V +0x8BC`, which calls `0x00CA71A0` | Virtual slot 9 (offset `0x24`) of the object at `V +0x664` |
| `_unloadWord` | `0x0075CD40` | `0x0056D9F0` on the object at `V +0x8BC`, which calls `0x00CA7120` | Virtual slot 10 (offset `0x28`) of the object at `V +0x664` |

`0x0056D990` and `0x0056D9F0` compare the path through `0x00445D20` with the three
`Utf8String` records of the static array that starts at `0x01338158`, with the
stride `0x54` and the end `0x01338254`. A match whose pointer at the object `+0x60`
plus 4 times the index is nonzero calls the table routine with the int. A path with
no match returns false. Neither native requests a yield. Each has 2 call sites in
the chunks `item/itembaseclass` and `quest/questbaseclass`, both with an argument
list that ends in a call or vararg (`MEASURED`, `INFERRED`). The three record
names, the routines `0x00CA71A0` and `0x00CA7120` and the object behind `V +0x664`
were not traced.

## Debug log

`_printDebugLog` (`0x006EC2F0`) is registered under the `WorldMaster` wrapper but
does not read its receiver. It constructs a stack `Debug` control with
`0x006DC5D0` (vftable `0x00FD51DC`), calls the `Debug` member `0x006E7AB0` and
destroys the temporary. The member reads a `Utf8String` from cell 0, builds a
`Utf8String` from the literal `<debug>` at `0x00FD46D4` and calls `0x0075D4C0`
with the world handle, the category `0x1F`, the literal string, the message and
the byte 0. That routine loads `V` from `W` and calls `0x004D6D90`. With the byte
0 the routine tests the log sink pointer at `V +0x660`, which the
[fade contracts](fade-actor-group-native-contract.md#fade-natives) record. A
nonzero pointer is the `this` of `0x004CE760`, called with the category, the
literal string and the message. A null pointer returns at once. The native
requests no yield.

It has 5 call sites in 3 chunks, `chara/player/playerbaseclass`,
`command/debuginputcommand` and `system/debug` (`MEASURED`). Every site passes one argument
(`INFERRED`, local scan). The class of the sink, the body of `0x004CE760`, the
meaning of the category and the formatting path of `0x004D6D90` for a nonzero
byte were not traced.

## Random float

`_randomFloat` (`0x006DDEE0`) reads two floats through `0x0071BAC0` and returns
one float. It builds the inert helper `0x0078BEB0` and calls the body `0x0078D130`
with the address of receiver `+0x64`. The body advances the state dword with the
generator of `_randomInteger` in the
[binding map contracts](binding-map-native-contract.md): the state times
`0x41C64E6D` plus `0x3039` is stored back, shifted right by 16 and masked with
`0x7FFF` to give `r`.

| Step | Value |
| --- | --- |
| Unit | `r` times the double `3.0517578125e-05` at `0x00FE0568`, which is 2 to the power -15, stored as a 32 bit float. |
| Candidate | The float of `lo` plus the unit times the double `hi` minus `lo`. |
| Lower clamp | A candidate below `lo` is replaced by `lo`. |
| Upper clamp | A candidate that is not below `hi` is replaced by `lo` plus `hi` minus `lo` times the double `0.999969482421875` at `0x00FE0580`, which is 32767 over 32768. |

The result goes through the float pusher `0x007489D0`. The native requests no
yield. It has 3 call sites in 2 chunks, `commanddebugger/commanddebuggerdev` and
`commanddebugger/commanddebuggergm`, each with two arguments of which the first is
the constant 0 (`MEASURED`, `INFERRED`). The initial value and other writers of
the state dword and the result for `lo` above `hi` were not run.

## Related registration

`_transformIntoChocobo` registers under two classes with the same name literal
`0x00FD6800`. The `WorldMaster` registrar `0x0073BA90` is order 19, declares two
ints and installs the callback `0x006EC5E0`. The `CharaBase` registrar
`0x00730420` is order 81, declares one int and installs `0x006DC330`, a bare
`ret 4`. The descriptor table of `chara/charabaseclass_u` does not name it and
the one of `world/worldmaster_u` does. The `WorldMaster` callback reads two ints, walks the control list from `0x00CC88D0`,
builds a `s_CharaIterateActorClass` object (vftable `0x00FD590C`, base
`CharaIterateInterface`) and a `s_WaitForTransformIntoChocoboResumeChecker`
(vftable `0x00FD5918`) and requests a yield with the second. The manifest
`relatedNatives` list carries one row per registration. The control filter, the use of
the two ints and the checker poll were not traced.

## Ledger rows

These rows of the unimplemented ledger have a registration, argument list,
return list, receiver check and callback contract: `_getAllGroup`,
`_createVirtualItem`, `_getNetStatUser`, `_printDebugLog`, `_getSubStatBreakage`,
`_preloadItemSpreadSheetContainer`, `_getNetStatSystem`,
`_isAccessibleInServer`, `_randomFloat`, `_getGear`,
`_releaseItemSpreadSheetContainer`, `_loadWord` and `_unloadWord`. A client that
implements them still needs the group registry behind `Y +0xE4`, the item
package manager and the `CreateClientItemResumeChecker` poll, the status record
at `CharaBase +0xDC` and the dword at chara `+0xF8`, the sheet manager behind
`V +0x174F8` and the `s_PreloadResumeChecker` poll, the word table array at
`0x01338158` and the state dword at `Math +0x64`.

## Not traced

- The group registry contents, group-record writers and authoritative membership.
  The [client group roles](nameplate-group-native-contract.md#client-group-roles-and-membership-guards)
  qualify the supported selectors and client predicates.
- The mapping of the three `_createVirtualItem` ints into the item object, the
  poll that the yield request makes and what a resumed script receives.
- The writers of the status record at `CharaBase +0xDC`, of the dword at chara
  `+0xF8`, of the byte at `CharaBase +0x5D` and of the word at chara `+0x210`.
- The class of the sheet manager at `V +0x174F8`, its slot 1 answer, the
  `s_PreloadResumeChecker` poll and the predicate `0x006DFFC0`.
- The names in the static array at `0x01338158`, the routines `0x00CA71A0` and
  `0x00CA7120` and the object behind `V +0x664`.
- The log sink behind `V +0x660` and the category `0x1F`.
- The initial value of the state dword at `Math +0x64`.

## Next natives

The next natives follow the ranking above. The table lists the natives that
remain after the selected rows and the left out records.

| Rank | Native | Class | Scripts | Call sites | Why |
| ---: | --- | --- | ---: | ---: | --- |
| 14 | `_transformIntoChocobo` | `WorldMaster` | 1 | 4 | Order 19 of the WorldMaster switchboard. A second registration under CharaBase is recorded in `relatedNatives`. |
| 15 | `_getSubStatStatus` | `CharaBaseClass` | 1 | 3 | Order 15 of the CharaBase switchboard. |
| 16 | `_getSystemFlag` | `CharaBaseClass` | 1 | 2 | Order 21 of the CharaBase switchboard. |
| 17 | `_getGroupCurrent` | `CharaBaseClass` | 1 | 2 | Order 48 of the CharaBase switchboard. |
| 18 | `_getSubStatWaste` | `CharaBaseClass` | 1 | 1 | Order 8 of the CharaBase switchboard. |
| 19 | `_getSubStatGuard` | `CharaBaseClass` | 1 | 1 | Order 9 of the CharaBase switchboard. |
| 20 | `_getSubStatChant` | `CharaBaseClass` | 1 | 1 | Order 10 of the CharaBase switchboard. |
| 21 | `_getSubStatObject` | `CharaBaseClass` | 1 | 1 | Order 11 of the CharaBase switchboard. |
| 22 | `_getSubStatMotionPack` | `CharaBaseClass` | 1 | 1 | Order 13 of the CharaBase switchboard. |
| 23 | `_getSubStatMode` | `CharaBaseClass` | 1 | 1 | Order 14 of the CharaBase switchboard. |

The manifest rows under `nextTranche` carry the same order.

The rows of `_transformIntoChocobo`, `_getSubStatStatus` and `_getSystemFlag` are
in the [achievement, target, group, item package, reaction box, Chocobo and cut scene native contracts](achievement-target-native-contract.md).

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes with the route of the
[binding map contracts](binding-map-native-contract.md#reproduction). The argument
counts and the constants come from the `.le.lpb` files of an installed client,
decoded by [`tools/decode_lpb.py`](../tools/decode_lpb.py) and read with a Lua 5.1
bytecode parser over the `SELF` call sites. They are `INFERRED` because no tracked
artifact carries them. The function VAs for `$Addresses` are:

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Registrars | `0x00755520,0x007568D0,0x0074B720,0x0073AEC0,0x0074B090,0x0073F860,0x0074B870,0x0074BB10,0x0073CBA0,0x0074A8B0,0x00746510,0x0073B010,0x0073B160` |
| Switchboards and holders | `0x007574A0,0x00754850,0x00754C70,0x00740EC0,0x00726460,0x00726510,0x00726CA0,0x0072D4B0,0x00726F60,0x0071E1E0,0x0072D1B0,0x0071AE70,0x0071AF90` |
| Callbacks | `0x00708430,0x00708E60,0x006FA250,0x006EC2F0,0x006FA020,0x006F2620,0x006FA2C0,0x006FA3A0,0x006DDEE0,0x006F9C70,0x006F6480,0x006EC380,0x006EC4B0,0x006EC5E0,0x006DC330` |
| List builders and registry | `0x0072B870,0x0072B660,0x0072C310,0x0072B390,0x0073D5A0,0x0072B5B0,0x0072BD30,0x0072C260,0x00728B70,0x00728C20,0x0072B440,0x007270B0,0x007271F0,0x00CC9D60,0x00CFA1D0` |
| Group list | `0x00701250,0x006C5840,0x006C5850,0x006C46F0,0x006C47B0,0x006D4860,0x006C3B30,0x006E2240,0x00581AE0` |
| Virtual item | `0x00702A20,0x006DD450,0x006DD4D0,0x006F51A0,0x006E5BA0,0x006EF0D0,0x006F19D0,0x006EF490,0x00758E00,0x0076B4C0,0x006E0440,0x006DF2F0,0x006F6A80,0x006E0550,0x006E2D30,0x006E2770,0x006ED9E0,0x00CD2860` |
| Status bits | `0x006EEC00,0x006EEA80,0x007222D0,0x00722DA0,0x0075C1D0,0x004D9970,0x00585410,0x0075C2E0` |
| Spreadsheet containers | `0x0075F5A0,0x004D74C0,0x007258C0,0x00CC7A20,0x006DFFC0,0x006F63A0` |
| Word tables | `0x0075CD00,0x0075CD40,0x0044AB90,0x0056D990,0x0056D9F0,0x004D7520,0x004D74F0,0x00445D20,0x00CA71A0,0x00CA7120` |
| Log and random | `0x006DC5D0,0x006E7AB0,0x0075D450,0x0075D4C0,0x004D6D90,0x004CE760,0x0078D130,0x0078BEB0,0x0078BEC0` |
| Related registration | `0x0073BA90,0x00730420,0x00CC88D0` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
