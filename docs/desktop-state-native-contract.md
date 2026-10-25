# User macro, display name target, text command, countdown, item search and widget container native contracts

[`manifests/desktop_state_native_call_contract.json`](../manifests/desktop_state_native_call_contract.json)
records the static Lua call contracts of sixteen `DesktopWidget` natives. Seven
read or write the user macro bank: `_setUserMacroTitle`, `_getUserMacroTitle`,
`_setUserMacroIcon`, `_getUserMacroIcon`, `_setUserMacroData`,
`_getUserMacroData` and `_saveUserMacro`. Three reach other client state:
`_setTargetCharacterByDisplayName`, `_parseTextCommand` and `_sendCountDown`.
`_waitForItemSearchWidget` opens a widget and yields. Five work on the widget
container: `_createWidgetInWidgetContainer`, `_isExistWidgetInWidgetContainer`,
`_isCreatingWidgetInWidgetContainer`, `_getWidgetFromWidgetContainer` and
`_deleteCreatingWidgetInWidgetContainer`. Each row gives the registration site,
the receiver holder, the declared argument and return lists, the pushes of every
branch, the reads, the effects on client state, the failure behavior and whether
the call yields. The contracts describe client marshalling and state, not macro
file contents, display name values, text command grammar, countdown semantics,
widget container contents or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data at
the cited addresses. `MEASURED` is counted or parsed by the method named in the
fact, from the executable or from the call-site index of the installed client
scripts. `INFERRED` is a name or role taken from the surrounding instructions or
script names that the bytes do not state. `unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
The listings, the caller scan and the reproduction route are the ones of the
[binding map contracts](binding-map-native-contract.md#binary-and-method). A
second pass checked that every cited locator begins an instruction of its decoded
function and compared the operands, name literals, vftable cells, list builder
calls, constants and call targets named below with the listings. `R`, `X`, `Y`,
`W`, `V` and `Z` name the world object chain of the
[Global contracts](global-native-contract.md#binary-and-method) and the
[target cursor state](target-cursor-native-contract.md#cursor-state). The registrar
shape, the type registry, the cell tags, the invalid-parameter route and the
holders are the ones of the
[nameplate, actor and group contracts](nameplate-group-native-contract.md), the
[chara desktop contracts](chara-desktop-native-contract.md#registration) and the
[widget contracts](widget-native-call-contract.md).

The call-site and script counts agree with
`xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. They show that a
script contains a call, not that a script reaches it at run time. The argument
counts and the descriptor selectors come from a local Lua 5.1 bytecode scan of the
installed client scripts, decoded with [`tools/decode_lpb.py`](../tools/decode_lpb.py).
The script sources are not redistributed and no tracked artifact carries those
values, so they are `INFERRED`.

## Selection

The selection covers every `DesktopWidget` native that
`xivl-client-scripts:lua/napi_index.json` lists and that the ledger of the client
rewrite marks unimplemented. The ledger has 17 such rows, less
`_getLastAttacker`, a row of the
[achievement and target contracts](achievement-target-native-contract.md#target-natives).
The 16 natives that remain are all registered by the `DesktopWidget` switchboard,
so no unimplemented `DesktopWidget` row of the ledger is left without a contract.
`_setTargetCursorImage` is a stub row of the ledger and is contracted in the
[target cursor contracts](target-cursor-native-contract.md).

## Registration

Every native is declared by a `_u` script descriptor named `<name>_inl` that
returns the selector `self` and the target `<name>_cpp`. The descriptor table is
`DesktopWidget` in `widget/desktopwidget_u` (`INFERRED`). All sixteen registrars
use the wrapper `0x00726BF0`, the `DesktopWidget` const holder. The order of a
native is its position among the 44 rel32 calls of the switchboard `0x00757EA0`,
counted from 1.

| Native | Order | Registrar | Caller | Callback |
| --- | ---: | --- | --- | --- |
| `_setTargetCharacterByDisplayName` | 12 | `0x007399C0` | `0x00757FA3` | `0x006E7D70` |
| `_setUserMacroTitle` | 25 | `0x0073FB00` | `0x007580B4` | `0x006E7FE0` |
| `_getUserMacroTitle` | 26 | `0x00751B80` | `0x007580C9` | `0x006FDF70` |
| `_setUserMacroIcon` | 27 | `0x0073A2F0` | `0x007580DE` | `0x006E5640` |
| `_getUserMacroIcon` | 28 | `0x00751CD0` | `0x007580F3` | `0x006FE090` |
| `_setUserMacroData` | 29 | `0x007418E0` | `0x00758108` | `0x006E80B0` |
| `_getUserMacroData` | 30 | `0x00751E20` | `0x0075811D` | `0x006FE140` |
| `_saveUserMacro` | 31 | `0x0073A440` | `0x00758132` | `0x006E1B70` |
| `_parseTextCommand` | 32 | `0x00751F70` | `0x00758147` | `0x006FE2A0` |
| `_waitForItemSearchWidget` | 33 | `0x0073A590` | `0x0075815C` | `0x006E1B90` |
| `_createWidgetInWidgetContainer` | 39 | `0x00756F60` | `0x007581DA` | `0x007094B0` |
| `_isExistWidgetInWidgetContainer` | 40 | `0x00752360` | `0x007581EF` | `0x006FE550` |
| `_isCreatingWidgetInWidgetContainer` | 41 | `0x007524B0` | `0x00758204` | `0x006FE5C0` |
| `_getWidgetFromWidgetContainer` | 42 | `0x00752600` | `0x00758219` | `0x006FE630` |
| `_deleteCreatingWidgetInWidgetContainer` | 43 | `0x0073AAD0` | `0x0075822E` | `0x006E5880` |
| `_sendCountDown` | 44 | `0x0073AC20` | `0x00758247` | `0x006E81D0` |

The switchboard is stored at slot 2 of the vftable `0x00FD5B8C`. Each of its calls
sits behind a test of the byte at `+0x0E` of the switchboard argument. The first
call of a registrar builds the return list and the second builds the argument
list. No callback is the target of a rel32 call or jump, so each is reached only
through the holder. The holder `0x00726BF0` has the vftable `0x00FD5C34` and casts
the receiver to the type descriptor `0x012C2108`. A null cast returns without
calling the callback.

## Contracts

| Native | Arguments | Returns | Yields |
| --- | --- | --- | --- |
| `_setUserMacroTitle` | `int`, `int`, `Utf8String` | none | no |
| `_getUserMacroTitle` | `int`, `int` | `Utf8String` | no |
| `_setUserMacroIcon` | `int`, `int`, `int` | none | no |
| `_getUserMacroIcon` | `int`, `int` | `int` | no |
| `_setUserMacroData` | `int`, `int`, `int`, `Utf8String` | none | no |
| `_getUserMacroData` | `int`, `int`, `int` | `Utf8String` | no |
| `_saveUserMacro` | none | none | no |
| `_setTargetCharacterByDisplayName` | `int`, `Utf8String` | none | no |
| `_parseTextCommand` | `Utf8String` | 13 values | no |
| `_sendCountDown` | `int` or `Nil`, `Utf8String` or `Nil` | none | no |
| `_waitForItemSearchWidget` | none | none | yes |
| `_createWidgetInWidgetContainer` | `int`, `Utf8String`, `Variable` | none | no |
| `_isExistWidgetInWidgetContainer` | `int` | `bool` | no |
| `_isCreatingWidgetInWidgetContainer` | `int` | `bool` | no |
| `_getWidgetFromWidgetContainer` | `int` | `LuaControl*` | no |
| `_deleteCreatingWidgetInWidgetContainer` | `int` | none | no |

The list builders are `0x0072B440` for none, `0x00728C20` for an int,
`0x00728B70` for a bool, `0x0072B5B0` for a `Utf8String`, `0x0072C260` for a
`LuaControl*`, `0x00583CE0` for two ints, `0x0072B660` for three ints,
`0x0072B4B0` for an int and a `Utf8String`, `0x0073D9F0` for two ints and a
`Utf8String`, `0x00740690` for three ints and a `Utf8String`, `0x0073DAF0` for an
int, a `Utf8String` and a `Variable`, and `0x00745380` for the thirteen results
of `_parseTextCommand`. The first call of a registrar builds the return list and
the second the argument list. The builders select registry entries by position.
`0x0072B440` reserves one slot and appends nothing. The argument readers are
`0x005819A0` for an int and `0x0071CE70` for a `Utf8String`, and `0x00753B90`
copies the cells from a start index to the end into a vector. The pushers are
`0x00584F70` for an int, `0x00748870` for a bool, `0x007487C0` for a `Utf8String`,
`0x00748920` for nil and `0x00748B30` for a control. Every callback tests the
size of the cell vector before it reads a cell, and a failed test calls
`0x009D22B4`, the invalid-parameter route of the
[target cursor record](target-cursor-native-contract.md#selection-and-the-failure-path).

## World object

The callbacks reach one client object through `0x00CC7510` on `ExecuteParameters`
`+0x04`. With `R` the address that routine returns, `X = [R]`, `Y = [X +0x04]`,
`W = [Y]`, `V = [W]` and `Z = [Y +0x04]`, the chain of the
[scheduler contracts](scheduler-item-native-contract.md#world-object-and-identity-lookup).
These natives read these fields. The roles are `INFERRED` from the natives that
use them.

| Field | Used by |
| --- | --- |
| `V +0x4DC` | The widget manager `M` of `_waitForItemSearchWidget`, through `0x004D7380`. |
| `V +0x4E4` | The actor identity container that `_setTargetCharacterByDisplayName` walks, through `0x004D73A0`. |
| `V +0x8BC` | The text command parser object of `_parseTextCommand`, through `0x004D7520`. |
| `V +0x998` | The user macro bank `B` of the macro natives, through `0x004D7540`. |
| `V +0x174EC` | The connection object `N` of `_sendCountDown`, through `0x004D7460`. |
| `Y +0x114` | The widget container manager `C` of the container natives. |

## User macro natives

The macro natives pass `W` to a routine of the `0x0075CB..` group, which loads
`V = [W]`, takes the bank `B = V +0x998` and finds a record through `0x004B54A0`.
That routine returns `B +0x14 + (20 * group + macro) * 0x3A0`, where both numbers
are the Lua numbers minus 1. The constructor `0x004B54C0` builds 5 groups of
`0x14` records, so the first number is `INFERRED` to select a group and the second
a macro inside it. No instruction on any macro path compares a number with a bound.

| Record offset | Content |
| --- | --- |
| `+0x000` | Icon dword. |
| `+0x004` | Title `Utf8String` of `0x54` bytes. |
| `+0x058` | Ten line `Utf8String` values of `0x54` bytes each. |

`_setUserMacroTitle` (`0x006E7FE0`) reads two ints and a string, assigns the string
to the title through `0x00447450` and stores the byte 1 at `B +0x0D`.
`_setUserMacroIcon` (`0x006E5640`) reads three ints and stores the third, without
a decrement, as the icon dword. `_setUserMacroData` (`0x006E80B0`) reads three ints
and a string and assigns the string to the line `0x58 + line * 0x54` of the record.
All three set the dirty byte at `B +0x0D`. The getters `_getUserMacroTitle`
(`0x006FDF70`), `_getUserMacroIcon` (`0x006FE090`) and `_getUserMacroData`
(`0x006FE140`) read the same numbers and write nothing. The two string getters copy
the field into an empty local `Utf8String` and push it through `0x007487C0`. The
icon getter pushes the dword through `0x00584F70`.

`_saveUserMacro` (`0x006E1B70`) reads no cell. It calls the writer `0x004C7A80` on
`B` with the force argument 0. The writer returns at once when the dirty byte is
zero and the force argument is zero, and it never clears the dirty byte. Otherwise
it loops over 5 groups with the stride `0x4880` and over `0x14` records, and it
builds a buffer. A record writes the title behind the tag byte `T` at
`0x00F8D648`, the icon behind the tag byte `I` at `0x00F8D654` as the 7 digits of
`%07X` with the length 8, and ten lines behind the tag byte `L` at `0x00F8D658`.
The title and line lengths are 16-bit values that count the terminating zero. A
byte of the writer record selects their byte order. The writer then formats the
file name `mcr%d` from the literal at `0x00F8D65C` and the byte at `B +0x0E` and
calls virtual slots of the object behind `B +0x04` with the dword at `B +0x10` and
the name. The meaning of that dword, the writer of the name byte, the slot effects
and the reader of the file were not traced.

## Display name target

`_setTargetCharacterByDisplayName` (`0x006E7D70`) reads a cursor number and a
name. It builds a visitor of the type `s_CharaIterateDisplayName` (vftable
`0x00FD5360`) with `0x00713AE0` and walks the actor container with `0x00764150`,
the walker that `_transformIntoChocobo` also uses. The visit method `0x00718F40`
resolves each identity through `0x00CC7A50` and casts the control to `CharaBase`
(`0x012709A4`). A control passes when its byte at `+0x5C` is nonzero, the record
that its dword at `+0x60` addresses has a nonzero byte at `+0x59` and the string
at record `+0x04` equals the name in length and bytes through `0x00445D20`. This
is the display name record of the
[chara desktop contracts](chara-desktop-native-contract.md#area-and-display-name-natives).
The first match stores its identity in the visitor and ends the walk. The callback
then calls the target cursor worker `0x0075B6C0` on `Z` with the cursor number
minus 1 and the identity. That worker resolves the chara through `0x004D9970` and
calls `0x00562D30`, the worker of `_setTargetCharacter`, which builds the
serverbound record `0x00CD` with the second dword `0x18` as the
[achievement and target contracts](achievement-target-native-contract.md#target-natives)
record. A name that no control holds ends the native without a call.

The visit method loads the record pointer at control `+0x60` and reads its `+0x59`
byte without a null test. A control with a nonzero `+0x5C` byte and a null record
pointer would dereference the address `0x59`. That case was not run.

## Text command and countdown

`_parseTextCommand` (`0x006FE2A0`) declares one `Utf8String` and thirteen results:
two ints, three `Which<Utf8String, int>` entries and eight `Utf8String` entries.
The callback reads the line, calls the parser core `0x0056E380` on the object at
`V +0x8BC` and fills a local record. The record holds a word at `+0x00`, a word at
`+0x02`, three dwords at `+0x04` and a vector of `Utf8String` values at `+0x10`.
A false answer pushes 13 nils. A true answer pushes the signed first word and the
unsigned second word as ints, then as many dwords as the second word says, with
nil for a negative dword, then every string of the vector, and then nils while
fewer than 13 values were pushed. Two routes of the parser core store `0xFFFF` in
the first word, which reaches the script as -1. 13 is the padding target and not a
cap: the callback starts a pad counter at 11 (`0x006FE375`), decrements it once per
dword and once per string and pads only while it is above 0 (`0x006FE42C`). Neither
the dword loop, bounded by the second word, nor the string loop, bounded by the
vector end, is capped, so more than 13 values are pushed when the second word plus
the string count exceeds 11. A second word above 3 reads past the three dwords into
the vector fields at record `+0x10`. The
[text command ingress record](../manifests/text_command_ingress.json) places the
native in the `executeTextCommand` route of the connector script, with the chat
route as the fallback for a failed parse. The grammar and the limits of the parser
core were not traced here.

`_sendCountDown` (`0x006E81D0`) accepts a `Nil` for either declared argument. A
`Nil` first argument keeps the default byte 5 and a `Nil` second argument keeps the
empty string. The routine `0x0075ED30` takes the connection object `N` at
`V +0x174EC` and sends nothing when `N` is null or when `1000 * [N +0x30C] +
[N +0x310]`, taken as a 64-bit sum, is zero. Otherwise it builds a record on the
stack and passes it to the sender `0x004D6D10`. The record is one contiguous
layout of `0x48` bytes (`STATIC`): the dword `0xCF` at `+0x00`, the dword `0x40`
at `+0x04`, the count byte at `+0x18`, the low and high dwords of the 64-bit sum at
`+0x20` and `+0x24`, and the `0x20` byte text buffer at `+0x28..+0x47`, written as
four consecutive qwords. Nothing in the routine writes `+0x08..+0x17` or
`+0x19..+0x1F`, so those bytes are uninitialized stack. The text is copied as
min(length, `0x20`) bytes with no forced terminator, so a text of 32 or more bytes
has no null byte. Reading the `0x40` as a payload length after an `0x08` byte
header matches the extent (`INFERRED`). `xivl-opcodes:opcodes.json` names the
serverbound opcode `0x00CF` `CountdownRequestPacket` with the note
`no_pcap_evidence` (`INFERRED`). The only script site passes one argument.

## Item search widget wait

`_waitForItemSearchWidget` (`0x006E1B90`) takes no argument. It calls `0x0075BB30`
on `Z`, which takes the widget manager `M = [V +0x4DC]` and runs `0x0066ED80`. That
routine asks the factory `0x0066DD00` for the widget of kind 1, calls `0x004FFCF0`
on it, stores it at `M +0xC8` and ORs the dword at `0x00F9D07C` into the widget
dword at `+0x224`. The kind 1 case constructs the widget through `0x0052A540`,
which builds the form path `\widget\ItemSearchWidget.form` from the literal at
`0x00F977B0`. The callback then builds a resume checker of 8 bytes with the vftable
`0x00FD537C`, whose RTTI name is `s_ItemSearchWidgetResumeChecker`, and requests a
yield through `0x00CD2860`. The poll in slot 1, `0x00713E20`, stores the waiting
result `0x0130CECC` while `M +0xC8` is nonzero and the done result `0x01377ECC`
afterwards, the convention of the
[presentation contracts](presentation-native-contract.md). The writer that clears
`M +0xC8` was not traced.

## Widget container natives

The container manager `C` is the dword at `Y +0x114`. It holds a vector of 8 byte
entries between `C +0x0C` and `C +0x10`. An entry has an identity dword at `+0x00`
and a state byte at `+0x04`. The empty identity is the dword at `0x0130C778`, whose
image value is `0xE0000000`. A map at `C +0x18` holds pending creation records.

`_createWidgetInWidgetContainer` (`0x007094B0`) reads a slot number, a name and the
remaining cells. It calls `0x00775DD0` on `C`, which joins the literal `/Widget/` at
`0x00FDF6E0` and the name, inserts a pending record through `0x0078B750`, stores the
slot number at record `+0x64`, tests the slot against the entry count and stores the
state byte 1 in the entry. `_isCreatingWidgetInWidgetContainer` (`0x006FE5C0`)
pushes that byte through `0x00748870`. `_isExistWidgetInWidgetContainer`
(`0x006FE550`) pushes true when the state byte is 1, and otherwise true unless the
entry identity is the empty identity. `_getWidgetFromWidgetContainer`
(`0x006FE630`) copies the identity of the entry, resolves it through `0x00CC7A50`,
casts the control to `WidgetBase` (`0x012C1964`) and pushes the result through
`0x00748B30` with no null test. The `LuaControl*` push slot `0x00CF9D60` pushes nil
for a zero dword, as the
[achievement and target contracts](achievement-target-native-contract.md) record, so
a script receives nil when the identity does not resolve to a `WidgetBase`. Every one of these four routines tests the slot
against the entry count with an unsigned compare and calls `0x009D22B4` on
failure, so slot 0 and a slot above the count reach the invalid-parameter route.

`_deleteCreatingWidgetInWidgetContainer` (`0x006E5880`) calls `0x00765150`. For an
entry that holds the empty identity the routine walks the map at `C +0x18` and
stores the byte 1 at element `+0xC8` of every element whose dword at `+0xC4` equals
the slot number. For any other identity it resolves the control and calls
`0x006DBE20` with it. In both cases it ends by storing the empty identity and the
state byte 0 in the entry. That the element fields are the slot number and a byte of
the pending records is `INFERRED` from the offsets. What `0x006DBE20` does and how a
pending record becomes a widget were not traced.

## Script call sites

| Native | Index sites | Scripts | Direct calls | Debug console |
| --- | ---: | ---: | ---: | ---: |
| `_setUserMacroTitle` | 1 | 1 | 1 | 0 |
| `_getUserMacroTitle` | 3 | 2 | 3 | 0 |
| `_setUserMacroIcon` | 1 | 1 | 1 | 0 |
| `_getUserMacroIcon` | 4 | 2 | 4 | 0 |
| `_setUserMacroData` | 1 | 1 | 1 | 0 |
| `_getUserMacroData` | 2 | 2 | 2 | 0 |
| `_saveUserMacro` | 1 | 1 | 1 | 0 |
| `_setTargetCharacterByDisplayName` | 1 | 1 | 1 | 1 |
| `_parseTextCommand` | 1 | 1 | 1 | 0 |
| `_sendCountDown` | 1 | 1 | 1 | 0 |
| `_waitForItemSearchWidget` | 1 | 1 | 1 | 0 |
| `_createWidgetInWidgetContainer` | 1 | 1 | 1 | 0 |
| `_isExistWidgetInWidgetContainer` | 3 | 1 | 3 | 0 |
| `_isCreatingWidgetInWidgetContainer` | 2 | 1 | 2 | 0 |
| `_getWidgetFromWidgetContainer` | 2 | 1 | 2 | 0 |
| `_deleteCreatingWidgetInWidgetContainer` | 1 | 1 | 1 | 0 |

The first three columns are `MEASURED` against the call-site index and total 26
sites. The direct call column is the count of method calls that the bytecode scan
resolves. The last column counts index sites in `commanddebugger` scripts. The
scan shows that every site passes the number of arguments that the registrar
declares, except `_sendCountDown`, which passes one of its two optional arguments,
and `_createWidgetInWidgetContainer`, whose argument list ends in a call or vararg
expression (`INFERRED`). `_parseTextCommand` takes its results as an open list.
`_getWidgetFromWidgetContainer` has one tail call site. The macro natives are called
from `widget/usermacroeditwidget`, `widget/desktopwidget_connector` and
`command/system/macrocommand`.

## Ledger rows

These rows of the unimplemented ledger now have a registration, argument list,
return list and callback contract: `_createWidgetInWidgetContainer`,
`_deleteCreatingWidgetInWidgetContainer`, `_getUserMacroData`, `_getUserMacroIcon`,
`_getUserMacroTitle`, `_getWidgetFromWidgetContainer`,
`_isCreatingWidgetInWidgetContainer`, `_isExistWidgetInWidgetContainer`,
`_parseTextCommand`, `_saveUserMacro`, `_sendCountDown`,
`_setTargetCharacterByDisplayName`, `_setUserMacroData`, `_setUserMacroIcon`,
`_setUserMacroTitle` and `_waitForItemSearchWidget`. A client that implements them
needs the macro bank behind `V +0x998` and a writer for the `mcr%d` file, the actor
container behind `V +0x4E4` with the display name records and the SetTarget
request, the parser core `0x0056E380`, the record `0x00CF` and the connection
object behind `V +0x174EC`, the container manager behind `Y +0x114` and the widget
manager behind `V +0x4DC` with the item search form.

## Open

- The file location, byte order and reader of the macro file, the writer of
  `B +0x0E` and the effect of a macro, group or line number outside the ranges.
- The meaning of the bytes at control `+0x5C` and record `+0x59` and the case of a
  null record pointer in the display name matcher.
- The grammar of the text commands, the command word values, the limits of the
  parser core and the stores that fill its output vector.
- The unit of the 64-bit sum of the `0x00CF` record, the meaning of the byte
  argument, the role of the dword `0x40` and server behavior.
- The writer that clears `M +0xC8` and the effect of `0x004FFCF0`.
- How a pending container record becomes a widget, where the byte at record
  `+0x68` comes from, and the effect of `0x00CC76F0` and `0x006DBE20`.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes with the route of the
[binding map contracts](binding-map-native-contract.md#reproduction). The script
call shapes come from the `.le.lpb` files of an installed client, decoded by
[`tools/decode_lpb.py`](../tools/decode_lpb.py) and read with a Lua 5.1 bytecode
parser over the `SELF` and `TAILCALL` call sites. They are `INFERRED` because no
tracked artifact carries them. The function VAs for `$Addresses` are:

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Registrars | `0x007399C0,0x0073FB00,0x00751B80,0x0073A2F0,0x00751CD0,0x007418E0,0x00751E20,0x0073A440,0x00751F70,0x0073A590,0x00756F60,0x00752360,0x007524B0,0x00752600,0x0073AAD0,0x0073AC20` |
| Switchboard and holder | `0x00757EA0,0x00726BF0` |
| Callbacks | `0x006E7D70,0x006E7FE0,0x006FDF70,0x006E5640,0x006FE090,0x006E80B0,0x006FE140,0x006E1B70,0x006FE2A0,0x006E1B90,0x007094B0,0x006FE550,0x006FE5C0,0x006FE630,0x006E5880,0x006E81D0` |
| Macro bank | `0x0075CBB0,0x0075CBE0,0x0075CC10,0x0075CC40,0x0075CC60,0x0075CCA0,0x0075CCD0,0x004B54A0,0x004B54C0,0x004D7540,0x004C7A80,0x00447450` |
| Display name target | `0x00713AE0,0x00718F40,0x00764150,0x00445D20,0x0075B6C0,0x004D9970,0x004DE190,0x00562D30` |
| Text command and countdown | `0x0075CCF0,0x0056E380,0x00745380,0x0072C4C0,0x0072BD30,0x00727F00,0x0075D460,0x0075ED30,0x004D7460,0x004D6D10` |
| Item search wait | `0x0075BB30,0x0075BB50,0x0066ED80,0x0066DD00,0x0066E9D0,0x0052A540,0x00713D50,0x00713E20,0x004D7380` |
| Widget container | `0x00775DD0,0x0075F460,0x0075F4B0,0x0075F4F0,0x00765150,0x0078B750,0x00753B90,0x00748B30,0x00CC7A50` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
