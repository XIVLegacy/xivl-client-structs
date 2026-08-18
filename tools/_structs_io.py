"""Serialized UTF-8 reader/writer for manifests/structs.json."""

from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path


STRUCTS_PATH = Path(__file__).resolve().parent.parent / "manifests" / "structs.json"
BCSS_PREFIX = "BCS-S-"
LOCK_TIMEOUT_S = 30.0
LOCK_STALE_S = 300.0
LOCK_POLL_S = 0.1


def load_structs(path: Path = STRUCTS_PATH) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def next_bcss_id(data: dict) -> str:
    numbers = [
        int(entry["id"].split("-")[-1])
        for entry in data["structs"]
        if str(entry.get("id", "")).startswith(BCSS_PREFIX)
    ]
    return f"{BCSS_PREFIX}{(max(numbers) + 1) if numbers else 1:04d}"


def append_struct(data: dict, entry: dict) -> str:
    struct_id = entry.get("id") or next_bcss_id(data)
    entry["id"] = struct_id
    data["structs"].append(entry)
    data["structCount"] = len(data["structs"])
    return struct_id


def write_structs(data: dict, path: Path = STRUCTS_PATH) -> None:
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


@contextmanager
def _structs_lock(path: Path = STRUCTS_PATH):
    lock = path.with_name(path.name + ".lock")
    deadline = time.monotonic() + LOCK_TIMEOUT_S
    descriptor = None
    while True:
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                if time.time() - lock.stat().st_mtime > LOCK_STALE_S:
                    lock.unlink()
                    continue
            except OSError:
                continue
            if time.monotonic() > deadline:
                raise TimeoutError(f"could not acquire {lock.name} within {LOCK_TIMEOUT_S}s")
            time.sleep(LOCK_POLL_S)
    try:
        os.write(descriptor, str(os.getpid()).encode("ascii"))
        os.close(descriptor)
        descriptor = None
        yield
    finally:
        if descriptor is not None:
            os.close(descriptor)
        try:
            lock.unlink()
        except OSError:
            pass


@contextmanager
def structs_transaction(path: Path = STRUCTS_PATH):
    with _structs_lock(path):
        data = load_structs(path)
        yield data
        write_structs(data, path)
