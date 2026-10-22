# Script binding map and character, group, item, world, math and player control native contracts

[`manifests/binding_map_native_call_contract.json`](../manifests/binding_map_native_call_contract.json)
records how a Lua name reaches a registered native, including the receiverless
names of the `Global` class, and the static Lua call contracts of thirteen
native registrations. Four character queries read a chara object (`_getPos`,
`_getDir`, `_getActorMainStat` and `_getDisplayName`). Four group queries read
the group data (`_isExistInWorldMember`, `_getMemberDisplayName`,
`_getDisplayName` and `_getKind`). Two item queries read an item reference
(`_getPackage` and `_getKind`). One world query reads the special event work
(`_getSpecialEventWork`), one `Math` call draws a random integer
(`_randomInteger`) and one player call unlocks player control
(`_unlockPlayerControl`). Four more names are script surfaces and not functor
natives (`_isAlive`, `_math`, `_string` and `_table`). Each row gives the
registration site, the receiver type check, the declared argument and return
lists, the reads, the effects on client state, the failure behavior and whether
the call yields. The contracts describe client marshalling and state, not name
presentation, group membership values, event work values, random seeds or
server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data
at the cited addresses. `MEASURED` is counted or parsed by the method named in
the fact, from the executable or from the Lua 5.1 bytecode of the installed
client scripts. `INFERRED` is a name or role taken from the surrounding
instructions that the bytes do not state. `unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
Addresses are absolute VAs. The instruction listings were decoded directly
from the PE bytes through the section table after the size and hash were
checked. Callers were found by scanning `.text` for `rel32` `call` and `jmp`
instructions, so virtual and indirect callers are not covered.

The script facts come from the Lua 5.1 bytecode of the installed client
scripts. The files were decoded with [`tools/decode_lpb.py`](../tools/decode_lpb.py)
and read with a bytecode parser, so no decompiler output is an evidence
dependency. The script sources are not redistributed. The tracked metadata of
`xivl-client-scripts:lua/registry.json` and `lua/napi_index.json` holds names
and line numbers only. The per-row `corpusCallSites` records carry the call-site
counts from `xivl-client-scripts:lua/napi_index.json`. They show that a script
contains a call, not that a script reaches it at run time.

## Script binding map

The earlier contracts follow the registrar of a native and its callback. This
section follows the other end, the Lua name.

### Registered key

Every native is stored in its class table under its registered name followed by
the suffix `_cpp`. The engine builds the string `_cpp` from the literal at
`0x00FDF2CC` in `0x007634B0` and stores it at engine implementation `+0x1C`
through `0x00CC96A0` and `0x00CD7630`. The registration routine `0x00CE1750`
that sits behind the install call `0x00CCCAD0` loads that field, concatenates it
to the registered name through `0x0044AB90` and stores the pooled result at
record `+0x44`. `0x00D07820` then pushes the name of record `+0x44` as the table
key and installs a C closure of `0x00D08000` with the record as its light
userdata. A registrar that installs `_getPosition` therefore provides the key
`_getPosition_cpp`. That the concatenation is the table key and that the
descriptor resolver reads the same string are `INFERRED` from the call
sequence.

A scan of the callers of `0x00CCCAD0` finds 409 install sites that register 393
distinct names (`MEASURED`).

### Descriptors

Each `_u` script assigns functions named `<name>_inl` to a class table. A
descriptor takes no meaningful argument. It returns two strings, a selector and
a key. The resolver `0x00D07890`, which `xivl-decomp:docs/script/lua-call-function-bridge.md`
describes, calls the descriptor with no argument and two results, searches the
key in the selected table and in its registered parents and stores the function
it finds under the descriptor name without the `_inl` suffix. The stored value
is the registered closure itself. The selector `self` selects the class table
that receives the assignment. Any other selector is resolved as a class record
name through `0x00CD8870`.

The 26 `_u` scripts hold 439 descriptors in 19 files, because 7 files hold no
code (`MEASURED`). Of those, 376 return a `_cpp` key and 63 return a `_lua`
key, which names a Lua helper from the embedded chunks. 414 use the selector
`self` and 25 use `global`. The scripts also hold 18 plain functions without an
`_inl` suffix. Every `_cpp` key resolves to a registered name. The 376 `_cpp`
descriptors name 366 distinct registered names. The other 27 registered names
have no `_cpp` descriptor, among them `_getInstanceName`, `_getLowResolutionTime`
and `_setTargetNearestCharacter`. The check is by name over all classes, so it
does not list a name that another class targets.

### Aliases

Eight descriptors return a key that differs from their own name. The Lua name is
an alias of the registered native. Scripts call the alias, and the registered
name does not occur in any script.

| Lua name | Class | Registered native | Order |
| --- | --- | --- | ---: |
| `_getPos` | `CharaBaseClass` | `_getPosition` | 1 |
| `_getDir` | `CharaBaseClass` | `_getDirection` | 2 |
| `_setPos` | `CharaBaseClass` | `_setPosition` | 3 |
| `_setDir` | `CharaBaseClass` | `_setDirection` | 4 |
| `_turnDir` | `CharaBaseClass` | `_turnClientDir` | 61 |
| `_getAllExtendedTemporaryGroup` | `CharaBaseClass` | `_getExtendedTemporaryAllGroup` | 44 |
| `_setPosDirInn` | `PlayerBaseClass` | `_setPositionDirectionInn` | 93 |
| `_callSuperClassFunc` | `ActorBaseClass` | `_callSuperClassFunction` | |

The alias hides the native from the script index. `_getPos` has 48 line
references in 11 scripts and `_getDir` has 14 in 7, yet the index lists no
binding for either. A registered `_turnDir` also exists at order 60 of the
`CharaBase` switchboard. The alias of `_turnClientDir` shadows it. The order of
`_callSuperClassFunction` is recorded in the
[widget contracts](widget-native-call-contract.md).

### Receiverless names

`global_u` assigns its descriptors to `_G` and returns the selector `global`
for 25 of them. 15 return a `_cpp` key and match the 15 natives of the `Global`
switchboard that the
[nameplate contracts](nameplate-group-native-contract.md#actor-identity-natives)
list, so `_isExistActor` has a descriptor like the others. 10 return a `_lua` key
for `print`, `tonumber`, `tostring`, `type`, `assert`, `error`, `select`,
`unpack`, `pcall` and `xpcall`. The script also defines the plain function
`_getTutorialJudge`, which calls `_getStaticActor_cpp` on the global object with
the number `320006`, and `_getLanguage`. The root table `__newindex`
(`0x00D099B0`, recorded by
[`manifests/lge_bootstrap_attribution.json`](../manifests/lge_bootstrap_attribution.json))
reads the string `global` at engine implementation `+0x70` and resolves the class
record of that name, which is how `_G` assignments reach the `Global` class
(`INFERRED`).

The index lists no binding for any of these names because they belong to no
class script. Of the 129 index names without a class binding, 15 are these
natives, 8 are the aliases above, 3 are the library namespaces, 1 is `_isAlive`,
77 are script callbacks that begin with `_on`, 4 are work declaration keys
(`_assignForChild`, `_globalSave`, `_globalTemp` and `_memberSave`), 14 are
registered natives without a descriptor, 5 are descriptor suffix identifiers and
2 are `_callFunction` and `_progFunc` (`MEASURED`).

The trampoline `0x00D04DA0` behind every installed closure tests that Lua stack
index 1 is a table (`0x00CF3740` compares the type code with 5). Otherwise it
reports through `0x00CCFB20` and `0x00CD4FA0` and returns no value. A call such
as `_getStaticActor(24301)` has a number at index 1 in the script, yet the
closure that the script reaches is not the native. The root table `__newindex`
installs a forwarder per descriptor that calls the native with the `global`
object as the first argument, so index 1 holds that table. The
[Global call convention](global-native-contract.md#receiverless-call-convention)
records the forwarder, the trampoline and the native frame.

### Library namespaces

`_math`, `_string` and `_table` are not natives. `0x0078FC90` renames six Lua
library tables by calling `0x00CC97D0` and `0x00CDBFB0` with a library name and a
new name. `0x00CDBFB0` reads the library name from the globals table, stores the
value under the new name and stores nil under the library name. The pairs are
`debug` to `_debug`, `math` to `_math`, `string` to `_string`, `table` to
`_table`, `io` to `_io` and `os` to `_os`. The argument order follows from the
stack offsets of the two strings at each call. `xivl-decomp:docs/script/lua-bootstrap-chunks.md`
records the same pairs and the later step that makes the lowercase `math`,
`string` and `table` globals registered class objects.

The shipped scripts read `_math` at 179 line references in 59 scripts, `_string`
at 341 in 19 and `_table` at 93 in 10, always as table members such as
`_math.floor` and `_string.match` (`MEASURED`). `_randomInteger` lives on the
`Math` class object that the global `math` holds, and a script calls it as
`math:_randomInteger(1, 2)`.

## Registration and dispatch

Six classes register the thirteen natives, each from the switchboard in slot 2
of its vftable. The switchboard shape, the skip byte and the single `rel32`
caller of each registrar are the ones recorded for `SpreadSheet` in the
[SpreadSheet contracts](spreadsheet-native-contract.md#registration-and-dispatch).
The order is the position among the registrar calls of the switchboard.

| Class | Switchboard | Vftable | Natives (order) |
| --- | --- | --- | --- |
| `CharaBase` | `0x007574A0` | `0x00FD5CAC` | `_getPosition` (1), `_getDirection` (2), `_getActorMainStat` (7), `_getDisplayName` (26) |
| `GroupBase` | `0x00757B70` | `0x00FD53CC` | `_getKind` (3), `_isExistInWorldMember` (5), `_getMemberDisplayName` (12), `_getDisplayName` (13) |
| `ItemBase` | `0x00753DD0` | `0x00FD5484` | `_getKind` (6), `_getPackage` (7) |
| `WorldMaster` | `0x00754C70` | `0x00FD5864` | `_getSpecialEventWork` (23) |
| `Math` | `0x00740EC0` | `0x00FD559C` | `_randomInteger` (1) |
| `PlayerBase` | `0x00753F90` | `0x00FD5E04` | `_lockPlayerControl` (27), `_unlockPlayerControl` (28) |

| Native | Registrar | Caller | Callback | Wrapper |
| --- | --- | --- | --- | --- |
| `_getPosition` | `0x0074A4C0` | `0x007574BC` | `0x006F9A30` | `0x00726460` |
| `_getDirection` | `0x0074A610` | `0x007574D1` | `0x006F9AC0` | `0x00726460` |
| `_getActorMainStat` | `0x0074AA00` | `0x0075753A` | `0x006F9CC0` | `0x00726460` |
| `_getDisplayName` (`CharaBase`) | `0x0074BF00` | `0x007576C9` | `0x006FA4C0` | `0x00726460` |
| `_getKind` (`GroupBase`) | `0x0074CD70` | `0x00757BB6` | `0x006FFBC0` | `0x007265C0` |
| `_isExistInWorldMember` | `0x0074D010` | `0x00757BE0` | `0x006FFD10` | `0x007265C0` |
| `_getMemberDisplayName` | `0x0074D6A0` | `0x00757C73` | `0x00700280` | `0x007265C0` |
| `_getDisplayName` (`GroupBase`) | `0x0074D7F0` | `0x00757C88` | `0x007003A0` | `0x007265C0` |
| `_getKind` (`ItemBase`) | `0x0074E120` | `0x00753E55` | `0x007019D0` | `0x00726670` |
| `_getPackage` | `0x0074E270` | `0x00753E6A` | `0x00701A30` | `0x00726670` |
| `_getSpecialEventWork` | `0x007531D0` | `0x00754E5E` | `0x00707CC0` | `0x00726CA0` |
| `_randomInteger` | `0x0072B0C0` | `0x00740EDC` | `0x006DDE70` | `0x00726F60` |
| `_unlockPlayerControl` | `0x00732790` | `0x007541E3` | `0x006DE7F0` | `0x007267D0` |

Every registrar builds the return list first and the argument list second and
installs the functor through `0x00CCCAD0` under the name literal with the
adjustment 0. The wrappers of the character, group, item, world and player rows
are recorded in the earlier contracts. The `Math` wrapper `0x00726F60` is new. It
constructs a `0x58` byte functor through `0x00725020` and `0x0071AF20` (vftable
`0x00FD5B7C`, RTTI `MemberFunctionHolder<Math, void (Math::*)(ExecuteParameters const&)>`).
Its invoke routine `0x0071AF90` casts the receiver with `0x009DA6CC` from
`LuaControl` (`0x01270B4C`) to `Math` (`0x012C09E8`). The holder is non-const.

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_getPosition` (`_getPos`) | `CharaBase` | none | three `float` | no |
| `_getDirection` (`_getDir`) | `CharaBase` | none | `float` | no |
| `_getActorMainStat` | `CharaBase` | none | `int` | no |
| `_getDisplayName` | `CharaBase` | none | `Which<Utf8String,int>`, `int` | no |
| `_getKind` | `GroupBase` | none | `int` | no |
| `_isExistInWorldMember` | `GroupBase` | `Which<LuaControl*,IndividualIndex,int>` | `bool` | no |
| `_getMemberDisplayName` | `GroupBase` | `int` | `Which<Utf8String,int>`, `int` | no |
| `_getDisplayName` | `GroupBase` | none | `Which<Utf8String,int>` | no |
| `_getKind` | `ItemBase` | none | `int` | no |
| `_getPackage` | `ItemBase` | none | `int` or nil | no |
| `_getSpecialEventWork` | `WorldMaster` | `int` | `Which<int,bool>` | no |
| `_randomInteger` | `Math` | two `int` | `int` | no |
| `_unlockPlayerControl` | `PlayerBase` | none | none | no |

No native here calls the yield request `0x00CD2860`. The cell tag is the byte at
cell `+0x0C`. The constructors `0x00583D90`, `0x0073E010`, `0x00583E30`,
`0x0073DF70` and `0x00583F70` store 0, 1, 2, 3 and 6 there for an int, a float, a
bool, a `Utf8String` and nil. The pushers are `0x00584F70`, `0x007489D0`,
`0x00748870`, `0x007487C0` and `0x00748920` in that order. The readers are
`0x005819A0` for an int, `0x0071CCB0` for a control and `0x0071CD90` for an
`IndividualIndex`. The list builders are `0x0072B440` for none, `0x00728C20` for
an int, `0x00583CE0` for two ints, `0x00728B70` for a bool, `0x0073CE40` for three
floats, `0x00742FA0` for the `Which` of the client member sibling, `0x00741DF0`
for a two entry list, `0x00741F90` for a one entry list and `0x00742120` for the
`Which` of an int and a bool. The two entry list `0x00741DF0` declares a `Which` of
registry entries 3 (`Utf8String`) and 0 (`int`) built through `0x0072BD30`, then
registry entry 0. `0x00742120` builds its `Which` through `0x0072BDC0` from registry
entries 0 and 2.

## Character natives

The character callbacks resolve the receiver identity at `ExecuteParameters`
`+0x0C` through `0x004D9970`, the lookup of the
[scheduler contracts](scheduler-item-native-contract.md#world-object-and-identity-lookup).
No instruction tests the pointer it returns, so an identity that is not in the
registry reaches the field reads with a null `this`. The run-time result was not
observed.

`_getPosition` (`0x006F9A30`) takes no argument. It passes the identity and a
`0x10` byte record to `0x0075C230` and pushes the floats at record `+0x00`,
`+0x04` and `+0x08` through `0x007489D0`. `0x0075C230` fills the record through
`0x004CFE30` with the flag 1. That routine reads the four floats at chara `+0x9C`
to `+0xA8`. When the dword at chara `+0x98` is nonzero it calls itself on that
object and adds the four floats it gets, componentwise, so the position is the
sum along the parent chain. That the floats are a position and a fourth
component and that `+0x98` is a parent object are `INFERRED` from the native name
and the recursion. A rotation of the parent is not applied.

`_getDirection` (`0x006F9AC0`) builds the same record and pushes only the float
at record `+0x0C`. `0x0075C230` stores there the float at chara `+0xAC` when the
parent dword is zero. Otherwise it adds that float to the result of `0x004DD8B0`
on the parent, which applies the same rule to the parent chain, and folds the sum
into the range around zero. The fold subtracts `2 pi` times the truncated quotient
of the sum plus `pi` by `2 pi` for a sum at or above zero, and the sum minus `pi`
below zero. The doubles are `pi` at `0x00F62F48` and `2 pi` at `0x00F62FE0`. That
the float is a heading in radians is `INFERRED` from the constants.

`_getActorMainStat` (`0x006F9CC0`) takes no argument. `0x0075C1B0` resolves the
identity and `0x00585400` loads the dword at chara `+0xF0`, which the callback
pushes as an int. The dword is `INFERRED` to be the main stat mode of the actor
from the native name and the sibling `_isActorMainStatMode`, which was not traced.

`_getDisplayName` on `CharaBase` (`0x006FA4C0`) reads the record pointer at the
receiver `+0x60`. The group member natives below copy the same record. Its first
dword selects the result.

| Record | Pushes |
| --- | --- |
| First dword other than -1 | The dword as an int, then nil. |
| First dword -1 | The `Utf8String` at record `+0x04`, then the byte at record `+0x58` as an int. |

The return list is two entries, a `Which` of `Utf8String` and `int` and an `int`.
That an index selects a name from a sheet and that -1 marks a literal name are
`INFERRED` from the shape of the branches. The meaning of the byte and the
writers of the record were not traced.

## Group natives

The group natives work on the group data pointer at the receiver `+0x68`, as in
the [fade, actor and group contracts](fade-actor-group-native-contract.md#group-natives).

`_getKind` (`0x006FFBC0`) calls `0x006BFD20`, which returns the dword at group
data `+0x04`, and pushes it as an int. The role as the group kind comes from the
name and is `INFERRED`.

`_getDisplayName` (`0x007003A0`) calls `0x006BFD40`, which copies the record at
group data `+0x08` through `0x006BF500`. That routine copies the dword at `+0x00`,
the `Utf8String` at `+0x04` and the bytes at `+0x58` and `+0x59`. The callback
pushes the dword as an int when it is not -1 and otherwise the string. It pushes
no second value.

`_getMemberDisplayName` (`0x00700280`) reads an int `n` after an empty cell vector
test that calls `0x009D22B4`. It builds the record of member `n - 1` through
`0x006C0D80` and `0x006C09E0`, which bounds-tests the position against the entry
vector at group data `+0x84` and chooses by the tag byte at entry `+0x0C`.

| Entry tag | Record |
| --- | --- |
| 3 | The record at `+0x08` of the object reached by two loads from entry `+0x08`. |
| 1 | The record that the pointer at `+0x60` of the actor addresses. The actor is the `CharaBase` cast of the control that `0x00CC7A50` resolves from the identity at `+0x04` of the object at entry `+0x08`. |
| Other | The default record from `0x006BF420`. It has the dword -1, an empty string, the byte 0 at `+0x58` and the byte 1 at `+0x59`. |

The callback pushes the record as `_getDisplayName` on `CharaBase` does. The
return list is the same two entries and the argument is one int. The layouts of
the entries were not traced.

`_isExistInWorldMember` (`0x006FFD10`) takes the `Which` of the client member
sibling and reads the tag of cell 0.

| Tag | Position |
| --- | --- |
| 0 (int) | `n - 1`. |
| 4 (control) | The index that `0x006C3560` finds for the control identity, or -1. |
| 8 (`IndividualIndex`) | The index found with the second dword of the pair, then with the first dword when the first search gives a negative index and the first dword is nonzero. |
| Other | Not found. |

The client member sibling reads every other tag as an int and answers false for
tag 8, so the two natives differ here. `0x006C3560` jumps to `0x006C3320`. That
routine builds the identity of each 16 byte entry through `0x006D3FE0` and returns
the first index whose first dword equals the first dword of the key, or -1. A
negative position pushes false. Otherwise `0x006C0D60` jumps to `0x006C0C40`,
which bounds-tests the position against the entry count and calls `0x009D22B4` at
or past it. An entry whose tag byte is not 3 gives 1. A tag 3 entry gives the byte
at `+0x64` of the object reached by two loads from entry `+0x08`. The callback
pushes the byte as a bool. That tag 3 entries carry a world presence byte is
`INFERRED` from the name and the sibling. The effect of a position at or past
the count was not run.

## Item natives

The item natives work on the `ItemBase` reference of the
[scheduler and item contracts](scheduler-item-native-contract.md#item-packages).
The reference holds an owner at `+0x64`, a package key at `+0x68`, a slot at
`+0x6C` and a variant byte at `+0x70`.

`_getKind` on `ItemBase` (`0x007019D0`) repeats the lookup of `_getCatalogID`.
The variant byte 1 selects `0x006EE480` and any other value `0x006EE3E0`. The
callback pushes the dword at record `+0x80` and does not test the lookup result.
The script index binds `_getKind` to `GroupBaseClass` only, and
`item/itembaseclass_u` has no `_getKind_inl`, so no script descriptor reaches this
registration. The writers of the dword were not traced.

`_getPackage` (`0x00701A30`) compares the key at receiver `+0x68` with the dword
`0xFF` at `0x00FE0508`. Equal pushes nil. Otherwise it repeats the lookup, loads
the dword at record `+0x08`, loads the first dword it points to and reads the
dword at `+0x04` of that target. `0x0078BCA0` returns the dword plus 1 and the
callback pushes it as an int. The result is `INFERRED` to be a one-based package
number from the name and from the one-based package arguments of the scheduler
contracts. The object at record `+0x08` was not traced.

## World and math natives

`_getSpecialEventWork` (`0x00707CC0`) reads an int `n` and loads the object at
`Y +0x10C`. For `n` from 1 to 8, which is `n - 1` below 8 as an unsigned compare,
`0x0075D390` returns the byte at `+0x84` plus `n - 1` and the callback pushes it
as a bool. For every other `n`, `0x0075D3A0` returns the 16 bit word at `+0x8C`
plus `(n - 9) * 2` and the callback pushes it as an int. There is no upper bound
test, and 0 or a negative `n` reads below `+0x8C`. A second caller of the two
accessors at `0x0057918F` selects the literals `true` or `false` from the byte.
The object is `INFERRED` to be the special event work store of the world object.
The writers and the size of the word run were not traced.

`_randomInteger` (`0x006DDE70`) passes `ExecuteParameters` and the address of the
dword at receiver `+0x64` to `0x0078D040`. That routine reads two ints `lo` and
`hi` and replaces the state `s` with `s * 0x41C64E6D + 0x3039` in 32 bits. It takes
`r = (s >> 16) & 0x7FFF` with an arithmetic shift, multiplies the float of `r` by
the double `-1 / 32768` at `0x00FE0578`, stores the product as a 32 bit float,
multiplies by `hi - lo + 1`, stores a 32 bit float again and truncates toward zero
through `0x009D6600`. The result is `lo` minus the truncated value, which equals
`lo` plus the floor of `r * (hi - lo + 1) / 32768` for `lo` at most `hi`, up to the
rounding of the two float stores. The Math switchboard registers `_randomInteger`,
`_randomFloat`, `_randomIntegerWithSeed` and `_randomFloatWithSeed` at orders 1
to 4. The initial state and its other writers were not traced.

## Player control

`_unlockPlayerControl` (`0x006DE7F0`) is the three instruction thunk that loads
the receiver vftable and jumps through slot `0x114`. `_lockPlayerControl`
(`0x006DE7E0`) is the same thunk for slot `0x110` and is carried as a related row.

| Native | Slot | `PlayerBase` cell | `MyPlayer` cell | `MyPlayer` routine |
| --- | --- | --- | --- | --- |
| `_lockPlayerControl` | `0x110` | `0x00FD5F14` | `0x00FD796C` | `0x006E3340` |
| `_unlockPlayerControl` | `0x114` | `0x00FD5F18` | `0x00FD7970` | `0x006E3360` |

The `PlayerBase` slots hold the bare returns `0x006DEA00` and `0x006DEA10`, so a
`PlayerBase` receiver that is not a `MyPlayer` does nothing. The `MyPlayer`
routines read the world chain and pass the dword at `Y +0x08` to `0x0075B240` and
`0x0075B250`. Those glue routines load `V` and call `0x004D7580`, which adds
`0x17758` to `V`. They then call virtual slot 1 or 2 of the object at that address.
The constructor `0x004DECF0` builds the object inside `0x004DBF40` at `0x004DC1E1`
with the vftable `0x00F90F64`, RTTI `Application::Main::SqwtInterface::RaptureUserControl`.

Slot 2 (`0x0054B600`) subtracts 1 from the dword at object `+0x18` and returns
it. Slot 1 (`0x0054B440`) adds 1. When `0x004D72E0` and a cast from
`RaptureElement` (`0x01269C58`) to `CharaElement` (`0x01269CC0`) give an object,
slot 1 first calls `0x004D7980` with the record number `0x22`, a null payload
and size 0, which gives the scene packet type `0x37` by the rule of the
[fade contracts](fade-actor-group-native-contract.md#fade-natives). It then looks
up an object for each of the strings `RaptureCommands.MoveCharacter` and
`RaptureCommands.ShiftMoveCharacter` through `0x00928F90` and calls virtual slot 2
of each. The dword is `INFERRED` to be a lock depth. There is no floor test, so
an unlock without a lock leaves the dword at -1. The readers of the dword and the
consumers of the packet and the looked up objects were not traced.

## Script surfaces

`_isAlive` is a method that no registrar installs. It has three surfaces.

| Receiver | Result | Source |
| --- | --- | --- |
| Live script instance | true | `ActorBaseClass._isAlive` in `actorbaseclass_u`, a function whose bytecode is `LOADBOOL true` and `RETURN` (`MEASURED`). |
| Released script instance | false | The instance `__index` closure `0x00D085B0` returns the global `__lge_isAlive`, which the embedded bootstrap source at `0x0110E680` defines as a function returning false. |
| `IndividualRef` userdata | The engine existence test | The `__index` closure `0x00D110B0` returns the C closure `0x00D11010`, which calls `0x00CE19C0` and the engine virtual slot 4 through `0x00CCCB20`. |

The instance `__index` closure compares the key with the literal `_isAlive` at
`0x0110F068`, and `0x00CE1BB0` decides that the instance is released. It returns
true when the byte at record `+0x7E` is set. When the dword at record `+0x08`
equals `0x00010009` at `0x0130D500` and differs from `0x0001000A` at `0x0130D504`,
it casts the object at record `+0x00` from `LuaControl` to `LuaTentativeControl`
(`0x012C0828`) and calls virtual slot 3 through `0x00CCCB10`. A false answer sets
the byte at `+0x7E` and returns true. For a released instance every key other than
`_isAlive` returns `__lge_returnNil`. The `IndividualRef` userdata is described in
[`manifests/individualref_userdata.json`](../manifests/individualref_userdata.json).
That `+0x7E` marks a released reference is `INFERRED` from the tentative state
writer of the [Lua class system](lua-class-system.md). The shipped scripts call
`_isAlive` at 162 line references in 50 scripts, always as a method.

## Ledger rows

These rows of the unimplemented ledger have a registration or a script surface,
an argument list, a return list and a callback contract: `_isAlive`, `_getPos`,
`_getDir`, `_getActorMainStat`, `_isExistInWorldMember`, `_getMemberDisplayName`,
`_getPackage`, `_randomInteger`, `_getDisplayName`, `_getSpecialEventWork`,
`_getKind`, `_unlockPlayerControl`, `_lockPlayerControl`, `_math`, `_string` and
`_table`. `_getKind` is bound to `GroupBaseClass` only. `_isAlive`, `_math`,
`_string` and `_table` are not functor natives, so a client implements them as
script and bootstrap behavior. A client that implements the rows still needs the
writers of the character, group, item and event work fields, the sheet behind the
name indexes and the consumer of the control scene packet, which this record
does not supply.

## Open

- The callbacks behind the aliases `_setPos`, `_setDir`, `_turnDir`,
  `_getAllExtendedTemporaryGroup` and `_setPosDirInn`.
- The run-time result of the chara queries for an identity that is not in the
  registry, and of the group queries for a position at or past the entry count.
- The writers of the chara fields at `+0x98`, `+0x9C`, `+0xAC` and `+0xF0`, of the
  item record dwords at `+0x08` and `+0x80`, of the special event work and of the
  `Math` state dword.
- The entry layouts of the group data and the sheet behind the name index.
- The readers of the lock depth, the consumer of the scene packet type `0x37` and
  the two objects that the lock slot looks up.

The next natives by value are ranked by the number of distinct scripts that
contain a call, with the call-site count as the tie break. Natives with a
contract in any manifest or a wire-level record in a contract page are left out,
and so are the script callbacks that begin with `_on`, the work keys and the
descriptor suffix identifiers. An alias takes the class of its descriptor.

| Rank | Native | Class | Scripts | Call sites | Why |
| ---: | --- | --- | ---: | ---: | --- |
| 1 | `_getInstanceName` | `Debug` | 6 | 16 | Order 4 of the `Debug` switchboard, wrapped by a Lua function in the `Debug` script. |
| 2 | `_turnDir` | `CharaBaseClass` | 6 | 9 | Alias of `_turnClientDir`, order 61 of `CharaBase`. |
| 3 | `_updateWork` | `CharaBaseClass` | 6 | 7 | Order 27 of `CharaBase`, 17 of `ItemBase`, 15 of `GroupBase` and 2 of `DirectorBase`. |
| 4 | `_getRegion` | `AreaBaseClass` | 6 | 6 | Order 1 of the `AreaBase` switchboard. |
| 5 | `_runCharaSchedulerTutorial` | `WorldMaster` | 5 | 44 | Order 12 of the `WorldMaster` switchboard. |
| 6 | `_lookAtPlayerTutorial` | `WorldMaster` | 5 | 23 | Order 14 of the `WorldMaster` switchboard. |
| 7 | `_aimCameraTutorial` | `WorldMaster` | 5 | 22 | Order 16 of the `WorldMaster` switchboard. |
| 8 | `_cancelAimCameraTutorial` | `WorldMaster` | 5 | 22 | Order 17 of the `WorldMaster` switchboard. |
| 9 | `_getMemberLocalizedDisplayName` | `GroupBaseClass` | 5 | 14 | Order 10 of `GroupBase`, next to `_getMemberDisplayName`. |
| 10 | `_lockLockonControl` | `PlayerBaseClass` | 5 | 12 | Order 30 of the `PlayerBase` switchboard. |
| 11 | `_lockTargetCursorControl` | `DesktopWidget` | 5 | 12 | Order 17 of the `DesktopWidget` switchboard. |
| 12 | `_unlockLockonControl` | `PlayerBaseClass` | 5 | 12 | Order 31 of the `PlayerBase` switchboard. |
| 13 | `_unlockTargetCursorControl` | `DesktopWidget` | 5 | 12 | Order 18 of the `DesktopWidget` switchboard. |
| 14 | `_cancelLookAtPlayerTutorial` | `WorldMaster` | 5 | 11 | Order 15 of the `WorldMaster` switchboard. |
| 15 | `_getOccupancyGroup` | `GroupBaseClass` | 5 | 11 | Order 7 of the `GroupBase` switchboard. |
| 16 | `_getGMRank` | `PlayerBaseClass` | 5 | 9 | Order 41 of the `PlayerBase` switchboard. |
| 17 | `_commandDebug` | `Debug` | 5 | 8 | Order 7 of the `Debug` switchboard. |
| 18 | `_waitForMapLoaded` | `PlayerBaseClass` | 5 | 8 | Order 38 of the `PlayerBase` switchboard, a candidate yield native. |
| 19 | `_getOrientation` | `CharaBaseClass` | 5 | 7 | Order 5 of `CharaBase`, next to `_getDirection`. |
| 20 | `_getAllCharacter` | `Debug` | 4 | 17 | Registered by the `Debug` switchboard. |

The manifest rows under `nextTranche` carry the same order.
The [work binder contracts](work-binder-native-contract.md) cover ranks 1, 2, 3, 4,
9, 10, 12, 15, 16 and 19. The [Global native contracts](global-native-contract.md)
cover the nine `Global` natives below the twentieth row and carry the refreshed
order.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes. The listings behind this
record came from a Capstone 5.0.7 x86-32 decode of the file through its
section table and the `rel32` caller scan of `.text` described in the
[binary and method](#binary-and-method) section. The script facts come from the
`.le.lpb` files of an installed client decoded by
[`tools/decode_lpb.py`](../tools/decode_lpb.py) and read with a Lua 5.1 bytecode
parser. With explicit project and JDK bindings and a new absolute output path,
the repository route for function listings is:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Switchboards and registrars | `0x007574A0,0x00757B70,0x00753DD0,0x00754C70,0x00740EC0,0x00753F90,0x0074A4C0,0x0074A610,0x0074AA00,0x0074BF00,0x0074CD70,0x0074D010,0x0074D6A0,0x0074D7F0,0x0074E120,0x0074E270,0x007531D0,0x0072B0C0,0x00732640,0x00732790` |
| Wrappers and list builders | `0x00726F60,0x00725020,0x0071AF20,0x0071AF90,0x0073CE40,0x00741DF0,0x00741F90,0x00742120,0x0072C4C0,0x0072BD30,0x00727F00,0x0072BDC0,0x0072C5D0,0x00583CE0` |
| Callbacks | `0x006F9A30,0x006F9AC0,0x006F9CC0,0x006FA4C0,0x006FFBC0,0x006FFD10,0x00700280,0x007003A0,0x007019D0,0x00701A30,0x00707CC0,0x006DDE70,0x006DE7E0,0x006DE7F0` |
| Character | `0x0075C230,0x0075C1B0,0x00585400,0x004D9970,0x004CFE30,0x004DD8B0` |
| Group | `0x006BFD20,0x006BFD40,0x006BF500,0x006BF420,0x006C0D60,0x006C0C40,0x006C0D80,0x006C09E0,0x006C3560,0x006C3320` |
| Item, world and math | `0x006F51A0,0x0078BCA0,0x0075D390,0x0075D3A0,0x0078D040,0x009D6600` |
| Player control | `0x006E3340,0x006E3360,0x0075B240,0x0075B250,0x004D7580,0x004DECF0,0x0054B440,0x0054B600` |
| Binding map | `0x007634B0,0x00CC96A0,0x00CD7630,0x00CE1750,0x00D07820,0x00D07890,0x00D08000,0x00D04DA0,0x00D099B0,0x0078FC90,0x00CDBFB0` |
| `_isAlive` | `0x00D085B0,0x00CE1BB0,0x00D110B0,0x00D11010,0x00CE19C0` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
