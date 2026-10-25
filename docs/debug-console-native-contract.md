# Debug console, seeded Math, position and sub stat native contracts

[`manifests/debug_console_native_call_contract.json`](../manifests/debug_console_native_call_contract.json)
records the static Lua call contracts of the natives that the commanddebugger,
debug and system script areas call. Sixteen belong to the `Debug` class, which
the shipped scripts reach through the global `debug` object: `_printWarning`,
`_getClassName`, `_getAllCharacter`, `_getLowResolutionTime`, `_commandDebug`,
`_getText`, `_printText`, `_getTimeCost`, `_getEventPriority`,
`_getCharacterLocation`, `_getPlayingCutSceneActor`,
`_deleteQuestActorForPreview`, `_copyClipboard`, `_getSpreadSheetAllAttribute`,
`_isSpreadSheetExistAttribute` and `_getAllItem`. Two are the seeded `Math`
natives `_randomIntegerWithSeed` and `_randomFloatWithSeed`. Four are position and
group natives that scripts call under alias names: `_setPos`, `_setDir`,
`_setPosDirInn` and `_getAllExtendedTemporaryGroup`. The last seven read group
member and sub stat state: `_getMemberLocation` and six `_getSubStat` natives.
The record also settles that five script names are not registered literals.
Each row gives the registration site, the receiver type check, the declared
argument and return lists, the reads, the effects on client state, the failure
behavior and whether the call yields. The contracts describe client marshalling
and state, not debug console presentation, server commands or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data at
the cited addresses. `MEASURED` is counted or parsed by the method named in the
fact, from the executable, from the call-site index or from the Lua 5.1
bytecode of the installed client scripts. `INFERRED` is a name or role taken
from the surrounding instructions or script names that the bytes do not state.
`unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
Addresses are absolute VAs. The instruction listings were decoded directly
from the PE bytes through the section table after the size and hash were
checked. Callers were found by scanning `.text` for `rel32` `call` and `jmp`
instructions, so virtual and indirect callers are not covered. The registrar
shape, the type registry, the cell tags, the world object chain and the holder
adapter are the ones of the
[binding map contracts](binding-map-native-contract.md#binary-and-method), the
[scheduler contracts](scheduler-item-native-contract.md) and the
[tutorial control contracts](tutorial-control-native-contract.md#registration-and-dispatch).

The call-site and script counts agree with
`xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. They show that a
script contains a call, not that a script reaches it at run time. The
descriptors come from the `.le.lpb` files of an installed client, decoded by
[`tools/decode_lpb.py`](../tools/decode_lpb.py) and read with a Lua 5.1 bytecode
parser. The receivers, argument counts and result counts of the call sites come
from a local scan of the same bytecode. No tracked artifact carries them, so
they are `INFERRED`.

The type registry has fourteen entries. Entries 0 to 9 are `int`, `float`,
`bool`, `Utf8String`, `LuaControl*`, `AutoReleaseTentative`, `Nil`, `Table`,
`IndividualIndex` and `Variable`. Entries 10 to 13 are `LuaControlArray`,
`LuaManyTentativeControlArray`, `IntegerArray` and `VariantVectorArray`. The
constructor `0x00CC9D60` stores the `StackOperator` vftables `0x0110DF38` to
`0x0110E140` in steps of `0x28`.

## Registration and dispatch

The `Debug` class registers twenty natives from one switchboard, `0x00757CE0`, in
slot 2 of the `Debug` vftable `0x00FD51DC`. Four of them belong to earlier
records: `_printLog` (order 1) in the [scheduler contracts](scheduler-item-native-contract.md), `_getInstanceName`
(order 4) in the [work binder contracts](work-binder-native-contract.md),
`_getLocalizedDisplayName` (order 10) in the
[chara desktop contracts](chara-desktop-native-contract.md) and `_getItem`
(order 19) in the [item contracts](item-native-contract.md).

| Order | Native | Order | Native |
| ---: | --- | ---: | --- |
| 1 | `_printLog` | 11 | `_getTimeCost` |
| 2 | `_printWarning` | 12 | `_getEventPriority` |
| 3 | `_getClassName` | 13 | `_getCharacterLocation` |
| 4 | `_getInstanceName` | 14 | `_getPlayingCutSceneActor` |
| 5 | `_getAllCharacter` | 15 | `_deleteQuestActorForPreview` |
| 6 | `_getLowResolutionTime` | 16 | `_copyClipboard` |
| 7 | `_commandDebug` | 17 | `_getSpreadSheetAllAttribute` |
| 8 | `_getText` | 18 | `_isSpreadSheetExistAttribute` |
| 9 | `_printText` | 19 | `_getItem` |
| 10 | `_getLocalizedDisplayName` | 20 | `_getAllItem` |

Every `Debug` registrar builds the return list first and the argument list second
and installs the functor through `0x00CCCAD0` under the name literal with the
adjustment 0. The wrapper `0x00726930` constructs the `0x58` byte functor in
place with `0x00724A70`, and the holder constructor `0x0071AAE0` stores the holder
vftable `0x00FD5B4C`. Its invoke routine `0x0071AB50`, in cell `0x00FD5B50`, casts
the receiver with `0x009DA6CC` from `LuaControl` to the type descriptor
`0x012C0324`, which is `Debug`. A null cast returns false without calling the
callback. The holder is a const member function holder, so the native runs only
on a `Debug` control.

| Native | Class | Order | Registrar | Caller | Callback | Wrapper |
| --- | --- | ---: | --- | --- | --- | --- |
| `_printWarning` | `Debug` | 2 | `0x00736540` | `0x00757D11` | `0x006E7B90` | `0x00726930` |
| `_getClassName` | `Debug` | 3 | `0x00736690` | `0x00757D26` | `0x006DC680` | `0x00726930` |
| `_getAllCharacter` | `Debug` | 5 | `0x00736930` | `0x00757D50` | `0x006E7BA0` | `0x00726930` |
| `_getLowResolutionTime` | `Debug` | 6 | `0x00736A80` | `0x00757D65` | `0x006DC760` | `0x00726930` |
| `_commandDebug` | `Debug` | 7 | `0x00756E10` | `0x00757D7A` | `0x00708FC0` | `0x00726930` |
| `_getText` | `Debug` | 8 | `0x0073F470` | `0x00757D8F` | `0x006E4C50` | `0x00726930` |
| `_printText` | `Debug` | 9 | `0x0073F5C0` | `0x00757DA4` | `0x006E4DA0` | `0x00726930` |
| `_getTimeCost` | `Debug` | 11 | `0x00736BD0` | `0x00757DCE` | `0x006DC7D0` | `0x00726930` |
| `_getEventPriority` | `Debug` | 12 | `0x0074FAB0` | `0x00757DE3` | `0x006FCFB0` | `0x00726930` |
| `_getCharacterLocation` | `Debug` | 13 | `0x0074FC00` | `0x00757DF8` | `0x006FD040` | `0x00726930` |
| `_getPlayingCutSceneActor` | `Debug` | 14 | `0x0074FD50` | `0x00757E0D` | `0x006FD140` | `0x00726930` |
| `_deleteQuestActorForPreview` | `Debug` | 15 | `0x00736D20` | `0x00757E22` | `0x006E4F80` | `0x00726930` |
| `_copyClipboard` | `Debug` | 16 | `0x00736E70` | `0x00757E37` | `0x006DC840` | `0x00726930` |
| `_getSpreadSheetAllAttribute` | `Debug` | 17 | `0x0074FEA0` | `0x00757E4C` | `0x006FD180` | `0x00726930` |
| `_isSpreadSheetExistAttribute` | `Debug` | 18 | `0x0074FFF0` | `0x00757E61` | `0x006FD2C0` | `0x00726930` |
| `_getAllItem` | `Debug` | 20 | `0x00750290` | `0x00757E8F` | `0x006FD500` | `0x00726930` |

| Native | Class | Order | Registrar | Caller | Callback | Wrapper |
| --- | --- | ---: | --- | --- | --- | --- |
| `_randomIntegerWithSeed` | `Math` | 3 | `0x0073CCF0` | `0x00740F06` | `0x006DDF50` | `0x00726F60` |
| `_randomFloatWithSeed` | `Math` | 4 | `0x0073FDA0` | `0x00740F1F` | `0x006DDFC0` | `0x00726F60` |

| Native | Class | Order | Registrar | Caller | Callback | Wrapper |
| --- | --- | ---: | --- | --- | --- | --- |
| `_setPos` (`_setPosition`) | `CharaBase` | 3 | `0x0073E9F0` | `0x007574E6` | `0x006E3C60` | `0x00726460` |
| `_setDir` (`_setDirection`) | `CharaBase` | 4 | `0x0072E740` | `0x007574FB` | `0x006E3D70` | `0x00726460` |
| `_setPosDirInn` (`_setPositionDirectionInn`) | `PlayerBase` | 93 | `0x00741250` | `0x00754738` | `0x0071E6E0` | `0x007267D0` |
| `_getAllExtendedTemporaryGroup` (`_getExtendedTemporaryAllGroup`) | `CharaBase` | 44 | `0x00755670` | `0x00757843` | `0x00708450` | `0x00726460` |

| Native | Class | Order | Registrar | Caller | Callback | Wrapper |
| --- | --- | ---: | --- | --- | --- | --- |
| `_getMemberLocation` | `GroupBase` | 9 | `0x0074D2B0` | `0x00757C34` | `0x007000A0` | `0x007265C0` |
| `_getSubStatWaste` | `CharaBase` | 8 | `0x0074AB50` | `0x0075754F` | `0x006F9D60` | `0x00726460` |
| `_getSubStatGuard` | `CharaBase` | 9 | `0x0074ACA0` | `0x00757564` | `0x006F9E20` | `0x00726460` |
| `_getSubStatChant` | `CharaBase` | 10 | `0x0074ADF0` | `0x00757579` | `0x006F9EC0` | `0x00726460` |
| `_getSubStatObject` | `CharaBase` | 11 | `0x0074AF40` | `0x0075758E` | `0x006F9F70` | `0x00726460` |
| `_getSubStatMotionPack` | `CharaBase` | 13 | `0x0074B1E0` | `0x007575B8` | `0x006FA100` | `0x00726460` |
| `_getSubStatMode` | `CharaBase` | 14 | `0x00754E90` | `0x007575CD` | `0x00707FB0` | `0x00726510` |

The `Math` switchboard `0x00740EC0` registers four natives. `_randomInteger` and
`_randomFloat` are in earlier records. The `CharaBase` switchboard `0x007574A0`,
the `PlayerBase` switchboard `0x00753F90` and the `GroupBase` switchboard
`0x00757B70` are recorded in the scheduler, fade and nameplate contracts. The
wrappers `0x00726460`, `0x00726510`, `0x007267D0` and `0x007265C0` are the
`CharaBase` const, `CharaBase` non-const, `PlayerBase` const and `GroupBase` const
holders of those records, and `0x00726F60` is the `Math` non-const holder.

The registrar list builders are the ones of earlier records plus a few new
combinations. `0x0073D320` declares a control, a `Utf8String` and a `Variable`
and `0x0073D460` a control, an int and a `Variable`. `0x0072BFC0` declares a float
and an int, `0x0072C1B0` one `LuaManyTentativeControlArray` and `0x0073DD00` two
floats and an int. `0x0072BEC0`, `0x0072B660`, `0x0072B870`, `0x0072BBF0` and
`0x00740130` keep the declarations of the earlier records.

## Names that are not registered

`xivl-client-scripts:lua/napi_index.json` lists five names that the executable does
not register. Searching the whole file for each name as a NUL delimited ASCII or
UTF-16 literal finds none. The bytes of `_setDir` and `_setPos` occur only inside
the longer registered literals `_setDirection` (`0x00FD6644`), `_setPosition`
(`0x00FD7414`) and `_setPositionDirectionInn` (`0x00FD753C`). The bytes of
`_setPosDirInn`, `_callServerOnCommand_cpp` and `_getAllExtendedTemporaryGroup`
occur nowhere.

| Script name | What it is | Registered native |
| --- | --- | --- |
| `_setPos` | Alias descriptor `_setPos_inl` of `chara/charabaseclass_u` | `_setPosition` |
| `_setDir` | Alias descriptor `_setDir_inl` of `chara/charabaseclass_u` | `_setDirection` |
| `_setPosDirInn` | Alias descriptor `_setPosDirInn_inl` of `chara/player/playerbaseclass_u` | `_setPositionDirectionInn` |
| `_getAllExtendedTemporaryGroup` | Alias descriptor `_getAllExtendedTemporaryGroup_inl` of `chara/charabaseclass_u` | `_getExtendedTemporaryAllGroup` |
| `_callServerOnCommand_cpp` | Second value of the descriptor `_callServerOnCommand_inl` | `_callServerOnCommand` |

Scanning the 409 `rel32` callers of the install routine `0x00CCCAD0` confirms the
result. None passes a registrar literal equal to any of the five names. The
manifest field `installSiteScan` records the scan.

The first four are the aliases of the
[binding map contracts](binding-map-native-contract.md#aliases). The descriptor
returns the pair `self` and the registered name followed by `_cpp`. The resolver
stores the registered closure under the descriptor name without `_inl`, so a
script call of `obj:_setPos(x, y, z)` runs `_setPosition`. The index counts the
string constants of the descriptors, which is why the scripts appear to
reference names that the executable lacks. `_callServerOnCommand_cpp` is the
registered key itself. No script calls it, and the row of `_callServerOnCommand` in
the [command and talk contracts](command-talk-native-contract.md) records the
registration. All five resolve in the 1.23b client.

A script name that no descriptor targets and that has no registered literal would
reach the standard Lua 5.1 call of a nil value (`INFERRED`). The `Debug` natives that no
descriptor targets are a related case. `system/debug_u` assigns descriptors only
for `_getClassName`, `_getAllCharacter`, `_commandDebug` and `_getAllItem`, and a
plain function for `_getInstanceName`. The scripts call the other registered
names under their plain name on the global `debug` object, for example
`debug:_getText(...)`, while the registered key is the name followed by `_cpp`.
Whether a lookup joins the two was not traced.

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_printWarning` | `Debug` | `Utf8String` | none | no |
| `_getClassName` | `Debug` | `control` | `Utf8String` | no |
| `_getAllCharacter` | `Debug` | `Utf8String` | `LuaControlArray` | no |
| `_getLowResolutionTime` | `Debug` | none | `float` | no |
| `_commandDebug` | `Debug` | `control`, `Utf8String`, `Variable` | `Variable` | no |
| `_getText` | `Debug` | `control`, `int`, `Variable` | `Utf8String` | yes |
| `_printText` | `Debug` | `control`, `int`, `Variable` | none | no |
| `_getTimeCost` | `Debug` | `Utf8String`, `Utf8String` | `float`, `int` | no |
| `_getEventPriority` | `Debug` | `control` | `int` | no |
| `_getCharacterLocation` | `Debug` | `control` | `Utf8String` | no |
| `_getPlayingCutSceneActor` | `Debug` | none | `control` | no |
| `_deleteQuestActorForPreview` | `Debug` | `control` | none | no |
| `_copyClipboard` | `Debug` | `Utf8String` | none | no |
| `_getSpreadSheetAllAttribute` | `Debug` | `control` | `IntegerArray` | no |
| `_isSpreadSheetExistAttribute` | `Debug` | `control`, `int` | `bool` | no |
| `_getAllItem` | `Debug` | `control` | `LuaManyTentativeControlArray` | no |

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_randomIntegerWithSeed` | `Math` | `int`, `int`, `int` | `int`, `int` | no |
| `_randomFloatWithSeed` | `Math` | `float`, `float`, `int` | `float`, `int` | no |

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_setPos` | `CharaBase` | `float`, `float`, `float` | none | no |
| `_setDir` | `CharaBase` | `float` | none | no |
| `_setPosDirInn` | `PlayerBase` | `float`, `float`, `float`, `float` | none | no |
| `_getAllExtendedTemporaryGroup` | `CharaBase` | `int` | `LuaControlArray` | no |

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_getMemberLocation` | `GroupBase` | `int` | `int` | no |
| `_getSubStatWaste` | `CharaBase` | `int` | `int` | no |
| `_getSubStatGuard` | `CharaBase` | `int` | `bool` | no |
| `_getSubStatChant` | `CharaBase` | `int` | `int` | no |
| `_getSubStatObject` | `CharaBase` | none | `int`, `int`, `int` | no |
| `_getSubStatMotionPack` | `CharaBase` | none | `int` | no |
| `_getSubStatMode` | `CharaBase` | none | `Variable` | no |

`_getText` is the only native here that can suspend. Its text routine `0x00773B00`
calls the yield request `0x00CD2860` at `0x00773D24` on a path that does not
return the text at once.

## Debug class natives

### Class names, controls and items

`_getClassName` takes a control and pushes the name of the class record that the
registration record of the control links. The record lookup is `0x00CD7A30`. The
routine `0x00CC6FA0` copies the string at `+0x50` of the record linked at record
`+0x0C`, the same field that `_getInstanceName` reads from the record itself. The
body `0x0078C3C0` takes the flag 1 from this callback and replaces the name
`MyPlayer` with `Player`.

`_getAllCharacter` takes a class name and pushes the matching controls from the
engine registry. The names `ActorBaseClass`, `CharaBaseClass`, `PlayerBaseClass`
and `NpcBaseClass` select four fixed predicates. Any other name builds a named
predicate with `0x0071B2A0`. The body `0x0078C620` enumerates the handles with
`0x00CC88D0` and keeps a handle that passes the validity test `0x00CC72A0`, fails
the flag test `0x00CC7310` and is accepted by the predicate. A handle whose
instance name starts with `__debug` is left out. The count goes first and then
one control per element, the layout of `LuaControlArray` that the
[chara world contracts](chara-world-native-contract.md#group-list) describe.

`_getAllItem` takes a chara control, fills a dword vector from the item package
manager at chara `+0xD8` through `0x006EF630`, calls `0x006EF3F0` for each
element to fill a vector of its own, appends it to a result vector with
`0x007208E0` and builds one `0x8C` byte list object from the result with
`0x007252B0`. It pushes the object as a control. The element layout and the bodies of the
three routines were not traced.

### Command dispatch

`_commandDebug` takes a player control, a selector string and optional values. The
selectors `dev`, `gm`, `test` and `func` name a debug object by the format
`_comdebDEV%08X`, `_comdebGM%08X`, `_comdebTEST%08X` or `_comdebFUNC%08X` with the
first dword of the binding reference of the control. `dev`, `gm` and `test` look
the name up with `0x00CC7A00`, which the catalog names as the lookup that
creates. `func` uses `0x00CC7A20`, which does not create, and pushes Nil and the
selector when nothing is found. A resolved object receives the Lua call
`_onCommand` through `0x00CD25C0` with the values from cell 2 on, and the results
go back through `0x00CCA950`. The selector `prog` calls `0x006FCB80` and never
calls `_onCommand`. Which scripts create the named objects was not traced.

### Text and log

`_getText` and `_printText` take an actor control, a text id and optional values.
Both load the object at `Y +0x0DC` and collect the cells from index 2 on with
`0x007702C0`. `_getText` calls `0x00773B00` on that object and pushes the
resulting `Utf8String`. `_printText` builds a `PrintTextListener` with
`0x00713220` and calls `0x00771C20`. The listener slot `0x0071C5F0` prefixes the
text with `<debug>: ` and writes it to the log sink with the kind `0x1F`, as the
[scheduler contracts](scheduler-item-native-contract.md) record for the other
`<debug>` callers. `_printWarning` is a jump to the callback of the `Debug`
`_printLog` registration and writes with the same kind and prefix. No script of the
installed client references `_printWarning`.

### Constant and empty results

Three natives return a value that does not depend on client state. The routine
`0x006F0F10` that `_getSpreadSheetAllAttribute` calls only clears the output
vector, so the native pushes the count 0 and no element. `_isSpreadSheetExistAttribute`
reads a `SpreadSheet` and an int and pushes false. `_getTimeCost` tests with
`0x00CD9C80` whether the Lua class named by its first string has a function member
named by the second, and pushes the float 0.0 and the int 0 on both outcomes. A
client that mirrors these natives should return the same constants.

### State reads and actions

`_getLowResolutionTime` pushes a float. It is the unsigned qword at the address
that `0x00CC7B20` returns, offset 8 of the object that engine implementation
`+0x184` points to, divided by 1000000.0. `_getEventPriority` reads the chara
dword at `+0x0F8` (the policy manager slot, INFERRED) and pushes a byte that
virtual slot 8 of the object linked by that dword reports, or Nil.
`_getCharacterLocation` pushes the `Utf8String` at `+0xB3C` of the chara record
that the identity names. `_getPlayingCutSceneActor` pushes the control of the first
match in the container at `Y +0x104`. `_copyClipboard` converts its `Utf8String`
to UTF-16 and sets it as `CF_UNICODETEXT` through `GlobalAlloc`, `OpenClipboard`
and `SetClipboardData`. `_deleteQuestActorForPreview` calls virtual slot 29 of a
`QuestBase` control, which is the routine `0x006DBEA0`.

## Seeded Math natives

`_randomIntegerWithSeed` and `_randomFloatWithSeed` take a seed in cell 2 and
push the result followed by the stepped seed. They never touch the state dword at
`Math +0x64` that `_randomInteger` and `_randomFloat` advance. The step is
`seed * 0x41C64E6D + 0x3039` in 32 bits, and r is bits 16 to 30 of the result.
The integer native computes the value of `_randomInteger` from r and the float
native computes the value of `_randomFloat`. Only `_randomIntegerWithSeed` has a
script caller, in `chara/npc/mapobj/mapobjfireworks`.

## Position natives

`_setPosition` and `_setDirection` do not read their receiver. They take the
identity at `ExecuteParameters +0x0C`, build a four float vector of position and
facing for the chara record with `0x0075C230`, replace the position or the facing
with the arguments and post two scene records through `0x0075F120`. Record `0x24`
carries the payload 0, facing, 0, 0 and record `0x25` carries x, y, z and facing. The
scene packets are `0x39` and `0x3A` because `0x004D7980` adds `0x15`. The
[scene record choke point record](../manifests/scene_record_choke_point.json)
names both natives as the position and direction state trigger. The facing taken
from the record is folded into one turn when the record has a parent transform.
`_setPositionDirectionInn` is a thunk through `PlayerBase` slot `0x1F8`. The
`PlayerBase` routine only returns and the `MyPlayer` routine posts the same two
records with all four floats and then calls `0x0075C770`.
`_getExtendedTemporaryAllGroup` calls the group list helper `0x00701250` with the
flag 1, the sibling of `_getAllGroup`.

## Group member and sub stat natives

`_getMemberLocation` subtracts 1 from its int and reads the entry at that index of
the 0x10 byte member vector at `+0x84` of the group data object that the pointer at
receiver `+0x68` addresses, with an unsigned bounds test. The `_getSubStat` natives read
bit fields of the dword at chara `+0xF8` that `0x0075C1D0` returns. The sibling
`_getSubStatBreakage` is in the
[chara world contracts](chara-world-native-contract.md).

| Native | Input | Result |
| --- | --- | --- |
| `_getSubStatWaste` | Slot 0 to 6 | Two bit field. Slot 0 is bits 30 and 31, slot 1 bits 28 and 29, slot 5 bits 26 and 27 and slot 6 bits 24 and 25. Slots 2 to 4, slots above 6 and negative values give 0 (the compare is unsigned). |
| `_getSubStatGuard` | 1 or 2 | Bit 17 for 1 and bit 16 for 2 as a bool. Other values give false. |
| `_getSubStatChant` | 1 or 2 | Bits 12 to 15 for 1 and bits 8 to 11 for 2. A zero field and other values give Nil. |
| `_getSubStatObject` | none | Bits 14 and 15, bits 12 and 13, and bits 8 to 11 or Nil when zero. |
| `_getSubStatMotionPack` | none | The byte at chara `+0xFE`. |
| `_getSubStatMode` | none | The word at chara `+0xFC` expanded by the count byte at the status record. See below. |

`_getSubStatMode` reads the count at byte `+0x18` of the status record that
`0x006EEC00` returns. The routine `0x006F1100` masks the low byte of the word with
the table `0xFF`, `0x7F`, `0x3F`, `0x1F`, `0x0F`, `0x07`, `0x03`, `0x01` at
`0x00FD616C` indexed by the count. The native pushes that remainder as an int unless
the count is 8, then one bool per counted bit from bit 7 down.

## Script surface

The shipped scripts call the `Debug` natives on the global `debug` object, as in
`debug:_getAllCharacter(name)`. The seeded integer native is called on the global
`math` object. The call counts and the chunks that contain them are in each row
under `corpusCallSites`. The local scan finds no method call for twelve of the
natives (INFERRED), only string constants of `commanddebugger/commanddebuggerdev`: `_getTimeCost`,
`_getEventPriority`, `_getSpreadSheetAllAttribute`, `_isSpreadSheetExistAttribute`,
`_getAllItem`, `_getMemberLocation` and the six `_getSubStat` natives. What the
chunk does with the constants was not traced.

## Not covered

The commanddebugger and system areas call a few more unimplemented natives that
other records own. `_getGroupCurrent` and `_getGroupByDisplayName` are group
natives. `_getKeyboardFocusedControl` belongs to the widget tree natives and
`_setTargetCharacterByDisplayName` to the desktop natives. `_skip` is a `CutScene`
native. `_getHamletSupplyRanking` and `_countHamletSupplyRanking` are hamlet
natives. The names `_math`, `_string` and `_table` are library namespaces, not
natives, as the binding map contracts record.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using the
procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes with the route of the
[binding map contracts](binding-map-native-contract.md#reproduction). The function
VAs for `$Addresses` are:

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Switchboards | `0x00757CE0,0x00740EC0,0x007574A0,0x00753F90,0x00757B70` |
| Registrars | `0x0072E740,0x00736540,0x00736690,0x00736930,0x00736A80,0x00736BD0,0x00736D20,0x00736E70,0x0073CCF0,0x0073E9F0,0x0073F470,0x0073F5C0,0x0073FDA0,0x00741250,0x0074AB50,0x0074ACA0,0x0074ADF0,0x0074AF40,0x0074B1E0,0x0074D2B0,0x0074FAB0,0x0074FC00,0x0074FD50,0x0074FEA0,0x0074FFF0,0x00750290,0x00754E90,0x00755670,0x00756E10` |
| Callbacks | `0x006DC680,0x006DC760,0x006DC7D0,0x006DC840,0x006DDF50,0x006DDFC0,0x006E3C60,0x006E3D70,0x006E4C50,0x006E4DA0,0x006E4F80,0x006E7B90,0x006E7BA0,0x006F9D60,0x006F9E20,0x006F9EC0,0x006F9F70,0x006FA100,0x006FCFB0,0x006FD040,0x006FD140,0x006FD180,0x006FD2C0,0x006FD500,0x007000A0,0x00707FB0,0x00708450,0x00708FC0,0x0071E6E0` |
| Debug bodies | `0x0078C3C0,0x0078C620,0x0078CA80,0x0078C930,0x0078C180,0x00CC7560,0x00CC6FA0,0x00CC7B20,0x00CC8890,0x00CD9C80` |
| Text and log | `0x00773B00,0x00771C20,0x007702C0,0x00713220,0x0071C5F0,0x006BF420,0x006E7AB0` |
| Console | `0x0078B910,0x0078B9B0,0x0078BA50,0x0078BAF0,0x00CC73B0,0x00CC7A00,0x00CC7A20,0x00CD25C0,0x00CCA950,0x006FCB80` |
| Math | `0x0078D270,0x0078D3A0,0x0078BEB0,0x0078BEC0` |
| Position | `0x0075C230,0x0075F120,0x004CFE30,0x004D7980,0x006E6420,0x0075C770,0x00701250` |
| Sub stat | `0x0075C1D0,0x0075C1F0,0x0075C210,0x006F1100,0x0074F770,0x006C08A0,0x006C0D70` |

## Boundaries

- These are static client observations. No live Lua call or retail-client walk
  was performed.
- Script call-site counts are static presence in the shipped scripts. They do not
  establish which natives a given script reaches at run time.
- The bodies of the `_getAllCharacter` predicates, of the text routines
  `0x00773B00` and `0x00771C20`, of `0x006FCB80` and of the group record routines
  were not traced.
- The consumers of the scene packets `0x39` and `0x3A` and the effect of
  `0x00587020` were not traced.
- Whether a plain script name joins the registered `_cpp` key for the `Debug`
  natives that have no descriptor was not traced.
