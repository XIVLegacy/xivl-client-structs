# Command-slot actor and category context

[Documentation index](../README.md)

The retained server-to-client `0x0137` property corpus contains 394 writes to
resolved `charaWork.command[index]` paths. Of those, 374 are nonzero and use 52
unique actor IDs. Every unique value matches the established static-actor
partition `(actorId & 0xffff0000) == 0xa0f00000`. Masking the low 16 bits gives
a qualified cross-artifact join: all 52 values match both the retail SAN
class-path catalog and the command catalog. The transform is directly proven
for qualifying EventStart owner IDs; no native command-slot producer proves
that the same transform is intrinsic to this field.

The result is reproducible in
`manifests/command_slot_context.json`. Its generator consumes explicit capture
and client-data checkouts, pins their commits and input hashes, and refuses an
incomplete static-actor or command-catalog join.

## Category observations

The property stream is ordered within each reconstructed capture lane. The
generator resets state at each `(capture, lane_index, source_actor_id)`, applies
command-slot writes in record order, and joins a category write to the current
nonzero command actor in the same slot.

This produces 174 category observations for 26 command IDs. The manifest keeps
them grouped by command ID and array slot because a command can occur in more
than one slot. Every observation has value 1. The other 66 category writes
occur without a current nonzero command for that slot in the retained lane, so
they remain unjoined. No value 2 occurs anywhere in the 240 retained category
writes.

These are partial corpus observations. They do not establish a semantic name
for value 1, the complete category domain, a category assignment policy, or the
native bridge from the property sync cache to Lua work binding 3003.

## Reproduction

```text
python tools/extractors/build_command_slot_context.py --captures-repo <xivl-captures> --client-data-repo <xivl-client-data>
python tools/extractors/build_command_slot_context.py --captures-repo <xivl-captures> --client-data-repo <xivl-client-data> --check
```
