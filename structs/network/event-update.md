# C2S EventUpdate fields and talk-request boundary

C2S `0x012E` EventUpdate contains a 64-byte serialized parameter block. The
normal callback-completion route checksums that block with CRC32. Its final
seven application bytes are copied from an
unwritten stack tail. They have no established selector meaning.
`BCS-S-0014` in [the struct catalog](../../manifests/structs.json) owns the
machine-readable layout.

## Binary and method

The target is retail `ffxivgame.exe`, build `2012.09.19.0001`, 15,996,808
bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
Addresses are VAs at image base `0x00400000`, x86 little-endian 32-bit.
Selected function bytes were read from PE sections with pefile 2024.8.26 and
decoded with Capstone 5.0.7, then compared with complete read-only Ghidra
function listings. All 41 selected complete bodies, including disjoint
ranges, agreed with the pinned file and the two completed listings. No client
execution is claimed.

The producing tools are [DumpVAs.java](../../ghidra/DumpVAs.java),
[DumpFunctionListing.java](../../ghidra/DumpFunctionListing.java), and
[VerifyProgramFileBytes.java](../../ghidra/VerifyProgramFileBytes.java).
Their SHA-256 identities are, respectively,
`01b64442746c9652cdc9ef1387d0367af481d68a484c48f0096538a5ecb5c344`,
`59c1c0a2f0852d5919728acb1dedff3dbec15a8b3c3b0904b27297f6c3e7f465`,
and `0277d0f837006579432673172d827a9340b74a55b15fb1c15137cebf320e64bb`.
The selected exports completed. Retained original and modified file bytes,
and initialized file-backed mapped ranges, matched the pinned input.
Excluded ranges remain outside that authentication.

The context provenance trace below separately authenticated the selected
complete function bodies against the same PE with pefile 2024.8.26 and
Capstone 5.0.7 in x86-32 mode. Every retained instruction byte matched the
file, and decoding covered every byte in each selected body span, including
disjoint spans. The `0x00CC` dispatch table entries at `0x004D8C24` and
`0x004D8BC0` were read directly from the PE. This check establishes the
listed static paths, not every possible alias or historical runtime value.

## Builder and copied extent

Builder `0x0075E670` writes opcode `0x012E` and record body length `0x68`.
The application begins at record `+0x18`; the body length includes a
separate `0x10`-byte game-message prefix. The resulting application length
is `0x58` bytes.

| Application offset | Bytes | Native provenance |
|---|---:|---|
| `0x00` | 4 | First DWORD of the supplied context record, from the wrapper's resolved binding through `0x00CC73B0` and `0x00CC7030` |
| `0x04` | 4 | Context record `+0x08`, copied by `0x0075D460` from the cached incoming `0x00CC` prefix dword at its input `+0x14`; see the provenance below |
| `0x08` | 4 | Sign-extended byte supplied by the caller; normal callback completion supplies the byte at `0x0134C3FC` |
| `0x0C` | 4 | CRC32 returned through `0x00D3AAE0` after `0x00D3AB60` processes the supplied parameter span; normal completion supplies length `0x40` at `0x00894B4C` |
| `0x10` | 1 | Supplied event-type byte; the normal completion route obtains it through `0x00892550` and current event-condition virtual slot `+0x14` |
| `0x11` | 64 | Parameter buffer copied by the 16-DWORD loop at `0x0075E714-0x0075E723` |
| `0x51` | 7 | Stack bytes outside the builder's initialized prefix and parameter block |

The checksum helper receives a separate eight-byte object preceding the
packet record, plus the input buffer and size. It does not initialize the
packet tail. The inspected builder has no packet constructor or zeroing
operation that fills `0x51-0x57`.

The checksum core `0x00D3A380` complements on entry and exit and uses the
256-entry table at `0x01110808`. Every entry matches reflected CRC32
polynomial `0xEDB88320`. The global at `0x0134C3FC` is outside the
authenticated file-backed ranges. Its address is proved as an input, but
its historical runtime value remains unknown.

Forwarder `0x00DAE010` copies from record `+0x18` for body length minus
`0x10`, including those seven unwritten bytes. This establishes the copied
extent without assigning a stable value to the tail. The builder's complete
247-byte body has SHA-256
`6f48df642eb8d2bf4700aa6a3a6277904c60578db3bf08d3bd774e1af43212bf`.

`xivl-captures:studies/local-guildleve-dialogue` records the independent wire
check: every one of the 71 EventUpdates in `local_leve_complete.pcapng` has
`zlib.crc32` of its exact 64-byte parameter block at application `+0x0C`.
The two retained quest-choice replies have equal first 81 application bytes
and differing seven-byte tails. The static writer trace supplies no
initialized selector in those differing positions.

## Context dword provenance and correlation

Application `+0x04` comes from shared cached state from incoming records, with
confirmed static provenance. Its numerical identity domain remains
unresolved. It is not produced from the completed request's owner, event
name, result container, or Lua thread on the inspected reply paths.

At `0x008940BA-0x008940C9`, the reply wrapper calls `0x00CC7510`,
dereferences its returned holder, and uses the holder's pointer at `+4` as
the receiver of `0x0075D460`. `0x00CC7510 -> 0x00CD7910` returns
`[wrapper context]+0x220`. On the traced construction route, the holder's
payload is the object constructed by `0x00773270`. Caller `0x0057A3C0`
passes that object from its own `+4` at `0x0057AA9E-0x0057AAB1`;
`0x007634B0` wraps its second argument through
`0x00779B50 -> 0x00778D80` at `0x00763628-0x00763634`, then installs the
holder through `0x00CC9820 -> 0x00CD78E0` at `0x00763648`. The holder
constructor stores the supplied pointer at `0x00778DC1`; the installation
store is `0x00CD7902`.

The outer object's `+0x510` supplies the `0x0057A3C0` receiver at
`0x004D7AD4-0x004D7ADA`. The special incoming branch first loads its outer
pointer from dispatch receiver `+0x7C` at `0x004D8899`, then adds `0x510`
and calls `0x00575860` at `0x004D88A5-0x004D88AB`. Constructor
`0x004DAB50` copies its third argument to receiver `+0x7C` at
`0x004DAB95-0x004DABA9`. On the documented factory route, wrapper
`0x004D90C0` supplies outer pointer `W` and `W+0x510` as the third and
fourth arguments at `0x004D90DC-0x004D90ED`; the four-argument forwarding
through `0x00537620 -> 0x00533540 -> 0x0058B4E0 -> 0x00534090` preserves
them into `0x004DAB50`. This parent-pointer producer is documented by
`xivl-decomp:docs/input/chara-interface-attachment.md`, sections
"Container, factory and child" and "Constructor attachment". The copied
outer pointer, rather than equal offsets alone, joins the two uses of
`+0x510`.

The reached writers of this object's `+0x14` are:

| Writer | Source and condition |
|---|---|
| `0x00773338` in constructor `0x00773270` | Initializes the dword to zero. |
| `0x00758E8B` in `0x00758E80` | Copies the supplied dword when it differs. The special `0x00CC` branch at `0x004D8883` passes game-message `+0x10` through `0x00575860` at `0x004D88AB`; that wrapper selects its object's `+4` receiver at `0x00575888` and calls the setter at `0x0057588C`. |
| `0x00774BE6` in `0x00774AD0` | Copies the ordinary `0x00CC` application's first dword when it differs. Dispatch arm `0x004D88E2` passes game-message `+0x10` to `0x00574780` at `0x004D8902`, which calls `0x00774AD0` at `0x005747FB`. The consumer resolves the same holder/payload chain at `0x00774B39-0x00774B49`, then reads application `+0` at `0x00774BDA`. |

The ordinary incoming record is independently documented by
`xivl-decomp:config/actor_instantiation.json`, `record.firstDword`. Neither
that record nor these copies establishes whether the source dword denotes
an actor, sequence, generation, connection, or another server-side domain.
The first remaining semantic edge is the identity assigned to incoming
`0x00CC` application `+0`, beyond its unchanged copy into this cache.

Equal offsets do not join unrelated objects. Setter `0x0075D230` writes
the separate object reached through this payload's `+0x10C` at
`0x00578D22-0x00578D28`; constructor `0x00773270` allocates that object
through `0x0076DF60` and stores its pointer at `0x00773472`. The later
`+0x14` store at `0x00774F2E` likewise follows a receiver change to
`[payload+0x10C]` at `0x00774EB4`. Neither store writes the cached dword
read by `0x0075D460`.

Normal completion at `0x00894B65` and both refusal sends at `0x008970ED`
and `0x0089722B` use `0x00894090` and its same context resolution.
They read the cache at send time. No request-specific snapshot, increment,
generation of a fresh token, or comparison with the request is present in this
copy chain. Replies can therefore retain the same dword while the cache is
unchanged, including across normal and refusal paths. A different dword
establishes a different observed cached value; it does not establish a new
booking invocation. This field alone has no supported stale- or
duplicate-reply rejection contract.

To reproduce the finite check, verify the binary identity above and decode
the complete bodies of the cited constructors, wrappers, setters and reply
builder directly from their file-backed PE spans. Assert the receiver chain
at `0x008940BA-0x008940C9`, the holder stores at `0x00778DC1` and
`0x00CD7902`, and the three writer sites in the table. For the ordinary
dispatch, assert byte zero at `0x004D8C24` and dword `0x004D88E2` at
`0x004D8BC0`. For the special branch, assert its outer-pointer load at
`0x004D8899`, the constructor argument copy at `0x004DAB95-0x004DABA9`,
and the factory's four-argument forwarding described above. Check the
receiver changes before the two excluded `+0x14`
stores, and the three completion/refusal calls to `0x00894090`. Require
full-span byte agreement and decode coverage before accepting the result.

## Named talk request

Registrar `0x00736FC0` binds the native name `_callServerOnTalk` to
`0x006E9520`. The implementation converts a supplied player and request name,
finds the named talk condition, and follows the generic EventStart path.
This is a request lookup, with no identified `passiveGL_craft` read or text-ID
choice. The separate Lua `_callServerOnTalk_cpp` inline marker does not by
itself prove an alias to this registration.

Talk-condition vtables `0x01056E74`, `0x01056F44`, and `0x01056F78`, slot
`+0x14`, target `0x00899800`. That accessor returns the address `0x012C3F7A`,
whose pinned file byte is `1`. This supports the talk-kind byte without
assigning a source-column meaning to another prefix field.

The surrounding Lua and capture state evidence is owned by
`xivl-client-scripts:docs/passivegl-dialogue-producer.md`. Neither this
request path nor the EventUpdate layout identifies the sender's text-ID
selection routine or its state predicate.
