# RetainerListRecord

48-byte record carried by the RetainerList lobby packet (opcode `0x17`,
deserializer `FUN_00DA4D80` per MDI-004 / MDI-017 promotion ledger
distillation). The machine-readable layout lives in
`..\..\..\..\manifests\structs.json` (`BCS-S-0004`).

## Layout

| Offset | Size | Field | Notes |
|---|---|---|---|
| `0x00` | 4 | `id` | Retainer id. |
| `0x04` | 4 | `character_id` | Owning player character id. |
| `0x08` | 2 | `total` | List/index counter. |
| `0x0A` | 2 | `do_rename` | Client-visible needs-rename flag. The retainer rename UI keys on this. |
| `0x0C` | 4 | `zero` | Always zero. |
| `0x10` | 32 | `name` | Zero-padded retainer name buffer. |

## Related Routes

- `ServiceLoginOperation::vtable[1]` (`FUN_00DAA9F0`) dispatches opcode
  `0x17` to `FUN_00DA4D80(packet+0x10)` with log strings `"CHR_SEQ:"`
  and `"CHR_Count:"`.
- `CharaMakeOperation::vtable[1]` (`FUN_00DAAC30`) opcode `0x0E`
  sub-switch carries the matching rename request (string pool includes
  `"CALL onRenameRetainerName"`).

## Cross-References

- `..\..\..\..\manifests\symbols.json` `BCS-Y-0022` (`FUN_00DA4D80`).
