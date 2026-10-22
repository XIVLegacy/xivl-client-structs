# Desktop native call contracts

[`manifests/desktop_native_call_contract.json`](../manifests/desktop_native_call_contract.json)
records the static Lua call contracts of the natives that the shipped desktop
widget and `WorldMaster` `_onInit` paths reach after the
[boot contracts](boot-native-call-contract.md). It also records the user
config key domain and the object that a `LuaControl*` return pushes. Natives
already in the boot or [widget](widget-native-call-contract.md) contracts are
referenced there and not repeated. The contracts describe client marshalling,
not config content, widget layout or server behavior.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
Addresses are absolute VAs. The observations came from Ghidra decompilation
and instruction listings of that executable. Name literals, holder RTTI
names, the property name literals, the `_static%X` literal and the
`0x012C3F78` condition byte were compared with the PE bytes through its
section table.

Registration, the StackOperator type registry and argument marshalling follow
the [widget contract framework](widget-native-call-contract.md#registration).
Each registrar builds the return list first and the argument list second.
Wrapper `0x00726A90` installs the `WidgetBase` const holder at vftable
`0x00FD5B64`. Wrapper `0x00726BF0` installs the `DesktopWidget` const holder
at vftable `0x00FD5C34`.

## Reach

Reach paths are script-derived. They use the boot call-order walk over the
Lua 5.1 bytecode of the shipped client scripts, whose identities are indexed
by `xivl-client-scripts:lua/registry.json`. That walk resolves receivers
loaded from the `desktopWidget` and `worldMaster` globals, and it includes
method definitions whose key is held in a register. The second rule covers
the `DesktopWidget` methods defined in `widget/desktopwidget_connector`. A
position counts names listed by `xivl-client-scripts:lua/napi_index.json`,
value namespaces included.

| Entry | Native | Position | Through |
| --- | --- | ---: | --- |
| `DesktopWidget._onInit` | `_getUserConfig` | 9 | `DesktopWidget.init`, `checkConfigLogData` |
| `DesktopWidget._onInit` | `_getMyPlayer` | 20 | `DesktopWidget.init`, `createWidget` |
| `MainMenuWidget._onInit` | `_setListTextProperty` | 10 | `MainMenuWidget.init`, `setListText` |
| `MapNavigationWidget._onInit` | `_setUICommandTemplateCondition` | 10 | `MapNavigationWidget.init`, `setTemplateConfirmCondition` |
| `PlayerParameterWidget._onInit` | `_getMyPlayer` | 10 | `setParameter`, `DesktopWidget.getPlayerGaugeMaxParameter` |
| `StatusEffectWidget._onInit` | `_getMyPlayer` | 11 | `clearStatus`, `DesktopWidget.getPlayerStatusSlotLength` |
| `WorldMaster._onInit` | `_getStaticActor` | 3 | direct |

Each widget path starts in `WidgetBaseClass._onInit`. The four widgets other
than `DesktopWidget` reach `_setUICommandCondition` at position 9 first, so
its contract is recorded here. The manifest lists the full paths and the
names each widget reaches next.

## Contracts

Argument positions exclude the receiver. A return list states capacity. A
handler may push fewer values.

| Native | Owning class | Arguments | Returns | Callback | Forwards to |
| --- | --- | --- | --- | --- | --- |
| `_getUserConfig` | `DesktopWidget` | `int`, `int` | `Which<Utf8String,int>` | `0x006FDE20` | `0x0075CAB0` |
| `_setListTextProperty` | `WidgetBase` | `Utf8String`, `int`, `Utf8String`, `int`, `Which<Utf8String,int>` x8 | none | `0x006F5030` | `0x006F4C80`, `0x006EAA20` |
| `_setUICommandCondition` | `WidgetBase` | `Utf8String`, `Utf8String`, `int` | none | `0x006EB6A0` | `0x0075B7B0` |
| `_setUICommandTemplateCondition` | `WidgetBase` | `Utf8String` x3, `int` | none | `0x006EB870` | `0x0075B7E0` |

None of these natives yields. The manifest rows carry each registrar, name
reference and list builder.

### User config

`_getUserConfig` takes a one-based group and a one-based key and passes each
minus 1 to `0x0075CAB0`. The store is the object `0x004D73C0` returns at
`+0x17430`. Its `+0x04` holds the group count and `+0x08` the record array.
`0x00443EA0` addresses record `(group * 32 + (key & 0x1F)) * 0xBC`. The group
is not range-checked and the key wraps every 32 values.

The record type tag at `+0x00` selects the return. Type 1 returns the int at
`+0x60`. Type 2 returns the string at `+0x68`. Any other type returns nil.
`0x00443DA0` restores a type 1 record from its default at `+0x64`.

Of the 11 shipped call sites, four pass group 6 with a key computed from a
log index. `widget/logwidget` and `widget/logcolorsettingwidget` each pass
group 2 with a computed key. The other five are `DesktopWidget` wrapper
methods that forward both values from their caller.

### List text

`_setListTextProperty` composes text the way `_setTextProperty` does. A
non-Nil identifier in argument 3 writes `@` and the identifier. Each later int
appends `/i` and the value, each string appends `/s` and the string, and the
first Nil ends the scan. A Nil identifier leaves the text empty.
`0x006EAA20` then sets five properties on the list control named by argument
0 through `0x0075BB80`: `Index` from argument 1, `AttributeName` from
argument 2, `ValueType` and `Action` from static pickups at `0x0134B898` and
`0x0134B8F0`, and `StringValue` from the composed text.

### UI command conditions

Both condition natives build a condition through `0x007172A0` from the
condition name, a kind byte at `+0x54` and a value byte at `+0x55`. A Nil
value uses the kind byte at `0x012C3F78`, which holds `0x01` in the image,
and value 0. An int value uses the kind byte at `0x0134C3FE` and the low byte
of the int. That byte lies in the zero-filled part of `.data` and has no
direct writer reference. `_setUICommandCondition` passes the command name and
the condition to `0x0053AB80`. `_setUICommandTemplateCondition` passes its
first two strings and the condition to `0x0053AA00`. Both resolve the
receiver identity through `0x004D9910` first.

## LuaControl returns

`_getMyPlayer` and `_getStaticActor` keep their call contracts in the boot
manifest. Both push their control through `0x00748B30`. The
`StackOperator<LuaControl*>` push slot `0x00CF9D60` pushes nil for Nil or a
null control. Otherwise `0x00CD7A30` returns the control's object reference,
which is the record at the control's `+0x04` or the root record held at
`GameEngine +0x1BC`.
`0x00CD7A50` indexes the Lua registry with the record's pool at `+0x08`, then
indexes that pool with its key at `+0x04`. When the result is not a table,
it indexes the registry pool named by the value at `0x0130D4F8` with the
root record key and does not check that result.

The return is therefore the control's instance table when its pool holds
one, otherwise the root record's entry in the pool named by the value at
`0x0130D4F8`. The push creates no Lua object.

The value at `ExecuteParameters +0x04` is an engine handle whose `+0x00`
holds the `GameEngine`. `0x00CC7510` returns the address `GameEngine +0x220`.
`_getMyPlayer` reads the pointer stored there, follows the pointer at `+0x04`
of that object, and loads the `LuaControl*` at `+0x0C` of the second object.
Shipped scripts call `CharaBaseClass` methods such as `getHPMax` on the
result.

`_getStaticActor` turns a number into an identity by adding the static kind
base in `0x00D03A50`. A name is matched against the `0x68`-byte entries at
`+0xE4` of the object held at `GameEngine +0x1C8`. Every constant argument
in the shipped scripts is a number, and `WorldMaster._onInit` passes 310001.
When no control resolves, the call yields through
`CreateStaticActorResumeChecker` on three routes: the identity is already in
the list at `+0x100` of that `GameEngine +0x1C8` object, `0x00CC78C0`
returns null, or the `+0x7D` flag of the new control's object reference is
clear. `0x00CC78C0` and its resolver `0x00CDDE20` run only when the
identity is absent from that list. `0x00CDDE20` returns null when the class
record's `+0x7B` byte is clear, and otherwise names a new static instance
with the `_static%X` literal at `0x0110E8C0` and the low 20 bits of the
identity.

## Open

- The Lua class of the MyPlayer control and the site that registers its
  instance table were not traced.
- The class selection and instance construction inside `0x00CDDE20` were not
  traced.
- The run-time value of the kind byte at `0x0134C3FE` and the meaning of the
  condition kinds were not traced.
- The user config group count, its source file and the names of groups and
  keys were not traced.
- Deferred rows for `_setUserConfig`, `_saveUserConfig`, `_resetUserConfig`,
  `_setListProperty`, `_updateList`, `_addItem` and
  `_setKeyboardFocusedControl` carry registration and declared lists only.
  The [talk widget contracts](talk-native-contract.md) record the handler of
  `_setKeyboardFocusedControl`.
- Reach positions are static call-site order across every branch, not a
  runtime trace.

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
| Wrappers and holders | `0x00726A90,0x00724C10,0x0071ACE0,0x00726BF0,0x00724DB0,0x0071B460` |
| Registrars | `0x00751A30,0x00746140,0x0073F9B0,0x007414F0,0x00742E50,0x0073A1A0,0x0073A050,0x00744460,0x00738F40,0x00741790,0x007388B0` |
| Handlers and targets | `0x006FDE20,0x0075CAB0,0x004D73C0,0x00443EA0,0x00443E40,0x00443E70,0x00443DA0,0x0075C9C0,0x006F4C80,0x006EAA20,0x006EB6A0,0x006EB870,0x007172A0,0x0075B7B0,0x0075B7E0` |
| LuaControl return | `0x00707970,0x00748B30,0x00CF9D60,0x00CD7A30,0x00CD7A50,0x0078CC30,0x00D03A50,0x00D13310,0x00D037A0,0x00CDDE20` |

The callback at `0x006F5030` is not a function entry in the analyzed
program. Read it as an instruction listing from that address. The list
builders named in the manifest are short and are also read as instruction
listings. No decompiled body, script body or ignored export is a tracked
evidence dependency.
