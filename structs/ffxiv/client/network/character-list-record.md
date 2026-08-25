# Lobby character-list record projection

Lobby s2c `0x000D` enters `FUN_00DAA9F0` (`BCS-Y-0017`) and reaches
`FUN_00DA76B0` (`BCS-Y-0019`) with the packet body.
The canonical field, branch, and evidence table is
[`manifests/lobby_character_list_projection.json`](../../../../manifests/lobby_character_list_projection.json).

The parser's indexed unit is a `0x1D0` window. For a new low-six-bit slot key,
it copies `window+0x10` for `0x1D0` bytes into a temporary `0x2E0`
`CharaMakeSlotEntry`, zeroes destination `+0x1D0..+0x2CF`, initializes the
embedded vector at `+0x2D0`, and pushes the result. For an existing key it
instead appends the NUL-terminated string at `window+0x50` to the string at
slot `+0x40`.

This is a mechanical projection contract, not a semantic decode of the copied
wire bytes. The unnamed spans remain opaque. The parser also supplies no
payload-length check and no bound for either C-string scan or the append.
