"""Client PE extraction toolkit.

Surfaces:
- rtti_dumper        scan PE for .?AV markers, walk to TypeDescriptor -> COL -> vtable
- vtable_analyzer    walk a class vtable, estimate function sizes / detect stubs
- import_table_dumper PE import directory walker
- string_extractor   find string xrefs from a function or by literal value
- struct_analyzer    constructor decomp -> field offsets + sub-objects

CLI: `python -m tools.extractors.client_pe --rtti --exe <path-to-ffxivgame.exe>`
"""

IMAGE_BASE = 0x00400000

TEXT_VA_START = 0x00401000
TEXT_VA_END = 0x00F3D000

RDATA_FILE_START = 0x00B3E000
RDATA_FILE_END = 0x00B3E000 + 0x00327000

TEXT_FILE_START = 0x1000
TEXT_FILE_END = 0xB3C000
