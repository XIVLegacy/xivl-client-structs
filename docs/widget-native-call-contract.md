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
`Component::Lua::GameEngine::Functor::GetArguments_`, walks the declared
argument list from Lua stack index 2. Index 1 holds the receiver. For each
entry `FUN_00CFAA10` calls the StackOperator's slot 1, which consumes one
stack slot. The int, float, bool, Utf8String and Variable readers convert Lua
nil to tag 6.

A declared position beyond the stack top is filled with tag 6 without a stack
read. Calls may therefore omit trailing arguments. When Lua arguments remain
after the declared list, `FUN_00D19A20` pushes the `GetArguments_` literal at
`0x0110F5B4` with line `0x9A` and raises through `FUN_00CF38A0`. A call with
more arguments than the declared list is a Lua error, not a silent discard.

Handlers then read values by position. `FUN_005819A0` requires tag 0,
`FUN_0071BAC0` tag 1, `FUN_0071BA00` tag 2, `FUN_0071CE70` tag 3 and
`FUN_0071BEB0` tag 4. A mismatched tag reaches `FUN_00CCA730`. Handlers that
accept nil test tag 6 before reading.

## Contracts

Argument positions exclude the receiver. A return list states capacity. A
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

The manifest rows carry each registrar, name reference and list builder.

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

Actual Variable cardinality, per-operator output counts, runtime Nil
emission, host/global binding, class defaults and live scheduling remain
unresolved. The general marshalling assertions above are neither
revalidated nor revoked by this finite path.

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
The `GetArguments_` check above raises on that call shape. The two
observations are unreconciled.

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
