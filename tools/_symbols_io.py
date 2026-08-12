"""Shared reader/writer for manifests/symbols.json (the BCS-Y catalog).

This module is the single home for the two documented symbols.json gotchas:

1. UTF-8 must be explicit. symbols.json carries multibyte content in its notes
   prose; opening it under the Windows default cp1252 codec raises
   UnicodeDecodeError. Every read/write here passes encoding="utf-8".
2. BCS-Y id allocation must be max-based and serialized. Max-based: take max()
   over the parsed id numbers -- never symbols[-1], whose id is not guaranteed
   to be the maximum (the array is not globally sorted and symbolCount 1805 <
   last id 1818 because superseded entries leave gaps). Serialized: the whole
   load-allocate-write cycle runs under symbols_transaction(), which holds an
   exclusive lock file. Doing the cycle inside one Python process is NOT
   sufficient on its own -- the race is between concurrent processes, where two
   unlocked writers allocate the same id and the second write drops the first
   writer's entry outright. Read-only callers can use load_symbols() directly.

House style for the on-disk file mirrors ../xivl-client-data/tools/_json_io.py:
2-space indent, ensure_ascii=False (non-ASCII kept verbatim), LF line endings
(newline="" so json's internal "\n" is written without CRLF translation on
Windows), and a single trailing newline, for byte-consistency with the sibling
repo.

Stdlib only. Import from a sibling tool with:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import _symbols_io
"""

from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path

SYMBOLS_PATH = Path(__file__).resolve().parent.parent / "manifests" / "symbols.json"

BCSY_PREFIX = "BCS-Y-"

# O_CREAT|O_EXCL acquisition is atomic. Stale locks are treated as abandoned.
LOCK_TIMEOUT_S = 30.0
LOCK_STALE_S = 300.0
LOCK_POLL_S = 0.1


def load_symbols(path: Path = SYMBOLS_PATH) -> dict:
    """Load and return the parsed symbols.json document (always UTF-8)."""
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def next_bcsy_id(data: dict) -> str:
    """Return the next free BCS-Y-NNNN id for the loaded document.

    Max-based: parses the numeric suffix of every BCS-Y- id and returns
    max + 1, zero-padded to four digits. Never trusts array position.
    """
    nums = [
        int(s["id"].split("-")[-1])
        for s in data["symbols"]
        if str(s.get("id", "")).startswith(BCSY_PREFIX)
    ]
    return f"{BCSY_PREFIX}{(max(nums) + 1) if nums else 1:04d}"


def append_symbol(data: dict, entry: dict) -> str:
    """Append entry to data, allocating its id if absent, and return the id.

    If entry already carries an "id", it is kept as-is (pinned by the caller).
    otherwise next_bcsy_id() allocates one. Keeps data["symbolCount"] in
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
def _symbols_lock(path: Path = SYMBOLS_PATH):
    """Hold an exclusive advisory lock on path for the duration of the block."""
    lock = path.with_name(path.name + ".lock")
    deadline = time.monotonic() + LOCK_TIMEOUT_S
    fd = None
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                if time.time() - lock.stat().st_mtime > LOCK_STALE_S:
                    lock.unlink()
                    continue
            except OSError:
                continue  # the holder released it between the check and stat
            if time.monotonic() > deadline:
                raise TimeoutError(
                    f"could not acquire {lock.name} within {LOCK_TIMEOUT_S}s; "
                    "another writer is active (delete the lock file if stale)"
                )
            time.sleep(LOCK_POLL_S)
    try:
        os.write(fd, str(os.getpid()).encode("ascii"))
        os.close(fd)
        fd = None
        yield
    finally:
        if fd is not None:
            os.close(fd)
        try:
            lock.unlink()
        except OSError:
            pass


@contextmanager
def symbols_transaction(path: Path = SYMBOLS_PATH):
    """Serialized read-modify-write of symbols.json.

    Yields the freshly loaded document. Mutate it (typically via
    append_symbol) and it is written back on clean exit. An exception
    inside the block propagates and leaves the file untouched.

        with symbols_transaction() as d:
            print(append_symbol(d, entry))
    """
    with _symbols_lock(path):
        data = load_symbols(path)
        yield data
        write_symbols(data, path)
