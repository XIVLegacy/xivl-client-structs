# Client architecture

Use these findings to interpret the Final Fantasy XIV 1.23b client from the
tracked catalog and direct analysis of client build 2012.09.19.0001. Each
section names its client, capture, runtime, or repository evidence. Catalog
claims use `BCS-Y` and `BCS-S` entries from
`manifests/symbols.json` and `manifests/structs.json`. See
[`ir-schema.md`](ir-schema.md) for how those entries join into the generated IR and
[`manifests/README.md`](../manifests/README.md) for the BCS-Y (Receiver-name)
versus BCS-S (Packet-name) naming boundary applied throughout.

## Wire dispatch

### S2C dispatch has five architectural patterns, not one uniform receiver registry

The synchronous zone-tick s2c path enters through the central dispatcher
`FUN_004DC690` (BCS-Y-0279, 3364 bytes), whose sole caller is the Map tick
handler `FUN_004E20A0` (BCS-Y-0314) - s2c dispatch happens on the main-thread
tick, not asynchronously. It reads the opcode at `*(short *)(packet + 2)` and
routes through a two-branch switch (high branch: opcodes `0x13E..0x1A8`; low
branch: opcodes `0x02..0x12D`) into five distinct dispatch patterns:

- **Pattern A - `*Receiver` classes.** Dozens of opcodes route to a
  `Network::<Name>Receiver` class whose `vtable[1]` is the `Receive` method,
  each an RTTI-confirmed type (event-shaped packets: KickEvent,
  ChangeActorXxxStat, scene events).
- **Pattern B - Element `vtable[9]`/`vtable[8]` dual dispatch.** The documented
  synchronous and asynchronous tables contain 24 and 50 cases, respectively. They resolve
  the actor via `FUN_004d9910` and call `actor->vftable[9]` for the
  synchronous tier. The actor type stored in the zone's actor map is
  `Application::Main::RaptureElement` (BCS-Y-0539, vftable 0x00F91014 +
  secondary 0x00F91138) - not `Application::Scene::Actor::*` or a Lua
  control class. There are 23 `Element` classes (1 base `RaptureElement` + 22
  derived: DaemonElement, RelativeElement, XamlElement, FormElement,
  ClientWorkElement, CustomControlElement, BootupElement, CameraElement,
  CommonResourceElement, GameManagerElement, ScreenshotManagerElement,
  CutManagerElement, MainElement, TargetElement, CharaElement,
  MapLayoutElement, SqwtElement, WidgetElement, EffectElement,
  EffectDebugElement, LightElement, DebugInfoElement). Two classes have
  large per-class sync handlers: `CharaElement::vftable[9]` = `FUN_0058CCA0`
  (BCS-Y-0540, 2563 bytes, 41 opcodes) and
  `MapLayoutElement::vftable[9]` = `FUN_0059CED0` (BCS-Y-0541, 272 bytes, 5
  opcodes). The other 20 derived classes share
  `FUN_004d8860` (BCS-Y-0280, 864 bytes, 24 cases).

  A parallel **async tier** runs on `vtable[8]` (not 9), fed by a lock-free
  `Sqex::Thread::Queue<MainPacket>` (BCS-S-0048) hosted in
  `Application::Main::MainModule` at `+0x17928` (MainPacket is the 0x60-byte
  entry, BCS-S-0049). Game logic - not s2c
  traffic - is the producer: `FUN_007CE7B0` (65+ call sites) builds a
  MainPacket with `event_type = opcode + 3` and enqueues it. The next frame
  `FUN_004DAA10` (BCS-Y-0537) drains the queue, subtracts 3, and calls
  `actor->vtable[8](opcode, payload, length)`. Of the 23 Element classes'
  secondary-vtable slot 8, 10 have per-class opcode-switch dispatchers (for
  example `CharaElement`'s async dispatcher `FUN_0058E0C0`, 17 cases,
  0x4A..0x64) and 13 default to a 3-byte no-op
  (`FUN_00A72A20`). The async tier is the engine's per-frame internal event
  bus, not a second packet-handling tier.
- **Pattern C - dedicated case handlers.** 14 low-switch cases run bespoke
  logic: `0x02` peer init, `0x03` string command, `0x04` complex re-init,
  `0x06` simple call, `0x07` tick-style walk (also emits c2s `0x00CA` as
  periodic sync via `FUN_004E0240`), `0x08..0x0B` position/vector arrays,
  `0x0C` scalar pair, `0x0E`/`0x11` shutdown, `0x00CA` AddActor,
  `0x00CB` RemoveActor (`vftable[0](1)` destroy), `0x05`/`0x0D`/`0x10`
  fallthrough to `vftable[9]` on a session-level object at
  `param_1 + 0x4e0`.
- **Pattern D - sub-dispatchers.** `FUN_004D8860` (BCS-Y-0280) and siblings
  reachable from `FUN_004DC690`'s case bodies route a further layer of
  opcodes.
- **Pattern E - unrouted observed opcodes.** Some pcap-observed s2c opcodes
  have no case in any documented dispatcher: `0x0147` InventorySetEndPacket,
  `0x00D2` (33 pcap hits). Their routes are unresolved in this model.

Refs: `manifests/receiver_discovery.json`, `manifests/actor_cluster_dispatch_model.json`,
and `manifests/operation_opcode_map_outbound.json`. BCS-Y-0279, BCS-Y-0280, BCS-Y-0314,
BCS-Y-0321, BCS-Y-0525..BCS-Y-0527, BCS-Y-0535..BCS-Y-0541,
BCS-Y-0612..BCS-Y-0613, BCS-Y-0838; BCS-Y-0791 (Element class enumeration, 23 total;
multiple-inheritance secondary vtables are not distinct classes).

### Two independent s2c dispatch paths converge on the LuaActorImpl vtable

The client runs a second, independent inbound path parallel to the sync
zone-tick path above. On the network thread, per-channel `PacketBufferBase`
accumulators (one per Lobby/Zone/Chat) frame bytes into 0x238-byte packet
objects and drain them via `FUN_00DB6140` (BCS-Y-1035), dispatching each
through `FUN_00DB5300` (BCS-Y-1034) - a `std::map<uint, Handler*>` keyed on
the segment-header `target` field, using MSVC red-black-tree helpers
`FUN_004E4B40`/`FUN_004E4BA0`. This registry is structurally orthogonal to
`FUN_004DC690`'s switch tables and runs on a different thread. This evidence
does not establish whether the two opcode sets overlap.

Both paths converge at `LuaActorImpl::vftable` (BCS-Y-0092, 90 slots,
0x00FDFB2C..0x00FDFC94). Three independent slot identifications confirm
this is a single vtable indexed by ordinal, not a second opcode-keyed
dispatch table: slot 21 `onTouch` (BCS-Y-0203), slot 25 `onTargetChanged`
(BCS-Y-0156), slot 59 `onReceiveDataPacket` (BCS-Y-0152, reached from the
sync path's case `0x133` trampoline `FUN_00575060` BCS-Y-0595, whose body is
exactly `(*(*param_1+0xEC))()`).

Refs: BCS-Y-1034, BCS-Y-1035, BCS-Y-1036 (catalogued redundant with
BCS-Y-0092), BCS-Y-0092, BCS-Y-0152, BCS-Y-0156, BCS-Y-0203, BCS-Y-0279,
BCS-Y-0314, BCS-Y-0535, BCS-Y-0536, BCS-Y-0595, BCS-Y-0280.

### The C++/Lua bridge dispatch chain is a single 6-layer pipeline

For Pattern B opcodes whose handler terminates inside a `*Receiver` Lua-side
class (for example s2c `0x016B` `SetNoticeEventConditionReceiver`, `0x016C`
`SetEmoteEventConditionReceiver`), dispatch from wire arrival to the
Receiver's `Receive` method crosses the C++/Lua boundary through 6 stacked
layers, all on one continuous chain (not two parallel paths):

| Layer | Function | BCS-Y | Role |
|---:|---|---|---|
| 1 | `FUN_004DC690` case `0x16B`/`0x16C` | BCS-Y-0279, BCS-Y-0527 | wire arrival, falls to `actor->vftable[9]` |
| 2 | `CharaElement::vftable[9]` = `FUN_0058CCA0` | BCS-Y-0540 | per-Element sync handler; opcode not in its table, falls to default |
| 3 | `FUN_004D8860` sub-dispatcher | BCS-Y-0280 | 24-case default-branch router |
| 4 | `FUN_00574FE0`/`FUN_00574FF0` bridge trampoline | BCS-Y-0548, BCS-Y-0549 | reads `LuaActorImpl*` at `actor+0x88`, indexes vtable slot 51/52 |
| 5 | `LuaActorImpl::vftable[51]`/`[52]` | (slot indirection) | virtual call into the actor's Lua-side subclass |
| 6 | `SetNoticeEventConditionReceiver::slot1` / `SetEmoteEventConditionReceiver::slot1` | BCS-Y-0734, BCS-Y-0736 | `RTDynamicCast` (ActorBase -> DirectorBase), routes to registration helpers |

`BCS-Y-0734` and `BCS-Y-0736` have zero direct callers anywhere in the
binary - they are exclusively virtual dispatch targets. This generalizes: a
static call-graph search from any `*Receiver::slot1` method returns empty,
because the receiver-class registry is wired into the runtime via C++
multiple-inheritance vtable slots, not direct calls. Finding the caller
means finding which trampoline reads the actor's `LuaActorImpl` vtable slot.

Refs: `manifests/0x16b_0x16c_dual_path_resolution.json`. BCS-Y-0279,
BCS-Y-0280, BCS-Y-0527, BCS-Y-0540, BCS-Y-0548, BCS-Y-0549, BCS-Y-0734,
BCS-Y-0736.

### The per-actor rebuild transaction: s2c 0x00CA opens, only 0x00CC closes it

`FUN_004DC690` case `0xCA` (BCS-Y-0525) looks up or creates the actor,
writes `actor+0x92 = 1` (a `RaptureElement` byte zeroed by the ctor
`FUN_004DAB50`, BCS-Y-0539), and calls `FUN_004CAF60` (BCS-Y-1835). While
`+0x92` is set, `CharaElement::vftable[9]`'s entry predicate
`FUN_004D8830` (BCS-Y-1836) returns false unless the opcode is on a fixed
whitelist (`0x000F`, `0x00CC`, `0x00E2`, `0x00E3`, `0x0134`, `0x0137`,
`0x0144`, `0x0145`, `0x0197`, `0x01A0`, and `0x00CE` only when
`*(int*)(packet+0x14) == -1`). Every other opcode routed to that actor is
silently dropped, including `0x017B` SetActorIsZoning, `0x00CD`, `0x00D0`,
`0x00D6`, `0x012E..0x0133`, `0x013D`, `0x0157..0x016A`, `0x018E`, `0x0192`,
`0x0195`, `0x01A6`, `0x01A8`. Only `0x00CC` clears `+0x92`: inside
`FUN_004D8860` (BCS-Y-0280) the same predicate selects a branch that accepts
opcode `0xCC` alone, runs `FUN_00575860` (BCS-Y-0613 -> `FUN_00764630`
BCS-Y-1020), and unconditionally zeroes `+0x92`. `0x00CA`/`0x00CC` therefore
bracket a per-actor rebuild transaction: packets sent between them are
deliberately discarded because the closing `0x00CC` carries the full,
authoritative actor record (`FUN_00774AD0`, BCS-Y-0588/BCS-Y-1019) anyway.

The two cited retail captures pair the bracket: s2c `0x00CA` and s2c
`0x00CC` occur in a 1:1 ratio in `xivl-captures:sources/pcap-1.23b/objects/moving_around_gridania.pcapng`
(281:281) and `from_gridania_to_blackshroud.pcapng` (27:27). A self `0x00CA`
sent without a matching self `0x00CC` parks the client's own actor in a
permanently packet-deaf state until relog rebuilds it through the
zeroing ctor.

Refs: [xivl-captures:derived/payload_layouts.json](https://github.com/XIVLegacy/xivl-captures/blob/main/derived/payload_layouts.json); `xivl-captures:sources/pcap-1.23b/objects/moving_around_gridania.pcapng`,
`from_gridania_to_blackshroud.pcapng` (via [xivl-captures:tools/extractors/extract_streams.py](https://github.com/XIVLegacy/xivl-captures/blob/main/tools/extractors/extract_streams.py)).
BCS-Y-0279, BCS-Y-0280, BCS-Y-0525, BCS-Y-0539, BCS-Y-0540, BCS-Y-0588,
BCS-Y-0612, BCS-Y-0613, BCS-Y-1019, BCS-Y-1020, BCS-Y-1071,
BCS-Y-1834..BCS-Y-1837.

## Command intent and state model

### 1.x combat is asymmetric between s2c display and c2s intent

The s2c display side uses dedicated `CommandResult*` opcodes (`0x0139..0x013C`,
four shape variants for 0/1/10/18 targets). The c2s intent side rides the
generic `EventStartPacket` `0x012D` frame, with combat semantics carried by
`eventName` and `luaParams` rather than a dedicated combat opcode. The
`CharaActionController` RTTI (BCS-Y-0055) is a receive-side
playback/queue class, not a c2s emitter. The `0x012D` builder is
`FUN_00776760` (BCS-Y-0426); its payload layout is BCS-S-0034
`MapEventStartPayload`. Send chain: `FUN_0075E230`/`FUN_0075E1C0`+`FUN_0089E0D0`
-> `FUN_00776760` -> `FUN_004D6D30` (zone gate) -> `FUN_004E0240` (forwarder)
-> `FUN_00DAE010` (terminal). Any combat-side server work should expect to
extract command semantics from the EventStart payload's `eventName`/`luaParams`
rather than looking for a per-action opcode.

Refs: `manifests/combat_action_c2s_findings.json`.
BCS-Y-0426..BCS-Y-0434; BCS-S-0034.

### Surveyed Lua N-API setters remain client-local

Surveyed Lua N-API setters stay local to the client and never emit c2s packets:

| Setter | Local write target | Server-visible mirror | BCS-Y |
|---|---|---|---|
| `_setActorExtraStat` | `CharaSubStatStorage+0x10` low byte via `FUN_006FA980` (BCS-Y-0349); fires `_onChangeNetStatUser`/`_onChangeNetStatSystem` | s2c `0x0145` ChangeActorExtraStat (inbound) | BCS-Y-0442 |
| `_setVisible` | scene packet ids `0x10`/`0x11` (local scene state) | none observed | n/a |
| `_setGroundOn` | record `0x12` -> scene packet `0x27` | none observed | n/a |
| `_setSubStatStatus` | empty Lua stub; no native N-API registration | n/a | n/a |

No path from these setters reaches the EventStart `0x012D` builder or any
other c2s emitter. The observed state synchronization is inbound through s2c
`0x0144` ChangeActorSubStatModeBorder, `0x0145` ChangeActorExtraStat, and
`0x0179` ChangeActorSubStatStatus. The c2s evidence here covers command intent,
not server retransmission behavior.
`_setSubStatStatus` demonstrates that not every advertised Lua name has a
native binding wired up.

Refs: `manifests/lua_napi_c2s_trace_findings.json`,
`manifests/lua_napi_c2s_survey_findings.json`. BCS-Y-0349, BCS-Y-0442.

### s2c state-push receivers do not gate on Group::SharedWork registration

The `Group::SharedWork` member lookup is a single funnel:
`FUN_006C97A0` (BCS-Y-1792) is the only lookup-or-create accessor, calling
`FUN_006C8AC0` (BCS-Y-1793, find) and `FUN_006C8C20` (BCS-Y-1794,
create-if-absent). All 6 callers of `FUN_006C97A0` are in the SharedWork
`vftable` slot-22 property-copy family (`FUN_006C9930` BCS-Y-1796 + 5
siblings) - covering all 38 receivers at once. No s2c state-push receiver
consults the SharedWork member lookup: general receivers (`UserDataReceiver::apply`
at `0x0133`, BCS-Y-1665; `SetTalkEventConditionReceiver::apply` at `0x012E`)
apply against their own payload and an RTTI-cast of the actor object handed
to them directly. SharedWork gating is confined to the Group property-sync
opcodes themselves: `0x017A` SynchGroupWorkValues (BCS-Y-1795/BCS-Y-0873),
`0x0187` SetOccupancyGroup (BCS-Y-0885), and `0x018B` SetGroupLayoutId.

Refs: `manifests/sharedwork_gate_audit.json`,
`manifests/receiver_opcode_map_inbound.json`. BCS-Y-0873, BCS-Y-0885,
BCS-Y-1665, BCS-Y-1792..BCS-Y-1796.

## Zone actor binding and Lua class readiness

A single causal chain runs from the Group spawn burst to loading-screen
dismissal. Each stage gates the next.

**Group spawn-burst completion (ring drain).** `Group::PacketProcessor::OnPacket`
(`FUN_006CDE30`, BCS-Y-1056, vtable slot 1) latches `+0xe8` (sub-decoder 1 at
`this+0x40`) and `+0xe9` (sub-decoder 2 at `this+0x94`) independently per
packet via buffer-equality compares (`FUN_00445D20`). The ring-buffer drain
(`FUN_006CDA80`) fires only when both are set. The 0x17C header handler
`FUN_00576250` (BCS-Y-0564) forwards into `FUN_006CC620` (BCS-Y-0874), which
on first hit performs one-time instance init (magic tag `0x2711` at
`packet+0x30`) and thereafter tail-calls the per-packet processor
`FUN_006cc070`. On a drain, `FUN_006CD8E0` (dispose-chain orchestrator) runs
an unconditional teardown that routes on the (old, new) state pair via
`FUN_006DB9A0`: ADD emits c2s `0x0133` GroupCreated (56 bytes,
`FUN_0075E950`, BCS-Y-0984, gated by `FUN_004D6D30` BCS-Y-0983) through
`FUN_006C8CF0` (84-byte actor alloc) and `FUN_006C72E0` (GroupStateAggregator,
BCS-Y-0985); two further conditional emits in the same teardown
(`FUN_006DAE90`, `FUN_006DACD0`) each fire c2s `0x0130` (32 bytes,
`FUN_0075E860`, sibling of BCS-Y-0329). For a spawn ADD transition, the
three emits produce exactly 2x c2s `0x0130` + 1x c2s `0x0133`. The
capture-derived manifest records (`manifests/pcap_opcode_evidence.json`:
c2s `0x0133` count=5, subpacket size 72 bytes = 56-byte body + 16-byte
header). This ACK triple is an emit-side effect of the client's own
ring-drain, not a sequencing token the server must wait on. If the
spawn-burst is structurally incomplete (a `0x17D` MembersBegin without a
matching `0x17E` MembersEnd, or a sequenceId mismatch), the ring never
drains and the actor never registers.

**Lua-bound readiness flag, `actor+0x5C`.** A one-byte flag on
`Application::Lua::Script::Client::Control::*` objects (actors and UI
widgets alike) meaning "this object's `LuaActorImpl` is installed / the
object is Lua-bound." Zero-initialized by the `ActorBase` ctor
`FUN_006DBB70` (BCS-Y-1710). Set to 1 by the per-frame actor-list installer
`FUN_00766F00` (BCS-Y-0135), gated on the owning actor-list reaching state
`+0x16C == 10` and on the validity predicate below. Consumers gate on it
directly: `KickClientOrderEventReceiver::Receive` (BCS-Y-0724)
short-circuits when `actor+0x5C == 0`; the preWarp engine gate `FUN_008A4410`
(BCS-Y-1789) fires `_onPreWarp` only if the widget's `+0x5C != 0`.

**Bind state machine, `+0x16C` on the container.** `FUN_007663D0`
(BCS-Y-1799) is a switch on the *container* object's `+0x16C` field (the
container is `InitializeWaitingActorContainer`, vftable `0x00FE0478`, ctor
`FUN_00773A30` BCS-Y-1802; the field is container-level, not
per-record): register `Debug` class (0->1), register
`WorldMaster` class (1->2), a native check (2->3), CommandDebugger
GM/DEV/TEST class loads (3/5->5/7/4), load the `/Area/` resource by name
compare via `FUN_00712BB0` (BCS-Y-1800) (7->8), match the pushed record's id
against the MyPlayer SID `0xC0000024` via `FUN_00CC9320` (BCS-Y-1801)
(8->9), match the container's paired handle at `+0x170` (9->10, terminal).

**The unifying validity gate, `+0x7d`.** `FUN_00CC72A0` (BCS-Y-1803, 19
callers) reads byte `+0x7d` off the object returned by the universal
handle-to-object resolver `FUN_00CD7A30` (BCS-Y-1581). This single predicate
gates both the `+0x16C` bind-state advance from 9 to 10 (a pre-switch
validation block, distinct from the case-9 handle compare) and the
`actor+0x5C = 1` install in `FUN_00766F00` - the two gates described above
are the same gate, not two independent ones. `+0x7d` lives on a lazy,
Lua class binding keyed by name with a flag cluster: `+0xc` = resolved
class object, `+0x7d` = VALID (class is defined), `+0x7e` = TENTATIVE
(named but undefined), `+0x7f` = active, `+0x80` = set on promotion. The
writer is `FUN_00CE1DD0` (BCS-Y-1805); the tentative-setter is `FUN_00CE2880`
(BCS-Y-1807, sets `+0x7e=1` when `FUN_00CD8870(name, create=0)` finds
nothing); the promoter is `FUN_00CD9360` (BCS-Y-1806), the Lua
class definition registrar, which uses names as keys - defining a class promotes
any pre-existing tentative entry of that name.

**The observed class definition path is driven by `require()`.**
The boot chunk redefines `require(name)` to call `_luaGameEngineRequire`
(`FUN_00D08A10`, BCS-Y-1809) -> file lookup `FUN_00D0CFB0` (BCS-Y-1811,
retries with `.lpb`) -> `_luaGameEngineLoad` (`FUN_00D08180`, BCS-Y-1810) ->
`luaL_loadbuffer` (`FUN_00CF4680`, BCS-Y-1812) -> run the chunk under a
guarded `pcall`. Running the chunk executes its top-level `_defineClass`,
reaching the promoter above. `FUN_00D08A10` has only a data cross-reference
(registered as a Lua C function by the boot registrar `FUN_00CD8990`,
BCS-Y-1813). Static references show Lua `require()` dispatch from bytecode
but do not exclude unresolved indirect callers. An actor
created via `_createActor(className, ...)` (dispatched through vtable slot
`0x6c`) requires its class to already be defined - creation binds a name, it
does not load the class.

**Class hierarchy is a 2-layer build.** `FUN_0078eb70` (BCS-Y-1819)
registers exactly 57 native base-class path literals in the binary (for
example `/Area/Zone/ZoneBaseClass`, `/Chara/Npc/NpcBaseClass`,
`/Chara/Player/PlayerBaseClass`, `/World/WorldMaster`,
`/GameData/SpreadSheet`) via `FUN_00447260`; the full indexed list is
`manifests/client_class_registry.json`. Every concrete leaf class
(zone masters, populace variants, directors) is defined at runtime by Lua
`_defineClass(child, parent)` from the LPB script corpus (2435
`_defineClass` reference sites) - none of these leaf class names exist as
string literals in the binary. The player's class is a core class
`require`d by the login/world bootstrap, so it is always defined by the
time its control is created. A content class (for example the opening
sequence's `OpeningDirector`, extending `DirectorBaseClass`) is `require`d
only when the content flow that uses it runs. Spawning the actor
(`AddActor` + `ActorInstantiate`) creates the control and a tentative class
reference but does not itself `require` the class. If nothing ever
`require`s that class during a given client session, its `+0x7d` stays 0
forever, the actor never becomes Lua-bound, and any Lua callback gated on
`+0x5C` (including the `_onPreWarp`/`_onPostWarp` -> `_fadeOut` dismiss
cascade) never fires.

`FUN_0055d2b0` (BCS-Y-1820) observes numeric-column reads for
`actorclass_graphic`, but no tracked artifact identifies the id-to-classPath
or zone-id-to-internal-name string bindings.

Refs: `manifests/sharedwork_gate_audit.json`,
`manifests/actor_5c_readiness_gate.json`,
`manifests/actor_16c_bind_state_machine.json`,
`manifests/bind_state_stall_resolution.json`,
`manifests/director_tentative_class.json`,
`manifests/director_class_load_trigger.json`,
`manifests/seed_classpath_audit.json`,
`manifests/client_class_registry.json`. BCS-Y-0135, BCS-Y-0724, BCS-Y-0873,
BCS-Y-0983..BCS-Y-0985, BCS-Y-1019, BCS-Y-1020, BCS-Y-1056, BCS-Y-1557,
BCS-Y-1576, BCS-Y-1581, BCS-Y-1665, BCS-Y-1701, BCS-Y-1710, BCS-Y-1711,
BCS-Y-1789, BCS-Y-1792..BCS-Y-1813, BCS-Y-1819, BCS-Y-1820,
BCS-Y-1834..BCS-Y-1837.

## Environment and movement subsystems

### SetDalamud s2c 0x0010 selects one of eight scene states

`FUN_004DC690` case `0x10` routes to the zone environment manager
(`MapLayoutElement`, `vftable[9]` = `FUN_0059CED0`, BCS-Y-0541), which stores
the received unsigned byte at `+0xf0` (default `0xFFFFFFFF` = "nothing
pending", set by ctor `FUN_0059EE50`). On the next `MapLayoutElement` tick
(`vftable[6]` = `FUN_0059EBA0`), `FUN_0059CA60` fans the level out to 8
mutually-exclusive scene records (id `0x93` = posted type `0x7E` + `0x15`,
via `FUN_004D7980`/`FUN_004EC080`) - enabling the index equal to the
received level and disabling the other seven - then resets `+0xf0` to `-1`.
The fan-out is one-shot per packet. Values `8..255` pass the `>= 0` gate but
match no index, so they disable all eight ("hide everything"). Weather
(s2c `0x000D`) is a fully independent path: `+0xbb` dirty + `+0xb0`/`+0xb4`
-> `FUN_0059E4D0` -> scene record `0x21`, never touching `+0xf0` - no
weather id can drive the eight-state selector.

`_getHydaelynMoon` (registrar `FUN_00752F30`, impl `FUN_00707C00`) is a
separate path: its body is a pure `(clock / 0x1068 & 0x1f) + 4 >> 2` time-derived
8-phase value feeding `MoonPhaseIconControl`, unrelated to `+0xf0`.

Refs: [xivl-captures:derived/payload_layouts.json](https://github.com/XIVLegacy/xivl-captures/blob/main/derived/payload_layouts.json) (s2c 0x0010).
Vftable: `Application::Main::Element::Map::MapLayoutElement::vftable` at
0x00FAAD88. BCS-Y-0279, BCS-Y-0541, BCS-Y-0661.

### Auto-run is client-only movement state, cancelled by per-frame geometry only

The local player's auto-run flag is bit 3 (`0x08`) of the dword at `+0x04`
of the CharaActor motion controller
(`Application::Scene::Actor::Chara::CharaActor`, vftable 0x00FC0D34,
BCS-Y-1846; `CharaActor+0x169` is the companion latch byte and `+0x168`
the separate walk/run move mode) - Scene-layer state, not Element-layer
state - read by
`FUN_007A4610` (BCS-Y-1839) and written only by `FUN_007B04A0`
(BCS-Y-1840). There is no wire field and no s2c opcode carrying it.
`RaptureCommands.MoveCharacterAutoRun` reaches the CharaElement input
listener `FUN_00589490` (BCS-Y-1838), which raises scene op `0x20` through
`FUN_004D7980` (BCS-Y-1083); delivery crosses `Sqex::Thread::Queue<ScenePacket>`
to the Scene-layer dispatcher `FUN_007C93C0` (BCS-Y-1845), landing on
`FUN_00662D30` (BCS-Y-0838, case `0x20`) - a sixth, client-internal,
input-sourced dispatch fabric distinct from the wire-side patterns above.
`FUN_007B04A0` has exactly three callers: the keybind handler
(`FUN_00662D30`), the camera-relative move-input handler (`FUN_00618CB0`,
BCS-Y-1842, clears on a null stick vector), and the per-frame movement
update `FUN_00665220` (BCS-Y-1841). The cancel in the movement update is
purely geometric: auto-run survives only while direction-cosine terms stay
within thresholds read from `.rdata` (`0.8`, `0.7`, `-0.7`) against the
frame's movement vector. Static reachability from
every s2c packet-apply function to all four functions adjacent to auto-run
returns no path. Enumerating all 190 `FUN_004D7980` call sites by pushed op
id shows scene op `0x20` is raised from exactly one address in the binary
(the keybind handler). No packet handler can cancel or set auto-run other
than the zone-teardown paths forcing it on (op `0x22`) during a full
zone unload - not an in-place seam crossing.

Refs: field scan over displacement `0x168`/`0x169`; reachability via
`build/callgraph.json`. BCS-Y-0808, BCS-Y-0838, BCS-Y-1083,
BCS-Y-1838..BCS-Y-1846.

## Lua coroutines and deferred execution

### Deferred event execution uses native C++ state machines, not Lua coroutines

The deferred event-condition path fires Lua callbacks (`_onPreEvent`,
`_onPostEvent`, `_onTalkEvent`, `_onPushEvent`, etc.) via native C++ state
machines: `FUN_00897310` (block events) and `FUN_008955C0` (non-block queue
walker), holding current/continuation pointers at owner `+0x08`/`+0x0c`.
The handoff store is a two-slot 0x54-stride callback table (BCS-S-0037
`EventConditionCallbackSlot`); non-block events use 0x2c list nodes
(BCS-S-0038 `EventExecutionQueueNode`) at owner `+0x14`.

Stock Lua 5.1 coroutine bodies do exist in the binary: `FUN_00DCFD30`
(`lua_resume`, anchored by the `cannot resume` diagnostic) and
`FUN_00DCF7D0` (`lua_yield`, anchored by the `attempt to yield across
metamethod/C-call boundary` diagnostic); client wrappers are BCS-Y-0477 and
BCS-Y-0478, with a shared internal Call-or-Resume helper BCS-Y-0482. So
coroutines exist in the binary. They are not the mechanism behind deferred
event continuation. Their observed uses are described below.

Refs: `manifests/deferred_scheduler_findings.json`,
`manifests/negatives_verification_findings.json`. BCS-Y-0470..BCS-Y-0478,
BCS-Y-0482;
BCS-S-0037, BCS-S-0038.

### The Lua coroutine consumer surface is fully attributed to three mechanisms

Three primary uses account for every coroutine yield/resume pair in the
binary:

1. **Async script require.** `_luaGameEngineRequire(path)`
   (BCS-Y-0480, `FUN_00D08A10`) yields the calling Lua thread when the
   target `.prog` resource is not yet loaded; the LPB loader
   (BCS-Y-0466, `FUN_00D0FD70`) drives the load, and completion resume
   (BCS-Y-0481, `FUN_00D0C070`) pushes `"require"` plus the loaded module
   and resumes.
2. **Timed/scheduled waits.** `_wait` (BCS-Y-0485, impl `FUN_006DBCB0`,
   1218 corpus refs across 219 scripts) and `_waitForCharaSchedulerFinished`
   (BCS-Y-0486, impl `FUN_006E4B40`, 159 refs) yield through the engine's
   universal Lua-side N-API dispatcher `FUN_00D08000` (BCS-Y-0495); its
   yield path `FUN_00D04DA0` (BCS-Y-0496) is not a specific API - it runs
   for every registered-method call and yields when the native impl signals
   it. The resume side is the per-thread timer scheduler `FUN_00CEF510`
   (BCS-Y-0497) firing `FUN_00CCEAC0` (BCS-Y-0498) when a thread's
   wait-deadline expires.
3. **Public Resume API.** `Component::Lua::GameEngine::LuaThreadImpl::Resume`
   at `FUN_00CCF290` (BCS-Y-0479, confirmed by diagnostic string).

Refs: `manifests/coroutine_caller_scan_findings.json`,
`manifests/coroutine_caller_scan_l2_findings.json`,
`manifests/high_signal_napi_attribution_findings.json`. BCS-Y-0466,
BCS-Y-0477..BCS-Y-0482, BCS-Y-0485, BCS-Y-0486,
BCS-Y-0495..BCS-Y-0498.

## Lua N-API surface

### The bound N-API surface is broader than shipped-script usage

The zero-caller survey compared a 387-entry snapshot of
`manifests/lua_api_index.json` with the shipped Lua corpus (2671 scripts) and
found 58 N-APIs with zero shipped callsites of any kind
(identifier, string literal, or bind-table init); 4 are naming artifacts,
leaving 54 genuine client-local stubs clustering into five structural
groups:

| Group | Count | Examples | Why zero-caller |
|---|---:|---|---|
| Systems registered in the binary but unused by shipped scripts | 15 | `_getAchievement`, `_hasAchievementTitle`, `_getHamlet`, `_getHydaelynDay`, `_getExtendedTemporary*` (5), `_getEntrustItem`/`_count*` | present in the engine without Lua-side wiring in 1.23b |
| Position/direction primitives | 7 | `_getPosition`, `_setPosition`, `_getDirection`, `_setDirection`, `_getLocation`, `_turnClientDir`, `_setPositionDirectionInn` | called from C++ engine internals; scripts use higher-level move/teleport ops |
| Engine callbacks no shipped script implements | 7 | `_onCancelJobQuestComplete`, `_onChangeNetStat`, `_onChatMessage`, `_onJobQuestComplete`, `_onUpdate`, `_onUpdateGroup`, `_updateGroup` | registered but no class table assigns a handler in 1.23b |
| Server-RPC base names | 2 | `_doServerOn`, `_callServerOn` | scripts only call typed variants (`_doServerOnTalk` etc) |
| Misc per-feature getters/setters/predicates | 23 | `_setActorExtraStat`, `_getActorExtraStat`, `_isMapObj`/`_initAsMapObj`, `_setNameplateGauge`, `_isEnmity`, `_isPushing`, debug/dev hooks, `_callSuperClassFunction` | per-feature bindings unused by shipped content |

The surveyed shipped scripts contain no call site for these 54 APIs.

Refs: `manifests/zero_caller_napi_survey_findings.json`. At the survey snapshot,
the corpus join compared
[xivl-client-scripts:lua/napi_index.json](https://github.com/XIVLegacy/xivl-client-scripts/blob/main/lua/napi_index.json)
(329 called) with the then-current `manifests/lua_api_index.json` (387
catalogued).

### Corpus reconciliation separates missed N-APIs from Lua-side names

Scanning the 2671-script corpus for underscore-prefixed identifiers yields
1009 distinct names. After subtracting the 387 catalogued APIs and 467
script-defined Lua helpers, 622 corpus-called names had no catalog entry. 8
were heavily-used engine APIs the catalog had missed:

| Missed API | Refs | Attribution |
|---|---:|---|
| `_runCharaScheduler` | 5230 | BCS-Y-0483, impl `FUN_006E48A0`, reg `FUN_0072F850` |
| `_defineClass` | 2435 | BCS-Y-0484, impl `FUN_006DCC30`, reg `FUN_0073C270` |
| `_wait` | 1218 | BCS-Y-0485, impl `FUN_006DBCB0`, reg `FUN_0072E0B0` |
| `_string` | 341 | BCS-Y-0490, stdlib alias (`FUN_0078FC90`) |
| `_math` | 179 | BCS-Y-0490 |
| `_waitForCharaSchedulerFinished` | 159 | BCS-Y-0486, impl `FUN_006E4B40`, reg `FUN_0072FC40` |
| `_defineBaseClass` | 139 | BCS-Y-0487, impl `FUN_006DCCA0`, reg `FUN_0073C3C0` |
| `_printLog` | 122 | BCS-Y-0488/0489, two registration sites |

A bulk `.rdata` string search across the remaining 21 top-rank candidates by
reference count produced 7 string matches, 4 of them cataloguable. The 14
candidates with no `.rdata` match do not support a C++ binding. Confirmed
stdlib aliases (`_floor`, `_gsub`,
etc.) are Lua-side assignments (`_floor = math.floor`) with no C-side
registration, and class methods like `_ask`/`_bindWork` are user-defined
script methods registered through `_defineClass`/`_onLoop.__newindex`
paths, living as Lua-string constants in bytecode rather than C-strings in
`.rdata`. The resulting `lua_api_index` contains the confirmed C++ bindings
found by this reconciliation. Unexamined candidates remain leads.
The FFXIV 1.23b client also replaces four Lua stdlib functions (`assert`,
`error`, `pcall`, `type`), with the original `pcall` preserved as `_pcall` -
any analysis assuming stock Lua 5.1 stdlib semantics for those 4 names is
incorrect.

Refs: `manifests/corpus_napi_residual_findings.json`,
`manifests/high_signal_napi_attribution_findings.json`,
`manifests/bulk_napi_classification.json`. BCS-Y-0483..BCS-Y-0494,
BCS-Y-0500..BCS-Y-0502.

## Lua Game Engine (LGE) class substrate

### LGE exposes five Lua metatables over one C++ storage substrate

The Lua Game Engine class system underlying `_defineClass` and
`_defineBaseClass` exposes five metatables. The catalog models five inner
struct shapes; BCS-S-0041 through BCS-S-0045 remain `hypothesis-strong`.

| Role | Metatable | Inner size | BCS-Y | BCS-S |
|---|---|---:|---|---|
| Class instance | `FUN_00D20B00` | caller-allocated; minimum +0x68 = 104 bytes | BCS-Y-0505 | BCS-S-0041 `LGEClassInstanceInner` |
| Memory pool wrapper | `FUN_00D208A0` | 0x28 | BCS-Y-0506 | BCS-S-0042 `LGEMemoryPoolInner` |
| Member descriptor | `FUN_00D207A0` | 0x54 | BCS-Y-0507 | BCS-S-0043 `LGEMemberDescriptorInner` |
| Indexed container | `FUN_00D20540` | 0x5c | BCS-Y-0508 | BCS-S-0044 `LGEIndexedContainerInner` |
| Cursor/pair entry | `FUN_00D20670` | 0x08 | BCS-Y-0509 | BCS-S-0045 `LGECursorInner` |

Entrypoint: `_onLoop` (BCS-Y-0501), whose `__index` (`FUN_00d085b0`) calls
`FUN_00d1ce10`, which installs `FUN_00D20B00` as the metatable for new class
instances. Every instance carries 3 allocator pools at `+0x60`/`+0x64`/`+0x68`
- `save`, `temp`, and `sync`. `FUN_00d272d0` is the single generic member-write
chokepoint used by both `D207A0::__newindex` and `D20540::__newindex` - the
one point where Lua-side mutation crosses into C++ class state.

The C++ storage substrate confirmed by RTTI is
`Component::Lua::GameEngine::Work::MetamethodArray2D` (vftable refs in
`FUN_00d2e360`/`FUN_00d2e2d0`/`FUN_00d2e4d0`; BCS-S-0046 documents the C++
layout). The `+0x60`/`+0x64`/`+0x68` scope pointers are 3
`MetamethodArray2D::Impl` pointers - the first dimension of the 2D array,
with member descriptors as the second. `FUN_00d16cd0` dispatches member
lookups across the 3 scopes in priority order own (`+0x64`) > save
(`+0x60`) > sync (`+0x68`), tagging the active-dispatch byte at `+0x30`.
`FUN_00d272d0`'s write is a 9-param polymorphic call: vtable `+0x6c` on the
class context validates, then vtable `+4` on the member descriptor performs
the write. The Cursor wrapper (BCS-Y-0509) delegates through the wrapped
`MetamethodArray2D::Impl` vtable. The memory pool wrapper (BCS-Y-0506)
exposes allocator fields read-only.

The registration pipeline starts at `FUN_0078E3A0` (BCS-Y-0398). `_defineClass`
(`FUN_0078C2A0`, called through shim `FUN_006DCC30`) and `_defineBaseClass`
(`FUN_0078C330`, through shim `FUN_006DCCA0`) are byte-identical 134-byte
routines sharing the same registration helpers as the static path
(`FUN_00CC71E0`/`FUN_00CC71F0`). Dynamic method binding
(`_onLoop.SomeName = function()...end`) goes through `FUN_00d07eb0`
(the `__newindex`) -> `FUN_00d07bb0`, which allocates an 8-byte upvalue
pair and pushes a 2-upvalue cclosure. `FUN_00cd77d0` is the LGE
state-to-engine-context resolver used by 21 distinct functions across the
namespace.

Refs: `manifests/d2fxxx_userdata_attribution.json`,
`manifests/lge_substrate.json`,
`manifests/class_registry_bridge.json`. BCS-Y-0398, BCS-Y-0484, BCS-Y-0487,
BCS-Y-0501, BCS-Y-0505..BCS-Y-0524; BCS-S-0041..BCS-S-0046.

## LuaControl class hierarchy and Lua-bridge callback dispatch

### The cataloged control classes share the LuaControl hierarchy

The cataloged C++ control classes that Lua scripts manipulate derive from a
multi-tier hierarchy rooted at `Component::Lua::GameEngine::LuaControl`
(BCS-Y-1394 vftable, BCS-Y-1393 ctor, BCS-Y-1677 TD). `LuaControl` itself
has genuine multiple inheritance: primary chain `LuaControl <- LuaObject`
(BCS-Y-1476, 3 further unenumerated ancestors above it); secondary chain
(offset `+4`) `LuaControl <- LgeBase` (BCS-Y-1477) `<- LgeCommonMemoryAllocator`
(BCS-Y-1478) `<- LgeBasicMemoryAllocator` (BCS-Y-1479, root) - the same
Lua-Game-Engine memory-allocator chain the LGE substrate above uses. The
ctor writes only the primary vftable. The Lge chain is data-only
(no virtual methods) and contributes no vtable write.

`Application::Lua::Script::Client::Control::ActorBase` (BCS-Y-1408/BCS-Y-1496,
ctor `FUN_006DBB70` BCS-Y-1710) is the script-side intermediate tier, with
23 constructor callers associated with the cataloged hierarchy, including the
entire `CharaBase` actor family and 11 sibling "control" classes:
`StatusBase`, `GroupBase`, `ItemBase`, `WidgetHandle`, `Math`, `Global`,
`CommandBase`, `JudgeBase`, `QuestBase`, `String`, `Table`.

**The CharaBase actor chain.** `CharaBase` (BCS-Y-1721, TD 0x012709A4, 232
bytes total) is single-inheritance: `CharaBase <- ActorBase <- LuaControl
<- LuaObject <- LgeBase <- LgeCommonMemoryAllocator <- LgeBasicMemoryAllocator`
(the Lge chain lands at `+4` via a split at `LuaObject`, not multiple
inheritance). `PlayerBase` (ctor `FUN_006ED720`, BCS-Y-1736, vftable
BCS-Y-0185) and `NpcBase` (ctor `FUN_006F3650`, BCS-Y-1737, vftable
BCS-Y-0186) both derive from `CharaBase`. This same
`ActorBase <- LuaControl <- LuaObject <- Lge*` backbone is inherited by
every class in the `Application::Lua::Script::Client::Control::*` tree
(36 classes registered by the class registry below), giving every
Control-namespace instance an embedded Lge allocator subobject at `+4`.

**Tentative state for the 11 control classes.** Each of the 11
control classes (StatusBase and its 10 siblings above) attaches a second
inheritance chain at offset `+0x60`, to one of two sibling "tentative
control" classes under `Component::Lua::GameEngine::`:
`LuaGlobalTentativeControl` (LGTC, per-class transient state, vftable
BCS-Y-1509, ctor BCS-Y-1510) for `StatusBase`, `Global`, `JudgeBase`,
`CommandBase`, `String`, `Math`, `QuestBase`, `Table` (8 classes); or
`LuaTentativeControl` (LTC, singleton transient state, vftable BCS-Y-1515,
ctor BCS-Y-1516) for `GroupBase`, `ItemBase`, `WidgetHandle` (3 classes,
each with a single UI/group container per session). Both
siblings inherit only the same Lge memory-allocator chain
(structural clones of each other) and are routed by a shared RTTI
dispatcher `FUN_00CDCBA0` (BCS-Y-1513). This is a second, independent Lge
allocator subobject - every one of the 11 control classes therefore has
two distinct non-polymorphic Lge allocator scopes: actor-side (via
`ActorBase` at `+4`) and Lua-side (via LTC/LGTC at `+0x64`,
i.e. `+4` of the `+0x60` subobject). `Global` is the sole outlier with a
third Lge scope, via a `LuaThreadEndListenerInterface` (LTELI, see below)
subobject at `+0x68`.

The LTC/LGTC secondary vtable is a shared 34-slot polymorphic interface
across all 11 classes; only 4 of the 34 slots are class-specific in
practice (slot 0 vector-deleting dtor, slot 1 clone/factory - both by
uniform per-class templates. Slots 2 and 6 are overridden by a handful of
classes with internal substructure to walk). Slot 5 is a single
engine-wide shared routine, `FUN_006F6900` (BCS-Y-1530), that fires the
`_onFinalize` Lua callback for whichever class instance calls it (adapts to
runtime class context via the class-registry lookup below, not via 11
separate per-class implementations). Slot 20 is the Lua `_onLoop`
`__newindex` read-only blocker (`FUN_00AB7340`) - the secondary vtable
encodes Lua-bridge metatable handlers as well as C++ methods. The rest are
engine-wide no-op/error stubs shared across all 11 classes.

**Cross-cutting interfaces.** `Component::Lua::GameEngine::LuaThreadEndListenerInterface`
(LTELI, BCS-Y-1480, vftable 0x00FD4F48) is implemented by 6 classes needing
notification when a Lua coroutine ends: `Global`, `CutScene`, an anonymous
cutscene-preview listener, `ClientItemSpreadSheetBinderContainer`,
`Event::FormManager`, `Event::PlayerManager`. `Application::Lua::LuaAppBase`
(BCS-Y-1582) is the root abstract base of a separate family of Lua-bridge
interfaces: `LuaActorImplInterface` (BCS-Y-1049, 90 slots - 1 dtor + 89
pure-virtual, implemented concretely by `LuaActorImpl` BCS-Y-1048),
`Command::CommandInterface` (BCS-Y-1584, distinct from the receiver-class
`CommandInterface`), `SpreadSheetLoadedDataDisappearListenerInterface`
(BCS-Y-1583), `ActorInitializeParameter::DisplayNameResolverListener`
(BCS-Y-1585), and two `InterfaceToSqwt::*` Lua-to-Sqwt-UI bridge classes
(BCS-Y-1586, BCS-Y-1587).

**Lua class registry.** `FUN_0078E3A0` (BCS-Y-0398) registers exactly 36
named classes at engine init, split into two registration styles by
trampoline (`FUN_00CC71E0` BaseClass-style, `FUN_00CC71F0` LGTC-style), both
funneling into the class-table find-or-create routine `FUN_00CD8870`
(BCS-Y-1670). Of the 36, 14 have no C++ RTTI type descriptor anywhere in
the binary (`OtherArea`, `SystemBaseClass`, `ProgDebugBaseClass`,
`WorldBaseClass`, `ZoneBaseClass`, `ImportantItemBaseClass`,
`MoneyItemBaseClass`, `NormalItemBaseClass`, `GameDataBaseClass`,
`CommandDebuggerBaseClass`, `CommandDebuggerFUNCBaseClass`, and the 3
`CommandDebuggerGM`/`DEV`/`TEST` user-mode variants) - these are
abstract Lua-bridge bases that exist only as named registry slots for
Lua-script-defined derived classes to declare against; the sole C++
implementation behind all 3 CommandDebugger variants is
`Application::Lua::Script::Client::Control::CommandDebuggerBase` (vftable
0x00FD510C), with the 3 variants existing purely as Lua-defined permission
wrappers.

**Callback dispatch.** The primary synchronous Lua-fire dispatcher is
`FUN_00CC7A90` (BCS-Y-0399), reached by 79 distinct fire sites covering 67
named Lua events (actor lifecycle - `_onInit`, `_onFinalize`; network -
`_onReceiveDataPacket`; update - `_onUpdateWork`; state-change -
`_onChangeJob`; pre/post hooks - `_onPreWarp`/`_onPostWarp`; UI, input,
cancellation-cascade, and per-feature events). Every fire site shares the
signature `FUN_00447260("<event_name>", DAT_00f67298)` immediately followed
by `FUN_00CC7A90(this, &str, &args)`; the dispatcher resolves the
runtime-class-specific handler via `FUN_00CD7A30` (BCS-Y-1581), which reads
a per-instance class-identity pointer. A rarer alternate synchronous path
(`FUN_00CD25C0`, BCS-Y-1685, 1 fire site: `_onCommand`) and two scheduled
paths complete the fire-site inventory: a microsecond-resolution and a
millisecond-resolution red-black-tree scheduler, each rooted in a
`Component::Lua::GameEngine` singleton (BCS-Y-1691, 552 bytes, the true
owner of the per-instance class-identity fields used throughout this
dispatch surface - not `LuaControl` or `CharaBase`, both of which are
too small to hold those field offsets). The millisecond-scheduled path
uses a separate dispatch core, `FUN_00CCEAC0` (BCS-Y-1697), routing through
4 callback-type branches. It is the mechanism behind `_onTimer`. The tick
chain that drives all of this is Scene-driven, not a raw per-frame call:
`Application::Scene::SceneThreadImpl` embeds a
`Sqex::Thread::Queue<ScenePacket>` message channel (vftable 0x00F931C0);
its drain dispatches each `ScenePacket`'s tick slot into
`Application_FrameTick` (BCS-Y-1711) -> `LuaFrameTick` (BCS-Y-1701) ->
`LuaTickOrchestrator` (BCS-Y-1694) -> the two scheduler ticks.
`Application::Main::MainModule` embeds a parallel
`Sqex::Thread::Queue<MainPacket>` for the s2c Actor-cluster async tier
described in the wire-dispatch section above; `Sqex::Thread::*` is a
reusable primitive namespace (`Mutex`, `Thread`, `ThreadManager`,
`ReadWriteLock`, plus 6 `Queue<T>` instantiations for Scene, Main, async
work, resource loading, install-writer, and HTTP event channels).

Refs: `manifests/symbols.json` (BCS-Y-1393..BCS-Y-1813 span this hierarchy).
BCS-Y-0135, BCS-Y-0185, BCS-Y-0186, BCS-Y-0279, BCS-Y-0314, BCS-Y-0398,
BCS-Y-0399, BCS-Y-0537, BCS-Y-0538, BCS-Y-1048, BCS-Y-1049, BCS-Y-1056,
BCS-Y-1393..BCS-Y-1410, BCS-Y-1476..BCS-Y-1480,
BCS-Y-1496..BCS-Y-1520, BCS-Y-1529..BCS-Y-1553, BCS-Y-1557,
BCS-Y-1569..BCS-Y-1587, BCS-Y-1670..BCS-Y-1743;
BCS-S-0046..BCS-S-0049.

## Sqwt UI framework

### Sqwt UI factories construct elements and subscribe handlers

The cataloged Sqwt UI Element classes (`LuaDebugLog`, `LuaDebugSelect`, `FormElement`,
`XamlElement`, `CameraElement`, and the broader Element-namespace tree)
instantiate through a standard 3-layer pattern: a heap factory
(e.g. `FUN_00533840` for `LuaDebugLog`, `FUN_00533940` for `LuaDebugSelect`)
that allocates a class-specific size and calls the ctor, reached
exclusively via function-pointer table dispatch (zero instruction-level
callers); an owner ctor that chains to the parent ctor, writes its own
primary and MI-secondary vtables, zero-initializes fields, loads its form
definition, constructs one or more `EventHandler<Owner,EventArgs>` delegates,
and subscribes each. The subscription call itself,
the event source's secondary vtable at `+0xB4`, slot `+0x28`, with the event
id global and handler instance.

The `+0xB4` access is the literal MSVC multiple-inheritance secondary
vtable at that byte offset (not a pointer to a separate interface object).
`Sqwt::UIElement` has 8 RTTI base classes across two chains: primary
(offset 0, 6 deep) `UIElement <- Sqwt::Media::Visual <- Sqwt::DependencyObject
<- Sqwt::DependencyObjectBase <- Sqwt::AllocatorBase <- Sqwt::Object` (root);
secondary (offset `+0xB4`, 2 deep) `Sqwt::InputElement <- Sqwt::IInputElement`
(interface root). The class names and topology are Windows Presentation
Foundation's `System.Windows.*` hierarchy re-implemented in C++: SQEX
hand-rolled a WPF-shaped UI framework for the FFXIV client, and slot `+0x28`
within the `+0xB4` `InputElement` secondary vtable is the `IInputElement`
subscribe method, parallel to WPF's `UIElement.AddHandler(RoutedEvent, Delegate)`.

In the client Element hierarchy, concrete classes such as `LuaDebugLog` inherit
`Application::Main::Element::XamlElement`, which composes (has-a, not
inherits) `Application::Main::RaptureElement`; `RaptureElement` in turn
inherits `Sqwt::InputElement` - the point where the Element tree and the
Sqwt-side widget tree (Window, ListBox, Button, ScrollBar,
etc., all deriving `Sqwt::FrameworkElement <- Sqwt::UIElement <- Sqwt::InputElement`)
converge on a shared deep base.

Refs: BCS-Y-1330..BCS-Y-1334, BCS-Y-1375..BCS-Y-1392,
BCS-Y-1499..BCS-Y-1508. The LuaControl hierarchy above uses the same fixed
secondary-vtable pattern at `+0x60` for LTC/LGTC.

### Sqwt uses a separate event source registry for each channel

Rather than one unified map, each Sqwt event channel has its own
static-address registry container (a small `std::_Tree`-based structure);
the lookup wrapper takes the channel registry as its `this` argument, with
no separate key argument - channel selection is the choice of which
registry global to pass. Lookup is RTTI-typed per consumer: raw lookup
(`FUN_0053E480`, BCS-Y-1355) returns the registry value untyped; typed
wrappers (`FUN_0053E580` `FindAsWindow` BCS-Y-1356, `FUN_0053E7C0`
`FindAsListBox` BCS-Y-1358) `dynamic_cast` the result via the universal
MSVC RTTI helper `FUN_009DA6CC` (BCS-Y-1359), returning null on a type
mismatch rather than dispatching incorrectly. The subscribe-side event-id
(the global passed to the `+0xB4`/`+0x28` subscribe call) is a separate
per-channel global from the lookup-side registry key: lookup finds the
source object, the event-id identifies the broadcaster for the subscriber
list.

Refs: BCS-Y-1355..BCS-Y-1359, BCS-Y-1370..BCS-Y-1374.

## Real implementations with no static caller are structurally legitimate

A non-trivial function body with no static caller chain reaching wire
arrival is not, by itself, a sign of incomplete analysis. Three
independent surface types converge on the same conclusion: a receiver
class with complete RTTI/vtable/ctor/Lua-registration but zero callers
anywhere on its factory (`SetCommandEventConditionReceiver`, real body,
factory ctor `FUN_0089D400` has 0 callers across the binary). Vtable slots with a
real body but zero static dispatch site under either an operand-scalar or
absolute-VA reference search (`NullActorImpl::vftable` slots 72/73/81); and
a utility function whose callers are all client-internal, none arriving
from the wire (`FUN_00578540`, a party-marker utility with 4 callers, none
of them packet-receiver entry points). The MSVC C++ build emits whole
vtable layouts. Per-slot dead code is not stripped, and a receiver class can
survive in the binary without a factory site. Where a body is
real but has zero static callers,
static analysis alone cannot distinguish dead code from a runtime-computed
dispatch mechanism it cannot see (for example a method-name hash indexing
the vtable) - that distinction requires runtime instrumentation.

Refs: BCS-Y-0162, BCS-Y-0945, BCS-Y-0946, BCS-Y-1032, BCS-Y-1037.
