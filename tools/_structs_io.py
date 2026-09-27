"""Serialized UTF-8 reader/writer for manifests/structs.json."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path

from _catalog_lock import catalog_lock

STRUCTS_PATH = Path(__file__).resolve().parent.parent / "manifests" / "structs.json"
BCSS_PREFIX = "BCS-S-"


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
def structs_transaction(path: Path = STRUCTS_PATH):
    with catalog_lock(path):
        data = load_structs(path)
        yield data
        write_structs(data, path)
