# Direct equipped-gear repair fulfillment

Command 24244 has an actual issuer in `RepairEquipmentWidget`. It submits an
equipment-slot number or RepairAll selector 27, followed by explicit nil
positions and a separate target player control. A repair-specific server
reply and authoritative completion transaction are not established.

## Client path and command identity

`MainMenuWidget` adds 24244 when `getTargetRepairType()` is nonzero. Selecting
it calls `executePlayerRepair`, which opens `RepairEquipmentWidget` for the
main target after `isOtherPlayer` passes. This opens the UI; the fulfillment
command is issued later by `RepairEquipmentWidget.processUICommandOperate`.
The widget's initial system-command 24238 request is also separate.

Source: `xivl-client-scripts:lua/scripts/widget/mainmenuwidget.lua:1617-1629,2162-2166`;
`widget/desktopwidget_connector.lua:14095-14118`;
`widget/repairequipmentwidget.lua:81-84,1888-2100`, at the source revision
and authenticated identities below.

`xivl-client-data:manifests/staticactor_class_paths.json`, row 24244,
binds `/Command/System/RepairEquipmentsCommand`. `command.csv` row 24244,
numeric header column 29, contains signed32 priority 4.
`CommandBaseClass.getPriority` reads that column, and
`CharaBaseClass.getCommandName` selects `commandContent` for a system command
of priority 4 (`command/commandbaseclass.lua:4-23,106-125`;
`chara/charabaseclass.lua:399-496`).

## Ordered operands and identity domains

The RepairAll and individual-slot calls are
`executePlayerCommand(24244,S,nil,nil,nil,T)`
(`repairequipmentwidget.lua:1935-1944,2025-2034`). The connector resolves
24244 to a command actor and submits the following nine values after that
actor to `PlayerBaseClass.command` (`desktopwidget_connector.lua:13615-13674`).

| Operand | Authored value | Client meaning and type | Conditional serialized width |
| ---: | --- | --- | --- |
| 1 | S | Integral Lua equipment-slot number, or bulk selector 27 | Integer tag `00` plus u32 big-endian, 5 bytes total |
| 2 | nil | Explicit nil | Tag `05`, 1 byte |
| 3 | nil | Explicit nil | Tag `05`, 1 byte |
| 4 | nil | Explicit nil | Tag `05`, 1 byte |
| 5 | T | Target player control object | Control tag `06` plus resolved binding-reference u32 big-endian, 5 bytes total |
| 6 | nil | Explicit nil | Tag `05`, 1 byte |
| 7 | nil | Explicit nil | Tag `05`, 1 byte |
| 8 | nil | Explicit nil | Tag `05`, 1 byte |
| 9 | nil | Absent connector argument becomes explicit nil | Tag `05`, 1 byte |

T originates in the widget's argument actor. The connector preserves it when
nonnull and `_isAlive()` is not exactly false; otherwise it substitutes the
current target (`desktopwidget_connector.lua:13648-13660`). The command
predicate below then checks the target actually supplied to it. This is a
control-object domain, not a raw numeric actor ID or an ItemBase reference.

S is the slot selector itself. The caller does not serialize the item returned
by `_getEquippingItem`, nor its native package key `0xFE`. The established
[equipped-item lookup](scheduler-item-native-contract.md#item-packages)
uses 1-based Lua slots; it is a lookup contract, not an extra operand here.
No material, package, commission, price or quantity operand is authored by
these callers.

`slotNameToEquipSlotNum` gives the individual submitting button domain
(`repairequipmentwidget.lua:1823-1885`):

| Button suffix after `Button_` | S |
| --- | ---: |
| PrimaryArm | 1 |
| SecondaryArm | 2 |
| Head | 9 |
| Body | 11 |
| Hands | 14 |
| Waist | 16 |
| Legs | 13 |
| Feet | 15 |
| Accessories_RightEar | 18 |
| Accessories_Neck | 17 |
| Accessories_RightFinger_1 | 22 |
| Accessories_RightBracelet | 20 |
| Accessories_LeftFinger_1 | 23 |

ThrowingWeapon 5, LargePouch 6, SmallPouch 7, Undershirt 10 and Undergarment
12 are mapped but explicitly refused by Operate with alert 40272. Unknown
button names map to zero and return. RepairAll instead sets S to 27 for
target `getRepairType()` 1, 2 or 3; otherwise S stays zero. These are authored
UI values, not an exhaustive server admission range.

## Admission and local result

`RepairEquipmentsCommand.canFire` requires source `isPlayer()` and
`isMyPlayer()` truthy, a nonnil different player target whose `_isAlive()`
is not exactly false, source and target `isLiving()` not exactly false, and
source `isActiveMode()` not exactly true. It requires operand 1's type to be
`number` and rejects values below 1. It has no upper-bound or integral-value
check (`command/system/repairequipmentscommand.lua:11-85`). The widget's
actual submitted scalar values are the integers above.

Operate also returns while `firsttime == true` and while `lastcommand` is at
least the current server time. The individual-slot path requires a nonnil
widget argument actor. Its item-present, repairability, condition, repair-skill
and repair-level comparisons all converge before the command call: they do
not block submission. Original LPB control flow establishes this despite
the decompiler's empty branches (`repairequipmentwidget.lua:1888-2024`).

The connector returns the local `PlayerBaseClass.command` result. On exactly
false, the SystemCommand route invokes `alertCommandError`; for a still-alive
24244 command it emits alert 32708 with the command ID as context
(`desktopwidget_connector.lua:13674-13732,14427-14469`). Early missing/invalid
command checks return false before this alert. Operate records current server
time in `lastcommand` only on exactly true. It does not close the UI, change
condition or wait for a named repair reply on that branch.

## Conditional transport and completion boundary

The existing [command descriptor contract](command-descriptor-registration.md)
and `manifests/command_descriptor_registration.json`, named `commandContent`
record, establish priority input 4, selector 0 and conditional CommandBlock
construction when the selector global is zero. The selected runtime descriptor
at VA `0x0071CA50`, from player `+0xFC`, remains unobserved.

If the block route is selected, `PlayerBaseClass._onCommandEvent` forwards
the complete operands to `_callServerOnCommand`
(`playerbaseclass.lua:1820-1840`). The
[native wire contract](player-command-wire-contract.md) and
`manifests/player_command_wire_contract.json` own the authenticated fallback
through `0x006E2FB0`, serializer `0x00790ED0` and serverbound `0x012D`
builder `0x00776760`. Its typed tail for these values is:

```text
I(S) N N N A(T) N N N N E
```

I is `00` plus u32 big-endian, N is `05`, A is `06` plus the resolved control
binding reference, and E is `0F`, followed by tail padding. The envelope uses
the event name and command object's reference; scalar 24244 is not inserted
into this tail. The shared contract's binding-reference domain, endian state,
queue gates and descriptor-selection limits apply. This is conditional
construction evidence, not a retained 24244 socket exchange.

`RepairEquipmentsCommand.processResultRepair` is empty
(`repairequipmentscommand.lua:88-91`). Its existence does not establish a
server dispatch to it. The ordinary equipment-update route is separate:
DesktopWidget forwards actor, package selector and slots to the open repair
widget; the widget accepts only its argument actor and package selector -1,
rereads `_getEquippingItem(slot)` and refreshes presentation
(`desktopwidget_connector.lua:5914-5929`;
`repairequipmentwidget.lua:1314-1715`). That generic update has no causal
24244 completion identifier.

The remaining joins are the selected runtime command descriptor, an incoming
repair-specific result dispatch or demonstrated alternative completion route,
and a transaction tying that command's target/slot to durability, material,
reward and refusal changes. Neither local true nor an ordinary item refresh
proves those joins. The NPC and self-repair findings remain in the
[repair contract](repair-contract.md).

## Source identity and original instruction checks

Lua sources matched `xivl-client-scripts:manifests/scripts.json` and original
LPB/payload identities matched `manifests/retail_lua_coverage.json` at revision
`0badc824adb353ca36ea41a61ee255a92a3231e2`. The Lua archive matched
`manifests/private_lua_corpus.json`: 14385427 bytes, SHA-256
`0e8f902f7a2f592fc1220d41b89a3f35ec395cfb261806d4bd590a530099ae31`.
All Lua paths above are relative to that repository's `lua/scripts/`.

| Selected source | Bytes | SHA-256 |
| --- | ---: | --- |
| `widget/repairequipmentwidget.lua` | 62583 | `eb2dc988cdcd31d69c1e4fed6e23b00cb287c9bbb64574872d138766408594b7` |
| `command/system/repairequipmentscommand.lua` | 1684 | `83cf65826c18c3c405f92195d624268218179f86b7e99d0c9a6f0a7296463e2d` |
| `widget/desktopwidget_connector.lua` | 660617 | `9c33f21c1f70a0056147e716d53300634efabe5b744ef6e8690114db21613a01` |
| `chara/player/playerbaseclass.lua` | 66466 | `6226b3fa15dfdbad279b7dba453f8a3b76fcb8b68bad6e14f5403d52987f76e4` |

The widget LPB `n1635q/s5u91s5tp1ux5wqn1635q.le.lpb` is 24728 bytes,
SHA-256 `5042ab1e0e23fe322ff3c608c78ee6430a13b0b1e5b6e7f3dddc7a31f03e3a17`.
Its decoded payload SHA-256 is
`159e2e26ea2fed1693698fddd75a17f5911c22909f4d84727edd171f9e96cadb`.
The command LPB `7vxx9w6/rlrq5x/s5u91s5tp1ux5wqr7vxx9w6.le.lpb`
is 743 bytes, SHA-256
`044692ef626cce36a7a652c505600138775e9347f07f2966867ac4e4e40fd080`.
Its payload SHA-256 is
`23192720bdd235bc089162c096780bfc87f675bf290555802c7a183edb737c62`.
`tools/retail_script.py:decode_lpb` and
`tools/build_quest_contracts.py:ChunkReader` supplied the following observations.
PCs are zero-based and offsets refer to decoded payloads.

| Observation | Original bytecode locator |
| --- | --- |
| RepairAll and individual issuer calls | Widget `root/proto29`, code `0x47CB`, CALL PC 48 at `0x488B` and PC 129 at `0x49CF`, both B=8,C=2 |
| Individual comparisons converge before submission | Same prototype, PCs 94-122 all reach PC 123 |
| Nine operands after command actor | Connector `root/proto278`, CALL PC 43 at `0x1EB06`, B=12,C=2 |
| Block callback preserves complete varargs | PlayerBase `root/proto42`, VARARG PC 14 and CALL PC 15 with open arity |
| Empty repair result method | Command `root/proto1`, code `0x2B6`, single RETURN A=0,B=1 |

The data revision is
`f4bd2734570441a3721f460b85681435040b2724`. Its CSV archive matched
`manifests/private_csv_corpus.json`: 70110686 bytes, SHA-256
`006f9438a8cfd9277376f0ab28474500c67e4665050aa631cae64c9e6f38a5b0`.
`manifests/tables.json` pins `csv/command.csv`, 126638 bytes, SHA-256
`14548e379a6c4f76c10a4ac53866161ebf1622ce7f1e76a760e85f0577f38848`.
The numeric header identifies priority column 29; row 24244 is CSV line 819.
The staticactor SAN matched its retail input manifest: 108911 bytes, SHA-256
`bb7306461b1728493242016a16d9dd5257d7512c60e423b017de5ec7aced3d14`.
In-memory `tools/extract_staticactor_san.py:parse_san` output equaled the
tracked class-path records, including 24244.

Native transport facts are reused from the linked promoted contracts at
`xivl-client-structs` revision `24be660305d3f027aacba708c73b11a50c9261ed`.
Their source is retail 1.23b `ffxivgame.exe`, 15996808 bytes, image base
`0x00400000`, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
They retain the producing Ghidra/PE observations and do not claim an observed
24244 runtime dispatch.
