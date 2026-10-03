# Retail 1.23b login state boundaries

Launcher login checks must distinguish UI labels, native operation results,
and the identity of a player ready in the world. A menu label, loading overlay,
or arbitrary actor does not establish login success. The native checks
described below support only the stated observations.

## Binary and method

The observations target `ffxivgame.exe`, retail 1.23b, build
`2012.09.19.0001`, image base `0x00400000`, file size `15996808`, and SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
Both input copies were independently checked against this identity. Function
addresses below are absolute virtual addresses.

The reproducible static recipe is:

1. From the repository root, set the four `BCS_*` tool environment variables
   required by [the headless Ghidra setup](../tools/README.md#headless-ghidra),
   then run one read-only export for each target list:

   ```powershell
   & tools\ghidra\run-headless.ps1 -Script DumpVAs.java -ReadOnly `
       -Out '<ignored-output>\dump.txt' `
       -ScriptEnv @{ XIVL_TARGET_VAS = '0x006B0220,0x00DAA740' } `
       -ScriptPath @('ghidra')
   ```

2. Inspect the resulting instructions with portable `llvm-objdump` 22.1.4,
   using the same image and the stated absolute address ranges.
3. Record a fact only when the instruction and the matching DumpVAs entry
   agree. The producing tool baseline was
   `51be90574ef0e76da4fa432b8e095c5fe9fc574e` with Ghidra 12.1.3.

The fresh DumpVAs target sets were
`0x006B0220,0x004DFDF0,0x00DA9880,0x00DA9EC0,0x00DAA070,0x00DAA740,0x00DAA950,0x00DAA9F0,0x00DA76B0,0x00DA5030,0x00DA5110,0x00DA64B0,0x00DAD7B0`,
`0x004DFB20,0x004DFBA0,0x004DFCD0,0x004DFF10,0x004E0690,0x006AF200,0x006AD1D0,0x006A9280,0x006A4DB0,0x006A9600,0x006B3D40,0x0088C810,0x0088B070,0x008838A0`,
and
`0x00DA60C0,0x00DA4770,0x00DA4AE0,0x00DA5A00,0x00DA4660,0x00DA4390,0x00DA4370,0x00DA2BE0,0x00DA4840,0x00DA5110,0x00DA5030`.
The instruction ranges included `0x006B0200-0x006B2600` and
`0x00DA9880-0x00DAAA00`, plus direct caller ranges for the listed
`FUN_006B3D40` consumers.

Three fresh DumpVAs batches covered 13, 14, and 11 requested entries. Each
batch had exactly one `Name` section and one decompilation section per entry,
with zero `ERROR` or `DECOMP FAILED` entries. The checks are static only; no
runtime or connected-retail result is implied.

Evidence strength is explicit: direct facts have instruction locators and a
matching DumpVAs entry; projection facts describe mechanical parser behavior;
RTTI and event names are locator hints only; unresolved claims name the direct
caller or reader set that was inspected.

The read-only `tools/ghidra/export-references.ps1` wrapper also completed an
exact-string run for `OnSuccessfulLobbyLogin`, `NowLoading`, `Continue`,
`SelectCharacter`, and `ZoneLogin`: 28,414 defined strings, five queries, three
matches, two recorded references, and a `COMPLETE` marker. The only login
string reference was `OnSuccessfulLobbyLogin` at `0x00DA9FAA`, owned by
`0x00DA9EC0`; `NowLoading`, `SelectCharacter`, and `ZoneLogin` had no defined
native string match. This limits name-based native evidence and does not rule
out computed, indirect, dynamic, or script-side relationships.

## Native owners and readers

| Boundary | Native owner or reader | Supported observation | Operation boundary and limit |
| --- | --- | --- | --- |
| Title and start | `TitlePhase` RTTI/vftables `0x0105339C` and `0x010533AC`; `TitlePhase` and `InstallTitleMenu` event types | The title classes and routed event types exist in this image | RTTI and event names expose no title-visible flag, transition counter, or start operation. A title event is not a ready predicate. |
| Bootup owner | `BootupManager` vtable `0x00FD25E0`, slot 2 -> `0x006B0220` | Slot 2 is a native driver with a raw selector at `B+0x44` (`param_1[0x11]`) and counters at `B+0x1B78` and `B+0x1B7C` (`param_1[0x6DE]` and `[0x6DF]`) | These are switch and substate fields, not public UI labels. At `0x006B0D55`, one selector-10 path tests nested bytes at `+0x68/+0x69` and dispatches `0x004DFDF0`; that helper emits local operation state 3 through `0x00DA60C0` only after `0x00DA4660` accepts nested state 3, 4, or 5. |
| Service request | `ServiceLoginOperation::vtable[0]`, `0x00DAA070` | Allocates c2s opcode `0x0003`, size `0x20`, copies the request fields, writes expected s2c `0x000D` on the successful path, and returns success | The exact ABI is `ECX=O`, original stack arg 1 `P` is read at `0x00DAA0A7`, and original stack arg 2 `E` is the expected-opcode pointer. The success path stores `*E=0x000D` at `0x00DAA12E-0x00DAA136` and sets `AL=1` at `0x00DAA149`. Failure `AL=0` is set at `0x00DAA16D` without this function initializing `*E`; the two exits use `RET 8` at `0x00DAA15D` and `0x00DAA181`. This is a send boundary, not proof that a roster is loaded. |
| Roster response | `ServiceLoginOperation::vtable[1]`, `0x00DAA9F0` | s2c `0x000D` reaches the roster parser with `packet+0x10` | At `0x00DAAA79`, the receiver loads `C=[O+0x08]` into `ECX` and calls `0x00DAAA7D`. On a false parser result, `0x00DAAA86-0x00DAAA8D` passes `ECX=C` and original stack arg 1 `[O+0x34]` to `0x00DA5030`; the receiver returns `AL=0` and `RET 4`. The callback is a failure boundary, not a populated-roster proof. |
| Roster projection | `0x00DA76B0`, with context `C=[O+0x08]` | The parser owns its vector at `C+0x1D0`, with begin/end at `C+0x1D4` and `C+0x1D8`; it reads the body count and inserts records in arrival order | `C` is the parser context, not `O`. The route proves projection mechanics and vector order only; it does not prove a full identity, selected record, or generation. |
| Lobby operation request | `0x00DA9880` | The nested state at `C+0x0C`, `state+4`, selects c2s `0x01F5`, `0x0005`, `0x0006`, or `0x01F6`; expected opcodes are `0x01F5` or `0x000C`, and the request sets nested `+0x8C=4` | This is a native request state machine with no statically resolved title-button caller. Its state values are operation data, not UI labels. |
| Lobby admission response | `0x00DA9EC0` | For s2c `0x000C`, `FUN_00DA4B80(packet+0x10)` returns the parser result. For s2c `0x01F5`, a nonzero ticket at `packet+0x14` and nonempty frontend at `packet+0x1C` reach `FUN_00DA4F80(0)` after the `OnSuccessfulLobbyLogin` log | The ticket/frontend check is an auth or lobby admission edge. It returns `AL=0` after the callback and does not establish world readiness. Other opcodes write `O+0x10=4` and return false. |
| Character selection request | `GameLoginOperation::vtable[0]`, `0x00DAA740` | Allocates c2s `0x0004`, size `0x28`, copies `O+0x0C`, and reads the selected-record candidate described below; it writes expected s2c `0x000F` only on the successful path | The exact ABI is `ECX=O`, original stack arg 1 `P` is read at `0x00DAA777`, and original stack arg 2 `E` is the expected-opcode pointer. The success path stores `*E=0x000F` at `0x00DAA806-0x00DAA80E` and sets `AL=1` at `0x00DAA821`. Failure `AL=0` is set at `0x00DAA845` without this function initializing `*E`; the two exits use `RET 8` at `0x00DAA835` and `0x00DAA859`. The call does not prove that a UI selection owner supplied the record. |
| Character selection response | `GameLoginOperation::vtable[1]`, `0x00DAA950` | s2c `0x000F` reaches `0x00DA64B0(packet+0x10)`; a nonzero parser result returns true | On false, `0x00DAA9B3-0x00DAA9BA` passes `ECX=C=[O+0x08]` and original stack arg 1 `[O+0x34]` to `0x00DA5110`, then returns `AL=0`. A nonzero parser result is a lobby response result, not a world-ready identity result. |
| Separate CharaMake path | `CharaMakeOperation::vtable[0]`, `0x00DAA190`; sequence-gated response `0x00DAD7B0` | A separate step emits c2s `0x000F` and expects s2c `0x0010`; the ack compares response context `+0x10` with operation `+0x0C` before dispatching the operation callback | The reused wire opcode does not prove an ordinary roster select or confirm. The ack's operation state write and callback are a separate path. |
| Roster vector consumers | `FUN_006B3D40` and its analyzed-database direct-caller set `0x00889250`, `0x0088C4C0`, `0x0088BD50`, `0x00884CB0`, `0x006AD530`, `0x006B0220`, `0x0088B880`, plus `0x00DA79D0` | These callers index the `0x2E0` vector and read or copy entry fields such as `+0x04`, `+0x08`, `+0x10`, and `+0x40` | Within this analyzed direct-edge set, no direct call to `0x00DAA740` and no direct store to the selected-record cascade was traced. Virtual or dynamic dispatch edges remain possible, so the selected-record writer and UI admission caller remain unresolved. |
| Loading form | `NowLoading` RTTI and tracked Lua metadata names | The native RTTI type and script metadata expose form or API identifiers only; no direct ready reader is qualified in this slice | Showing or dismissing the form is not a native loading or ready predicate. |

The expected-opcode outputs are both 32-bit dword stores on the success path:
the decoded `MOV dword ptr [EDX],0xD` at `0x00DAA136` writes `*E=0x0000000D`,
and decoded `MOV dword ptr [EAX],0xF` at `0x00DAA80E` writes `*E=0x0000000F`.
Each failure path returns `AL=0` without this function initializing `*E`.

The RTTI index also identifies `CharacterSelectionPhase`,
`AccountSelectionPhase`, `Waiting`, `BootupDialog`, and
`RaptureLobbyCallback`. Those type identities locate possible owners but do not
provide a field that distinguishes title, roster loading, populated roster,
selection, confirmation, world loading, world ready, or disconnect. Type names
remain UI or class labels. Parser returns, callback writes, and `O+0x10=4`
remain native operation observations.

At verified sibling revision `xivl-client-scripts@aeef43f9721b9b011cefe8bad5a88e6784263937`,
the tracked sidecar
`xivl-client-scripts:lua/scripts/command/system/logineventcommand.calls.json:1`
identifies `LoginEventCommand`; its API rows record identifier locations for
`_fadeIn` at `:19`, `_fadeInAfterWarp` at `:22`, `_lockPlayerControl` at `:32`,
`_runCharaScheduler` at `:35`, `_unlockPlayerControl` at `:38`, and `_wait` at
`:41`. The source manifest
`xivl-client-scripts:manifests/scripts.json:7503` pins the decoded source to
203 lines and SHA-256
`07340E0EDF4669E3842B7843EEDA59DBA314CD016B9E3B9476759E1C3EB13A75`.
The tracked corpus contract at `xivl-client-scripts:lua/README.md:11` and
`:34` says these sidecars record identifier references, not script statements,
guaranteed invocations, or runtime semantics. The
producing `lua_corpus.py annotate` step is specified at
`xivl-client-scripts:lua/README.md:66`; this is metadata provenance, not a
source-body or runtime trace. The
generated index row
`xivl-client-scripts:lua/napi_index.json:13698` similarly records the generic
`_fadeInNowLoadingForNoticeEventJustInArea` API with 16 indexed callsites at
`:13709`; none of these metadata rows exposes a selected identity, native ready
state, or disconnect/error owner.

## Roster ownership, count, and identity limits

The mechanical projection is documented in
[`character-list-record.md`](../structs/ffxiv/client/network/character-list-record.md)
and
[`lobby_character_list_projection.json`](../manifests/lobby_character_list_projection.json).
The parser reads the count byte at `body+0x09` and inserts new records in
arrival order. Its vector count is the byte span from `C+0x1D4` to `C+0x1D8`
divided by `0x2E0`, available to an observer that has already qualified the
owner thread and timing. A clear flag can empty the vector before processing;
zero count, cleared, and not-yet-received therefore remain distinct runtime
questions.

The route proves only these roster keys:

- `record+0x14` is copied to slot `+0x04` and compared by
  `FUN_00DA9550` with `+0x04` of a separate `0x30`-stride operation record.
- The low six bits of `record+0x18` are the lookup key; upper bits can cause
  slot key bytes to be masked with `0x3F`.
- `record+0x50` is an unbounded NUL-terminated append source for slot `+0x40`
  on a repeated key.
- Other copied bytes stay opaque in this route. No stable character ID, full
  name, world, restriction, account, or selection field is proven by the
  `0x000D` reader.

The separate character-modify response path joins `body+0x10` to a slot first
dword, copies 32 bytes from `body+0x20` to slot `+0x10` at
`0x00DA804B-0x00DA805A`, and passes the pointer at `body+0x40` to the
`MAKECHR[wld]` logger at `0x00DA7C3F-0x00DA7C56`. This qualifies a rename
field and a world-name logging argument in that response path; it does not
retroactively assign those meanings to the opaque `0x000D` projection or prove
that either field is a complete roster identity.

Consequences for an autologin observer are:

- A copied vector is only a candidate snapshot. Static inspection does not
  prove owner-thread coherence, a generation value, or a mutation barrier.
- Exact-name uniqueness cannot be proved from this native snapshot. A stable
  native ID is preferred when a separate reader resolves one; otherwise a
  launcher must require a separate uniqueness observation.
- Restrictions and unavailable slots have no instruction-backed field in this
  route. Do not infer them from position, copied bytes, or upper key bits.
- The native account or session object is separate from a launcher username.
  No username-to-roster binding occurs in this chain.

## Request and response fragments

The static result is a set of request and response fragments, rather than a
proven normal continue/select/confirm chain:

1. `0x00DAA070` emits c2s `0x0003` and supplies expected s2c `0x000D`.
2. `0x00DAA9F0` dispatches s2c `0x000D` into `0x00DA76B0`, or to
   `0x00DA5030` on the parser-false path.
3. `0x00DA9880` emits one of the lobby state-machine requests, and
   `0x00DA9EC0` exposes the ticket/frontend admission edge.
4. `0x00DAA740` emits c2s `0x0004` and supplies expected s2c `0x000F`.
5. `0x00DAA950` dispatches s2c `0x000F` into `0x00DA64B0`, or to
   `0x00DA5110` on the parser-false path.

For the selection request, whole-pointer notation is required:

```text
R = *(*(O + 0x08) + 0x14)
payload dword = *(R + 0x0C)
payload byte  = *(u8 *)(R + 0x08)
```

The reads occur at `0x00DAA7A2-0x00DAA7A5` and
`0x00DAA7C0-0x00DAA7C6`. They prove an indirect selected-record input to the
packet builder. They do not prove whether `R+0x0C` is an ID, an index, or
another protocol key, and the static slice does not identify the writer of
`*(C+0x14)` or the UI caller that admits this operation.

The smallest typed native candidate is therefore an observation boundary:

| Candidate | Owner and validation | Result | Lifetime and staleness limit |
| --- | --- | --- | --- |
| Service send | `O` is the operation; `P` and writable `uint32_t *E` are caller arguments. The owner thread and generation are unresolved. | `AL=1` writes `*E=0x000D`; `AL=0` leaves `*E` unwritten by this function; both exits use `RET 8`; response parser or `0x00DA5030` supplies the next observation | Do not retain `P`, vector pointers, or callback pointers across a generation change. |
| Game send | `O` is the operation; `P` and writable `uint32_t *E` are caller arguments. `R` must be resolved on the same owner path before the call; no UI admission or cancellation owner is proven. | `AL=1` writes `*E=0x000F`; `AL=0` leaves `*E` unwritten by this function; both exits use `RET 8`; response parser or `0x00DA5110` supplies the next observation | The selected-record pointer and parser output can be replaced or invalidated asynchronously; copy only after a qualified owner boundary and reacquire after invalidation. |
| Nested operation gate | `FUN_00DA4660` accepts only nested `C+0x8C` values 3, 4, or 5; `FUN_004DFDF0` builds local state 3 before `FUN_00DA60C0`. | A native callback admission result, not a UI phase result | The helper has a timeout and callback queues; it does not establish a roster generation or world identity. |

No typed native continue or start operation is proven between the title/event
owners and these request boundaries. Owner thread, generation, cancellation,
selected-record writer, and UI admission remain blockers. Raw slot pointers,
embedded strings, and iterator positions cannot cross an asynchronous boundary
on the evidence here.

## Manual input and focus

[`native-input-ui-boundaries.md`](native-input-ui-boundaries.md) establishes
the native pad route, routed keyboard-focus token, ancestor-key lookup, and
modal/focus registration mechanics. These are borrowed same-thread pointers:
the route can stop on an event and focus objects can be replaced. The bounded
evidence does not identify a login-phase recipient or cancel callback.
Keyboard focus, pad routing, a modal token, and an update serial are therefore
manual intervention or invalidation observations, not proof that a login
operation is active.

## World-ready boundary

The s2c `0x000F` result closes the lobby GameLogin response loop, but it does
not prove that the world has loaded or that the displayed actor matches the
selected roster identity. The loading form has script-side metadata, but no
bounded native reader links its dismissal to a selected character. A fresh
world-ready chain must resolve all of these on the same session generation:

1. the selected roster identity used by the `0x0004` request;
2. the world identity returned or stored by the world-entry path;
3. a ready state owned by that generation; and
4. a failure or disconnect reader that invalidates all three observations.

Until those readers are traced, dismissing a prompt, observing an arbitrary
actor, or seeing the loading form hidden is not success.

## Exact unresolved discriminators

The remaining static questions are concrete:

- Which `BootupManager` callback edge maps the raw selector and counters to
  `TitlePhase`, `CharacterSelectionPhase`, `AccountSelectionPhase`, `Waiting`,
  and `BootupDialog`?
- Which writer supplies `*(C+0x14)` for
  `R=*(*(O+0x08)+0x14)`, and what thread, generation, and cancellation event
  own it?
- Which reader turns the copied `0x000D` slots into a full name, world, stable
  ID, and restriction state, and what proves exact-name uniqueness?
- Which world-entry reader supplies a selected-identity match and ready state,
  and which disconnect or error reader invalidates that match?

## Adoption map

| Public source | Supported observation or boundary | Blocker |
| --- | --- | --- |
| [`character-list-record.md`](../structs/ffxiv/client/network/character-list-record.md) and [`lobby_character_list_projection.json`](../manifests/lobby_character_list_projection.json) | After a qualified s2c `0x000D` parser return, copy only the documented vector count, arrival order, and explicitly named keys | Full identity, restrictions, loading-versus-empty, owner thread, and generation are unresolved |
| This page's native-owner and request-fragment sections | Observe c2s `0x0003`/s2c `0x000D`, lobby admission fragments, and c2s `0x0004`/s2c `0x000F` results with the stated ABI and failure callbacks | No typed title admission, selected-record writer, cancellation owner, or world-ready match is closed |
| [`native-input-ui-boundaries.md`](native-input-ui-boundaries.md) | Observe routed input and borrowed focus tokens as same-thread intervention or invalidation clues | Login-phase recipient and modal ownership are unresolved |
| This page's world-ready section | Require a fresh selected-identity plus matching world-ready observation before reporting success | No native world-ready identity chain is closed |

The launcher username remains an external account label until a native
account-binding reader is resolved.
