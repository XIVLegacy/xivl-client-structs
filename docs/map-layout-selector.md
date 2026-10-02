# Additive custom-zone selection contract

Retail 1.23b can enumerate an appended RegionInfo and submit its eligible
LayoutInfo children through the normal SetMap path. This establishes a static
selection mechanism, not acceptance of an independent authored scene. No new
region, zone or resource ID is allocated by this contract.

## Evidence and scope

The executable is build `2012.09.19.0001`, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
Addresses are VAs, image base `0x00400000`. The public instruction findings
are owned by:

- `xivl-decomp:docs/resource/map-layout-selector.md`, root/child construction,
  lookup widths, normal enumeration and derived-resource fallback.
- `xivl-decomp:docs/resource/map-layout-request-boundary.md`, conditional
  manager request, name reuse, concrete ResourceModule target and native ABIs.
- `xivl-decomp:docs/resource/region-auxiliary-resource.md`, embedded resource
  event, completion/decoder boundary and unresolved payload-consumer targets.
- `xivl-decomp:docs/resource/resource-path-producer.md`, numeric formatter,
  asynchronous FileThread/LocalFile opens and bounded observation seams.

The retained C556-C558 selector study supplied the initial research lead.
The named raw C558 JSONL was unavailable for independent replay here; its
reported ten unique region-202 manager requests are not an ordered producer
or DAT-open baseline. Static checks against the pinned executable support the
public findings above. An alias to retail resources is not custom-scene
acceptance. Rendering, collision and walking require their own evidence.

## SetMap framing and native base

A complete integration SetMap subpacket is 48 bytes: outer header 16,
game header 16, application payload 16. Preserve the application's dwords
at `+0/+4` as region/zone. The remaining application bytes retain their
control profile, including the following mode byte.

| Base | Region dword | Zone dword | Following byte |
|---|---|---|---|
| Complete subpacket | `+0x20` | `+0x24` | `+0x28` |
| GameMessageHeader / native packet | `+0x10` | `+0x14` | `+0x18` |
| Application payload | `+0x00` | `+0x04` | `+0x08` |

At `0x0059CED0` (BCS-Y-0541), ECX is MapLayoutElement and entry
`[ESP+0x04]` is the packet pointer. Three register pushes precede its
load from adjusted `[ESP+0x10]` at `0x0059CED3`. Dispatcher `0x004DC690`
passes its GameMessageHeader pointer unchanged at opcode-5 target
`0x004DCBF7` through virtual slot `+0x24`, and the receiver reads its
opcode at pointer `+2`. Record the actual pointer, entry ESP, ECX, return
address and original argument slots at a hook. Generated SetMapBody offsets
must not be rebased into application offsets. Header ownership is in
[Packet Headers](../structs/ffxiv/client/network/packet-headers.md),
BCS-S-0002/0003; instruction locators are `0x0059CED3`, `0x0059CEF9`,
`0x0059CEFD`, `0x0059CF0E` and the receiver call in `0x004DC690`.

The tick path posts region/mode through scene operations 5, 6, 7 and 9;
zone travels separately in operation 10. `0x0062DBE0`/`0x0062D1C0`
carry region in the low 16 bits. `0x0064E830` submits every child except
types zero and one. A different zone value with the same region does not
select an independent child set through this path.

## Minimal candidate and allocation constraints

The smallest static selection candidate adds one root and one eligible child
to catalog resource `0x03C00000`. In the zero-`+0xB8` retail profile, it also
requests an auxiliary resource derived from the children. This is a minimum
request shape, not a complete authored-resource format:

| Addition | Required constraint |
|---|---|
| RegionResourceData root | New nonzero region key representable in 16 bits; one following child; distinct terminated name; supported retained opaque/root profile |
| LayoutInfo child | New child key/name; raw `+0x04` eligible type, raw `+0x08` distinct `u32` resource key; preserve supported kind/opaque profile |
| Layout resource | Independent authored native payload and dependencies at unused resource keys and paths |
| Auxiliary resource | For zero root `+0x20`, reserve `(first child resource key & 0xFFFF0000) | (max low16 across child resource keys + 1)`, including type 0/1 rows; account for its numeric request and unresolved payload contract |
| Zone identity | Separately allocate an unused representable zone; the current integration's script actor identity needs a nine-bit zone component, `0..511` |

RegionInfo lookup compares full dwords across 4-byte pointer slots, without
a fixed ID-indexed array bound. The 16-bit limit above comes from the normal
scene transport. The nine-bit zone restriction is an integration requirement,
not a demonstrated native RegionInfo width. Neither permits choosing an ID
solely because it lies inside the numeric range.

Inventory all retained roots, children, effective names, numeric resources,
path-table mappings and zone/script identities before allocation. Manager
name lookup can fall back across all regions, and named manager reuse can
alias a retail resource even when the numeric ID differs. Compare effective
NUL-terminated names, including the native 15-byte copy, not only raw token
bytes. Terminate root names inside their 16-byte raw span. Keep child resource
low indices below `0xFFFF` so the derived key does not overflow into group bits.
In formatter mode zero, numeric byte-group filenames alone are insufficient;
the resource path-table mapping must also be supported and additive.

The auxiliary completion trace reaches a generic resource decoder and a
forwarded actor consumer. It does not establish an authored payload profile
or prove that auxiliary failure is harmless. Layout-manager readiness alone
does not test this resource. The cited completion finding owns the precise
remaining virtual edges and native observation arguments.

Preserve every existing root/child record byte-for-byte and in order,
including type 0/1 rows. Append the candidate group, update only demonstrated
count/size metadata, and retain opaque bytes. Compare every retail root's
ordered eligible set, names, profile values and derived key before/after.
Preserve all occupied resource files and mappings. The shared catalog is
extended; an existing retail root or resource is never repurposed.

## Zone-master and script dependencies

The LayoutInfo selection loop has no numeric zone-to-ZoneMaster class lookup.
For class-dependent normal-zone actors, the tracked Lua registry records
retail ZoneMaster leaves requiring `/Area/Zone/ZoneBaseClass`, for example
`xivl-client-scripts:lua/registry.json`, key `area/zone/zonemasterseas0`.
Their top-level `_defineClass` metadata is in the corresponding `.calls.json`
sidecars. [Client class registry](../manifests/client_class_registry.json)
records the native base path and script-derived leaf vocabulary; vocabulary
does not bind a numeric zone to a class.

The address-backed loading rule is in
[Client architecture](client-architecture.md): `require` reaches
`0x00D08A10` -> file lookup `0x00D0CFB0` (including `.lpb` retry) ->
load `0x00D08180` -> `luaL_loadbuffer` `0x00CF4680` and guarded execution.
Executing `_defineClass` promotes the named class through `0x00CD9360`.
Class-dependent actor creation requires an already defined class; creation
alone does not load its script. Observe the concrete require path and class
definition before creation rather than substituting a registry row for load
evidence. Existing base scripts also have `_getRegion`/`_getZoneName` uses;
`xivl-client-scripts:docs/area-base-client-initialization.md` owns conditional
common-sheet preparation during AreaBaseClass initialization. Those calls do
not prove custom sheet availability or additional hard selection prerequisites.

The concrete missing dependency edge is the native or observed loader that
maps the new numeric zone/region to its internal name and ZoneMaster class
path, then executes that require chain. Existing class-path evidence does
not close it. `xivl-client-data:manifests/zone_internal_names.json`,
`_provenance.limitations` and `zoneBindings`, is a bounded retail name/layout
join; it is not a complete class-path allocation or native script selector.
No minimal set of new sheet rows or script filenames can yet be declared
sufficient for a fully initialized custom zone. A separate owner-operated
class-load observation must record the unchanged control and candidate's
numeric inputs, resolved name/path, LPB lookup result, definition and first
class-dependent creation. Keep that acceptance separate from DAT selection.

## Bounded owner-operated selection probe

The experiment establishes additive selection and correlated resource opens.
Native payload parsing/activation and auxiliary payload semantics remain
separate acceptance requirements. Keep this experiment independent of
render/collision edits and live server changes.

1. Freeze the pinned executable, unmodified catalog, resource inventory and
   an owner-operated local selection input. Capture an unchanged retail
   control first; retained region 202 / zone 134 / mode 40 is a comparison
   lead, and region 207 supplies a singleton eligible-layout profile. Both
   are occupied controls, never candidate allocation slots.
2. Build an isolated additive candidate only after allocating symbolic
   region/zone/resource keys from the inventory. Use a retained non-weather
   type `0x3000` profile and an independently authored resource set. Account
   for the derived auxiliary request. Do not borrow retail scene resources
   and call the resulting alias a new scene.
3. In fresh owner-controlled processes, run control, candidate, then control
   with identical observation settings. Bound each to one named selection
   and a declared timeout. The owner launches, logs in and operates controls.
4. Observe SetMap's actual native base; RegionInfo/child selection and
   LayoutWorld submission; manager request `0x0079C890`; ResourceModule
   `0x00C99130`; FileThread callsite `0x00C9697F`; and LocalFile `0x00453C00`.
   Record ordered requests from both manager and auxiliary paths. Cache hits
   and helper `0x0044B350` returning true are not file-open success.
   For the auxiliary path, extend observation through primary event completion
   `0x00631C70`, the decoder call at `0x00631DEB` when reached, and forwarding
   at `0x00620917`. If the alternative decoder branch occurs, record
   `0x00631970` and its queued continuation instead. Preserve actual bases,
   targets, arguments and branch
   selectors using the completion finding's ABI. An absent request or failed
   control completion is evidence to retain, not a reason to invent a dummy DAT.
5. Join each producer return Resource pointer to the later path-wrapper
   argument minus four, preserving request epoch and object lifetime. Record
   monotonic sequence, thread, caller, actual registers/stack arguments,
   numeric IDs, formatter mode, original and opened paths, open results and
   terminal completeness/dropped/output-failure counts. An open may occur
   before its producer return record; retain both for the offline join.
6. Accept new selection only when its distinct authored request set and
   correlated DAT opens are demonstrated and the retail controls retain
   their original ordered selection/path/results. Missing auxiliary payload,
   unjoined opens, failures or name reuse leave the claim unresolved.

No selector probe is performed by this contract. Static preservation across
all retail rows complements the sampled runtime controls; neither is a claim
that every retail zone was walked or that a new city rendered successfully.
