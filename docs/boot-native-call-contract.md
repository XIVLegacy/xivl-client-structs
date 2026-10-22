# Boot native call contracts

[`manifests/boot_native_call_contract.json`](../manifests/boot_native_call_contract.json)
records the static Lua call contracts of the natives that `WorldMaster._onInit`
and `DesktopWidget._onInit` reach first. Rows follow the measured call order.
Natives already in the
[widget and class contracts](widget-native-call-contract.md) are referenced
there and not repeated. The contracts describe client marshalling, not text
data, widget content or server behavior.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
Addresses are absolute VAs. The observations came from Ghidra decompilation
and instruction listings of that executable. Name literals, the vftable slots
named below and the `0x03A20000` immediate were compared with the PE bytes
through its section table.

Registration, the StackOperator type registry and argument marshalling follow
the [widget contract framework](widget-native-call-contract.md#registration).
Each registrar builds the return list first and the argument list second.

## Measured call order

Call order is script-derived. It was measured from the Lua 5.1 bytecode of
the shipped client scripts, whose script identities are indexed by
`xivl-client-scripts:lua/registry.json`. Call sites are taken in instruction
order. Each Lua-defined method is expanded at its first call through the class
method tables of the shipped scripts. Every branch is included, and a leading
unconditional jump over compiled-out code is skipped. Receivers loaded from
the `desktopWidget` and `worldMaster` globals resolve through `DesktopWidget`
and `WorldMaster`, and every other receiver resolves through the walking
class. The method tables include definitions whose key is held in a
register, which covers the `DesktopWidget` methods defined in
`widget/desktopwidget_connector`. Only names listed by
`xivl-client-scripts:lua/napi_index.json` are kept, each at its first
occurrence. The order is static call-site order, not a runtime trace.

`WorldMaster._onInit` reaches `_callSuperClassFunc`,
`_loadTextDataPermanently` and `_getStaticActor`.

`DesktopWidget._onInit` reaches these names in order:

1. `_callSuperClassFunc`
2. `_isInstanceOf`
3. `_string`
4. `_setFilename`
5. `_loadForm`
6. `_setProperty`
7. `_getProperty`
8. `_sendStoryboardCommand`
9. `_getUserConfig`
10. `_table`
11. `_setUserConfig`
12. `_saveUserConfig`
13. `_initTargetCursors`
14. `_setTargetCursorImage`
15. `_setTargetableDistance`
16. `_setTargetCharacter`
17. `_setCurrentTargetCursor`
18. `_setAllTargetCursorMask`
19. `_createActor`
20. `_getMyPlayer`
21. `_isAlive`
22. `_getTargetCharacter`
23. `_getCurrentTargetCursor`
24. `_getLockonTarget`
25. `_setLockonTarget`
26. `_getKeyboardFocusedWidget`
27. `_setKeyboardFocusedWidget`
28. `_haveEnmityCharacters`
29. `_countMember`
30. `_isMember`
31. `_getPos`
32. `_isTalkable`
33. `_getLocalizedDisplayNameForChat`
34. `_getUTF8StringByteLength`
35. `_delete`
36. `_setUICommandCondition`
37. `_countChildWidgets`
38. `_getChildWidget`
39. `_lockPlayerControl`
40. `_setParentWidget`
41. `_getParentWidget`
42. `_setLoopInterval`

`_string` and `_table` are value namespaces and `_isAlive` is an
IndividualRef metatable field. None of them is a functor native. The
[desktop contracts](desktop-native-call-contract.md) record
`_getUserConfig`, `_setUserConfig`, `_saveUserConfig` and
`_setUICommandCondition`. The first three rows also record call-site argument
counts measured from the same bytecode. Each count fits the declared argument
list.

## Script binding

Each row's `_u` script declares a descriptor named `<luaName>_inl`. The
manifest `inlBinding` field names that script and table. The descriptor
returns two strings, a receiver selector and `<luaName>_cpp`. The selector is
`global` for `_getStaticActor` and `self` for the other rows. The
`ActorBaseClass` descriptor for `_callSuperClassFunc` names
`_callSuperClassFunction_cpp`, which is the alias recorded by the widget
contract.

## Contracts

Argument indices count internal `ExecuteParameters` cells. Receiverless
Global mapping remains unresolved. A return list states capacity. A
handler may push fewer values.

| Native | Owning class | Arguments | Returns | Callback | Forwards to |
| --- | --- | --- | --- | --- | --- |
| `_loadTextDataPermanently` | `ActorBase` | `int`, `Utf8String` | none | `0x006E7500` | `0x00767230`, may yield |
| `_getStaticActor` | `Global` | `Which<int,Utf8String>` | `LuaControl*` | `0x006DCDF0` | `0x0078CC30`, may yield |
| `_sendStoryboardCommand` | `WidgetBase` | `Utf8String` x3, `Which<Utf8String,int>`, `int` | none | `0x006DED90` | slot `+0x94`, `0x006EBF30` |
| `_initTargetCursors` | `DesktopWidget` | `int` | none | `0x006E4FD0` | `0x0075EE70` |
| `_setTargetCursorImage` | `DesktopWidget` | `int`, `int` | none | `0x006E5030` | `0x0075EFC0` |
| `_setTargetableDistance` | `DesktopWidget` | `int`, `float` | none | `0x006E5230` | `0x0075F010` |
| `_setTargetCharacter` | `DesktopWidget` | `int`, `LuaControl*` | none | `0x006E53A0` | `0x0075B6C0` or `0x0075B700` |
| `_setCurrentTargetCursor` | `DesktopWidget` | `int` | none | `0x006E52E0` | `0x0075F060` |
| `_setAllTargetCursorMask` | `DesktopWidget` | `bool` | none | `0x006E5340` | `0x0075F070` |
| `_getMyPlayer` | `WorldMaster` | none | `LuaControl*` | `0x00707970` | push only |
| `_getTargetCharacter` | `DesktopWidget` | `int` | `LuaControl*` or nil | `0x006FD990` | `0x0075F0E0` |
| `_getCurrentTargetCursor` | `DesktopWidget` | none | `int` | `0x006FD950` | `0x0075B690` |
| `_getLockonTarget` | `PlayerBase` | none | `LuaControl*` or nil | `0x006DE880` | slot `+0x138` |
| `_setLockonTarget` | `PlayerBase` | `LuaControl*` | none | `0x006DE870` | slot `+0x134` |
| `_setKeyboardFocusedWidget` | `DesktopWidget` | `LuaControl*` | `bool` | `0x006FDCF0` | `0x0075BA30` |

The manifest rows carry each registrar, name reference and list builder.

### Text data loading

`_loadTextDataPermanently` adds `0x03A20000` to its integer argument. It calls
`0x00767230` with the sheet object from `0x0075F5A0`, the sheet name and that
number. Virtual slot 1 of the sheet object is then called with the name. A
nonzero result returns at once. A zero result suspends the Lua thread through
`0x00CD2860` with a `TextDataReadResumeChecker` built by `0x00712C80`, vftable
`0x00FD4FD0`. Its poll slot `0x00718640` repeats the slot 1 test. Its push
slot `0x00A72A20` pushes nothing, so the call returns no value.

### Static actor lookup

`_getStaticActor` resolves a string argument through `0x00CC7130` and any
other value as an integer through `0x00CC70E0`. A control that already
resolves is pushed at once. Otherwise the call may suspend with a
`CreateStaticActorResumeChecker` built by `0x0078D800`, vftable `0x00FE0558`.
Its poll slot `0x0078D880` waits for the control's `+0x7D` flag. Its push
slot `0x0078DD70` pushes the control.

### Storyboard commands

`_sendStoryboardCommand` jumps through receiver vftable slot `+0x94`, which is
`0x006EBF30` for both `WidgetBase` and `DesktopWidget`. Argument 0 is an
optional leading name with the same Nil routing as `_setProperty`, through
`0x0075BAD0` or `0x0075BB00`. Argument 3 selects the pickup class. An int
builds `SendStoryboardCommandPickUpWithInt`, or `WithTwoInts` when argument 4
is also an int. A string builds `WithString` and Nil builds `WithNone`. Any
other combination sends nothing.

### Target cursors

The cursor natives take a one-based cursor number and pass it minus 1.
`_getCurrentTargetCursor` returns its index plus 1. `_initTargetCursors`
stores the count at DesktopWidget `+0x68` and `_setTargetableDistance` stores
the distance at `+0x74`. `_setTargetCharacter` reads its control through the
CharaBase cast reader `0x0071BC90` and clears the cursor on Nil. The
[target cursor state](target-cursor-native-contract.md) records what the
workers do to the cursor vector, the current cursor and the cursor objects.

### Lock-on and focus

`_getLockonTarget` and `_setLockonTarget` dispatch through receiver vftable
slots `+0x138` and `+0x134`. The PlayerBase slots `0x006DEAA0` and
`0x006DEA90` return at once, so a plain PlayerBase receiver pushes nothing and
ignores the setter. The MyPlayer vftable `0x00FD785C` supplies `0x007051F0`
and `0x006E5DC0`. `_setKeyboardFocusedWidget` reads its widget through the
WidgetBase cast reader `0x0071C190` and returns false for a null widget.

## Open

- The manifest `deferred` rows record the registrars and declared lists of
  `_setUICommandCondition`, `_lockPlayerControl`, `_countChildWidgets`,
  `_getChildWidget` and `_setParentWidget`. Their handlers and forwarding
  targets are not recorded here. The desktop contracts record
  `_setUICommandCondition` in full. `_haveEnmityCharacters`, `_countMember`,
  `_isMember`, `_getPos`, `_isTalkable`, `_getLocalizedDisplayNameForChat`,
  `_getUTF8StringByteLength`, `_delete` and `_getParentWidget` have no call
  contract row.
- `_loadTextDataPermanently` is registered on `ActorBase`, and
  `WorldMaster._onInit` calls it on its own receiver. The binding that
  resolves it for `WorldMaster` was not traced.
- The DesktopWidget order expands its superclass `_onInit` as
  `WidgetBaseClass._onInit`. The scripts do not declare that parent. The
  expansion is inferred from the `DesktopWidget` test inside
  `WidgetBaseClass._onInit`.
- The semantics of the identity behind `0x0075C690` and the sheet object from
  `0x0075F5A0` were not traced.
- `WorldMaster._onInit` passes one argument to `_callSuperClassFunc`.
  `DesktopWidget._onInit` passes the method name followed by all five results
  of a Lua method, a six-argument call. The declared
  `_callSuperClassFunction` list holds Utf8String and Variable. The
  [Variable argument reader](widget-native-call-contract.md#variable-argument-reader)
  can consume a successful recognized suffix, so list length alone does not
  imply a `GetArguments_` error. Source-level binding and runtime success
  remain unresolved.
- The step that maps a `_cpp` name onto the registered functor was not
  traced. The only `_cpp` literal is at `0x00FDF2CC`, referenced from
  `0x007634B0`.

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
| Wrappers and holders | `0x007263B0,0x007243F0,0x0071A660,0x00726E00,0x007256D0,0x007254D0,0x00726B40,0x00724CE0,0x0071B380,0x00726BF0,0x00724DB0,0x0071B460,0x00726CA0,0x00724E80,0x0071AE00,0x007267D0,0x007248D0,0x0071E880` |
| Registrars | `0x0072E350,0x00741A30,0x00743550,0x007391E0,0x00739330,0x00739480,0x00739870,0x007395D0,0x00739720,0x00752750,0x007513A0,0x00751250,0x00733360,0x00733210,0x00751790` |
| Handlers and targets | `0x006E7500,0x00767230,0x006DCDF0,0x0078CC30,0x006EBF30,0x006EBE80,0x0075EE70,0x006E5030,0x0075F010,0x006E53A0,0x006E52E0,0x006E5340,0x00707970,0x006FD990,0x006FD950,0x007051F0,0x006E5DC0,0x006FDCF0` |
| Resume checkers | `0x00712C80,0x00718640,0x0078D800,0x0078D880,0x0078DD70` |

The callbacks at `0x006DED90`, `0x006E4FD0`, `0x006E5230`, `0x006DE870` and
`0x006DE880` are not function entries in the analyzed program. Read them as
instruction listings from those addresses. The list builders named in the
manifest are short and are also read as instruction listings. No decompiled
body, script body or ignored export is a tracked evidence dependency.
