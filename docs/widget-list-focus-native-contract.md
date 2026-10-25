# Widget list and keyboard focus native contracts

[`manifests/widget_list_focus_native_call_contract.json`](../manifests/widget_list_focus_native_call_contract.json)
records the static Lua call contracts of six `WidgetBase` natives. Four drive the list model of the Sqwt data control that
the [stub overload record](stub-overload-native-contract.md#lists) describes. They are `_addList`, `_removeList`,
`_clearAllList` and `_getListProperty`. Two read the keyboard focus. They are `_isKeyboardFocused` and
`_getKeyboardFocusedControl`. Each row gives the registration site, the declared lists, the property writes or reads, the
Lua pushes of every branch, failure behavior and whether the call yields. The contracts describe client marshalling and
state. They do not describe form markup, list content or focus handling beyond the compared pointers.

Each fact carries a tier. `STATIC` is read directly from instructions or data at the cited addresses. `MEASURED` is counted
from the call-site index of the installed client scripts. `INFERRED` is a role taken from the surrounding instructions or
scripts that the bytes do not state. `unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned by
[`manifests/retail_inputs.json`](../manifests/retail_inputs.json). The method, the registrar shape, the cell readers and the
return pushers are the ones of the [trophy and group record](trophy-group-native-contract.md#binary-and-method). The
property write route is the one of the [visibility property path](native-input-ui-boundaries.md#visibility-property-path)
and the [stub overload record](stub-overload-native-contract.md#lists). The container and control resolution of the focus
natives is the one of `_setKeyboardFocusedControl` in the [talk record](talk-native-contract.md#keyboard-focus).

## Ranking

The ranking uses the basis of the [trophy and group record](trophy-group-native-contract.md#ranking) at the ledger revision
`f6e50df28ebcfe7f542a05c23756dac08e26b20b`. The rank is the rank among the 28 natives of the two records.

| Rank | Native | Class | Scripts | Call sites | Index sites | Order |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `_removeList` | `WidgetBase` | 2 | 6 | 6 | 20 |
| 2 | `_isKeyboardFocused` | `WidgetBase` | 3 | 3 | 3 | 9 |
| 3 | `_getKeyboardFocusedControl` | `WidgetBase` | 2 | 2 | 3 | 10 |
| 4 | `_clearAllList` | `WidgetBase` | 2 | 2 | 2 | 21 |
| 25 | `_getListProperty` | `WidgetBase` | 1 | 1 | 1 | 18 |
| 26 | `_addList` | `WidgetBase` | 1 | 1 | 1 | 19 |

## Registration

Every native is declared by a `_u` script descriptor named `<name>_inl` in `widget/widgetbaseclass_u` whose key is
`<name>_cpp`. The script contains both strings (`MEASURED`). The order of a native is its position among the rel32 calls of
the `WidgetBase` switchboard `0x00754A60`, stored at slot 2 of the vftable `0x00FD5A74`. Each registrar has one rel32 caller
and each name literal has one referencing instruction. All six wrappers construct the const `WidgetBase` holder `0x00726A90`
with the vftable `0x00FD5B64` and the target type descriptor `0x012C1964`.

| Native | Order | Registrar | Caller | Callback | Wrapper | Forwards to |
| --- | --- | --- | --- | --- | --- | --- |
| `_addList` | 19 | `0x00738B50` | `0x00754BF6` | `0x006EBE00` | `0x00726A90` | `0x006EB070` |
| `_removeList` | 20 | `0x00738CA0` | `0x00754C0B` | `0x006EBE20` | `0x00726A90` | `0x006EB1F0` |
| `_clearAllList` | 21 | `0x00738DF0` | `0x00754C20` | `0x006EBE40` | `0x00726A90` | `0x006EB370` |
| `_getListProperty` | 18 | `0x007436A0` | `0x00754BE1` | `0x006EBDF0` | `0x00726A90` | `0x006EADA0` |
| `_isKeyboardFocused` | 9 | `0x00738610` | `0x00754B24` | `0x006DED60` | `0x00726A90` | slot `0x88` |
| `_getKeyboardFocusedControl` | 10 | `0x00738760` | `0x00754B39` | `0x006DED70` | `0x00726A90` | slot `0x8C` |

The four list callbacks are plain functions that pass the engine handle, the argument object and the address of the receiver
identity at `ExecuteParameters +0x0C` to the forwarder. They never read the receiver object. The two focus callbacks are
thunks through the receiver vftable. The `WidgetBase` cells are `0x00FD5AFC` and `0x00FD5B00` and hold `0x00707770` and
`0x006E3890`. The `DesktopWidget` cells `0x00FD5C14` and `0x00FD5C18` hold `0x006DCAD0` and `0x006DCAE0`, both bare `ret 4`
routines, so a `DesktopWidget` receiver pushes nothing.

## Contracts

| Native | Arguments | Returns | Yields |
| --- | --- | --- | --- |
| `_addList` | `Utf8String`, `int` | none | no |
| `_removeList` | `Utf8String`, `int` | none | no |
| `_clearAllList` | `Utf8String` | none | no |
| `_getListProperty` | `Utf8String`, `int`, `Utf8String` | `Which of Utf8String, int and bool` | no |
| `_isKeyboardFocused` | `Utf8String`, `Utf8String` | `bool` | no |
| `_getKeyboardFocusedControl` | none | `Utf8String`, `Utf8String` | no |

No callback requests a yield. Every cell read follows a size test that calls `0x009D22B4` on failure. An int reader that
finds a mismatched tag and a `Utf8String` reader that finds a mismatched tag reach `0x00CCA730`.

## List natives

The control is a Sqwt data control with the properties `Index`, `AttributeName`, `ValueType`, `StringValue` and `Action`
(see the [stub overload record](stub-overload-native-contract.md#sqwtxmldatamaker)). Each list native resolves the widget
handle of the receiver identity through `0x0075BB60` and writes properties of the control named by argument 0 through
`0x0075BB80`, which jumps to `0x005355A0`. A list name that no control answers to ends the write without an error.

| Native | Property writes in order | Action text |
| --- | --- | --- |
| `_addList` | `Index` = row index, `Action` | `InsertIndex`, the static text at `0x0134B948` |
| `_removeList` | `Index` = row index, `Action` | `RemoveIndex`, the static text at `0x0134B9A0` |
| `_clearAllList` | `Action` | `RemoveRange(0-)`, the static text at `0x0134B9F8` |

The row index is an int property value built by `0x00716950`. The property names are the literals `Index` at `0x00FD4D10`
and `Action` at `0x00FD4D60`. `_clearAllList` calls `0x0075B810`, which resolves the widget and jumps into the same
routine. The names of the three action texts come from the [stub overload record](stub-overload-native-contract.md#lists),
which reads the static initializers of the text objects. None of the three natives pushes a value. The scripts reach them
through wrappers in `widget/widgetbaseclass_common`, at the lines 3130, 3142 and 3154. `widget/retaineritemlistwidget`
calls `_removeList` at five lines and `widget/aetherytelistwidget` calls `_clearAllList` at line 344.

### _getListProperty

`_getListProperty` (`0x006EADA0`) reads the list name, the row index and the attribute name. It writes `Index`, then
`AttributeName` from the literal at `0x00FD4D1C` and then `ValueType` from the literal at `0x00FD4D30` with the static text
at `0x0134B898`. It builds a processor object of the class `s_GetListPropertyProcessor` with the vftable `0x00FD56F4` over
the result list and reads the property `StringValue` (the literal at `0x00FD4D50`) through `0x0075BB90`. Only the string
handler of the processor, slot 3 at `0x00749400`, pushes a value. The other handlers are bare returns.

| Attribute text | Push |
| --- | --- |
| empty | `int` 0 |
| `True` | `bool` true |
| `False` | `bool` false |
| accepted by the test `0x004553A0` | `int`, the base 10 parse of `0x004555A0` |
| anything else | `Utf8String`, the text |

The conversion matches the text forms that `_setListProperty` writes in the stub overload record. A bool is written as
`True` or `False`, an int as a `%d` text and a string as itself. The result for a control that does not answer was not
traced. The only script site is the tail call in `widget/widgetbaseclass_common` at line 3117.

## Keyboard focus natives

`_isKeyboardFocused` (`0x00707770` on the `WidgetBase`) reads the control name from cell 1 and tests the tag byte of
cell 0. A Nil cell calls `0x0075B950` with the identity and the control name. Any other cell is read as the container name
and calls `0x0075B970` with the identity, the container name and the control name. Both resolve the widget through
`0x004D9910` and reach `0x00538630`. That routine takes the container index from the dword at widget `+0x98` for the empty
container name, or from the map at widget `+0xEC` through `0x005353E0`, resolves the control through `0x00537950` and
casts it from `DependencyObject` to `FrameworkElement`. It compares the address of element `+0xB4` with the dword at
`0x01356FCC` and pushes the result. A name that resolves to no element compares 0 with the same dword, so the answer is
true while nothing holds the focus.

`_getKeyboardFocusedControl` (`0x006E3890`) takes no argument. It builds a result sink with the vftable `0x00FD5784` over
the result list and calls `0x0075B9A0`, which resolves the widget and calls `0x00535A90`. The routine loads the dword at
`0x01356FCC`.

| Case | Sink slot | Pushes |
| --- | --- | --- |
| The dword is null, or the container index of the focused element is not above 0 and differs from the dword at widget `+0x98` | 1, `0x00749710` | nil, nil |
| The container index equals the dword at widget `+0x98` | 2, `0x00749740` | nil, the element name |
| The container index is above 0 and differs | 3, `0x00749770` | the container name, the element name |

The focused element is the dword at holder `+0x64`, cast to the framework type. The element name comes from the element
vftable slot 2. In the third case the routine pushes the element name, then pushes the container name that `0x00535450` returns for the
container index, and calls the slot, so the container name is the first value and the element name the second. This is the
argument order of `_isKeyboardFocused`. `0x00535450` looks the index up in the map at widget `+0xEC` and returns the node
key, or the empty string at `0x01266B10`. The two non-debug script sites take two
results. They are `widget/journallistwidget` line 284 and the wrapper in `widget/widgetbaseclass_common` line 2949. The
third site is in `commanddebugger/commanddebuggerdev`. The wrapper at `widget/widgetbaseclass_common` line 2937 tail calls
`_isKeyboardFocused`, and `widget/guildleveareaorderwidget` line 268 and `widget/guildlevecardorderwidget` line 492 call it
with two arguments and one result.

## Script call sites

| Native | Index sites | Scripts | Direct calls | Argument counts |
| --- | --- | --- | --- | --- |
| `_addList` | 1 | 1 | 1 | 2: 1 |
| `_removeList` | 6 | 2 | 6 | 2: 6 |
| `_clearAllList` | 2 | 2 | 2 | 1: 2 |
| `_getListProperty` | 1 | 1 | 1 | 3: 1 |
| `_isKeyboardFocused` | 3 | 3 | 3 | 2: 3 |
| `_getKeyboardFocusedControl` | 3 | 3 | 2 | 0: 2 |

The counts agree with `xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. The direct call and argument columns
are `INFERRED` from the local bytecode scan.

## Host obligations

- `_addList`, `_removeList` and `_clearAllList` edit the row set of the named list control and push nothing.
- `_getListProperty` pushes the attribute text of a row converted by the table above.
- `_isKeyboardFocused` pushes true for the control that holds the focus and for an unresolved name while nothing holds it.
- `_getKeyboardFocusedControl` pushes nil and nil without a focus, nil and the element name in the container of the
  receiver, and the container name followed by the element name for another container.

## Ledger rows

These rows of the unimplemented ledger now have a registration, argument list, return list, receiver check and callback
contract: `_addList`, `_removeList`, `_clearAllList`, `_getListProperty`, `_isKeyboardFocused` and
`_getKeyboardFocusedControl`. A host that implements the list rows still needs the control names that the form markup
declares.

## Open

- The list controls and attribute names that the forms declare.
- The writer and the class of the focus dword at `0x01356FCC`.

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
| Registrars | `0x00738B50,0x00738CA0,0x00738DF0,0x007436A0,0x00738610,0x00738760` |
| List natives | `0x006EBE00,0x006EBE20,0x006EBE40,0x006EBDF0,0x006EB070,0x006EB1F0,0x006EB370,0x006EADA0` |
| Property route | `0x0075BB60,0x0075BB80,0x0075BB90,0x0075B810,0x00716950,0x00716DA0,0x00538500` |
| Result conversion | `0x00749400,0x004553A0,0x004555A0,0x00445D60` |
| Focus | `0x00707770,0x006E3890,0x0075B950,0x0075B970,0x0075B9A0,0x00538630,0x005386B0,0x00535A90,0x00717460,0x00749710,0x00749740,0x00749770` |

No decompiled body or ignored export is a tracked evidence dependency.
