# Linkshell rank and 0x017A work contract

This record covers the 1.23b linkshell implementation identified as community
group type `20002`, and the native receiver for map s2c opcode `0x017A`.
Claims below use the frozen decoded Lua corpus and the exact retail client
binary. The native decompiler output is used as a locator and control-flow
description; it is not source code.

## Identity and source boundaries

The native input was `ffxivgame.exe`, a 32-bit PE image with size `15996808`
bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, and
image base `0x00400000`. REA used the `ghidra` provider, observed Ghidra
`12.1.3`, and reported analysis profile digest
`44bc792e0da2f944576805bbd496f5de8b85f040449b1daa16ebf6d298518d1b`.

The script paths below are the exact entries in
`xivl-client-scripts:manifests/scripts.json`:

| Script | Bytes | SHA-256 | Manifest lines |
| --- | ---: | --- | --- |
| `group/communitygroup/companygroup.lua` | 9896 | `C7B931666F80EAF47FDF033A4F749DBFAFF4CA88547E274C14CB3D4BB5B54E0E` | 9561-9564 |
| `command/system/linkshellkickcommand.lua` | 3522 | `F5960D95AC01B3CE2659CABA014354AAACA4AD86A5F90996B0E46E95E53E679D` | 7491-7494 |
| `command/system/linkshellappointcommand.lua` | 3985 | `CBFB53F5CD1ABE8D322592CD05808E251E7B6B4D3139061E4691F6AFFD638A60` | 7467-7470 |
| `widget/ask/linkshelllistwidget.lua` | 8381 | `972C23332019A49EDE0CE1E48592F8F56A93FC678C9DC229CEA8E4DC497BB3B1` | 15021-15024 |
| `widget/linkshellmemberslistwidget.lua` | 10085 | `0E6350D37859499D7524DACED5CEE933D7FEB30D474BDAFA90E74896A5BDEEF3` | 15591-15594 |
| `widget/linkshellmenusubwidget.lua` | 10590 | `339976897789EA6E546CA3B8F066ACD375DD9C31D3687BC5D32654F5055DEA0A` | 15597-15600 |
| `widget/linkshellmenuwidget.lua` | 8219 | `AD8F857551A6F6B57E319ECE55EC9D69A9E1EC6BE83646264961C5264E1ABA5E` | 15603-15606 |
| `widget/desktopwidget_connector.lua` | 660617 | `9C33F21C1F70A0056147E716D53300634EFABE5B744EF6E8690114DB21613A01` | 15399-15402 |
| `chara/npc/populace/populacelinkshellmanager.lua` | 26951 | `E17548300E1BE2B8E10CB998FE687A8BA5542346FCE4191E6689BE0F6976A891` | 6453-6456 |

The wire layout and native route are cataloged in
[`manifests/party_subsystem.json`](../manifests/party_subsystem.json#L191),
and the frozen capture limits are in
`xivl-captures:studies/group-combat-wire-contracts/README.md:78-112`.

## Type-20002 rank fields

`group/communitygroup/companygroup.lua:89-219` creates the work shape. Each
`_memberSave[*].rank` is declared `integer8` at lines 123-135. The separate
`_globalSave.rank` is also declared `integer8` at lines 136-161. The `baseInfo`
tag maps `_globalSave.rank`, while `memberRank` maps
`_memberSave[*].rank`, at lines 162-202. The member rank array is bound through
the work update path at lines 203-216.

`getCompanyRank` at `companygroup.lua:22-30` reads
`work._globalSave.rank`. A complete literal search of the frozen corpus found
no caller for `getCompanyRank`; line 30 is its only occurrence. The script
function `updateRankInGroup` is empty at `companygroup.lua:382-386`. The
linkshell manager calls that function while refreshing every live type-20002
group (`populacelinkshellmanager.lua:1267-1302`, with call sites at
321-322, 1064-1065, 1107-1108, and 1145-1146), so those calls do not establish
a positive `_globalSave.rank` consumer.

`getMemberRank` at `companygroup.lua:482-515` accepts either a numeric member
index or an actor resolved by `getMemberIndex`. An index outside the
member array returns `0`; a valid index returns
`work._memberSave[index].rank`. The frozen corpus has 16 direct `getMemberRank`
call sites; those calls read the member array:

| Consumer | Locator | Use |
| --- | --- | --- |
| `LinkshellKickCommand` | `command/system/linkshellkickcommand.lua:42-57,75,104-110,113-160` | Gets the current type-20002 group, requires the actor rank to be at least `7`, then requires actor rank to exceed the target rank. The nil-target branch resolves the identifier to a member index; the nonnil branch validates an explicit target actor with `_isAlive`/`isPlayer`, then checks `_isMember`/`getMemberRank` for that actor. |
| `LinkshellAppointCommand` | `command/system/linkshellappointcommand.lua:57-72,97,126-132,135-182` | Applies the same `>=7` actor gate and strict actor-over-target comparisons. The nil-target branch resolves the identifier to a member index; the nonnil branch validates an explicit target actor with `_isAlive`/`isPlayer`, then checks `_isMember`/`getMemberRank` for that actor. |
| Linkshell list display | `widget/ask/linkshelllistwidget.lua:154-185,211-218` | Reads the local player's member rank for each type-20002 group and maps it through `getLinkshellRankIcon`. |
| Member list load and row display | `widget/linkshellmemberslistwidget.lua:128-162,268-360` | Reads the local player's rank, stores each row's `MemberRank`, and renders the rank icon, visibility, help text, member id, and rank value. Rank `7` and rank `10` get distinct help ids. |
| Current linkshell menu | `widget/linkshellmenuwidget.lua:189-191,222-258`; `widget/desktopwidget_connector.lua:19083-19105`; `group/communitygroup/companygroup.lua:348-367` | The owner branch takes icon `383` when `isMyCurrnetLinkshell` reaches `CompanyGroup.isOwner`, which reads `_globalSave.master`. The non-owner branch reads local member rank and selects icon `384` only for rank `7`; the owner icon `383` here is not a rank `10` member read. |
| Member action subwidget | `widget/linkshellmenusubwidget.lua:63-80,106-138,264-278,323-346` | Initializes action booleans from the local member rank passed by the member list: rank `10` enables both, while rank `7` enables the second only when the selected row rank is `4`. Login state gates `Button_4` and `Button_5` at lines 106-125. It stores the selected row rank, maps rank `7` to appointment role `4` and other ranks to role `7`, and invokes kick at lines 350-362 after a current-linkshell validity check. |
| Linkshell owner display | `widget/desktopwidget_connector.lua:19121-19147` | Scans type-20002 members and uses rank `10` to select the localized owner name. |
| Invite eligibility | `widget/desktopwidget_connector.lua:19198-19221` | Allows the current linkshell invite path for local rank `7` or `10`. |
| Member row status | `widget/desktopwidget_connector.lua:19341-19393` | Reads each member rank; rank `0` changes the row's client/member status before the list item is written. |

The rank icon mapping helper itself is at
`widget/desktopwidget_connector.lua:19490-19508`: rank `7` maps to icon
`384`, rank `10` maps to icon `383`, and other values map to `0` for callers
that use `getLinkshellRankIcon`. The current menu's owner icon `383` is
assigned separately by the `isMyCurrnetLinkshell` / `_globalSave.master` path
above. The `memberRank` work update at `companygroup.lua:297-303` calls
`processUpdateCurrentCommunityGroup`; its connector implementation refreshes
the linkshell list and member list at `desktopwidget_connector.lua:19513-19555`.

The rank consumer conclusion is field-specific: type-20002 display and
command gates read `_memberSave[index].rank` through `getMemberRank`. The
frozen corpus contains no literal/static script display or gate consumer of
`_globalSave.rank`; this does not bound native generic-state reads.

## Native `0x017A` receiver

The party manifest describes s2c `0x017A` as
`SynchGroupWorkValuesPacket`: `groupId` at offset `0`, the one-byte
`runningByteTotal` at offset `8`, and a variable property stream at offset `9`.
The manifest records `0x62` as a two-byte generic buffer and target trailers
as `0x82 + ASCII length`; its continuation semantics remain unestablished.

The exact client call path is:

`FUN_004DC690` case `0x017A` -> `FUN_005763B0` -> `FUN_006C9910` ->
`FUN_006C96B0` -> `FUN_006C84A0`.

`FUN_005763B0` is an eight-byte trampoline whose only outgoing edge is the
tail call to `FUN_006C9910`. `FUN_006C9910` forwards its packet argument into
`FUN_006C96B0` and returns with a four-byte stack cleanup. In
`FUN_006C96B0`, the byte at packet offset `8` controls a temporary vector;
exactly that many bytes are copied from packet offset `9`, then the temporary
vector is passed to `FUN_006C84A0`. The temporary allocation is released after
the call.

The parser thresholds are the initialized client bytes at `0x00FE059B`,
`0x00FE05A0`, and `0x00FE05A1`, observed as `0x60`, `0x82`, and `0xA4`.
`FUN_006C84A0` walks the current temporary stream and uses these classes:

- Tags below `0x60` are typed properties. The parser reads the four-byte
  property id, resolves it, and invokes the resolved property's setter while
  the current packet is being parsed.
- Tags from `0x60` through `0x81` are buffer records with length `tag -
  0x60`. Consequently, `0x62` consumes a two-byte buffer. It follows the
  generic buffer path, creates a flag-`0` work record, queues that record in
  the current invocation, and calls `FUN_006C72E0`.
- Tags from `0x82` through `0xA3` are target records with length `tag -
  0x82`. Their target bytes are kept in a per-invocation work record and are
  consumed by the post-parse `FUN_006C7020` loop. `0x62` does not enter this
  target path and does not retain a target trailer.
- Tags at or above `0xA4` use the other generic buffer class and also route
  through `FUN_006C72E0`.

For the `0x62` generic path, `FUN_006C72E0` prepares a queued buffer record
and calls `FUN_0075E950`. That function copies the record bytes into the c2s
`0x0133` payload, sets event type `0x133` and event size `0x38`, and submits it
through `FUN_004D6D30`. The static route establishes queued construction and
wire direction; it does not establish an incoming Lua callback. After the
stream loop, `FUN_006C7020` walks the queued records and performs deferred
record handling before `FUN_006C84A0` frees its local property and record
vectors. The high-level meaning of the two bytes and their relation to an end
marker remain unresolved.

The context retains a copy of the most recent temporary stream. Before
parsing, `FUN_006C84A0` calls `FUN_006D1A30` to compare the current stream's
length and bytes with the context-owned stream at `context + 0x3c`. An equal
stream returns before parsing. Otherwise `FUN_006D5BA0` copies the current
stream into that context buffer, replacing its contents or reallocating it;
the copy is not appended to a prior stream. The parser's property and record
vectors are initialized and freed on each `FUN_006C84A0` invocation.

Across multiple `0x017A` packets, this static path establishes per-packet
stream construction, duplicate suppression, and per-packet application. It
does not establish how the server uses `0x62` across packets, whether one
`/_init` spans packets, or which event/callback boundary consumes the resulting
`0x0133`. The manifest's continuation note remains a wire-level annotation
whose high-level meaning is unresolved.

## Native evidence IDs

These REA Evidence IDs identify the producing observations promoted in this
record. Each is reproducible from the pinned binary identity above, the
function VA or data VA in the table, and the listed REA tool call. The
Evidence ID records the original producing observation, while this tracked
document carries the claim. Function dossiers use
`analyze_function({procedure:"VA"})`; exact branch evidence uses
`procedure_assembly({procedure:"VA"})`; threshold evidence uses
`read_bytes({address:"0x00FE059B",length:16})`.

| Evidence ID | Native locator | Producing tool | Observation |
| --- | --- | --- | --- |
| `ev_e1ce8f67c61404779acda924d854f9755fed7a0185428f2607550a6aa8ee3579` | `FUN_005763B0` | `analyze_function({procedure:"0x005763B0"})` | `0x017A` handler trampoline tail-calls `FUN_006C9910`. |
| `ev_0afa4f7df0e5de6ddf17dbb90fcd80b3afdaebdea70f4abfcc7818356611400c` | `FUN_006C9910` | `analyze_function({procedure:"0x006C9910"})` | Forwards the packet argument to `FUN_006C96B0`; exact body range and stack cleanup observed. |
| `ev_32b8ca9f915ab78ad3a0baaf62da2724fde15f6656f789f254ce9549adc3aed7` | `FUN_006C96B0` | `analyze_function({procedure:"0x006C96B0"})` | Reads packet byte `8`, copies the packet stream from byte `9`, calls `FUN_006C84A0`, and releases the temporary buffer. |
| `ev_448a1f8164d4a3291d56b774304cbb9abed07666956690a56b8b88d24ae119bb` | `FUN_006C84A0` | `analyze_function({procedure:"0x006C84A0"})` | Complete parser body, property loop, marker classes, post-parse queue loop, and cleanup. |
| `ev_7e93f0bb3cfcfeeff9bd76ca456cda5c42da4a35593d9d51178672dae75eedd5` | `FUN_006C84A0` assembly | `procedure_assembly({procedure:"0x006C84A0"})` | Exact threshold comparisons, setter call, generic `0x60`-class route, target route, and deferred loop call sites. |
| `ev_c941dcdef468907f23b0991f57cf13418ec04a46eab8b9e61b2452bfaedd0c9c` | `0x00FE059B` | `read_bytes({address:"0x00FE059B",length:16})` | Initialized parser threshold bytes, including `0x60`, `0x82`, and `0xA4`. |
| `ev_4847192d0d04b89a6a1e7cd36d2d8ef0f18175b36347a7f692596a787da78247` | `FUN_006D1A30` | `analyze_function({procedure:"0x006D1A30"})` | Equal-length byte comparison used before parse; equality returns the duplicate-suppression result. |
| `ev_b8614ed9aae5fe794c06e58e3e0bb5e9166de0273e4fc2852d558c4d2f2ff5f3` | `FUN_006D5BA0` | `analyze_function({procedure:"0x006D5BA0"})` | Replaces or reallocates the context-owned stream copy from the current temporary vector. |
| `ev_0effefa0abf75f61dfe001c5925695a6ac4f34941da7771494a0a9994e9f9d5d` | `FUN_006C72E0` | `analyze_function({procedure:"0x006C72E0"})` | Generic buffer record preparation and queued c2s `0x0133` emission setup. |
| `ev_d3b72737b9e486304b83e04f56037ede0589ebbe8d2184e13053ca8873439c10` | `FUN_0075E950` | `analyze_function({procedure:"0x0075E950"})` | Copies the buffer record into a c2s `0x0133` payload, size `0x38`, and submits it through `FUN_004D6D30`. |
| `ev_6f0e0923595771f108ca4c93511da4e4fbd5643156046f73ab5da98d8453d450` | `FUN_006C7020` | `analyze_function({procedure:"0x006C7020"})` | End-of-current-parse queued-record processing. |
| `ev_5d8e8e3b30f9ee1caa01b756de6f2e7735b4e62bcb8ca176e2256b0ca9b5e8e3` | `FUN_006BF7C0` | `analyze_function({procedure:"0x006BF7C0"})` | Stores the record property count and class flag used by the queued record. |

REA reports Ghidra decompiler types and pseudocode as provider-derived
representations. Calling-convention names, recovered types, indirect setter
targets, and the business meaning of c2s `0x133` remain qualified by that
limit. The static records prove the parser's byte classes and call order; they
do not prove server scheduling, Lua callback consumption, or high-level `0x62`
meaning.

## Frozen-corpus runtime boundary

The existing capture study has no type-20002 player-linkshell group and no
observed `0x62` continuation specimen. Its observed target tags are `0x88`,
`0x97`, `0x9A`, and `0x9B`, and repeated same-group packets are explicitly not
continuation evidence (`xivl-captures:studies/group-combat-wire-contracts/README.md:89-103`).

The exact missing retained evidence for the remaining runtime claim is a
capture preserving:

- the type-20002 group header;
- two `0x017A` packets for the same group in per-direction wire order;
- the full two-byte payload following each `0x62` tag and all following
  property or target data;
- the group-created c2s `0x0133` emission and the corresponding `/_init`
  event/callback boundary, if present in the capture's observable trace; and
- observable member/rank state sufficient to test whether the update reached
  the type-20002 work object.

Until that retained specimen exists, the `0x62` high-level meaning, its
multi-packet use, the packet boundary for one `/_init`, and the consumer
boundary for c2s `0x0133` remain unresolved. The frozen corpus supplies no
acquisition path or runtime proof for those claims.
