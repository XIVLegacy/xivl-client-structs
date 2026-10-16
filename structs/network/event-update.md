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

## Builder and copied extent

Builder `0x0075E670` writes opcode `0x012E` and record body length `0x68`.
The application begins at record `+0x18`; the body length includes a
separate `0x10`-byte game-message prefix. The resulting application length
is `0x58` bytes.

| Application offset | Bytes | Native provenance |
|---|---:|---|
| `0x00` | 4 | First DWORD of the supplied context record, from the wrapper's resolved binding through `0x00CC73B0` and `0x00CC7030` |
| `0x04` | 4 | Context record `+0x08`, copied by `0x0075D460` from its input `+0x14`; its domain meaning is unresolved |
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
