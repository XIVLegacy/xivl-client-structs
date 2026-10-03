"""Read and write manifests/symbols.json, the BCS-Y catalog.

Use UTF-8 because catalog notes contain characters that Windows cp1252
cannot decode. Allocate IDs from the greatest numeric suffix, not the last
row or row count: the array is unsorted and may contain ID gaps.

Hold symbols_transaction() across the entire load, allocate, and write
operation. Its exclusive file lock prevents concurrent processes from
allocating the same ID or overwriting each other. Read-only callers may use
load_symbols() directly.

Formatting follows xivl-client-data:tools/_json_io.py: two-space indentation,
ensure_ascii=False, LF endings without Windows newline translation, and one
trailing newline. This module uses only the standard library.

Import from another tool in this directory:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import _symbols_io
"""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path

from _catalog_lock import catalog_lock

SYMBOLS_PATH = Path(__file__).resolve().parent.parent / "manifests" / "symbols.json"

BCSY_PREFIX = "BCS-Y-"


def load_symbols(path: Path = SYMBOLS_PATH) -> dict:
    """Load and return the parsed symbols.json document (always UTF-8)."""
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def next_bcsy_id(data: dict) -> str:
    """Return one more than the greatest BCS-Y numeric suffix, padded to four digits.

    Array order does not determine the next ID."""
    nums = [
        int(s["id"].split("-")[-1])
        for s in data["symbols"]
        if str(s.get("id", "")).startswith(BCSY_PREFIX)
    ]
    return f"{BCSY_PREFIX}{(max(nums) + 1) if nums else 1:04d}"


def append_symbol(data: dict, entry: dict) -> str:
    """Append entry to data, allocating its id if absent, and return the id.

    If entry already carries an "id", it is kept as-is (pinned by the caller).
    Otherwise next_bcsy_id() allocates one. Keep data["symbolCount"] in
    sync with the array length.
    """
    sym_id = entry.get("id") or next_bcsy_id(data)
    entry["id"] = sym_id
    data["symbols"].append(entry)
    data["symbolCount"] = len(data["symbols"])
    return sym_id


def write_symbols(data: dict, path: Path = SYMBOLS_PATH) -> None:
    """Write data to symbols.json in the repo house style (UTF-8, LF, indent 2).

    Writes a sibling temp file and os.replace()s it into position, so an
    interrupted write leaves the previous catalog intact rather than a
    truncated one. Prefer symbols_transaction() over calling this directly.
    """
    # Include the PID so concurrent writers cannot collide on rename.
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


@contextmanager
def symbols_transaction(path: Path = SYMBOLS_PATH):
    """Serialized read-modify-write of symbols.json.

    Yields the freshly loaded document. Mutate it (typically via
    append_symbol) and it is written back on clean exit. An exception
    inside the block propagates and leaves the file untouched.

        with symbols_transaction() as d:
            print(append_symbol(d, entry))
    """
    with catalog_lock(path):
        data = load_symbols(path)
        yield data
        write_symbols(data, path)
