# Appearance record payload

Clientbound `0x00d7` uses an array of eight-byte records. Each record has a
little-endian dword value at `+0`, a byte slot index at `+4`, and three bytes
not read by the inspected handler. The count is a byte at application
`+0x80`. A count of one selects one record; the handler also processes
multiple records.

The [native contract](../manifests/appearance_record_wire_contract.json)
records authenticated instructions and the distinction between application
offsets and the handler's packet pointer. The handler passes each record to
`0x00586870`, which writes `actor+0xaac+4*index` for indices below 28 and
marks the actor dirty. No write occurs for an out-of-range index.

The count offset proves a minimum readable application extent of 129 bytes.
Sixteen records fit before it, but the loop itself does not clamp the count.
No retained capture establishes the complete packet length or trailing bytes.
`0x00d6` has the same record base and format with its count farther along at
application `+0x100`; that difference is array space, not a larger preamble.

The native apply path does not establish which server event selects each
slot, the legal values, or a single-record-only server policy.
