# Bazaar appearance contract

The remote Bazaar sign is selected from the actor work booleans
`charaWork.eventTemp.bazaarRetail` and `charaWork.eventTemp.bazaarRepair`.
The retail sign reaches the NamePlate icon setter with category `2`, sheet `1`
and icon `220`. The client evidence establishes how a false work value is
consumed, but it does not identify the server event that writes false after the
last listing sells.

## Binary and source identity

The native input is retail `ffxivgame.exe`, version `2012.09.19.0001`, size
`15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, PE32
x86, image base `0x00400000`. Native locators below come from retained
manifests and the read-only Ghidra/export records they cite; they were not all
fresh exports for this contract. The final setter edge also uses pinned PE
instruction inspection with pefile `2024.8.26` and Capstone `5.0.7`. The
retained presentation records specify Ghidra `12.1.3`. Addresses below are
absolute VAs.

`VerifyProgramFileBytes.java` completed with
`COMPLETE: program-file-bytes-v1` for the authenticated program. This
authenticates the identified file-backed code and data; it does not establish
runtime state or a server transition.

The Lua observations came from verified members of the 1.23b client-script
archive. The member hashes below are the identities recorded in
`xivl-client-scripts:manifests/scripts.json`:

| Member | Size | SHA-256 |
| --- | ---: | --- |
| `chara/charabaseclass.lua` | 34320 | `f17b3e62a137d8f524ba88d55296e1fb064512dc803f7a85dc980dd4bcbc9625` |
| `chara/charabaseclass_event.lua` | 8494 | `5fc7daa8450e109f8d2eac6e9f3c126496ae843f76326fc5a0fb34a0f404b986` |
| `chara/charabaseclass_cliprog.lua` | 8202 | `ea04844921f8820562afd172845cab7baf2df235725d20ad179bb713754c87fd` |
| `judge/depictionjudge.lua` | 22540 | `8db4d613d72ddf1921e3c9c4a961714371d2eac38fcc3b0211023105cb41a3e1` |
| `widget/bazaarlistwidget.lua` | 131819 | `f539b71353ee2860f535bc962ca2038ecf51bf99fdbeca314ed1eaa20bc39164` |
| `widget/desktopwidget_connector.lua` | 660617 | `9c33f21c1f70a0056147e716d53300634efabe5b744ef6e8690114db21613a01` |

The Lua line observations were produced with the read-only archive member
reader after checking each member against that manifest. No private archive
path is part of this contract.

## Work fields and dealer predicates

`CharaBaseClass._onInit` binds work key `4001` to
`charaWork.eventTemp.bazaarRetail` and work key `4002` to
`charaWork.eventTemp.bazaarRepair` (`xivl-client-scripts:lua/scripts/chara/charabaseclass.lua:1094-1107`).
The same event source declares `bazaarRetail`, `bazaarRepair` and
`bazaarMateria` as Boolean temporary fields and includes them in the event
sync mapping (`xivl-client-scripts:lua/scripts/chara/charabaseclass_event.lua:194-266`).
The save field `eventSave.bazaar` is also declared there, but the sign judge
does not read it.

`isRetailDealer`, `isRepairDealer` and `isMateriaAttachDealer` return those
three temporary fields after the `hasGameParameter` guard
(`xivl-client-scripts:lua/scripts/chara/charabaseclass_event.lua:4-49`).
The target-facing `isDealer` predicate returns true only when the retail or
repair field is true; materia alone is not included
(`xivl-client-scripts:lua/scripts/chara/charabaseclass_cliprog.lua:14-38`).
The desktop connector uses `isDealer()` for another player and for an outside
retainer Bazaar target (`xivl-client-scripts:lua/scripts/widget/desktopwidget_connector.lua:13168-13191,13265-13306`).
This establishes target reachability through the dealer predicate, not a
separate sign field.

## Lua sign selection

`judgeNameplate` first tests `isRetailDealer()`. A true result calls
`_setNameplateIcon(2, 1, 220)` (`xivl-client-scripts:lua/scripts/judge/depictionjudge.lua:141-150`).
When that predicate is false, the player branch selects category `2`, sheet
`1`, icon `0`; other non-player branches can select their combat icons
(`xivl-client-scripts:lua/scripts/judge/depictionjudge.lua:151-191`). Thus icon
`220` is the retail Bazaar sign choice, while a false retail value reaches the
ordinary non-Bazaar branch.

The verified original LPB is `0p635/65u17q1vw0p635.le.lpb`, 4142 bytes with
SHA-256 `9EB9B7054434CD5281CB52C89A2D5B43A40913DC47AB4D11CC18FDDA4ADE6E76`;
its decoded Lua payload is 4129 bytes with SHA-256
`756FA626BF9703AFB5F97A36EB5BC3643EAF216CC602137DDE5F034F678B9F19`
(`xivl-client-scripts:manifests/retail_lua_coverage.json:169-181`). Parsing
that payload with the pinned Lua chunk reader
(`xivl-client-scripts:tools/build_quest_contracts.py:67-158`) gives prototype
`0.0` at payload offset `0xDE`: PC 105 calls `isRetailDealer`, PCs 107-108
branch on its result, and PCs 109-113 invoke `_setNameplateIcon` with constants
`2, 1, 220`. This bytecode locator corroborates source lines 141-150 without
claiming runtime execution.

The category `3` icon is selected independently. Nonzero repair type selects
icon `928`; otherwise `isRepairDealer()` selects `380`,
`isMateriaAttachDealer()` selects `929`, and the fallback is `0`
(`xivl-client-scripts:lua/scripts/judge/depictionjudge.lua:194-235`). A
repair or materia icon must not be treated as the retail sign.

`CharaBaseClass._onUpdateWork` invokes `worldMaster._getMyPlayer()
  .getDepictionJudge().judgeNameplate(actor)` before its property-specific
visibility handling. The same callback receives a `charaWork` `property`
update and then updates NamePlate visibility
(`xivl-client-scripts:lua/scripts/chara/charabaseclass.lua:1142-1174`). The
ordering proves that an applied work property can trigger a fresh sign
decision; it does not prove which packet or server event caused that property
change.

## Native NamePlate consumer

The retained Lua/native indexes identify the `_setNameplateIcon` registration
at `0x0072E890`, shared binder at `0x00726460`, and implementation at
`0x006E3F80` (`manifests/bulk_napi_classification.json:2617-2622`,
`manifests/napi_field_access_enhanced.json:1081-1089`). The API dispatch
switchboard is `Control::CharaBase` vtable slot 2 at `0x007574A0`; its
`_setNameplateIcon` entry is confirmed in the Lua API indexes
(`manifests/lua_api_index.json:13054-13080`).

The final native edge closes the setter attribution. `0x006E3F80` converts
three Lua arguments and calls `0x0075B5C0`; raw PE instructions at
`0x0075B5C9`, `0x0075B5DB`, `0x0075B5E3` and `0x0075B5EC` perform actor lookup,
form `actor+0xBA0`, load vtable slot `+0x0C`, and call it with the three
arguments. The retained recursive field manifest independently records the
`0x0075B5C0` indirect read at `+0xBA0` and slot `+0x0C`
(`manifests/control_class_napi_field_access_recursive.json:1081-1102`,
`manifests/virtual_dispatch_queries.json:5772-5784`).

The NamePlate vtable is `0x00FCF98C`; cell `0x00FCF998` at byte offset `+0x0C`
contains `0x006A2C50`. Constructor `0x006A3C00` stores `0x00FCF98C` at raw
instruction `0x006A3C47` with the constructor receiver in ESI. This proves the
concrete NamePlate target for the actor work path. `0x006A2C50` selects one of
two icon resource globals from its first argument, calls the resource helpers,
and forwards all three arguments to `FUN_006A2B30`
(`manifests/ir_catalog.json:114900-114918`).

`0x006A2B30` clears the indexed icon cache to `-1` when the icon parameter is
less than one; its positive path resolves the decimal icon resource and stores
the icon id. NamePlate is an inline subobject at `CharaElement+0xBA0`. The
per-actor tick `0x0058DF90` invokes slot 13 at `0x006A3560`, which synchronizes
cached presentation/color state rather than the Bazaar icon
(`docs/client-architecture.md:1233-1240`,
`manifests/player_render_boundary.json#presentationDecompilationInvocation`).

The appearance native target group for a read-only export is:

| Purpose | VAs |
| --- | --- |
| `_setNameplateIcon` registration and native consumer | `0x0072E890, 0x00726460, 0x006E3F80, 0x0075B5C0, 0x007574A0, 0x006A2C50, 0x006A2B30` |
| NamePlate tick and slot-13 boundary | `0x0058DF90, 0x006A3560` |

## Actor work-value packet

The generic actor work update is s2c `0x0137`, catalogued as Set Actor Work
Values / `SyncMemory`. Its confirmed receiver is `SyncMemoryReceiver`, Lua
actor vtable slot `60`, with wrapper `0x00759ED0`, constructor `0x0089F4C0`,
apply `0x0089E550`, and destructor `0x0089E6E0`
(`manifests/receiver_opcode_map_inbound.json:1994-2038`). The apply chain is:

```text
0x00759ED0 -> 0x0089F4C0 -> 0x0089E550 -> 0x00775A30 -> 0x00775180 -> 0x0089E6E0
```

`0x00775A30` and `0x00775180` consume a dynamic property stream. Each record
has a one-byte type tag; the native thresholds distinguish record-update,
property-set, end-marker and terminator records. The record-local four-byte
property id is at `+0x12`, and the retained backward MurmurHash2 helper at
`0x00D31490` resolves observed ids from property paths
(`manifests/symbols.json:667-676,2251-2261`). A fixed application offset for
`bazaarRetail` or `bazaarRepair` is therefore not established: the property
record position depends on the preceding dynamic work records.

The generic SyncWriter page records the common Boolean writer storage and
callback shape, and explicitly says that the writer class is selected by the
registered Information subtype rather than a fixed actor offset
(`xivl-decomp:docs/net/sync-writer.md:11-22,24-34,38-53,76-95`). That is the
replacement boundary for a false value: a zero-valued Boolean must arrive as
the same typed property update for the registered field. No retained source
equates omission of the record with false, and no retained source shows a
Bazaar-specific replacement opcode.

## Item package updates and the last listing

The item-package callback is a separate path. `_onUpdateItemPackage` forwards
to `DesktopWidget.processUpdateItemInformation`
(`xivl-client-scripts:lua/scripts/chara/charabaseclass.lua:1310-1324`). That
connector updates the Bazaar list widget and other item consumers
(`xivl-client-scripts:lua/scripts/widget/desktopwidget_connector.lua:5861-6046`).
The list rebuild accepts package `8`; if `getBazaarItem` returns nil for a
slot, `makeBazaarItemList` deletes the corresponding list property and updates
the list (`xivl-client-scripts:lua/scripts/widget/bazaarlistwidget.lua:2526-2565`).
The package-8 callback also has update-counter and actor/editor-state guards
before calling `makeBazaarItemList`
(`xivl-client-scripts:lua/scripts/widget/bazaarlistwidget.lua:5350-5414`).

Those operations remove or rebuild a UI row. They do not call
`isRetailDealer`, `_setNameplateIcon`, or a known actor work setter. A nil
package-8 row therefore does not prove that the remote sign clears when the
last listing sells.

The proven client clearing mechanism is conditional: after a received
`charaWork.eventTemp.bazaarRetail=false` update, `_onUpdateWork` reevaluates
`judgeNameplate`. For a player, the retail icon `220` is replaced by the
ordinary player branch icon `0`. This is the presentation consequence of a
false work value; it does not identify who caused that value to change.

**Client-compatible server action (inference):** when the last listing sale
leaves a seller with no retail listings, the server should send an
actor-targeted s2c `0x0137` typed Boolean update for the registered
`charaWork.eventTemp.bazaarRetail` field with value `false`. A package-8 row
removal may be sent separately for list consistency, but the artifacts do not
establish its ordering or coupling. The client artifacts do not identify the
historical sender or scheduler, so this is a compatibility action rather than
a claim about a historical sender sequence.

## Evidence ceiling and reproduction

The proven route is:

```text
0x0137 actor work property
  -> SyncMemoryReceiver
  -> registered Boolean field
  -> CharaBaseClass._onUpdateWork
  -> judgeNameplate
  -> _setNameplateIcon(2, 1, 220) when bazaarRetail is true
```

The proven native setter continuation is:

```text
0x006E3F80 -> 0x0075B5C0
  -> actor+0xBA0 -> vtable cell 0x00FCF998
  -> 0x006A2C50 -> 0x006A2B30
```

The route proves the client-side input required to clear the sign, but does not
identify the historical server scheduler, the resolved dealer-Boolean property
hash, or the ordering with package-8 row removal. For a compatible server
implementation, send the typed false work update through `0x0137` and handle
package-8 list removal as a separate concern. The absence of a decoded
`lastItem` or `clearLastItem` Lua member does not exclude a native implementation.

To reproduce the native locator set, authenticate the pinned program with
`ghidra/VerifyProgramFileBytes.java` and run the committed read-only
`ghidra/DumpVAs.java` exporter. The NamePlate tick group is pinned by
`manifests/player_render_boundary.json`; the actor work receiver and dynamic
property parser are pinned by
`manifests/receiver_opcode_map_inbound.json` and
`manifests/symbols.json`. The `0x0075B5C0` edge is reproduced from raw
instruction anchors at `0x0075B5C9`, `0x0075B5DB`, `0x0075B5E3` and
`0x0075B5EC`. Do not assign a fixed Bazaar property offset without first
resolving the dynamic stream record and its path hash.
