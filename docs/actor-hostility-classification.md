# Actor hostility classification inputs

For the desktop target-mode predicate, the minimal varying actor input is the
battle-property Boolean plus the actual script class behavior. Player methods
and class-defined allied battalion overrides select player mode. HP values,
`npcWork.hateType`, party color and a Monster path substring do not replace
those inputs. Complete reproduction from incoming messages across actor
lifetimes is not established.

The canonical recovered predicates, allied tests, name-color branches,
target-HP behavior and qualified native color-cache fallback are in
`xivl-decomp:docs/actor/actor-friend-enemy-classification.md`. This page owns
the wire input and lifetime contract. Neither page defines server attack
permission or a universal friendly/hostile enum.

## Source identity and method

Native evidence names retail 1.23b `ffxivgame.exe`, build
`2012.09.19.0001`, 15996808 bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`,
image base `0x00400000`, as pinned by
[`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
VAs are absolute; RVA is VA minus the image base. The companion finding
records fresh Capstone 5.0.7 original-byte checks and authenticated recovered
Lua identities. Those checks establish static operations and recovered
script logic, not live execution or historical server policy.

The retained property identities come from
[`gam_hash_names.json`](../manifests/gam_hash_names.json) and the
[`property-stream catalog`](../manifests/property_stream_hash_catalog.json)
at source revision `24be660305d3f027aacba708c73b11a50c9261ed`. The latter
pins capture accounting to `xivl-captures` revision
`54a24c87faa4e3cebde808b74d80b6f1bee4b013`,
`studies/property-stream-hash-catalog/derived/accounting.json`, SHA-256
`0bce5dd4ecacfbbf7d0f2d12a02b4613e76ffe23d5a058dbcab2cd59a5e70837`.
The observations below reuse that frozen corpus; they are not a new packet
history for a selected actor.

## Wire inputs

Application offsets below exclude the 16-byte game-message header and the
separate outer sub-event header. Class/path text has no integer signedness.
Property names include the literal bracket characters in the hash input.
The client hash is backward MurmurHash2 with seed 0, as documented in
`xivl-decomp:docs/resource/murmur2.md`.

| Input | Carrier, exact coordinate and representation | Supported consumer join |
| --- | --- | --- |
| Class name | Clientbound `0x00CC`, application `+0x24`, NUL-terminated `char[32]` | Selects the valid Lua class record during successful binding. |
| Script path | Same record, application `+0x44` starts the 192-byte tagged stream; its first item is tag plus NUL-terminated path | Loads the script defining class behavior and inheritance. |
| Game-parameter availability | First tagged `_onInit` argument after the path, five interleaved controls and optional control data; no fixed application offset | Chara initialization sets `charaWork.gameParameter` from this value and conditionally binds HP. This is not the first application dword. |
| Battle property | `0x0137`, full name `charaWork.property[2]`, u32 hash `0x7B675313`, observed value width 1; declared Boolean | Lua `isPropertyEnabled(3)` and `isBattleCharacter()`. |
| Target-admission property | `0x0137`, `charaWork.property[1]`, hash `0x2138FD71`, observed width 1; declared Boolean | Lua property 2, additionally disabled if Lua property 1 is false. |
| Admission prerequisite | `0x0137`, `charaWork.property[0]`, hash `0xE14B0CA8`, observed width 1; declared Boolean | Lua property 1 prerequisite above. It alone is not the entire admission test. |
| Hate-type selector | `0x0137`, `npcWork.hateType`, hash `0x8E9C05BE`, observed width 1; declared integer8 | NPC color compares values 1 and 2, then occupancy membership for other values. Width alone does not assign universal wire signedness. |
| First HP part | `0x0137`, `charaWork.parameterSave.hp[0]`, hash `0x4232BCAA`, observed width 2 | Lua part 1 via `getHP()`; declared integer16 work reads. |
| First maximum-HP part | `0x0137`, `charaWork.parameterSave.hpMax[0]`, hash `0x7BCDFB69`, observed width 2 | Lua part 1 via `getHPMax()`; declared integer16 work reads. |
| Battalion | No separate wire field in the examined definitions | Base `getBattalion()` returns 0; the two opening allies return 1 through class overrides. Actual inherited class behavior supplies this value. |
| Player identity behavior | Actual successfully bound class, not a numeric actor-ID kind | PlayerBaseClass returns true from `isPlayer()`, NpcBaseClass false. |

The Boolean array bridge subtracts one from positive Lua indices before the
child reader. Thus Lua index 3 is canonical/native element 2, relative bit 2
in the declared property array. `charaWork.property[3]`, hash `0x83AF687B`,
is a distinct property, corresponding to Lua index 4. These are not packet
offsets or constant CharaBase object displacements. The native index proof
and exact ranges are in the companion finding and
`xivl-decomp:docs/script/job-action-acquisition.md#native-boolean-layout`.

`0x0137` application `+0` is a u8 declared stream length. Each ordinary
property record is u8 width, u32 little-endian hash, then that many raw value
bytes. Target markers share the variable stream and change following target
context. No individual property's offset is constant. Boolean memory packs
one bit per element even though the observed wire records carry one value
byte. HP's two raw bytes have no signedness tag; integer16 declaration and
sign-extending work readers supply the client-side signed interpretation.
The typed writer and endian-adjusting HP array route are catalogued in
`property_stream_hash_catalog.json#applyStorageBoundary` and its
`calibrationCorrection` record.

Creation framing and class lookup are owned by
`xivl-decomp:docs/actor/actor-instantiation-and-self-player.md#stream-reads`:
`0x004D88E2 -> 0x00574780 -> 0x00774AD0`. Stream values, not the controls,
become `_onInit` arguments. The four raw bytes at application `+0` copy to
implementation `+0x14` at `0x00774BDA` with unresolved meaning. Do not use
that preamble as an actor ID, display ID, class ID or battalion.

## Other name-color inputs and evidence boundaries

These inputs are needed for exact name color, beyond player/enemy target mode.
They cannot be folded into one hostile flag. The companion finding gives
their recovered script call sites and branch order.

| Input | Established representation or producer | Remaining wire join |
| --- | --- | --- |
| Viewer and self comparison | `worldMaster:_getMyPlayer()`; self creation record key matches `0x0002` sub-event id, per actor-instantiation finding | Complete viewer/global lifecycle through zones and rebinds is not closed. |
| Death mode | `isDeadMode()` uses `_isActorMainStatMode(1)`; native main-stat getter is in [binding-map contract](binding-map-native-contract.md#character-natives) and its mode projection in [chara-desktop contract](chara-desktop-native-contract.md) | This finding does not establish the exact incoming producer for the selected actor's death state. |
| Other-player accessibility alpha | `_isAccessibleInServer`, callback `0x006FA3A0`, reads CharaBase `+0x5D`, as qualified in [chara-world contract](chara-world-native-contract.md) | That contract leaves the byte's writer untraced. It is not an actor-hostility field. |
| Viewer player-party membership | Script group 10001; `_isMember` resolves the current identity in GroupBase `+0x68` through `0x006C3560`, per [nameplate/group contract](nameplate-group-native-contract.md#group-natives) | Exact incoming group-to-current-player-party association and execution history are not closed here. |
| Content branch | `0x0137`, `charaWork.currentContentGroup`, hash `0x0DF9E189`, observed width 4; declared integer32. A nonzero id chooses an extended temporary group, followed by kind/membership queries | Only zero was retained for this property. The content-group branch's original bytecode fallthrough and selected registry association are unestablished. |
| Actor party and occupancy membership | `getParty()` chooses 10001, then 10002; `_getOccupancyGroup` reads group-data `+0x68/+0x6C` and resolves registry `Y+0xE4` through `0x006C2090`, per [work-binder contract](work-binder-native-contract.md) | `0x0187` to the particular registry record returned by this getter is not closed. |
| Retainer identity, owner-group membership and talkability | Recovered retainer/talkable branches query methods and viewer group 80001 | Exact packet-to-method/current-group joins are not established by this finding. A non-battle talkable actor can share allied green. |

The retained `0x0187` application is 0x40 bytes. Its first 0x10 bytes remain
opaque in `manifests/structs.json#BCS-S-0330` and
`manifests/unmapped_payload_decoding.json`, batch-3 `s2c_0x0187`. Application
`+0x10` is two u32 occupancy-work words, `+0x18` a u32 localized-name ID and
`+0x1C` `char[36]` occupancy name. The native arm reaches
`0x004DC690 -> 0x00576390`. These observations do not identify the opaque
header as a particular group key or establish that the packet writes
`npcWork.hateType`. Older stronger labels do not close the getter join.

Player-party header/member carriers are retained in `manifests/structs.json`,
BCS-S-0320 and BCS-S-0297/0298/0299, with member BCS-S-0260. A `0x017F`
application has framing u64s at `+0/+8`, then eight 0x30-byte rows at `+0x10`;
row `+0` is u32 actor identity. This is a group member input, not an actor
class or color enum. The native `_isMember` identity lookup is established;
its complete association to the viewer's particular party remains qualified.

Grand Company `currentAllegiance` is a separate u8 at `0x0194` application
`+0`. The [misc player contract](player-misc-native-contract.md) owns its
rank bytes. No source join equates it with the allied battalion constant.
The `0x0195` enmity-indicator receiver is likewise distinct from the synced
`npcWork.hateType` selector. Neither can replace the property/class predicate.

## Lifetime and sufficiency

For supplied initialized Boolean state, the recovered target-mode decision
needs only current `isPlayer()`, Lua battle property 3 and `getBattalion()`.
The first and third are class behavior in the inspected definitions. A wire
observer therefore needs the actual successful class binding/hierarchy and
the latest applied `charaWork.property[2]` value for that actor incarnation.
Party state is additionally needed for actor-to-actor `judgeRelation`, and
the larger table above is needed for color. Positive HPMax and game-parameter
availability suffice for the examined numeric HP visibility branch without
establishing any of those relations.

The native `0x0137` chain is conditional:
`0x004D8860 -> 0x00575070 -> 0x00759ED0 -> 0x0089E550 ->
0x00775A30 -> 0x00775180`. A registered hash selects the polymorphic writer
at property-map node `+0x10`, called at `0x00775652`. These routes and
initialization/completion guards are owned by
`xivl-decomp:docs/net/actorimpl-receiver-dispatch.md#native-0x0137-syncmemory-route`,
`docs/net/sync-writer.md` and `docs/net/actor-work-completion-targets.md`.
The latter does not equate parser context key Kp with the network actor ID.
Missing/inactive contexts take a cache route whose replay is not closed.
An observed wire value alone does not prove the selected actor's reader saw it.

An already-bound LuaActorImpl bypasses the ordinary `0x00CC` apply path.
The holder reset path `0x00574970` can construct a NullActorImpl before
rebinding, as traced in
`xivl-decomp:docs/input/chara-selection-producers.md#selected-actor-implementation-handle-and-slot23`.
Repeated class definitions can rewrite parent links, per
`xivl-decomp:docs/script/define-class-repeat-definition.md`. Zone teardown,
actor-ID reuse, initial work-pool contents and every reset/rebind path are
not fully closed. Class/path on one creation record is not proof of a
permanent classification or a generation token.

Consequently, the minimal conditional inputs are established, but a universal
incoming-message observer across lifetimes is not. The precise missing joins
are network identity to current work context/storage, initial property state
and cache replay, complete reset/rebind/teardown ordering, and current class
dispatch. Exact color additionally needs the occupancy/group associations
and the unverified player-fallback/content-branch fallthrough. The companion native cache
fallback reads the chosen presentation only; it does not fill these gaps.
