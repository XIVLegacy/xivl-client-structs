# Packet Headers

Wire framing structs for the three concurrent IPC channels. The
machine-readable layout lives in `..\..\..\..\manifests\structs.json`
(`BCS-S-0001` BasePacketHeader, `BCS-S-0002` SubPacketHeader,
`BCS-S-0003` GameMessageHeader, `BCS-S-0004` RetainerListRecord).

## Layering

A wire frame is one `BasePacketHeader` followed by `num_subpackets`
subpackets. Each subpacket is one `SubPacketHeader` plus a body. When
`SubPacketHeader.type == 0x03`, the body starts with a
`GameMessageHeader` followed by the per-opcode payload.

```
+------------------+
| BasePacketHeader |  16 bytes
+------------------+
| SubPacketHeader  |  16 bytes
+------------------+
| (type 0x03 only) |
| GameMessageHeader|  16 bytes
+------------------+
| payload bytes    |
+------------------+
| ... more subpackets, each with its own SubPacketHeader ...
```

## Channels

Captured chat traffic shows `0x0000` in
`BasePacketHeader.connection_type` (bytes 2..3), so the per-channel numeric
assignment is treated as `blocked`.

## Timestamps

Captured chat traffic shows real Unix-epoch timestamps (for example,
`0x50E0F572`). Packet builders should emit real Unix-epoch timestamps on chat
frames, not the `0x0A` constant.

## Sequence Numbers

There is no IPC-level sequence number. Reliable delivery and ordering live at
the transport layer below this framing.

## Cross-References

- `..\..\..\..\manifests\symbols.json` for the BuildHeader function
  RVAs (BCS-Y-0004 lobby/zone variant, BCS-Y-0005 chat variant) and
  the lobby down dispatch tables (BCS-Y-0001 .. BCS-Y-0003).
