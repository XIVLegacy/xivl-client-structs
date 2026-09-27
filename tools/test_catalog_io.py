"""Exercise catalog exclusion and preservation through real writer processes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import _catalog_lock
import _structs_io
import _symbols_io

TOOLS = Path(__file__).resolve().parent


class CatalogIoTests(unittest.TestCase):
    def test_live_aged_owner_excludes_another_process(self) -> None:
        for module, family, prefix in (
            (_symbols_io, "symbols", "BCS-Y"),
            (_structs_io, "structs", "BCS-S"),
        ):
            with (
                self.subTest(family=family),
                tempfile.TemporaryDirectory() as directory,
            ):
                path = Path(directory) / f"{family}.json"
                path.write_text(json.dumps({family: []}), encoding="utf-8")
                transaction = getattr(module, f"{family}_transaction")
                append = getattr(module, f"append_{family[:-1]}")
                with transaction(path) as data:
                    append(data, {"name": "first"})
                    lock = path.with_name(path.name + ".lock")
                    os.utime(lock, (1, 1))
                    result = self.run_writer(path, family, "contender")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("TimeoutError", result.stderr)
                    self.assertEqual(json.loads(path.read_text())[family], [])
                result = self.run_writer(path, family, "second")
                self.assertEqual(result.returncode, 0, result.stderr)
                entries = json.loads(path.read_text())[family]
                self.assertEqual(
                    [entry["name"] for entry in entries], ["first", "second"]
                )
                self.assertEqual(
                    [entry["id"] for entry in entries],
                    [f"{prefix}-0001", f"{prefix}-0002"],
                )

    def run_writer(
        self, path: Path, family: str, name: str
    ) -> subprocess.CompletedProcess[str]:
        source = (
            "import sys; from pathlib import Path; "
            "import _catalog_lock; _catalog_lock.LOCK_TIMEOUT_S = 0; "
            f"import _{family}_io as catalog\n"
            f"with catalog.{family}_transaction(Path(sys.argv[1])) as data:\n"
            f"    catalog.append_{family[:-1]}(data, {{'name': sys.argv[2]}})\n"
        )
        return subprocess.run(
            [sys.executable, "-c", source, str(path), name],
            cwd=TOOLS,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_abandoned_lock_requires_verified_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "symbols.json"
            source = (
                "import os, sys; from pathlib import Path; from _catalog_lock import catalog_lock\n"
                "with catalog_lock(Path(sys.argv[1])):\n    os._exit(7)\n"
            )
            result = subprocess.run(
                [sys.executable, "-c", source, str(path)], cwd=TOOLS, check=False
            )
            self.assertEqual(result.returncode, 7)
            lock = path.with_name(path.name + ".lock")
            with patch.object(_catalog_lock, "LOCK_TIMEOUT_S", 0):
                with self.assertRaises(TimeoutError), _catalog_lock.catalog_lock(path):
                    self.fail("abandoned lock was silently stolen")
            # The child has exited; removing this exact lock is explicit recovery.
            lock.unlink()
            with _catalog_lock.catalog_lock(path):
                self.assertTrue(lock.exists())
            self.assertFalse(lock.exists())

    def test_release_preserves_a_replaced_owner_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "symbols.json"
            lock = path.with_name(path.name + ".lock")
            replacement = f"{os.getpid()} another-acquisition\n".encode("ascii")
            with _catalog_lock.catalog_lock(path):
                lock.write_bytes(replacement)
            self.assertEqual(lock.read_bytes(), replacement)

    def test_transaction_exception_preserves_catalog(self) -> None:
        for module, family in ((_symbols_io, "symbols"), (_structs_io, "structs")):
            with (
                self.subTest(family=family),
                tempfile.TemporaryDirectory() as directory,
            ):
                path = Path(directory) / f"{family}.json"
                original = json.dumps({family: []}).encode("utf-8")
                path.write_bytes(original)
                with (
                    self.assertRaisesRegex(ValueError, "cancel"),
                    getattr(module, f"{family}_transaction")(path) as data,
                ):
                    data[family].append({"name": "uncommitted"})
                    raise ValueError("cancel")
                self.assertEqual(path.read_bytes(), original)
                self.assertFalse(path.with_name(path.name + ".lock").exists())


if __name__ == "__main__":
    unittest.main()
