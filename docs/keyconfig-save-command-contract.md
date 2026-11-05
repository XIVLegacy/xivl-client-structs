# KeyConfig.Save native command boundary

The retail client constructs a RoutedCommand named `KeyConfig.Save`. The
constructed `KeyConfigControl` has an input-handler override that recognizes
that command, marks the event handled, and calls `FUN_006819C0` with its stored
owner. This identifies a conditional native receiver and call. It does not
establish that ConfigKeyboardWidget Cancel selects that receiver or persists
changed key bindings.

## Binary and method

Input: retail `ffxivgame.exe`, build `2012.09.19.0001`, PE32 x86, image base
`0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [the retail-input manifest](../manifests/retail_inputs.json). All addresses
below are absolute VAs.

The observations used Python 3.12, Capstone 5.0.7 and pefile 2024.8.26 against
the authenticated original PE, mapped through its section table. Bounded
instruction decoding, constructor argument flow, table cells, COL offsets and
type names supplied the relationships below. These are static observations.
No client execution or successful file operation was observed.

## Command identity

Initializer `0x00F12400`, whose code pointer occurs at `0x00F44DF0`, supplies
the exact name literal `KeyConfig.Save` at `0x00FC3950` to string constructor
`0x00447260` at `0x00F12432`. The resulting temporary is passed to
`0x00928C90` at `0x00F12449`, with receiver `0x01340A98`. That constructor
copies its name argument to receiver `+0x24` at `0x00928D0F`.
The [RoutedCommand constructor contract](native-input-ui-boundaries.md#cached-command-target-and-slot-8)
qualifies its type and Execute slot. Thus `0x01340A98` is the statically
constructed command recognized below. Literal presence alone is not this join.

## Constructed receiver and Save branch

Let W0 be a complete constructor-qualified `KeyConfigControl`, and
Y = W0+0xB4 its input-interface receiver. Constructor `0x00681CC0` installs
primary table `0x00FC3DCC` and input table `0x00FC3CA4` at
`0x00681CF8-0x00681D08`. The input table's COL `0x01158B00` has displacement
`0xB4` and type descriptor `0x012BB260`, named
`.?AVKeyConfigControl@CustomControl@SqwtInterface@Main@Application@@`.
Input slot `+0x104`, at `0x00FC3DA8`, contains `0x00683E80`.
The [input dispatch contract](native-input-ui-boundaries.md#execute-and-routing)
reaches that slot: `0x0091D6BE` loads it and `0x0091D6C7` calls it. This
qualifies the constructed override, not every selected routed recipient.

`FUN_00683E80` takes Y and one event record E. After calling
`FUN_0092D1F0(E)` with the same Y, its Save branch requires both:

- The byte at the pointer stored in E+0x10 equals zero
  (`0x00683EBE-0x00683EC4`).
- The command pointer at E+0x1C equals `0x01340A98`
  (`0x00683ECA-0x00683ED2`).

The admitted branch writes byte E+0x19 to 1 at `0x00683ED4`, then loads
[Y+0x31C] at `0x00683ED8` and passes it to `FUN_006819C0` at `0x00683EDF`.
Since Y = W0+0xB4, this load addresses W0+0x3D0. The
[construction and stored-owner contract](native-input-ui-boundaries.md#keyconfigcontrol-construction-and-stored-owner)
qualifies the constructor's unchanged owner copy to that field and one
RaptureElementContainer producer path. The load adds no retention or lifetime
guarantee.

The existing [config parser contract](native-input-ui-boundaries.md#config-parser-callers-and-reentrancy-limits)
and [root selection contract](native-input-ui-boundaries.md#config-root-selection-and-temporary-markup-owner)
record `FUN_006819C0` selecting a root through `FUN_004D7550(V,-1)` and
calling `FUN_0054CAF0` for indices 0 and 1. The new command/receiver join
does not establish all effects of that loader, completed parsing, a file-write
request or a successful write.

## Cancel request and first unbound edge

The script-derived request is recorded in
`xivl-client-scripts:docs/config-keyboard-widget-contract.md:Cancel and toggle`.
ConfigKeyboardWidget Cancel requests
`sendControlCommand("KeyConfig_Saver", "KeyConfig.Save")`, then requests
widget closure. Its canonical LF source is 2872 bytes with SHA-256
`041d50b6e9d474ac7d6a4b75f675a84cf8ba2acfc88e375018698f53dbd2038d`.

The first unbound connection is that helper request's actual native route and
named-control binding: no qualified original control binding joins its
`KeyConfig_Saver` target to the constructed W0/Y above. The separate native
lookup through pointer cell `0x0126AB90`, holding the same name literal at
`0x00F94B64`, also does not prove this selection. The actual selected object,
its name-scope membership, stored owner, invoking thread and survival across
callbacks remain unqualified.

The [game, UI and system config stores](user-config-store-contract.md#stores)
remain separate contracts. The name `Save` does not join this command to
`_saveUserConfig`. No changed key binding, disk persistence, successful close
or server effect follows from this conditional receiver contract.
