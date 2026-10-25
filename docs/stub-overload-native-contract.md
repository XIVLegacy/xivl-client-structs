# Group property, cut scene file name, loop interval, list and super call native contracts

[`manifests/stub_overload_native_call_contract.json`](../manifests/stub_overload_native_call_contract.json)
records the static Lua call contracts of the overloads and natives that a host had to stub after the
[widget](widget-native-call-contract.md) and [desktop](desktop-native-call-contract.md) records gave only their
declared lists. It covers the `GroupBase` overload of `_getProperty`, the `CutScene` overload of `_setFilename`, the
`ActorBase` native `_setLoopInterval`, the `WidgetBase` natives `_setListProperty` and `_updateList` with the Sqwt
control that they drive, the argument and result handling of `_callSuperClassFunction` and the test of the
cursor-one branch of `_setTargetCursorImage`. Each row gives the
registration site, the declared lists, the Lua pushes of every branch, the client state that the callback reads
or writes, failure behavior and whether the call yields. The contracts describe client marshalling and state.
They do not describe group sheet content, cut scene content, list content, widget layout or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data at the cited addresses. `MEASURED`
is counted from the call-site index or from the decoded installed client scripts by the method named in the fact.
`INFERRED` is a role taken from the surrounding instructions or scripts that the bytes do not state. `unknown`
was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image base `0x00400000`, `15996808` bytes,
SHA-256 `9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned by
[`manifests/retail_inputs.json`](../manifests/retail_inputs.json). The registrar shape, the type registry, the cell
tags and the argument marshaller are the ones of the [widget contracts](widget-native-call-contract.md#registration).
The invalid-parameter route `0x009D22B4` is the one of the [target cursor record](target-cursor-native-contract.md#selection-and-the-failure-path).
The group data pointer at the receiver `+0x68` is the one of the [group natives](binding-map-native-contract.md#group-natives).
The property write route of the list natives is the one of the
[visibility property path](native-input-ui-boundaries.md#visibility-property-path) and the
[widget item consumer](widget-item-consumer-contract.md#indexed-context-and-property-receiver).

A script decoded each registrar, callback, jump table, vftable cell, static initializer and string literal from the
executable bytes and asserted the addresses. Callers, stores and loads come from a linear decode of the `.text`
section, so virtual and indirect references are not covered. The `MEASURED` script facts come from
`xivl-client-scripts:lua/napi_index.json` and from the Lua 5.1 bytecode of the installed client scripts, decoded
with [`tools/decode_lpb.py`](../tools/decode_lpb.py). A count reads each `CALL` that follows a `SELF` or a table
read of the name for its argument and result counts. The chunks and the scan are not tracked.

## Summary

| Native | Class | Arguments | Returns | Callback | Forwards to |
| --- | --- | --- | --- | --- | --- |
| `_getProperty` | `GroupBase` | `int` | `Which<Utf8String,int,bool>` | `0x00700450` | `0x006C2140` |
| `_setFilename` | `CutScene` | `Utf8String` | none | `0x006E7A60` | `0x00447450` |
| `_setLoopInterval` | `ActorBase` | `float` x5 | none | `0x006DBD90` | `0x0078C020` |
| `_setListProperty` | `WidgetBase` | `Utf8String`, `int`, `Utf8String`, `Which<Utf8String,int,bool>` | none | `0x006F3E70` | `0x0072B210` |
| `_updateList` | `WidgetBase` | `Utf8String` | none | `0x006EBE60` | `0x006EB450` |
| `_callSuperClassFunction` | `ActorBase` | `Utf8String`, `Variable` | `Variable` | `0x006DBC40` | `0x0078D520` |

None of these natives yields. `_callSuperClassFunc` is the Lua name of the last row through its `_inl` descriptor.

## GroupBase _getProperty

The registrar `0x0074D940` pushes the name literal `0x00FD76B4` at `0x0074DA29`, the same literal as the `WidgetBase`
overload. Its only caller is `0x00757C9D`, the 14th registrar call of the `GroupBase` switchboard `0x00757B70`.

The callback reads one int selector and pushes one value from the record of the receiver's group kind. The key is the
dword at group data `+0x04`. `0x006BFD20` returns it and `0x006C2140` searches the ordered map at `([[M]+4])+8`, where
`M` is the dword at `Y +0xE4` of the world object that `0x00CC7510` reaches from `ExecuteParameters +0x04`. A key
that is not in the map reaches the invalid parameter route. Only if that route returns, which depends on a run-time
handler that is `unknown` in the target cursor record, does the routine return the address at the end node `+0x10`.

| Selector | Push | Record field |
| --- | --- | --- |
| 0 | int | dword `+0x00` |
| 6, 7 | int | byte `+0x24`, `+0x25` |
| `0x10` through `0x13` | int | dword `+0x04`, `+0x08`, `+0x0C`, `+0x10` |
| 1 | bool | byte `+0x26` |
| `0x14` through `0x17` | bool | byte `+0x27` through `+0x2A` |
| 3 | `Utf8String` | text after the last `/` of the string at `+0x2C` |
| any other, negative included | nothing | none |

The selector is compared unsigned with `0x17` and then maps through the byte table `0x0070065C` and the dword table
`0x00700624`. The native reads and writes no other state.

### Group kind record

The loader `0x006C9CF0` fills the map from the sheet named `_group` (literal `0x00FD4018`). It walks the key ranges of
the sheet and, for every key above a high water mark, reads one row into a `0x80` byte record and inserts it. After
the last range it releases the sheet, so the table loads once. A missing row ends the load early. The selector equals
the sheet column for every column the callback exposes. Column 3 is stored as the literal `/Group/` followed by the
column text, and selector 3 returns the text after the last `/`. The word columns `0x18` through `0x1B` fill a word
vector at record `+0x18` that this native does not read. The tracked
`xivl-client-data:docs/corpus-inventory.md` counts 38 rows for the decoded `_group` table. No row value is promoted
here.

Five script sites call the native, all in `group/communitygroup/companygroup` (lines 104, 119 and 210) and
`group/communitygroup/retainergroup` (lines 19 and 33). All pass selector 0. The value is the length of the
`_memberSave` array in the sync declaration of the group work, the loop bound over the members and the array length
argument of `_bindWorkNestingArray`. It is read as the member capacity of the group kind (`INFERRED`). The site at
`companygroup` line 210 is the last argument of a call and forwards every result.

## CutScene _setFilename

The registrar `0x00735EB0` is the first registrar call of the `CutScene` switchboard `0x007547D0`. The callback reads
cell 0 as a `Utf8String` and assigns it to the string object at receiver `+0x6C` through `0x00447450`. It resolves
no control identity, calls no manager and starts no load. The `WidgetBase` overload resolves the control through
`0x004D9910` and the `SpreadSheet` overload calls a manager virtual slot, so this overload is the plain store.

`_play` (`0x006FB830`) is the consumer. It passes the address of `+0x6C` to `0x0076D610` on the cut scene manager, the
dword at `Y +0x08`. The routine zeroes a `0x20` byte field, copies the lesser of the name length and `0x1F` bytes
into it and posts a message with code `0xCE` and size `0x38` through `0x004D6D10`. `_replay` calls the sibling
`0x0076D820` with no file name and does not read the field. The message is the serverbound `0x00CE` record, and the
[cut scene contracts](cutscene-native-contract.md#serverbound-record) give its fields.

One script site calls the overload: `CutScene._onInit` in `gamedata/cutscene` line 35 passes its first parameter,
the payload value that `_createActor` hands to `_onInit` (see [_createActor](create-actor-native-contract.md)).

## ActorBase _setLoopInterval

The [widget record](widget-native-call-contract.md#loop-interval) gives the conversion. This record adds the store.
The thunk `0x006DBD90` calls `0x0078C020` with the receiver. An argument 0 of Nil appends the one word `0x7FFF`, which
is the file image value of the static at `0x0130CF00`, and stops. Otherwise the routine appends one word for each
leading non-Nil float, up to five, and stops at the first Nil. Each word is the low 16 bits of
`trunc(trunc(f * 10000.0 + 0.5) / 10)` with both truncations toward zero, which is `f` seconds in milliseconds for
values that fit.

`0x00CC7400` resolves the control record through `0x00CD7A30`, the record at control `+0x04` or the root record at
manager `+0x1BC`, and `0x00CE2E40` appends the word to the vector at record `+0x20`. It reserves 8 words when the
vector has no capacity. Nothing in this native clears the vector, so repeated calls accumulate. The engine bootstrap
function `__lge_setLoopInterval` (`0x00D083B0`) appends integer words to the same vector without the seconds
conversion.

Seven script sites call the native and none uses a result. The constants are 1 in `AreaBaseClass`,
`InstanceRaidBaseClass`, `DesktopWidget` and `CommandDebuggerDEV`, 10 in `MapObjFireworks` and 0.1 in
`WidgetBaseClass`. `DebugBaseClass.setLoopInterval` forwards its varargs. Six of the seven scripts define `_onLoop`.
That the vector holds the intervals at which `_onLoop` runs is `INFERRED`, and the reader of the vector is open.

## Lists

`_setListProperty` and `_updateList` write properties of a named Sqwt control through the route of the widget
property natives. The control is a `Sqwt::Data::SqwtXmlDataMaker`. The list is an XML document held by the control:
a row is a child element, and a column is an attribute of that element.

### SqwtXmlDataMaker

The constructor `0x009442B0` registers one property changed callback, `0x00943A00`, for eleven properties. The table
gives the property index, the value offset in the control and the default.

| Index | Property | Offset | Type | Default |
| ---: | --- | --- | --- | --- |
| 0 | `SortedIndex` | `+0xC4` | int | -1 |
| 1 | `Index` | `+0xCC` | int | -1 |
| 2 | `IntValue` | `+0xD4` | int | 0 |
| 3 | `Count` | `+0xDC` | int | 0 |
| 4 | `AttributeName` | `+0xE4` | string | empty |
| 5 | `ValueType` | `+0xEC` | string | empty |
| 6 | `StringValue` | `+0xF4` | string | empty |
| 7 | `Action` | `+0xFC` | string | empty |
| 8 | `FilteredSortKey` | `+0x104` | string | empty |
| 9 | `FilteredCount` | `+0x10C` | int | 0 |
| 10 | `FilteredIndex` | `+0x114` | int | -1 |

That the control the natives reach by name is this class follows from the exact match of the six property names the
natives write with its declared properties (`INFERRED`). The form markup that declares the names was not read.

The callback does work for six properties. Writing `Index` resolves the row and creates the rows up to it when the
index is at or above the row count. It stores the row element at `+0x200` and refreshes the read back, `Count` and the
sorted and filtered positions. A negative index, or a control with no document, stores no row and writes `Index` and
`SortedIndex` as -1. Writing `AttributeName` reads the attribute of the current row into `StringValue` and its integer
parse into `IntValue`, or the empty text and 0 when the attribute is absent. This is the read side of the list.
Writing `Action` runs one handler from the table below and then resets `Action` to the empty text, so writing the same
action twice runs it twice. `SortedIndex`, `FilteredIndex` and `FilteredSortKey` keep the sorted and filtered views
and `Index` in step. The other five properties only store.

| Action | Needs | Effect |
| --- | --- | --- |
| `SetAttr` | current row | Stores the attribute named by `AttributeName`. `ValueType` `Int` stores the `%d` text of `IntValue` and `String` stores `StringValue`. Any other `ValueType` stores nothing. |
| `Update` | none | Recounts the rows, rebuilds the filtered view and sets `SortedIndex` to -1. |
| `Filter` | none | Rebuilds the filtered view. |
| `InsertIndex` | current row | Inserts a new row element. |
| `RemoveIndex` | current row | Removes the row and refreshes `Count`. |
| `SetText`, `RemoveAttr` | current row | Sets the element text, or removes the attribute. |
| `RemoveRange(a-b)`, `Clear` | document | `Clear` writes `RemoveRange(0-)`. The range removes rows `a` through `b`. |

The filtered view is the full list while `FilteredSortKey` is empty. With a sort key it keeps the rows whose `visibility`
attribute is empty or not `False`, orders them by the key and sets `FilteredIndex` and `FilteredCount`.

### _setListProperty

The registrar `0x00744460` is the 17th registrar call of the `WidgetBase` switchboard `0x00754A60`. The callback
copies the engine context, the cell holder and the control identity into a local record and calls `0x0072B210` on
the cell at index 3, which carries the value. That routine branches on the value tag.

| Value tag | Branch | Property writes in order |
| --- | --- | --- |
| 0, int | `0x006EA360` | `Index`, `AttributeName`, `ValueType` = `Int`, `IntValue`, `Action` = `SetAttr` |
| 2, bool | `0x006EA6D0` | `Index`, `AttributeName`, `ValueType` = `String`, `StringValue` = `True` or `False`, `Action` = `SetAttr` |
| 3, `Utf8String` | `0x006EAA20` | `Index`, `AttributeName`, `ValueType` = `String`, `StringValue`, `Action` = `SetAttr` |
| 1, float, and any other | none | no write |

Argument 0 is the list name, argument 1 the row index and argument 2 the attribute name. Each write goes through
`0x0075BB80`, `0x005355A0` and `0x005354D0` with the empty context, which selects the default index at engine `+0x98`.
The pickup formats an int as `%d`, so `Index` and `IntValue` reach the control as text that the property engine
parses. A list name that no control answers to ends the write without an error.

The call sites are 62 direct sites in `widget/retaineritemlistwidget` (58), `widget/aetherytelistwidget` (3) and the
`widget/widgetbaseclass_common` wrapper `setListProperty` (1). The wrapper itself has 853 call sites in 46 scripts, so
most lists reach the native through it. `AetheryteListWidget.addListItem` writes `AetheryteID` and `Cost` as numbers
and `CostVisibility` as the bool false to the list `ListBox`, which uses the bool branch.
`AetheryteListWidget.createRegionList` writes rows 0 through 4 of `RegionList` through the wrapper with the attribute
`RegionID` and no row insertion, then calls `_updateList`. The row growth of the `Index` write is what makes that work.

How a Lua number with a fractional part reaches the int branch is open.

### _updateList

The registrar `0x00738F40` is the 22nd registrar call of the same switchboard. The callback forwards to `0x006EB450`,
which writes the one property `Action` of the named control with the text `Update` through `0x0075B810`. The handler
recounts the rows with `0x00944760`, rebuilds the filtered view with `0x00943580` and resets the sorted position. The
changes of `Count` and `FilteredCount` are the only redraw signal found. That a bound list box redraws from them is
`INFERRED` and the binding was not traced. The call sites are 13 direct ones in the same scripts and the wrapper
`updateListProperty` has 202 sites in 42 scripts.

### Sibling list natives

The same property route serves four siblings. They are not contracted further here.

| Native | Registrar | Callback | Writes |
| --- | --- | --- | --- |
| `_addList` | `0x00738B50` | `0x006EBE00` | `Index`, `Action` = `InsertIndex` |
| `_removeList` | `0x00738CA0` | `0x006EBE20` | `Index`, `Action` = `RemoveIndex` |
| `_clearAllList` | `0x00738DF0` | `0x006EBE40` | `Action` = `RemoveRange(0-)` |
| `_getListProperty` | `0x007436A0` | `0x006EBDF0` | `Index`, `AttributeName`, `ValueType`, then reads the attribute back |

## _callSuperClassFunction

The registrar `0x0072DF60` is the first registrar call of the `ActorBase` switchboard `0x00753C30`. The thunk
`0x006DBC40` calls `0x0078D520`. That routine reads the method name from cell 0, copies the cells from index 1 to the
end of the cell vector through `0x00753B90`, converts them through `0x00791030` and calls `0x00CD25F0` on the thread
context. It then pushes each result cell by its tag, so the native returns every value the super method returns.
The class selection is the call frame rule of the [door initialization record](door-initialization-native-contract.md#superclass-dispatch).

The widget record left an arity conflict open. The declared list holds one `Variable` after the name, and the door
record reads the call as preserving two trailing values. Under the inferred successful-reader contract (`INFERRED`) the `Variable` reader has no fixed limit. It consumes every
present trailing value of a recognized kind, so the declared list length does not bound the trailing values, and the
copy at index 1 passes all of them on. The recognized kinds are nil, boolean, number, string and a table that resolves
to a control (`INFERRED` from the raw tags). A value of another kind ends the scan and the call raises the
`GetArguments_` diagnostic. With no trailing value the marshaller supplies one `Nil` cell, and whether the super method
receives it as an explicit nil is open.

The installed scripts hold 84 call sites. 44 pass the method name only, 11 pass one trailing value, 19 pass two, 2 pass
three, 2 pass four and 6 forward varargs. None uses a result.

## DesktopWidget _setTargetCursorImage cursor-one branch

The [target cursor record](target-cursor-native-contract.md#image-native) leaves the test of the cursor-one branch
open. The callback is `0x006E5030`. After the image store it continues only for the zero-based index 0 with the byte at
`DesktopWidget +0x7C` clear. It builds the widget identity with `0x00CC73B0` and calls `0x00CC7BE0` with the identity,
the immediate `0x0007A124` and -1 at `0x006E511E`. The widget identity feeds only this test. The two `DesktopWidget`
methods `0x006FE960` and `0x006FEBB0` store `+0x7C` and make the same call at `0x006FEB1F` and `0x006FED56`.

The immediate is the work key 500004. `widget/desktopwidget_connector` binds that key as the work member
`mainTargetDecidedFlag` of the desktop widget, next to `tutorialMenuType`, `tutorialFlag` and `tutorialLockFlag`
(`MEASURED`). `0x00CC7BE0` returns false without a control record that is ready, and otherwise asks the work operator
of the manager for the member through `0x00CE53D0`. The routine finds the key entry with `0x00CE5040`, adds the index
only for an array member and reads the member through `0x00D11C00`. That the returned byte is the boolean value of
the member is `INFERRED`, so the branch tracks whether the main target is decided.

After the test the branch reads the identity of cursor 0. A true result with `+0x70` equal to the dword at `0x0130C778`
posts the `0xCD` message with that identity as both values and stores it at `+0x70`. A false result with `+0x70`
different from that dword posts the message with that identity and the dword, which holds `0xE0000000`, and stores the
dword at `+0x70`. The message reaches the outbound packet body through `0x004D6D10`, `0x004E0240` and `0x00DAE010`. The
two methods that store `+0x7C` are reached from `LuaActorImpl` vftable slots 25 and 26, fire `_onTargetChanged` and
`_onTargetDecided`, and hold `+0x7C` at 1 while the script callback runs. The
[target cursor record](target-cursor-native-contract.md#the-posted-message) holds the evidence. The virtual callers of
the two slots are still open.

## Host obligations

- `GroupBase _getProperty`: hold the `_group` rows by group kind, push the value of the selector's column with the
  type of the table above and push nothing for any other selector.
- `CutScene _setFilename`: store the name on the cut scene and return. Use it in `_play`, not `_replay`.
- `_setLoopInterval`: append the converted words, `0x7FFF` for a leading Nil, and do not clear the list in this native.
- `_setListProperty` and `_updateList`: keep a named row and attribute model per widget that follows the property
  order above, grows rows on `Index`, stores attributes on `SetAttr` and recounts on `Update`.
- `_setTargetCursorImage` cursor-one branch: read the work member `mainTargetDecidedFlag` as the test
  (`INFERRED`). Cache and post the identity of cursor 0, not the widget identity.
- `_callSuperClassFunction`: pass every trailing value, raise the argument diagnostic at the first value of another
  kind and push every result.

The manifest `hostContract` lists the obligations in full.

## Open

- The `_group` row values for the `CompanyGroup` and `RetainerGroup` kinds, and the reader of the word columns.
- The server side resolution of the cut scene path that the serverbound `0x00CE` record carries.
- The reader of the loop interval vector and the `_onLoop` firer.
- The values of the attribute type bytes at `0x013599D1` and `0x013599DC`.
- The data maker names that the widget forms declare and the bindings that read `Count`, `FilteredCount` and
  `FilteredIndex`.
- The virtual callers of `LuaActorImpl` vftable slots 25 and 26, which reach the methods that write `+0x7C`.
- The numeric reading of the `Which` value and the delivery of the `Nil` placeholder to the super method.

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
| Registrars | `0x0074D940,0x00735EB0,0x00742760,0x00744460,0x00738F40,0x0072DF60` |
| Group property | `0x00700450,0x006BFD20,0x006C2140,0x006BF830,0x006C9CF0,0x006CDF20` |
| Cut scene | `0x006FB830,0x006F11B0,0x0076D610,0x0076D820` |
| Loop interval | `0x0078C020,0x00CC7400,0x00CD7A30,0x00CE2E40,0x00D083B0` |
| List natives | `0x006F3E70,0x0072B210,0x006EA360,0x006EA6D0,0x006EAA20,0x006EB450,0x0075BB60,0x0075BB80,0x005355A0,0x005354D0` |
| Data maker | `0x009442B0,0x00943A00,0x00943980,0x00943580,0x00944850,0x00942FC0,0x009425B0,0x00944DA0,0x00944ED0` |
| Super call | `0x006DBC40,0x0078D520,0x00753B90,0x00791030,0x007941D0` |

The callbacks `0x006E7A60` and `0x006EBE60` are not function entries in the analyzed program. Read them as
instruction listings from those addresses. The property changed callback `0x00943A00` is analyzed only for its first
`0x71` bytes, so read the range through `0x00944000` as an instruction listing. The list builders named in the
manifest are short and are read the same way. No decompiled body or ignored export is a tracked evidence
dependency.
