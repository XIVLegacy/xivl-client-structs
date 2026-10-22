# XIVLegacy Client Structs documentation

The public documentation covers the evidence-backed FFXIV 1.23b client-structure
catalog. Machine-readable inventories and regeneration rules live under
`manifests/`.

## Policy

- [Repository style](style-guide.md) - authored code, manifests, and
  documentation conventions.
- [AI-assisted contributions](ai_agents/README.md) - contribution and
  documentation policy.
- [Evidence and claims](ai_agents/evidence-and-claims.md) -
  evidence classes, confidence, citations, and claim boundaries.
- [Comments and prose](ai_agents/comments-and-prose.md) -
  rules for deciding which comments to keep.
- [Retail-input validation](ai_agents/retail-input-validation.md) - bounded
  private-input workflow, credential boundary, and sanitized attestation.

## Consumer guides

- [Client architecture](client-architecture.md) - curated catalog of
  stable model-level findings about the 1.23b client (wire dispatch,
  Lua-bridge, LGE/LuaControl class substrate, Sqwt UI).
- [Client-structure IR](ir-schema.md) - reads the generated client-structure IR
  and the schemas that validate it.
- [Naming](naming.md) - naming rules for known/unknown structs and
  fields, the address convention, and the Receiver-vs-Packet naming pairing.
- [Lua Game Engine (LGE) class system](lua-class-system.md) - description of the
  LGE class system (5 Lua metatables, registration pipeline, write chokepoint).
- [Command-slot actor and category context](actor/command-slot-context.md) -
  joins observed property-stream slot values to static command identities.
- [Native pad routing and UI visibility](native-input-ui-boundaries.md) -
  exact-client receiver, dispatch, three-state conversion, and ownership limits.
- [Action movement wait](action-movement-wait.md) - native timer producers,
  consumers, and action eligibility limits.
- [Login state boundaries](login-state-boundaries.md) - roster projection,
  selection operations, and identity and readiness limits.
- [Retail repair contract](repair-contract.md) - client, wire, metadata, and
  capture boundaries for NPC repair and CraftCommand 22013 self-repair.
- [Command descriptor registration](command-descriptor-registration.md) -
  observed definitions, native constructors and runtime selection boundary.
- [Player command wire contract](player-command-wire-contract.md) - native
  dispatch, direct fallback fields and typed argument serialization.
- [Linkshell rank and group work](linkshell-rank-work-contract.md) - member
  rank consumers, native continuation keys and completion callbacks.
- [Bazaar command and item-package contract](bazaar-native-wire-contract.md) -
  request fields, settlement dependencies and
  [sign appearance](bazaar-appearance-contract.md).
- [Widget and class native call contracts](widget-native-call-contract.md) -
  declared Lua argument and return types, owning classes and native targets.
- [Boot native call contracts](boot-native-call-contract.md) - measured
  `_onInit` call order and the contracts of the first natives it reaches.
- [Desktop native call contracts](desktop-native-call-contract.md) - user
  config keys, list text, UI command conditions and `LuaControl*` returns.
- [Target cursor native state](target-cursor-native-contract.md) - cursor
  creation, selection, range check, empty identity and image side effects.
- [Talk widget native contracts](talk-native-contract.md) - parent and child
  widget accessors, keyboard focus, tutorial test and desktop message pools.
- [SpreadSheet native contracts](spreadsheet-native-contract.md) - row cache
  reads, key ranges, yielding load requests, row release and asynchronous loads.
- [Chara scheduler, wait, item and log native contracts](scheduler-item-native-contract.md) -
  scheduler queue entry, resume checkers and thread yield, item package
  lookup and log output.
- [Nameplate, actor, area, item reference and group native contracts](nameplate-group-native-contract.md) -
  nameplate listener, actor identity and name tests, area flags, sheet binding
  of item references and group queries.
- [Generic _progFunc native contract](progfunc-native-call-contract.md) -
  captured dispatch, bounded argument records and supported output representations.
- [WorldMaster server-time native contract](world-master-native-call-contract.md) -
  receiver validation, empty argument list and signed cached-clock return.
- [Chocobo naming native checks](chocobo-naming-native-contract.md) -
  UTF-8 sequence counting and the first-character property used by the widget.
- [Hamlet ranking and score payloads](hamlet-wire-contract.md) - receiver
  fields, cached rows and consuming score getters.
- [Appearance record payload](appearance-record-wire-contract.md) -
  `0x00d7` record width, count and actor-table writes.
- [Achievement rate consumer](achievement-rate-consumer.md) - native cache
  writes, Lua numerator/denominator, list-step bits and response boundary.
- [Search and recruitment wire contract](search-recruitment-wire-contract.md) -
  native requests, application consumers and widget projections.
- [Additive custom-zone selection](map-layout-selector.md) - SetMap framing,
  allocation constraints and the independent-scene acceptance boundary.

## Related contracts

- [Manifest contract](../manifests/README.md) - manifest families,
  generated products, and regeneration entry points.
- [Tooling](../tools/README.md) - local validation and research
  commands.
