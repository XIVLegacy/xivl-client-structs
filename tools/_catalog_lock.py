"""Exclusive catalog transactions with explicit abandoned-lock recovery."""

from __future__ import annotations

import os
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

LOCK_TIMEOUT_S = 30.0
LOCK_POLL_S = 0.1


@contextmanager
def catalog_lock(path: Path):
    """Hold a lock until release; age never proves that its owner has exited."""
    lock = path.with_name(path.name + ".lock")
    owner = f"{os.getpid()} {uuid.uuid4().hex}\n".encode("ascii")
    deadline = time.monotonic() + LOCK_TIMEOUT_S
    while True:
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"could not acquire {lock.name} within {LOCK_TIMEOUT_S}s; "
                    "remove an abandoned lock only after verifying its owner exited"
                ) from None
            time.sleep(LOCK_POLL_S)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(owner)
        yield
    finally:
        # A replaced lock belongs to someone else, even if it names the same PID.
        try:
            if lock.read_bytes() == owner:
                lock.unlink()
        except FileNotFoundError:
            pass
