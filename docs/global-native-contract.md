# Receiverless Global call convention and Global and WorldMaster tutorial native contracts

[`manifests/global_native_call_contract.json`](../manifests/global_native_call_contract.json)
records how a receiverless call such as `_getStaticActor(24301)` reaches the
registered native, and the static Lua call contracts of twelve native
registrations. Nine are `Global` natives that waited on that convention:
`_canCreateActorByName`, `_getActorByName`, `_getQuestActorForCutSceneReplay`,
`_isExistStaticActor`, `_prepareAllCommandStaticActor`, `_getUTF8StringLength`,
`_getUTF8StringByteLength`, `_normalizeDisplayName` and
`_replaceMacroCodeString`. Three are `WorldMaster` tutorial natives:
`_runCharaSchedulerTutorial`, `_lookAtPlayerTutorial` and `_aimCameraTutorial`.
Each row gives the registration site, the receiver type check, the declared
argument and return lists, the reads, the effects on client state, the failure
behavior and whether the call yields. The contracts describe client marshalling
and state, not actor names, static actor numbers, command sheet contents,
scheduler resources or server behavior.

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
Addresses are absolute VAs. The instruction listings were decoded directly from
the PE bytes through the section table after the size and hash were checked.
Callers were found by scanning `.text` for `rel32` `call` and `jmp`
instructions, so virtual and indirect callers are not covered.

The script facts come from the Lua 5.1 bytecode of the installed client
scripts, decoded with [`tools/decode_lpb.py`](../tools/decode_lpb.py). The
script sources are not redistributed. The per-row `corpusCallSites` records
carry the counts of `xivl-client-scripts:lua/napi_index.json`. They show that a
script contains a call, not that a script reaches it at run time.

## Receiverless call convention

The trampoline `0x00D04DA0` behind every installed native closure requires a
table at Lua stack index 1, the receiver. The shipped scripts call the `Global`
natives as plain globals, with no receiver. Two closures close that gap.

### Root table assignment

The Lua state creation routine `0x00CD8990` gives the globals table a
metatable whose only key is `__newindex`, bound to the C closure `0x00D099B0`
(`0x00CD90A9..0x00CD90DC`). The globals table has no `__index`, so a read of a
global name is a raw read.

`0x00D099B0` receives the globals table, the key and the value. It raw reads the
key and drops the assignment when the globals table already holds a function
there. It intercepts an assignment when all of these hold:

- the value is a function and not a C function (`0x00CF37E0`, which reads the C
  flag byte at closure `+0x06`),
- the key is none of `__lge_defineWork`, `__lge_setLoopInterval`, `_progFunc`
  and `_onProgFunc`, the strings behind the pointer cells `0x0130D514`,
  `0x0130D518`, `0x0130D520` and `0x0130D524`,
- the string at engine implementation `+0x70` is nonempty. `0x0078FF82` stores
  `global` there before any `_u` script runs.

Any other assignment is a raw set of the pair on the globals table
(`0x00D09C6E..0x00D09C8A`). The functions of the four reserved names therefore
stay plain functions without a receiver, as `_onProgFunc` is recorded in
`xivl-decomp:docs/script/lua-bootstrap-chunks.md`.

An intercepted assignment does two things:

1. It resolves the class record named by the engine string through `0x00CD8870`,
   reads the name of its registered parent through `0x00CC6FA0` and raw reads the
   global of that name, the `Global` class table. It sets the key on that table
   with the ordinary set operation. The class table `__newindex` `0x00D07EB0`
   runs, so a key that ends in `_inl` reaches the descriptor resolver
   `0x00D07890`, which stores the registered closure under the stripped name in
   the `Global` class table. That the parent is `Global` is `INFERRED`, because
   `0x00CD9160` links it when `0x00CD99F0` creates the object.
2. It strips a trailing `_inl` from the key and raw sets the closure `0x00D084A0`
   on the globals table under the stripped key, with the stripped key as its only
   upvalue.

So `global_u` leaves two entries per descriptor. `Global._getStaticActor` is the
native closure `0x00D08000` and `_G._getStaticActor` is the forwarder.

### Forwarder

`0x00D084A0` counts its n arguments, raw reads the global named by the string at
engine implementation `+0x70`, which is the `global` object, and indexes that
object with the upvalue. The index is the get operation that runs metamethods,
so the lookup goes through the metatable of the `global` object to the `Global`
class table and its registered parents. It then pushes the object again,
removes the first copy, pushes copies of the n arguments and calls the function
with n + 1 arguments and all results. The call is
`global[name](global, a1 .. an)` and every result is returned
(`0x00D084D3..0x00D08590`).

The forwarder does not test the looked up value. A name that does not resolve
fails in the call operation. The run-time result was not observed.

### Global object and trampoline

`0x0078FAD0` creates the `global`, `math`, `string` and `table` objects through
`0x00CC78A0` and `0x00CD99F0`, and then runs `0x00CC72C0` with the flag 1 on
each. `0x00CD99F0` makes the object table through `0x00CD7970` and
`0x00CD7690`. `0x00CD7690` stores a four byte userdata in the table under the
light userdata key `0x00010000`, the dword at `0x0130D4E0`. `0x00CE1DD0` stores
the flag in record `+0x7D` and clears the byte at `+0x7E` that `0x00CE2440`
sets, so the instance `__index` closure `0x00D085B0` does not treat the object as
released. That consequence is `INFERRED`.

The trampoline works on that table:

| Step | Instructions | Effect |
| --- | --- | --- |
| Record and context | `0x00D04DCD..0x00D04DE9` | Upvalue 1 gives the registration record and `0x00CF3CE0` gives the engine context. |
| Table test | `0x00D04DEE..0x00D04DFB` | `0x00CF3740` compares the type of index 1 with 5. |
| Not a table | `0x00D04DFD..0x00D04E36` | `0x00CCFB20` builds the class and method text, `0x00CD4FA0` hands it to virtual slot `0x50` of the diagnostic object at engine context `+0x1CC`, and the call returns zero results. No Lua error is raised. |
| Registered object | `0x00D04E3B..0x00D04E4E` | `0x00CD77D0` indexes the table by the key `0x00010000` and returns the dword in the userdata. `0x00CE1720` accepts it when the dword at record `+0x08` differs from the dword at `0x0130D4F8` (`0x00010007`). |
| Rejected record | `0x00D04E52..0x00D04E8B` | `0x00CD5060` reports through slot `0x54` and the call returns zero results. |
| Accepted | `0x00D04E8D..0x00D04EB4` | `0x00D04FE0` pushes the call frame and `0x00D19B70` reads the receiver from index 1 and marshals the declared arguments from index 2. |

A table without the key makes `0x00CD77D0` return 0, and the trampoline passes
that to `0x00CE1720` without a null test. The run-time effect of such a table
was not observed. That the userdata of the `global` object holds the record that
`0x00CE2D50` builds is `INFERRED`. `math:_randomInteger(1, 2)` dispatches through
the same trampoline in the shipped scripts, and the `global_u` function
`_getTutorialJudge` calls `global:_getStaticActor_cpp(320006)` as a method call
on the `global` object (`MEASURED`).

### Native frame

A receiverless call therefore has the same shape as a method call on the
`global` object. Native-frame position 1 is the `global` object and the Lua
arguments are positions 2 and up. The argument contracts of the Global rows
count the Lua arguments only. `_getStaticActor(24301)` reads 24301 at position 2.
This closes the position 1 gap of the
[widget contracts](widget-native-call-contract.md#argument-marshalling) and the
receiverless call convention of the earlier records.

The same forwarder carries every plain global call that `global_u` aliases. The
ten descriptors for `print`, `tonumber`, `tostring`, `type`, `assert`, `error`,
`select`, `unpack`, `pcall` and `xpcall` return the selector `global` and a
`_lua` key, so `tostring(x)` is `global.tostring(global, x)`. That passes the
receiver table test of the Lua forwarding wrapper `0x00D07F20 -> 0x00D04BF0`,
which `xivl-decomp:docs/script/lua-bootstrap-chunks.md` lists as open. This
step is `INFERRED`. A script defined global function is called with the
`global` object as its first parameter too. This is `INFERRED` from the same
forwarder. No shipped script calls `_getTutorialJudge`, and `global_u` declares
it with one unused parameter, so the parameter count is not evidence of it.

### Corpus

All shipped calls of the nine natives, of `_isExistActor`, `_getStaticActor` and
`_createActor` read the function with `GETGLOBAL`, with no method call form
(`MEASURED`). The argument counts are 1 for `_canCreateActorByName` (1 site),
`_getActorByName` (4), `_getQuestActorForCutSceneReplay` (2),
`_isExistStaticActor` (3), `_getUTF8StringLength` (3), `_getUTF8StringByteLength`
(4), `_normalizeDisplayName` (1), `_isExistActor` (7) and `_getStaticActor` (38),
0 for `_prepareAllCommandStaticActor` (1) and 3 for `_replaceMacroCodeString`
(1). The three tutorial natives are method calls on the global `worldMaster`.

## Registration and dispatch

The `Global` switchboard `0x007582E0` (vftable `0x00FD60AC`) and the
`WorldMaster` switchboard `0x00754C70` (vftable `0x00FD5864`) register the
twelve natives. The switchboard shape, the skip byte and the single `rel32`
caller of each registrar are the ones recorded for `SpreadSheet` in the
[SpreadSheet contracts](spreadsheet-native-contract.md#registration-and-dispatch).
The order is the position among the registrar calls of the switchboard.

| Native | Order | Registrar | Caller | Callback | Wrapper |
| --- | ---: | --- | --- | --- | --- |
| `_canCreateActorByName` | 4 | `0x00753320` | `0x0075833B` | `0x006FF1A0` | `0x00726E00` |
| `_getActorByName` | 5 | `0x0073C510` | `0x00758350` | `0x006DCD10` | `0x00726E00` |
| `_getQuestActorForCutSceneReplay` | 9 | `0x007535C0` | `0x007583A4` | `0x006FF3E0` | `0x00726E00` |
| `_isExistStaticActor` | 10 | `0x00741B80` | `0x007583B9` | `0x006DCE60` | `0x00726E00` |
| `_prepareAllCommandStaticActor` | 11 | `0x0073C7B0` | `0x007583CE` | `0x006E2000` | `0x00726E00` |
| `_getUTF8StringLength` | 12 | `0x0073C900` | `0x007583E3` | `0x006DCED0` | `0x00726E00` |
| `_getUTF8StringByteLength` | 13 | `0x0073CA50` | `0x007583F8` | `0x006DCF40` | `0x00726E00` |
| `_normalizeDisplayName` | 14 | `0x00753710` | `0x0075840D` | `0x006FF4E0` | `0x00726E00` |
| `_replaceMacroCodeString` | 15 | `0x00753860` | `0x00758426` | `0x006FF600` | `0x00726E00` |
| `_runCharaSchedulerTutorial` | 12 | `0x0073B2B0` | `0x00754D73` | `0x006E6B10` | `0x00726CA0` |
| `_lookAtPlayerTutorial` | 14 | `0x0073B550` | `0x00754D9D` | `0x006E6D90` | `0x00726CA0` |
| `_aimCameraTutorial` | 16 | `0x0073B7F0` | `0x00754DC7` | `0x006E6F60` | `0x00726CA0` |

Every registrar builds the return list first and the argument list second and
installs the functor through `0x00CCCAD0` under the name literal with the
adjustment 0. The holders are recorded in the earlier contracts. `0x00726E00`
is the const `Global` holder (invoke `0x00725620`, target type descriptor
`0x012C27C0`) and `0x00726CA0` is the const `WorldMaster` holder (target
`0x012C1328`). The invoke routines cast the receiver with `0x009DA6CC` from
`LuaControl` (`0x01270B4C`), and a null cast returns false without calling the
callback. The `Global` natives are reached through the `global` object, which is
the receiver at position 1.

## Contracts

| Native | Arguments | Returns | Yields |
| --- | --- | --- | --- |
| `_canCreateActorByName` | `Utf8String` | `bool` | no |
| `_getActorByName` | `Utf8String` | `LuaControl*` | no |
| `_getQuestActorForCutSceneReplay` | `int` | `LuaControl*` | yes, through `0x0078CC30` |
| `_isExistStaticActor` | `Which<int,Utf8String>` | `bool` | no |
| `_prepareAllCommandStaticActor` | none | none | no |
| `_getUTF8StringLength` | `Utf8String` | `int` | no |
| `_getUTF8StringByteLength` | `Utf8String` | `int` | no |
| `_normalizeDisplayName` | `Utf8String` | `Utf8String` | no |
| `_replaceMacroCodeString` | `Utf8String` x3 | `Utf8String` | no |
| `_runCharaSchedulerTutorial` | two `int` | none | no |
| `_lookAtPlayerTutorial` | `int` | none | no |
| `_aimCameraTutorial` | `int` | none | no |

The readers are `0x0071CE70` for a `Utf8String` and `0x005819A0` for an int. The
pushers are `0x00748870` for a bool, `0x00748B30` for a control, `0x007487C0` for
a `Utf8String` and `0x00584F70` for an int. A callback tests the cell vector
size first and calls the invalid-parameter route `0x009D22B4` for an empty
vector. The argument builders are `0x0072B5B0` (one `Utf8String`), `0x00728C20`
(one int), `0x00583CE0` (two ints), `0x00740F30` (the `Which` of
`_getStaticActor`), `0x0073D770` (three `Utf8String` entries, registry entry 3
each) and `0x0072B440` (none).

## Actor name natives

`_canCreateActorByName` (`0x006FF1A0`) reads one `Utf8String` and asks
`0x00CC7200` whether the name is known. That is the first question of
`_isExistActor`: `0x00CD9C60` looks the name up through `0x00CD8870` with the
create flag 0 and `0x00CE16C0` accepts one of the states `0x00010008`,
`0x00010009` and `0x0001000A`. The native pushes false when the name is known and
true otherwise. It reads no handle. A name in a state outside the three also
gives true. That the native answers whether a script may create an actor under
the name is `INFERRED`.

`_getActorByName` (`0x006DCD10`) is an adapter into the body `0x0078CAF0`. After
the same name test, `0x00CC7A00` looks the name up with the flag 1 and returns
the first dword of the entry, a control. `0x00CC72A0` reads the byte at `+0x7D` of
the object reference of that control, the flag that `_isExistActor` tests too.
A set byte pushes the control through `0x00748B30`. Any failure pushes a null
control, which the control push turns into Nil.

## Static actor natives

`_isExistStaticActor` (`0x006DCE60`, body `0x0078CE10`) takes the argument list of
`_getStaticActor`. A tag 3 cell is a name resolved through `0x00CC7130` and any
other cell is an int read by `0x005819A0` and resolved through `0x00CC70E0`. The
identity `0xE0000000`, the dword at `0x0130C778`, pushes false. Otherwise
`0x00CC7190` asks the container at engine `+0x1C4` whether the identity is known
(`0x00D035D0`), and a negative answer pushes false. `0x00CC7A50` then resolves a
control and the callback pushes whether it is nonzero. It does not read the
`+0x7D` flag, never creates an actor and never yields.

`_getQuestActorForCutSceneReplay` (`0x006FF3E0`) reads one int and builds the
identity with `0x00CC70E0`. A control that resolves through `0x00CC7A50` is pushed
at once, after `0x00CC7160` ran `0x00D037A0` on the identity. That routine
increments the dword at the node of the identity unless the early return holds,
which is `INFERRED` to be a use count. Without a control the callback runs the
`_getStaticActor` body `0x0078CC30` and may yield through `0x00CD2860` with the
`CreateStaticActorResumeChecker` of the
[boot contracts](boot-native-call-contract.md#static-actor-lookup). Every
shipped call passes an int.

`_prepareAllCommandStaticActor` (`0x006E2000`) takes no argument. It reads the
dword vector at `0x0134B77C..0x0134B780` and builds the identity of each static
actor number with `0x00CC70E0`. A control that resolves through `0x00CC7A50` and
carries the `+0x7D` flag needs nothing. For an identity with no control,
`0x00CC7180` decides: true goes to the request, false calls `0x00CC7160` and
`0x00CC78C0` and goes to the request when that gives no control or a control
without the flag. The request is `0x00767100` on the object at `Y +0x0D8`, which
forwards the identity address to `0x00582BC0`. The native creates no control
itself, returns nothing and never yields.

The vector is filled while the sheet named by the literal `command` loads. The
loop at `0x0076ABDE..0x0076ADC5` keeps the ids 12000..12999, 21000..21999,
24000..24999, 26000..26499, 30000 and 30101 whose byte at column 3 is zero and
rebuilds the vector with a copy and a swap through `0x00785F90`. That the ids are
command numbers and the static actors are command actors is `INFERRED` from the
native name. The meaning of the column 3 byte was not traced.

## String natives

`_getUTF8StringLength` (`0x006DCED0`, body `0x0078CF80`) pushes the result of
`0x00445E50`, the length in UTF-8 characters. The routine returns the count cached
at string `+0x0C` when the flag byte at `+0x10` is set. Otherwise it walks the
buffer and adds one per step. A step advances by 1 byte for a byte below `0x80`, 2
for `0xC0..0xDF`, 3 for `0xE0..0xEF`, 4 for `0xF0..0xF7`, 5 for `0xF8..0xFB` and 6
for `0xFC..0xFD`. The bytes `0x80..0xBF`, `0xFE` and `0xFF` advance by 0, and
the loop at `0x00445E70` has no exit for them. A well formed string never lands
there. The run-time effect on malformed text was not observed.

`_getUTF8StringByteLength` (`0x006DCF40`, body `0x0078CFE0`) pushes the result of
`0x004451F0`, the dword at string `+0x08` minus 1. That the dword counts the
terminating zero is `INFERRED` from the subtraction.

`_normalizeDisplayName` (`0x006FF4E0`) pushes the name unchanged when
`0x00445450` finds a byte below `0x20` in it, or when it ends with the literal at
`0x00FD48B0`, a space and three exclamation marks. The tail compare passes the
`0x00445E50` character counts. Any other name is converted in place and pushed.
`0x00445EE0` adds `0x20` to every byte `0x41..0x5A` and rewrites the second byte
of some two-byte sequences that start with `0xC3` or `0xC5`. `0x00445220` then
subtracts `0x20` from a byte `0x61..0x7A` at the first position and after each
`0x20` byte, and maps matching two-byte sequences to their uppercase forms. The
callback passes the flags 1, 1, 0, 0 and 0, which select the word start rule and
no exception list. That the native title cases a display name and that the
suffix marks a name to keep as typed are `INFERRED`.

`_replaceMacroCodeString` (`0x006FF600`) reads a text, a pattern and a
replacement. A tag 6 cell for the replacement pushes the text unchanged. A
replacement without a byte below `0x20` replaces every occurrence of the pattern
through `0x0067AC00`. A replacement with such a byte takes the loop at
`0x006FF73C..0x006FFA3F`, which finds the pattern with `0x006BE5E0`, replaces a hit
with `0x00596E10` when it lies before the next span and skips a hit that lies in
a span. A span starts at the byte at `0x012C3116` (`0x02`) and ends at the byte
at `0x012C3115` (`0x03`). Both initial span positions are the first `0x02` byte,
so a hit inside the first span is replaced. The loop was not run on text with
several spans. That the bytes delimit inline macro codes is `INFERRED`.

## Tutorial natives

The three `WorldMaster` natives share one prelude and one search. The callback
resolves the world chain of the
[scheduler contracts](scheduler-item-native-contract.md#world-object-and-identity-lookup)
(`X = [R]`, `Y = [X +0x04]`, `W = [Y]`) and calls `0x0075D120` on the object at
`Y +0x110`. That routine builds the identity `0xC0000024`, reads three work values
through `0x00CC7BE0`, `0x00CC7C30` and `0x00CC7B90` (keys `0x0007A122`,
`0x0007A123` and `0x0007A121`) and writes `((third << 5 | second) * 2 | 1)`, or 0,
into the dword at `V +0x500` through `0x004D7230` when the values change. The
roles of the keys were not traced.

The search builds a 0x10 byte iterator through `0x007176C0` (vftable
`0x00FD58F0`) with the first int and walks the node list at `V +0x4E4` through
`0x00764150`. Slot 1 of the iterator, `0x00719480`, resolves each identity,
casts it to `CharaBase` and accepts a chara whose byte at `+0x5C` is nonzero. It
compares the first dword of the record at chara `+0x60`, the display name record
of `_getDisplayName`, with the int, mapping -1 to 0. A match stores the identity
at iterator `+0x0C` and stops the walk. The int is therefore the name number of
the chara. The shipped scripts pass values such as `1000010`, `1100003` and
`2300120` (`MEASURED`). A walk that finds nothing leaves iterator `+0x0C` at 0.
The run and look-at natives resolve that identity without a test. In the aim
native only the first step tests the resolved chara.

`_runCharaSchedulerTutorial` (`0x006E6B10`) reads two ints and, after the walk,
runs `0x0075C420` on `W` with the found identity and the second int. That routine
resolves the identity through `0x004D9970` and calls `0x0058CAF0` on the chara.
`0x0058CAF0` runs `0x0058C690` with the int and the dword at chara `+0x88`, which
fills a 0x38 byte request record and submits it through `0x005901D0` to the object
at chara `+0xA80`. The shipped second ints are values such as `403087360`
(`0x1806A000`) and `353972224`. That they are packed scheduler resource numbers
is `INFERRED`. The fields of the request were not traced.

`_lookAtPlayerTutorial` (`0x006E6D90`) reads one int and, after the walk, reads
the dword at `Y +0x10` through `0x0057AB60` and calls `0x0075C580` with the found
identity, that dword and the float 1.0. `0x0075C580` resolves the chara and calls
`0x00589260`, which forwards the identity, the float and 0 to `0x00587F80` with the
constants 0 and 200 in front. `Y +0x0C` holds the local player control, so the
dword at `Y +0x10` is `INFERRED` to be its identity and the native tells the found
chara to look at the player. The constants and `0x00587F80` were not traced.

`_aimCameraTutorial` (`0x006E6F60`) reads one int. The target cursor workers take
the receiver `Z = [Y +0x04]`, as the
[target cursor contracts](target-cursor-native-contract.md#cursor-state) record.
After the walk the callback runs three steps:

1. `0x0075B6C0` on `Z` with the cursor index 0 and the found identity. It does
   nothing for a null chara and otherwise calls `0x00562D30`, the worker of
   `_setTargetCharacter`.
2. `0x0075C6B0` on `W`. It resolves the chara, saves the dword at `+0x0C` of the
   cursor object at state `+0xB4`, sets the target of the cursor at index state
   `+0xB8` to the chara when that index is not negative, calls `0x00561BB0` on the
   state with 1, then sets the target of that cursor back to the saved dword.
3. `0x0075F070` on `Z` with the flag 1, the worker of `_setAllTargetCursorMask`.

The effect of `0x00561BB0` and the role of the saved dword were not traced. The
natives `_cancelAimCameraTutorial` and `_cancelLookAtPlayerTutorial` run the same
prelude and walk. They are listed in the manifest under `relatedNatives`.

## Ledger rows

These rows of the unimplemented ledger have a registration, an argument list, a
return list and a callback contract: `_canCreateActorByName`,
`_getActorByName`, `_getQuestActorForCutSceneReplay`, `_isExistStaticActor`,
`_prepareAllCommandStaticActor`, `_getUTF8StringLength`,
`_getUTF8StringByteLength`, `_normalizeDisplayName`,
`_replaceMacroCodeString`, `_runCharaSchedulerTutorial`, `_lookAtPlayerTutorial`
and `_aimCameraTutorial`. A client that implements the `Global` rows installs the
forwarder per `Global` native and passes the `global` object at position 1. It
still needs the engine name tables behind `0x00CD8870`, the static actor
containers behind `0x00D035D0` and `0x00D132B0`, the command sheet and the request
service behind `0x00767100`. A client that implements the tutorial rows still
needs the chara scheduler and look-at request services behind `0x0058C690` and
`0x00587F80` and the target cursor state.

## Open

- What a forwarded call does when the name does not resolve on the `global`
  object, and what the trampoline does for a table that is not a registered
  object.
- The record behind the `global` object: that `0x00CE2D50` stores the record in
  the userdata under the key `0x00010000` and the value of its `+0x08` dword.
- The text of the diagnostics `0x00CD4FA0` and `0x00CD5060` and the sink behind
  engine context `+0x1CC`.
- The engine name tables and the state dwords behind `0x00CD8870`, the container
  behind `0x00D035D0` and the use count of `0x00D037A0`.
- The command sheet that fills the vector at `0x0134B77C`, the column 3 byte and
  the effect of `0x00582BC0`.
- The run-time result of the UTF-8 length scan on malformed text, of the macro
  replacement on text with several spans and of the tutorial natives for a name
  number that no chara carries.
- The chara scheduler request behind `0x0058C690`, the look-at request behind
  `0x00587F80`, the camera step `0x00561BB0` and the writers and readers of the
  dword at `V +0x500`.

The next natives by value are ranked by the number of distinct scripts that
contain a call, with the call-site count as the tie break. Natives with a
contract in any manifest or a wire-level record in a contract page are left out
(`_setReactionTriggerBox` and `_getDealingAttached` are two of them), and so are the script callbacks that begin with `_on`, the work keys, the
descriptor suffix identifiers and the Lua level `_callFunction`.

| Rank | Native | Class | Scripts | Call sites | Why |
| ---: | --- | --- | ---: | ---: | --- |
| 1 | `_cancelAimCameraTutorial` | `WorldMaster` | 5 | 22 | Order 17 of the `WorldMaster` switchboard, the counterpart of `_aimCameraTutorial`. |
| 2 | `_lockTargetCursorControl` | `DesktopWidget` | 5 | 12 | Order 17 of the `DesktopWidget` switchboard. |
| 3 | `_unlockTargetCursorControl` | `DesktopWidget` | 5 | 12 | Order 18 of the `DesktopWidget` switchboard. |
| 4 | `_cancelLookAtPlayerTutorial` | `WorldMaster` | 5 | 11 | Order 15 of the `WorldMaster` switchboard, the counterpart of `_lookAtPlayerTutorial`. |
| 5 | `_commandDebug` | `Debug` | 5 | 8 | Order 7 of the `Debug` switchboard. |
| 6 | `_waitForMapLoaded` | `PlayerBaseClass` | 5 | 8 | Order 38 of the `PlayerBase` switchboard, a candidate yield native. |
| 7 | `_getAllCharacter` | `Debug` | 4 | 17 | Order 5 of the `Debug` switchboard. |
| 8 | `_getAllGroup` | `CharaBaseClass` | 4 | 10 | Order 43 of the `CharaBase` switchboard. |
| 9 | `_getGrandCompanyRank` | `PlayerBaseClass` | 4 | 9 | Order 52 of the `PlayerBase` switchboard. |
| 10 | `_isActorMainStatMode` | `CharaBaseClass` | 4 | 8 | Order 36 of the `CharaBase` switchboard, the sibling of the traced `_getActorMainStat` dword. |
| 11 | `_setWeather` | `PlayerBaseClass` | 4 | 8 | Order 40 of the `PlayerBase` switchboard. |
| 12 | `_createVirtualItem` | `CharaBaseClass` | 4 | 6 | Order 76 of the `CharaBase` switchboard. |
| 13 | `_getNetStatUser` | `CharaBaseClass` | 4 | 6 | Order 19 of the `CharaBase` switchboard. |
| 14 | `_getAreaType` | `PrivateAreaBaseClass` | 4 | 5 | Order 1 of the `PrivateAreaBase` switchboard. |
| 15 | `_lockCameraControl` | `PlayerBaseClass` | 3 | 12 | Order 33 of the `PlayerBase` switchboard, next to the lock-on pair. |
| 16 | `_unlockCameraControl` | `PlayerBaseClass` | 3 | 12 | Order 34 of the `PlayerBase` switchboard, next to the lock-on pair. |
| 17 | `_getClassName` | `Debug` | 3 | 11 | Order 3 of the `Debug` switchboard, next to `_getInstanceName`. |
| 18 | `_waitForTargetTutorial` | `DesktopWidget` | 3 | 9 | Order 35 of the `DesktopWidget` switchboard, a candidate yield native. |
| 19 | `_getLocalizedDisplayName` | `CharaBaseClass` | 3 | 8 | Order 24 of the `CharaBase` switchboard, next to `_getLocalizedDisplayNameForChat`. |
| 20 | `_getLowResolutionTime` | `Debug` | 3 | 7 | Order 6 of the `Debug` switchboard. No descriptor of the shipped scripts targets the registered name. |
| 21 | `_waitForCameraTutorial` | `DesktopWidget` | 3 | 6 | Order 36 of the `DesktopWidget` switchboard, a candidate yield native. |
| 22 | `_waitForTurning` | `CharaBaseClass` | 3 | 6 | Order 63 of the `CharaBase` switchboard, a candidate yield native. |

The manifest rows under `nextTranche` carry the same order.
The [chara and desktop contracts](chara-desktop-native-contract.md) cover ranks 2, 3,
10 and 19 and carry the refreshed order.

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
parser: the `global_u` descriptors, the `GETGLOBAL` and `SELF` call sites with the
argument counts of the Global natives, and the constants passed to the tutorial
natives. With explicit project and JDK bindings and a new absolute output path,
the repository route for function listings is:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Root assignment and forwarder | `0x00CD8990,0x00D099B0,0x00D084A0,0x00D07890,0x00D07BB0,0x00D07E10,0x00D077B0,0x00712C00,0x00CC6FA0,0x00CF3A90,0x00CF3A50,0x00CF3440,0x00CF3510,0x00CF3DB0` |
| Trampoline and global object | `0x00D08000,0x00D04DA0,0x00D04FE0,0x00CD77D0,0x00CE1720,0x00CF3740,0x00CCFB20,0x00CD4FA0,0x00CD5060,0x0078FAD0,0x00CC78A0,0x00CD99F0,0x00CD7970,0x00CD7690,0x00CE1DD0,0x00CE1BB0,0x00D085B0` |
| Registrars | `0x00753320,0x0073C510,0x007535C0,0x00741B80,0x0073C7B0,0x0073C900,0x0073CA50,0x00753710,0x00753860,0x0073B2B0,0x0073B550,0x0073B7F0,0x0073D770` |
| Global callbacks | `0x006FF1A0,0x006DCD10,0x0078CAF0,0x006FF3E0,0x006DCE60,0x0078CE10,0x006E2000,0x006DCED0,0x0078CF80,0x006DCF40,0x0078CFE0,0x006FF4E0,0x006FF600` |
| Name and static actor lookups | `0x00CC7200,0x00CD9C60,0x00CD8870,0x00CE16C0,0x00CC7A00,0x00CC72A0,0x00CC7130,0x00CC70E0,0x00CC7190,0x00CC7A50,0x00CC7160,0x00CC78C0,0x00D037A0,0x00D035D0,0x00767100` |
| Command list | `0x0076A9C0,0x00785F90,0x00723C60` |
| Strings | `0x00445E50,0x004451F0,0x00445450,0x00445EE0,0x00445220,0x0067AC00,0x006BE5E0,0x00596E10` |
| Tutorial natives | `0x006E6B10,0x006E6D90,0x006E6F60,0x0075D120,0x007176C0,0x00719480,0x00764150,0x0075C420,0x0075C580,0x0075C6B0,0x0075B6C0,0x0075F070,0x0058CAF0,0x0058C690,0x00589260,0x0057AB60` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
