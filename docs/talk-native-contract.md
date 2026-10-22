# Talk widget native contracts

[`manifests/talk_native_call_contract.json`](../manifests/talk_native_call_contract.json)
records the static Lua call contracts of seven natives reached by `AskWidget`,
`CommonAskWidget`, the widget base scripts and the `DesktopWidget` message
path. They are the parent and child widget accessors, the keyboard focus
request, the keyboard-only tutorial test and the two desktop message pool
appenders. Each row gives the registration site, the receiver type check, the
declared argument and return lists, the reads, the effects on client state, the
failure behavior and whether the call yields. The contracts describe client marshalling and state,
not message text, widget layout or server behavior.

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

The native set comes from the script metadata. The per-row `corpusCallSites`
lists in the manifest name the scripts that contain each call. `NpcSayWidget` lists only
`_defineClass` in `xivl-client-scripts:lua/scripts/widget/npcsaywidget.calls.json`.
`AskWidget` and `CommonAskWidget` list `_setKeyboardFocusedControl`, and
`CommonAskWidget` lists `_getParentWidget`. `DesktopWidget` wraps
`_appendMessagePool` and `_appendLogPool`. The manifest rows carry the
call-site lines from `xivl-client-scripts:lua/napi_index.json`. They show that
a script contains a call, not that a widget instance reaches it. No call from
`NpcSayWidget` to these seven natives is recorded.

Registration, the StackOperator type registry and argument marshalling follow
the [widget contract framework](widget-native-call-contract.md#registration).
The holder receiver adapter follows the
[WorldMaster contract](world-master-native-call-contract.md).

## Registration and dispatch

Every registrar in the manifest builds the return list first and the argument
list second. It zeroes EDI, loads the callback into ESI, pushes the lists, EDI,
ESI and a stack value, calls a per-class wrapper and installs the functor
through `0x00CCCAD0` under the name literal. The wrapper stores the argument
list at functor `+0x14` and the return list at `+0x24`. The adjustment is 0 in
every row. Each registrar has one direct caller in `.text`, recorded in the manifest as
`registrarCaller`. The functions that contain those call sites were not
traced.

Four wrappers appear. Each constructs a holder whose invoke routine casts the
receiver with `0x009DA6CC` from `LuaControl` to the owner class.

| Wrapper | Owner class | Holder vftable | Invoke | Used by |
| --- | --- | --- | --- | --- |
| `0x00726A90` | `WidgetBase`, const | `0x00FD5B64` | `0x0071AD50` | the widget accessors and `_setKeyboardFocusedControl` |
| `0x00726B40` | `DesktopWidget` | `0x00FD5C28` | `0x0071B4D0` | `_appendMessagePool` |
| `0x00726BF0` | `DesktopWidget`, const | `0x00FD5C34` | `0x0071B4D0` | `_appendLogPool` |
| `0x00726CA0` | `WorldMaster`, const | `0x00FD5B70` | `0x0071AE70` | `_isKeyboardOnlyTutorial` |

A null cast returns false without calling the callback. A successful cast adds
the adjustment stored at holder `+0x0C`, calls the member function pointer at
holder `+0x08` with `ExecuteParameters` on the stack and returns true.
`0x00D19B70` tests the result at `0x00D19D3D`. A false result formats the
literal `Component::Lua::GameEngine::Functor::Execute` with the format
`%s,%i`, pushes it through `0x00CF3360` and calls `0x00CF38A0`, the pair that
also reports a `GetArguments_` failure. A call on a Lua value that is not a
widget therefore fails before any callback code runs.

A callback that indexes its argument cells tests the cell vector size first.
`_getChildWidget` at `0x0070756F` and the `_setKeyboardFocusedControl` slot
`0x00707870` at `0x00707893`, `0x007078D6` and `0x00707915` call `0x009D22B4`
when the vector is too short. The
[target cursor record](target-cursor-native-contract.md#cursor-state) records
that routine as the invalid-parameter route, and this page does not follow it
further. The no-argument callbacks and the two pool callbacks contain no such
call. The pool size checks, if any, sit in the shared worker `0x006E8360`,
which was not traced.

The callbacks read these `ExecuteParameters` cells.

| Offset | Content |
| --- | --- |
| `+0x04` | Engine handle |
| `+0x08` | Lua thread object, the receiver of the yield request `0x00CD2860` |
| `+0x0C` | Identity of the receiver control |
| `+0x10` | Argument container, whose cell vector has 16-byte cells with the tag byte at `+0x0C` |
| `+0x1C` | Return container, the receiver of the push routines |

The widget workers resolve their context the way the
[target cursor record](target-cursor-native-contract.md#cursor-state) does.
`0x00CC7510` turns the engine handle into the address of the engine field at
`+0x220`. The callback reads the dword there, then the dword at `+0x04` of it,
then the dword at `+0x04` of that value. The workers apply the first dword of
that last object as the context for `0x004D9910`. That routine searches the
tree at context `+0x17804` and returns the dword at `+0x10` of the found node,
or 0. Every widget worker below calls the next routine on that result without
a null test.

## Contracts

Argument indices count internal `ExecuteParameters` cells after the receiver.
A return list states capacity. A handler may push fewer values. A value beyond
the declared list raises the `GetArguments_` error described in the
[framework](widget-native-call-contract.md#argument-marshalling).

| Native | Owner | Arguments | Returns | Callback | Registrar | Yields |
| --- | --- | --- | --- | --- | --- | --- |
| `_getParentWidget` | `WidgetBase` | none | `LuaControl*` or Nil | `0x00707420` | `0x00750E60` | no |
| `_getChildWidget` | `WidgetBase` | `int` | `LuaControl*` or Nil | `0x00707530` | `0x00751100` | no |
| `_countChildWidgets` | `WidgetBase` | none | `int` | `0x007074F0` | `0x00750FB0` | no |
| `_setKeyboardFocusedControl` | `WidgetBase` | `Utf8String` x2 | `bool` | `0x006DED80`, slot `+0x90` | `0x007388B0` | no |
| `_isKeyboardOnlyTutorial` | `WorldMaster` | none | `bool` | `0x00707C70` | `0x00753080` | no |
| `_appendMessagePool` | `DesktopWidget` | `Which<LuaControl*,LuaControl*,Utf8String,int>`, `int`, `LuaControl*`, `int`, `Variable` | none | `0x006ECED0` | `0x00743ED0` | yes |
| `_appendLogPool` | `DesktopWidget` | the same five | none | `0x006ECF80` | `0x00744020` | no |

The manifest rows carry each name literal, name reference, install call,
callback load and list builder.

## Parent and child widgets

`_getParentWidget` takes no argument. The callback passes the receiver
identity to `0x0075BA50`, which resolves the widget and calls `0x00533ED0`.
That routine tests the dword at widget `+0xD8`. A nonzero value is an object
whose identity at `+0x88` is returned through `0x004D6750`. Zero returns the
empty identity `0xC0000000`. The empty identity pushes Nil through
`0x00748920`. Any other identity is resolved through `0x00CC7A50` and pushed as
`LuaControl*` through `0x00748B30`. A resolve that finds nothing is a null
control, which pushes Nil. `0x00CD8160` also returns null for an identity equal
to the dword at `0x0130C778`, which holds `0xE0000000` in the image.

Reading `+0xD8` as the parent widget is `INFERRED` from the name and the Nil
branch. No store to the field was traced. A receiver whose identity is absent
from the `0x004D9910` tree makes `0x00533ED0` read address `0x000000D8`.
Whether the process survives that fault is `unknown`.

`_countChildWidgets` returns the size of the child pointer vector at widget
`+0xDC`, whose first pointer is at `+0xE0` and end pointer at `+0xE4`. A null
first pointer gives 0. The count is pushed through `0x00584F70`.

`_getChildWidget` reads its argument through `0x005819A0` and subtracts 1. The
worker `0x00537C10` returns the empty identity for a negative index and for an
index greater than the count. Any other index calls `0x0052F7F0` and returns
the identity of the child object that the element points at. A Lua argument of
count plus 1 gives an index equal to the count. It passes the first test and
fails the size test in `0x0052F7F0`, which calls `0x005CF390`. That routine
builds `invalid vector<T> subscript` and throws a `std::out_of_range` through
`0x009D1B9F`. Whether the exception is caught before it leaves the Lua call is
`unknown`.

Unlike `_getParentWidget`, `_getChildWidget` does not compare the identity with
`0xC0000000` before it resolves and pushes it. That the empty identity
resolves to a null control and pushes Nil is `INFERRED`. `0x00CD8160` and
`0x00CD81D0` return null directly only for the identity `0xE0000000` and
otherwise search the containers.

## Keyboard focus

`_setKeyboardFocusedControl` takes a container name and a control name. The
callback is a thunk through receiver vftable slot `+0x90`. `WidgetBase`
holds `0x00707870` there. `DesktopWidget` holds `0x006DCAF0`, which is a bare
`ret 4`, so a `DesktopWidget` receiver pushes no value.

The `WidgetBase` slot reads argument 1 as a `Utf8String` and tests the tag
byte of cell 0. Tag 6 is Nil. A Nil container goes through `0x0075B9C0`
and `0x00538740`, which supplies the static empty string at `0x01266B10`. A string container
goes through `0x0075B9E0`. Both reach `0x005386D0` on the resolved widget.
That routine compares the container name with the static empty string. Equal
strings take the dword at widget `+0x98`. Any other name is looked up in the
map at widget `+0xEC` by `0x005353E0`, which returns the dword at node `+0x60`
or -1. `0x00537950` then resolves the control from the control name and that
value. It returns 0 for an empty control name. The routine casts the result
with `0x009DA6CC` from `.?AVDependencyObject@Sqwt@@` to
`.?AVFrameworkElement@Sqwt@@` and calls slot `+0x38` of the object at cast
`+0xB4`. The `AL` of that call is pushed as the bool. No instruction tests the
cast result for null, so a name that resolves to no control reaches a read at
`+0xB4` of a null pointer.

Calling slot `+0x38` is the focus request `INFERRED`. The slot body, the
lookups inside `0x00537950` and `0x00535690`, and whether the `Utf8String`
operator admits a Nil cell for argument 0 are `unknown`.

## Keyboard-only tutorial test

`_isKeyboardOnlyTutorial` takes no argument. The callback reads the dword at
the `0x00CC7510` address and then the dword at `+0x04` of it. It calls
`0x0075D120` with the engine handle on the object at `+0x110` of that value,
then calls `0x0075CE30` on the object at `+0x00` and pushes the `AL` of the
second call as the bool.

`0x0075CE30` returns false if and only if the dword at context `+0x508` and the
byte at `+0x505` are both nonzero. It returns true whenever `+0x508` is 0. The pushed value does not read
`+0x500`. `0x0075D120` is a refresh that queries property `0x0007A122` of the
object identified by `0xC0000024`. A true result queries `0x0007A123` and
`0x0007A121`, builds a dword with bit 0 set, the low 5 bits of the first
result in bits 1 to 5 and the low 2 bits of the second in bits 6 and 7, and
stores it at context `+0x500` when the pair changed from the cache at its
`+0x04` and `+0x08`. A false result stores 0 when the cache byte at `+0x09`
is set.

The only displacement encoded store of the byte at `+0x505` is `0x004DC02B`,
in the constructor `0x004DBF40` of `Application::Main::RaptureElementContainer`
(vftable `0x00F912E4`). The `MainModule` constructor `0x004DC3A0` calls it once
at `0x004DC414` on its subobject at `+0x10`. The constructor stores zero at
`+0x4FC` (byte), `+0x500` (dword), `+0x504` and `+0x505` (bytes) and `+0x508`
(`0x004DC031`) and `+0x50C` (dwords), and the dwords of its arguments at
`+0x4F4` and `+0x4F8`.

The same constructor initializes the identity registry at `+0x4AC`, the log
sink pointer at `+0x660` and the sheet manager pointer at `+0x174F8`, the fields
that the [scheduler contracts](scheduler-item-native-contract.md#world-object-and-identity-lookup)
record for the world object `V`. `0x0075CE30` takes the dword at its receiver
as `V`, and the callback passes the dword at `Y` as that receiver. Besides
`0x0075CE30`, only `0x0088C4C0` calls the readers `0x004D7250` and
`0x004D7260`. The setter `0x004D7230` of `+0x500` is called from `0x0055DFC4`
and `0x0075D1C9` and `0x0075D1DA`, and jumped to from `0x0075CD82`.

No other displacement encoded instruction in `.text` stores `+0x505`. The
stores of `+0x508` at `0x00514EDA`, `0x00C47904`, `0x00C48EA4` and `0x009E8D7A`
sit in routines that belong to other classes, and the last one lies in the C
runtime math code. That the receiver is the container is `INFERRED` from the
shared offsets. Under that reading both `+0x505` and `+0x508` are 0 after
construction, so `0x0075CE30` returns true and the native pushes true, unless a
store through a computed address exists. Such a store, the meaning of the three properties and the
object behind `0xC0000024` are `unknown`.

## Message and log pools

Both natives declare five arguments through the shared builder `0x00743A30`.
Argument 0 is a `Which` over `LuaControl*`, `LuaControl*`, `Utf8String` and
`int`, built through `0x007422C0` and `0x00740C30`. Arguments 1 to 4 are an
`int`, a `LuaControl*`, an `int` and a `Variable`. The return list is empty.

`_appendLogPool` is `0x006ECF80`. It calls the shared worker `0x006E8360`
with flag 0 and returns.

`_appendMessagePool` is `0x006ECED0`. It clears the byte at `DesktopWidget`
`+0x79`, builds an `AppendMessageResumeChecker` through `0x007139C0` and
requests a yield through `0x00CD2860` with the Lua thread at
`ExecuteParameters +0x08`. It then calls `0x006E8360` with flag 1. The
checker poll at `0x00713A20` tests the byte at `+0x79`. A nonzero byte marks
the checker done and stores the dword at `0x01377ECC` in the result cell. A
zero byte stores the dword at `0x0130CECC`. The text data checker poll at
`0x00718640` uses the same two cells. The checker destructor body at
`0x00718E10` sets `+0x79` to 1 when the checker was not marked. The other
writers of 1 in `DesktopWidget` code are the constructor and `0x006DCA80`,
which `0x0057596B` calls after resolving the identity `0xC0000024`. The
resume therefore waits for a later store of 1. That this store marks the end
of the message display is `INFERRED`. No consumer was traced.

The worker reads argument 1 and argument 3 as ints, reads argument 2 as a
control cast to `.?AVActorBase@Control@Client@Script@Lua@Application@@` and
converts it to an identity through `0x00CC73B0`. It collects arguments from
index 4 on through `0x007702C0`. The sink object is the dword at `+0xF8` of
the second object of the state chain. The tag byte of cell 0 selects the sink
call.

| Cell 0 | Call |
| --- | --- |
| tag 0, an `int` | `0x007721B0` |
| tag 3, a `Utf8String` read through `0x0071D770` | `0x00772560` |
| tag 4 control cast to `WorldMaster` | `0x00772650` |
| tag 4 control cast to `CharaBase` | `0x00772050` |
| anything else | nothing is appended |

`0x007721B0` builds a record through `0x0076B3D0`, stores its first argument
at record `+0x108` and passes a second object to the manager at `+0xE0` of the
second chain object. The bodies of the other three sinks, the pool record
lifetime and whether the yield takes effect before or after the worker are
`unknown`.

## Names that are not functor natives

`_math` is a value namespace for `math` in
`xivl-decomp:docs/script/lua-bootstrap-chunks.md`. Its literal at `0x00FE0850`
has one code reference and no registrar of the shape above. `_assignForChild`
is a work declaration key per
`xivl-decomp:docs/script/widget-work-members.md`, which is the basis for that
reading. Its literal at `0x0110F6BC` has no direct code reference. The only
reference found is the dword pointer to it at `0x0130D84C` in `.data`, which
the 39-byte helper at `0x00D212A0` loads at `0x00D212A8` and passes to
`0x00447260`. The pointer and that helper were not traced further.

`_defineClass` and `_defineBaseClass` are natives and every ask widget script
calls them. Their registrars `0x0073C270` and `0x0073C3C0`, name literals and
callbacks `0x006DCC30` and `0x006DCCA0` match
`xivl-decomp:docs/script/define-class-repeat-definition.md`, which holds their
contract.

## Open

- The parent field writers and the fault behavior of the unchecked widget
  lookup.
- Whether the C++ exception from the child index equal to the count, and the
  null cast read in the focus request, are handled before they leave a Lua
  call.
- The Sqwt focus slot, the control lookup behind `0x00537950` and the Nil
  admission of the `Utf8String` operator.
- Whether `0x00CF38A0` returns to the handler after a type mismatch.
- The writers of `+0x505` and `+0x508`, and the three properties behind the
  tutorial refresh.
- The sink bodies, the record lifetime and the message completion path of the
  pools.
- Which of these natives an `NpcSayWidget` or `AskWidget` instance reaches at
  run time.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes. The listings behind this
record came from a Capstone 5.0.7 x86-32 decode of the file through its
section table. With explicit project and JDK bindings and a new absolute
output path, the repository route for function listings is:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Registrars | `0x00750E60,0x00751100,0x00750FB0,0x007388B0,0x00753080,0x00743ED0,0x00744020` |
| List builders and wrappers | `0x0072C260,0x0072B440,0x00728C20,0x00728B70,0x0072BEC0,0x00743A30,0x007422C0,0x00740C30,0x00726A90,0x00726B40,0x00726BF0,0x00726CA0` |
| Holders | `0x00724C10,0x00724CE0,0x00724DB0,0x00724E80,0x0071AD50,0x0071B4D0,0x0071AE70` |
| Widget accessors | `0x0075BA50,0x0075BA90,0x0075BAB0,0x00533ED0,0x00533FF0,0x00537C10,0x0052F7F0,0x005CF390,0x004D9910,0x00CC7A50,0x00CD8160` |
| Focus request | `0x00707870,0x006DCAF0,0x0075B9C0,0x0075B9E0,0x00538740,0x005386D0,0x005353E0,0x00537950` |
| Tutorial test | `0x0075D120,0x0075CE30,0x004D7230,0x004D7250,0x004D7260` |
| Pools | `0x006E8360,0x007139C0,0x00713A20,0x00718E10,0x006DCA80,0x007721B0,0x0071BB80` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
