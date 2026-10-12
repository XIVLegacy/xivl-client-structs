# Structs

Struct notes are grouped by subsystem. Keep the durable machine inventory in `manifests/structs.json`. Use these folders for supporting notes when a struct needs more explanation than a manifest entry can carry.

- [Lobby character-list record projection](network/character-list-record.md)
- [ZoneClient RaptureChannelManager layout](network/zone-channel-manager.md)
- [ZoneProto buffer-factory partial layouts](network/buffer-factory.md)
- [ZoneProtoUp NetBufferTmpl layout](network/net-buffer-up.md)
- [ZoneProtoDown NetBufferTmpl layout](network/net-buffer-down.md)
- [Down receive-result record](network/receive-result-record.md)

## Subsystem scope

- `FFXIV.Client.Game`: Gameplay-facing client structures, including inventory, character, quest, action, and state managers when source-backed.
- `FFXIV.Client.System`: Framework, scheduler, resource, memory, file, and system-service structures when source-backed.
- `FFXIV.Client.UI`: UI module, addon, agent, text, input, menu, and shell structures when source-backed.
- `FFXIV.Common`: Common containers, math types, strings, allocators, and low-level helpers when source-backed.
- `FFXIV.Component.GUI`: GUI component structures, including nodes, resources, events, and rendering-facing layout data when source-backed.
