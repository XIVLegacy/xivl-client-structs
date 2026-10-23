# Dynamic widget item consumer

[`manifests/widget_item_consumer_contract.json`](../manifests/widget_item_consumer_contract.json)
records native resource construction, indexed context and part lookup, and the
Ask inherited wrapper arguments. Ask statically supplies an explicit template
key and numbered item names. For the selected resource and built-in factories,
successful allocation/parsing constructs a Button, publishes its answer-part
name in the item scope, and supplies it as a new ListBoxItem's Content.
Pre-existing registry entries and runtime success remain qualified.

`STATIC` identifies native instruction/data observations or authenticated Lua
operand flow. `INFERRED` identifies a conditional interpretation. `unknown`
marks an unresolved consumer. No successful native call or widget rendering is
established.

## Inputs and method

The executable is retail `ffxivgame.exe`, build `2012.09.19.0001`, PE32 i386,
image base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
The [retail input manifest](../manifests/retail_inputs.json) and
[registration contract](fade-actor-group-native-contract.md#widget-item)
own the executable identity and native entry framework.

| Script | Wrapped bytes and SHA-256 | Decoded bytes and SHA-256 |
| --- | --- | --- |
| `client/script/n1635q/9rz/9rzn1635q.le.lpb` | `5257`, `8541d21030988f4ed5460690156a71a5a0120b68ed38d8db181676b27a23bfe9` | `5244`, `1b0d5e2ca4c39b781305b98320eb597337e0d4c0fc0c9167244553dfc49d14c0` |
| `client/script/n1635q/n1635q89r57y9rr_7vxxvw.le.lpb` | `32996`, `c549f746370366f9827570ee22201516e07a05d91829ca643a2e2ec0c73bcf3c` | `32983`, `7c45426b1a9f168557d84e420c5767c6fdea4abf90b976b276546af4e6a5de5f` |

The selected template input is `client/sqwt/widget/AskWidget.tpl`, `535`
bytes, SHA-256
`e9ffd9acfb89498efd2ffac3e346e0f826082443cba64c6fc91e6b931e9189ad`.
Its decoded document is `527` bytes, SHA-256
`2cbe61b006602d9451419b64fa39abfc4bad908061e2d47cf82c225f67bd0e6f`.
Strict UTF-8, XML parsing and exact re-encryption corroborate that identity.
Only the selected direct declarations below are covered, not the Button's
subtree or complete resource closure.

### Producing method

Native observations used focused `ghidra-cli` static disasm/data queries in
an existing analyzed target. Decompilation supplied leads only. Selected
instructions, literals, vtable/COL/RTTI fields and call flow were independently
compared with the authenticated PE. This does not claim database-wide
analyzed-program/FileBytes identity.

Script observations used `tools/decode_lpb.py` and the unchanged AST-selected
`ChunkReader`, `walk`, `instruction` and `OPCODES` definitions in
`xivl-client-scripts:tools/build_quest_contracts.py`, with standard-library
dependencies. The walk consumes each entire decoded chunk, respectively
`5244` and `32983` bytes. PCs are one-based within the named prototype.
Chunk offsets are zero-based within the full decoded chunk. An offset range
includes the first and last instruction starts. Operands and referenced
constants are both part of the observation.

Template observations used `xivl-tools:tools/blowfish.py` with the basename-key
SQEX recipe in `xivl-tools:docs/formats/sqex.md`, strict UTF-8 and
`xml.etree.ElementTree`. Direct-child metadata and exact re-encryption were
checked. No raw instructions, Lua body, XML hierarchy or composed markup body
is retained. The alternative reproduction procedures below are separate from
these producing tools.

## Resource construction

The earlier contract owns `_addItem`'s four declared `Utf8String` arguments,
receiver check and optional leading-context callback routing. It also retains
the unresolved question of whether the marshaller admits `Nil` for that
declared string. The Ask helper's static nil argument does not resolve that
marshaller question.

`0x006EBC10` reaches `0x0053AA10` through the published widget route. At
`0x0053AA4F`, the construction call receives the requested item name, resolved
context index and template key. Its returned index enters `0x00537C60` with
the item name at `0x0053AA5E`.

`0x00538B70` allocates `0x48` bytes for a `XamlControlContainer`, constructs it
through `0x0096E4D0`, and uses the indexed context root at `X+0x2C` in that
routine. At `0x00538C62-0x00538CB7`, the literal `ControlTemplate` enters
`XamlStaticResource`, then `0x0094A270` reaches resource search `0x00948EF0`
and parsing `0x0096A4C0`. `0x009480E0` reads `x:Key` and `TargetType`, parses
`{x:Type`, and returns its single type token. This is a resource-based route,
not a type chosen solely from the list's name.

At `0x00538D2F-0x00538E08`, that target type and the requested item Name enter
new-element composition through selected literals at `0x00FA0844`,
`0x00FA084C` and `0x00FA0854`. The selected built-in factory binding below
qualifies the concrete object on this successful path.

## Selected Content composition

At `0x00538ECE-0x00538EDC`, the first parsed object is saved from
`container+0x30`, and that field is cleared before the second parse. The named
second root is also stored at `container+0x34` at
`0x00538F8B-0x00538F98`. `0x0052EA80` finds the named root and returns its
pointer plus `0x194`. At `0x00538FA4`, the saved first object is supplied to
slot `+4` of that interface, the `IAddChild` path.

For a `ListBoxItem` root, the constructor installs secondary vtable
`0x0107AE74` at complete-object offset `0x194`. Its `+4` cell
`0x0107AE78` contains `0x00935160`. That routine checks interface `+0x1C0`,
adjusts the receiver by `-0x194`, and calls `0x00934F40` with the supplied
object, `0` and `1`. `0x00934F40` passes descriptor `0x01358F94` to
`0x009367B0`. Initializer `0x00F221E0-0x00F221EF` names that descriptor
`Content` from `0x0106B16C`.

The interface result is conditional on a `ListBoxItem` root. The selected
built-in path below identifies that root and the saved Button, subject to
allocation/resource success and retained pre-existing registry entries.
The Button enters Content, not the Template setter through this interface.
The whole chain is a static reconstruction, not an executed construction.

## Built-in factories and selected template

The lazy registrar at `0x0094B37D-0x0094B392` supplies `ListBoxItem` from
`0x0106D3D8` to extension `0x01359EE0`. Constructor `0x00952550` installs
vtable `0x0106DF74` and registers the name through `0x0094AA00`.
Lookup `0x009492A0` searches the map at `[0x01359C70]+4` and returns
`node+0x60`. `TemplateMarkupObject` uses the current element tag as that key
at `0x0094B5B3-0x0094B5CA` and invokes extension slot `+4`.

Cell `0x0106DF78` holds callback `0x009525E0`. It allocates `0x36C` bytes
and calls `0x0099E140` at `0x0095264B`. The constructor installs primary
vtable `0x0107AFB4` and secondary `+0x194` vtable `0x0107AE74`.
COL `0x0118001C` points to TypeDescriptor `0x0126EBF4`, named
`.?AVListBoxItem@Controls@Sqwt@@`. These are constructor/RTTI observations,
not a binding inferred from a matching name alone.

The registration replacement flag is `0`. An existing name entry is retained.
The same qualification applies to Button. This identifies the built-in path,
not all possible runtime registry contents.

Selected-resource parsing uses non-control adapters. `XamlStaticResource`
vtable `0x00F9D2B4` slot `+8`, `0x0094A190`, recognizes
`ResourceDictionary` and constructs `XamlResourceDictionary` at `0x00545F20`.
Its vtable `0x00FA2680` slot `+8`, `0x0094A550`, handles
`ControlTemplate` through `XamlFrameworkTemplate` constructor `0x0094E8E0`
and selected-DOM traversal `0x00947040`. `XamlFrameworkTemplate` vtable
`0x0106D9CC` slot `+0x0C`, `0x00948FF0`, captures `x:Key` into
parser `+0x74` and handles TargetType. Slot `+0x18`, `0x00947300`, checks
the requested key/type before traversing children. These parsers preserve
the container at frame `+4` and set current-control frame `+0x10` to zero.
They do not create a ControlTemplate control in `C+0x30`.

The authenticated Ask template has exactly one keyed
`ControlTemplate_ListBoxItem`. Its two direct child elements are, in order,
a childless `Setter` with raw `Property=IsTabStop`, `Value=False`, then a
`Button` named `TemplateButton_Answer`. No Button descendants or full XML
hierarchy are covered. The scalar Setter therefore cannot hide an earlier
nested control parse in this selected input.

Child callback `0x0094BDF0` handles `.Triggers` separately. Other child tags
reach `0x0094AD90` at `0x0094BE97`. The direct Setter constructs
`SetterMarkupObject` at `0x0094F0E0`, leaving current control `+0x10` zero.
The selected Button uses registration `0x00950030`, literal `0x0106D2DC`,
vtable `0x0106DE14` and cell `0x0106DE18`, callback `0x009500C0`.
That callback allocates `0x3B4` bytes and calls `0x00974410` at
`0x0095012B`. Primary vtable `0x01073CAC`, COL `0x0117D44C` and
TypeDescriptor `0x0126D244` identify `.?AVButton@Controls@Sqwt@@`.

The callback passes Button `P` to `MarkupObject` constructor `0x00946830`.
That constructor copies parent frame `+4` into its own `+4`. If `C+0x30`
is null and `P` is nonnull, it writes `P` there at `0x009468AA`.
For this fresh selected scope, the saved first root is thus Button `P`.
A successful second parse constructs the separately named ListBoxItem `R`,
and the observed IAddChild call supplies `P` as `R.Content`.

## Answer name publication

`0x00947040` finds the Name attribute using literal `0x0106D244` at
`0x009470B3`, then applies it through `0x00912D50` at `0x00947104`.
The Name setter uses descriptor `0x01356BC8` and storage at control `+8`.
Initializer `0x00F20620` names that descriptor from `0x01068310`.

When the resulting Name is nonempty and control `+0x298` is zero,
`0x00947120` calls `0x0096E580` with receiver `C`, Name and `P`.
It searches `C+4`, suffixing duplicates when required. `0x0094D580` returns
the node's `+0x60` value slot. `0x0096E753` stores `P` there, and
`0x0096E75A` stores `C` at `P+0x298`.

The fresh selected scope has one direct named Button before the new
ListBoxItem parse. The second parse keeps that same `C`, so the indexed
resolver can retrieve `P` by `TemplateButton_Answer`, independently of the
new root's `Item_AnswersN` name. `P+0x298=C` is a raw name-scope association.
It is not a lifetime lease, stale-reference guarantee or proof that a
subsequent property setter succeeds.

## Indexed context and property receiver

The construction stores a separate container under the next integer index
through the map at `engine+0xD4` and increments `engine+0x94` at
`0x00538FA6-0x00538FC3`. `0x00537C60` inserts the supplied index into the
item-name map at `engine+0xEC` only if the name is absent. Its `ret 8` is
instruction evidence despite incomplete recovered parameters. Reusing a name
is not proved to replace its mapping.

`0x005353E0` resolves a context name through that map to `node+0x60`, or
`-1`. For a nonempty leading context, `0x005354D0` resolves the index and
constructs `SetPropertyProcessor` with engine, index, part name and property
name. `0x00535690` resolves an index through `engine+0xD4` to the stored
container pointer at `node+0x10`.

`0x00537950` uses the index/name cache at `engine+0x1DC`. On a miss,
`0x0053E480` searches `container+4` and returns `node+0x60`. If that misses,
`container+0x30` supplies a fallback root for `0x0053C310 -> 0x00910980`.
For the selected successful built-in path, this retrieves the published
Button in its item scope. Cache invalidation on row removal remains untraced.

At `0x00542710-0x00542729`, the processor's string slot forwards the stored
part name, property name, string value and index to `0x00537DE0`. That routine
calls `0x00537950` and returns on a null result. When its existing visibility
gate permits the update, `0x00537F61` makes the resolved part pointer the
receiver of property-engine call `0x00912850` at `0x00537F63`.
The [visibility property path](native-input-ui-boundaries.md#visibility-property-path)
owns the surrounding gate. Text evaluation and pixels are not established.

## Ask wrapper join

The Ask chunk's `root/proto0` supplies:

| PCs | Chunk offsets | Static call inputs |
| --- | --- | --- |
| `41-46` | `0x245-0x259` | `_setUICommandTemplateCondition` receives `ControlTemplate_ListBoxItem`, `TemplateButton_Answer`, `UILuaCommands.Operate` and `5`. |
| `47-51` | `0x25D-0x26D` | Inherited `addListBoxItem` receives `ListBox_Answers`, `Item_Answers` and `24`. |

The WidgetBase chunk's root PCs `499-504`, offsets `0x7E8-0x7FC`, bind
`proto166` as `WidgetBaseClass.addItem` and `proto167` as
`WidgetBaseClass.addListBoxItem`. In `root/proto167`, PCs `1-14`, offsets
`0x783B-0x786F`, the numeric loop runs from `1` to argument `3` with step
`1`. It appends `tostring` of that index to argument `2`, then calls
`addItem` with argument `1` and the resulting name.

In `root/proto166`, PCs `1-6`, offsets `0x778F-0x77A3`, that helper supplies
`_addItem` with nil context, its first argument, the literal
`ControlTemplate_ListBoxItem`, and its second argument. Thus Ask's static
frames supply `ListBox_Answers`, the explicit template key and names
`Item_Answers1` through `Item_Answers24`. These are precreated row names,
not a claim that 24 answers are visible or selectable.

The Ask property branch at `root/proto2` PCs `58-67`, offsets
`0x667-0x68B`, builds `Item_Answers` plus the loop index and names
`TemplateButton_Answer` and `Content`. The
`xivl-client-scripts:docs/duty-confirmation-client-contract.md#text-and-native-property-input`
record owns the selected question/answer text arguments and suffixes.
Together these facts support a static API-flow inference: an answer write
selects its row context index before resolving its named Button. The selected
built-in construction is supported under the conditions above, without an
executed materialization or property-acceptance claim.

`xivl-client-data:docs/sqwt-ask-structure.md` owns the separate Ask form and
template declarations. The wrapper supplies an explicit template key rather
than relying on a guessed implicit assignment to the empty answers list.
The selected factory and name-publication observations complete that bounded
static construction join. They do not establish a Template-property write,
a global registry rule or executed UI success.

## Separate list-action route

`_addList` is not the resource-construction operation. Its callback
`0x006EBE00-0x006EBE19` reaches `0x006EB070`, which picks a string and int
and writes `Index` and `Action` through `0x0075BB80`. `0x005355A0` is the
cited downstream route. The Action pickup value and list-action callback
semantics remain untraced.

## Claim boundary

The selected resource and built-in factory route identify Button Content in
ListBoxItem and the answer name map on a successful path. The observations
still do not establish:

- The contents of every runtime markup registry. Built-in registration retains
  an existing entry when replacement flag is `0`.
- Successful allocation, resource selection/loading or acceptance by every
  property-engine flag. Raw scope association does not provide a lifetime lease.
- Nil admission by the declared string marshaller, the widget registry class,
  complete bodies of `0x00535C80`, `0x00539010` and `0x0053A970`, dynamic
  removal/reopen behavior or cache invalidation.
- Arbitrary scripts, transitive form/style/resource closure, Button descendants
  or the full XML hierarchy.
- Native text evaluation, events, command delivery, selection/result mapping,
  geometry, layout, pixels, live-session behavior or server parity.

## Reproduction

Authenticate the exact executable, both wrapped/decoded scripts and selected
wrapped/decoded template against the identities above. These are alternative
reproduction procedures, not the producing-tool list. Follow [program authentication](../ghidra/README.md#verifyprogramfilebytesjava)
with `ghidra/VerifyProgramFileBytes.java`. Use the read-only
`DumpFunctionListing.java` route documented in the
[registration record](fade-actor-group-native-contract.md#reproduction)
for exact native function entries. `DumpVAs.java` supplies decompiler and caller context only. Use direct PE
instruction inspection for selected operands/data and callbacks that are not
function entries. The [native input method](native-input-ui-boundaries.md)
describes the bounded LLVM objdump route.
Compare the construction, interface slot, property descriptor, map fields and
null/visibility branches at the manifest's exact locators. Do not rely on a
decompiler's recovered parameter count at `0x00537C60`.

Decode only the two named script inputs through `tools/decode_lpb.py` as
specified in the [tool guide](../tools/README.md#lpb-decode-pipeline).
Walk the Lua 5.1 header and prototype records using their declared integer,
size_t and instruction widths. Retain prototype paths while reading each
constant pool and fixed instruction vector. Check the bindings, receiver and
argument positions, fixed call arities, loop bounds and concatenation inputs
at the PCs above, and require full decoded-chunk consumption. Compare constants
as well as operands. Do not replace that check with a decompiler's shortened
call or treat the static calls as executed.

For the template, reproduce the named basename-key SQEX decode with
`xivl-tools:tools/blowfish.py`, require strict UTF-8 and XML parsing, and
compare re-encrypted bytes with the authenticated wrapped input. Check exactly
the selected key, direct-child order/count, childless Setter attributes and
Button name. Do not broaden this into a full subtree or transitive-closure claim.

The tracked snapshot stores semantic assertions and locators only. Temporary
input copies, raw exports, decoded chunks, instruction listings, composed
markup and decompiled bodies are outside the public product.
