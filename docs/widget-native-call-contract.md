# Widget and class native call contracts

[`manifests/widget_native_call_contract.json`](../manifests/widget_native_call_contract.json)
records the static Lua call contract of selected Control-class natives. Each
row gives the declared argument and return types, the owning native class,
the callback and the native target it forwards to. This page explains how
those values are read from the client. The contracts describe client
marshalling, not widget content or server behavior.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
Addresses are absolute VAs. The observations came from Ghidra decompilation
and instruction listings of that executable. Name literals, StackOperator
vftable entries, the interval constants and the `GetArguments_` literal were
compared with the PE bytes through its section table.

## Registration

Each native has a registrar that references its exact name literal. The
registrar builds two type lists, then calls a per-class wrapper that
constructs a `0x58`-byte functor. In `FUN_00724C10` the argument list is
stored at functor `+0x14` and the return list at `+0x24`. The holder
constructor installs a
`Component::Lua::GameEngine::Functor::MemberFunctionHolder` vftable whose
RTTI name carries the owning class and the member signature
`void (Class::*)(ExecuteParameters const&)`. `FUN_00CCCAD0` installs the
functor under the name built by `FUN_00447260`.

The type lists hold entries from the registry returned by `FUN_00CCA210`.
Its constructor `FUN_00CC9D60` appends `StackOperator<T>` instances in this
order:

| Index | Type |
| ---: | --- |
| 0 | `int` |
| 1 | `float` |
| 2 | `bool` |
| 3 | `Sqex::Misc::Utf8String` |
| 4 | `LuaControl*` |
| 5 | `AutoReleaseTentative` |
| 6 | `Nil` |
| 7 | `Table` |
| 8 | `IndividualIndex` |
| 9 | `Variable` |
| 10 | `LuaControlArray` |
| 11 | `LuaManyTentativeControlArray` |
| 12 | `IntegerArray` |
| 13 | `VariantVectorArray` |

A list builder loads registry entry `n` from offset `4n` of the registry
vector. The 16-byte `ExecuteParameters` value tag at `+0x0C` uses the same
numbering. A `Which<...>` entry is a `WhichStackOperator` built by
`FUN_00CCA470` over the listed alternatives and appended through
`FUN_00CCA2D0`.

## Argument marshalling

`FUN_00D19A20`, whose diagnostic is
`Component::Lua::GameEngine::Functor::GetArguments_`, initializes a shared
cursor at native-frame index 2. For a present position `FUN_00CFAA10`
calls the declared StackOperator's slot `+4`. The selected int, float,
bool, Utf8String and LuaControl* readers advance that cursor once on normal
return. Variable can consume a recognized suffix, as described below.
Other operators are not revalidated by this finite record.

When the declared cursor exceeds the Lua top, the dispatcher constructs
one tag-6 placeholder through `FUN_00583F70` and `FUN_00584EE0`, then
advances the formal cursor once. It reads zero present Lua values.
After all declared readers, `FUN_00D19A20` compares the resulting cursor
with its saved bound. Cursor greater than the bound bypasses the diagnostic.
Otherwise the path reaches `FUN_00CF3360` and `FUN_00CF38A0` with the
`GetArguments_` diagnostic. Declared list length alone does not determine
that outcome when Variable is present.

### Variable argument reader

The manifest's `framework.variableArgumentReader` records the bounded
instruction observations, selected reader slots and conditional derivations.
The named Variable constructor installs vtable `0x0110E0A0`. Its slot `+4`
resolves to `FUN_00CF8980` in the original PE. Reader labels retain the
published builtin registry identities and named constructor evidence.
EH-state numbers do not establish registry ordinals.

Variable keeps a local scan index and delegates recognized positions to
selected readers. Raw tags 3, 4, 1, 5 and 0 select numeric, string, bool,
control and Nil paths. Numeric selection uses `FUN_00CF3670` to choose int
or float. Every selected reader advances the shared cursor once on normal
return. A present Nil is not a terminator. An unsupported raw tag returns
before consuming that position.

For a valid native frame and present suffix with entry cursor p <= saved
top T, successful recognized readers through T consume T-p+1 present values and leave the
cursor at T+1. This inference depends on the published registry identities,
the bounded top-wrapper pseudocode and normal helper completion. Numeric
conversion fidelity, arbitrary control-table acceptance and error paths
remain unresolved. One append-helper call per successful selected path
uses the existing internal-cell append contract. It does not establish
return emission to Lua.

With the published `_createActor` prefix Utf8String, Utf8String, bool and
successful prefix reads, native-frame positions 2, 3 and 4 map to internal
indices 0, 1 and 2. A present Variable suffix begins at native-frame position
5 and internal index 3. It consumes T-4 values if every suffix reader
completes. If T < 5, the dispatcher supplies the omitted placeholder without
reading a present value. This is a native-frame marshalling inference.
Receiverless script/global mapping remains unresolved. The bounded context
preparation observations below leave transitive helper effects unknown.

Selected instructions and read-slot DWORDs were compared with the identified
original PE. That comparison does not establish entire loaded-image/FileBytes
identity, pseudocode-only helper correspondence or live behavior.

Handlers then read values by position. `FUN_005819A0` requires tag 0,
`FUN_0071BAC0` tag 1, `FUN_0071BA00` tag 2, `FUN_0071CE70` tag 3 and
`FUN_0071BEB0` tag 4. A mismatched tag reaches `FUN_00CCA730`. Handlers that
accept nil test tag 6 before reading.

## Native callback registration

`framework.globalNativeRegistrationEvidence` records the static registration
path. `FUN_00D07820` supplies callback address `0x00D08000` and integer 1
through `FUN_00CF32E0` to `FUN_00DCE2C0`. The latter stores the callback at
returned record `+0x10`. Its inline count loop copies three DWORDs per
`0x10`-byte stride, then writes a record pointer and raw tag 6 to the stack
cell and advances `[state+8]` by `0x10`.

For count 1, on normal helper return with conventional preserved registers,
let Q be `[state+8]` immediately before the count subtraction and R the
returned record. The inline copies read DWORDs at Q-0x10, Q-0x0C and Q-8
into R+0x18, R+0x1C and R+0x20, then replace the cell at Q-0x10 with R
and raw tag 6. The inline
state field returns to Q. This is relative to post-helper state and does not
establish whole-function top effects or source-argument consumption.

`FUN_00CF3400` forwards state and an explicit operand to `FUN_00DCE680`.
The latter places the second input in EAX and state in ECX for
`FUN_00DCD900`. It obtains a slot through `FUN_00DD4900`, copies three
DWORDs from its saved top-minus-0x10 value into that slot, and finally
subtracts `0x20` from the then-current `[state+8]`. Uninspected helper effects
prevent a whole-function net-delta claim. The callback and cell operations
support a native-closure construction and candidate indexed table-entry
installation interpretation. Those labels remain inference.

`FUN_00CD7A50` has a conditional destination-selection fallback. The loaded
value at `0x0130D4F8`, destination keys and receiver class remain unidentified.
`FUN_00D04FE0` parent and initializer instructions show conditional context
selection before invocation. Their transitive effects and overall Lua-frame
changes remain unknown. Registration does not establish invocation, callable
or metamethod dispatch, source syntax or receiver insertion. Raw tag 6 does
not establish internal StackOperator nil semantics. The Variable native-frame
contract above remains unchanged.

Selected instruction encodings were compared with the identified original PE.
That does not establish entire loaded-image/FileBytes correspondence,
pseudocode-only helper correspondence or live behavior.

## Contracts

Argument indices count internal `ExecuteParameters` cells. Receiverless
Global mapping remains unresolved. A return list states capacity. A
handler may push fewer values.

| Native | Owning class | Arguments | Returns | Callback | Forwards to |
| --- | --- | --- | --- | --- | --- |
| `_setFilename` | `WidgetBase` | `Utf8String` | none | `0x006EB640` | `0x0075B730` |
| `_setFilename` | `CutScene` | `Utf8String` | none | `0x006E7A60` | string at `+0x6C` |
| `_setFilename` | `SpreadSheet` | `Utf8String` | none | `0x006EB530` | `0x0075F5A0` object, slot 1 |
| `_loadForm` | `WidgetBase` | none | none | `0x006E3760` | `0x0075B750`, then yields |
| `_setProperty` | `WidgetBase` | `Utf8String`, `Utf8String`, `Utf8String`, `Variable` | none | `0x006F4F70` | `0x006E9AC0` |
| `_getProperty` | `WidgetBase` | `Utf8String`, `Utf8String`, `Utf8String` | four `Which<Utf8String,int,bool,float>` | `0x006EBA80` | `0x0075B870` or `0x0075B8A0` |
| `_getProperty` | `GroupBase` | `int` | `Which<Utf8String,int,bool>` | `0x00700450` | `0x006C2140` record |
| `_setTextProperty` | `WidgetBase` | `Utf8String` x3, `int`, `Which<Utf8String,int>` x8 | none | `0x006F5010` | `0x006F4910` |
| `_isInstanceOf` | `Global` | `Which<int,float,Utf8String,bool,LuaControl*,Table>`, `Utf8String` | `bool` | `0x006FF210` | RTTI cast or `0x00CC7210` |
| `_createActor` | `Global` | `Utf8String`, `Utf8String`, `bool`, `Variable` | `LuaControl*` | `0x00709640` | slot `+0x6C`, then yields |
| `_setLoopInterval` | `ActorBase` | `float` x5 | none | `0x006DBD90` | `0x0078C020` |
| `_callSuperClassFunction` | `ActorBase` | `Utf8String`, `Variable` | `Variable` | `0x006DBC40` | `0x0078D520` |
| `_getKeyboardFocusedWidget` | `DesktopWidget` | none | `LuaControl*` or nil | `0x006FDBF0` | `0x0075BA10` |

The manifest rows carry each registrar, name reference and list builder. The
[SpreadSheet contracts](spreadsheet-native-contract.md) record the other
natives of the `SpreadSheet` class, which share the `_setFilename` handle
at `+0xB4`.

### Property access

`_setProperty` and `_getProperty` on `WidgetBase` take an optional leading
name, a second name and a property name. A Nil first argument selects
`FUN_0075B810` or `FUN_0075B870`. A string selects `FUN_0075B840` or
`FUN_0075B8A0` with that name added. The `_setProperty` value dispatch in
`FUN_0073DF10` handles tags 0 through 4 with separate pickup builders. Any
other tag, including Nil, performs no update.

`_setTextProperty` shares that name routing through `FUN_006E9AC0`. A Nil
text identifier passes the static pickup at `0x0134BAA8`. Otherwise
`FUN_006F4910` writes the literal `@` from `0x00FD4DC0` and the identifier.
Each following int appends `/i` from `0x00FD4DC8` and the value. Each string
appends `/s` from `0x00FD4DC4` and the string. The first Nil ends the scan.

The `GroupBase` overload of `_getProperty` switches on its integer selector.
Selectors 0, 6, 7 and `0x10` through `0x13` return an int. Selectors 1 and
`0x14` through `0x17` return a bool. Selector 3 returns a string. Other
selectors return no value.

### Yielding natives

`_loadForm` and `_createActor` suspend the calling Lua thread through
`FUN_00CD2860` and `LuaThreadImpl::YieldLua` at `FUN_00CCD390`. `_loadForm`
installs a `WaitLoadFormResumeChecker` built by `FUN_00717510`.
`_createActor` installs a `Global::OnInitResumeChecker` built by
`FUN_00713FE0`. Its slot `0x007140C0` polls the control's initialization and
its slot `0x007493A0` pushes the control as the call result. The
`_createActor` existing-control branch returns at once when that control is
already initialized.

### Widget creation payload

The manifest's `framework.widgetCreationOnInit` records the conditional
WidgetBase new-control path. The creation callback copies its internal
argument-cell suffix beginning at index 3, converts it in order and passes
the converted container through the WidgetBase creation slot into the named
`_onInit` path. Its observed invocation counter is C + 1, where C
accumulates callback EAX results. This is not a Lua arity contract.

The successful-lookup layout is a supported inference: the lookup-derived
receiver is Lua argument 1, followed by emitted payload values. That
reconstruction uses thin-helper and negative-index-resolver pseudocode as
well as the observed replace-and-pop instructions. The manifest retains
the exact locators and the limited original-PE instruction comparison.

The Variable argument record supplies conditional input cardinality.
Per-operator output counts, runtime Nil emission, host/global binding,
class defaults and live scheduling remain unresolved.

### Loop interval

`_setLoopInterval` stops at its first Nil argument. A Nil first argument
passes the static value at `0x0130CF00` to `FUN_00CC7400`. Each float `f`
becomes `trunc(f * 10000.0 + 0.5) / 10` with signed division truncating
toward zero, using the doubles at `0x00FE0570` and `0x00F59898`. The result
is wrapped by `FUN_00CD6AB0` and passed to `FUN_00CC7400` in argument order.

### Instance test

`_isInstanceOf` returns false unless its first argument has tag 4.
`ActorBaseClass` matches every control. `CharaBaseClass`, `PlayerBaseClass`,
`NpcBaseClass`, `AreaBaseClass`, `DirectorBaseClass` and `DesktopWidget`
use the RTTI cast `FUN_009DA6CC` against the native class. Other names are
tested by `FUN_00CC7210`.

## Limits

`_callSuperClassFunction` declares one `Variable` after the method name. The
[door initialization record](door-initialization-native-contract.md) reads
`FUN_0078D520` as preserving two trailing values for a three-argument call.
Variable can consume a successful recognized suffix, so the declared
list length alone does not imply a `GetArguments_` error. This does not
establish the callback's source-level binding or runtime success.

`_isInstanceOf` and `_createActor` belong to `Global` and are called from
Lua without a receiver. Their positions are `ExecuteParameters` positions.
The binding that maps a global call onto those positions was not traced.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
With explicit project and JDK bindings and a new absolute output path, use:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Type registry and functor | `0x00CC9D60,0x00CCA210,0x00CCA2D0,0x00CCA470,0x00724C10,0x0071ACE0,0x00CCCAD0` |
| Argument marshalling | `0x00D04DA0,0x00D19B70,0x00D19A20,0x00CFAA10,0x00CFAC40,0x00CFB810,0x00CF38A0` |
| Registrars | `0x00738220,0x00735EB0,0x00746E70,0x00738370,0x00741640,0x00744990,0x0074D940,0x00745FF0,0x00753470,0x00757350,0x00742760,0x0072DF60,0x00751640` |
| Handlers | `0x006F4F70,0x0073DF10,0x006E9AC0,0x006EBA80,0x00700450,0x006F4910,0x006FF210,0x00709640,0x0078C020,0x0078D520,0x006FDBF0,0x006E3760` |
| Resume checkers | `0x00717510,0x00713FE0,0x007140C0,0x007493A0,0x00CCD390` |

The `_setFilename` callbacks at `0x006EB640`, `0x006E7A60` and `0x006EB530`
and the `_setTextProperty` callback at `0x006F5010` are not function entries
in the analyzed program. Read them as instruction listings from those
addresses. The list builders named in the manifest are short and are also
read as instruction listings. No decompiled body or ignored export is a
tracked evidence dependency.
