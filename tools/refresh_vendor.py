#!/usr/bin/env python3
"""Refresh the vendored evidence under data/vendor/ from its declared source.

Each PROVENANCE.json entry names the source repository, path, license,
canonical license URL, and sha256 of the copied bytes. The sha256 is the
identity of the promoted snapshot: this tool re-fetches the bytes from the
named source checkout and restamps the entry, so a drifted or corrupted vendor
file can be restored to the recorded content (this repo's own history holds
the fixture) and a newer source state can be promoted through the same path.

The source path is tracked in the first-party source repository. Bytes come
from `git show HEAD:<path>` in that checkout, so the promotion reflects its
committed state rather than its working tree.

Source checkouts are named explicitly - there is no workspace-layout default:

    python tools/refresh_vendor.py --repo xivl-opcodes=../xivl-opcodes
    python tools/refresh_vendor.py --repo xivl-captures=../xivl-captures \
        --only data/vendor/captures/payload_samples.json

Promote a newer source state for one fixture (pass --source-path when the
file moved in the source repository):

    python tools/refresh_vendor.py --repo xivl-opcodes=../xivl-opcodes \
        --only data/vendor/opcodes/opcodes.json --promote
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENDOR = REPO / "data" / "vendor"


class RefreshError(Exception):
    """A refresh cannot be completed safely."""


def git(checkout: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(checkout), *args], capture_output=True, check=False
    )
    if result.returncode != 0:
        raise RefreshError(
            f"git {' '.join(args)} failed in {checkout}: "
            f"{result.stderr.decode('utf-8', 'replace').strip()}"
        )
    return result.stdout


def fetch_copy(checkout: Path, source_path: str) -> bytes:
    return git(checkout, "show", f"HEAD:{source_path}")


def load_provenance(path: Path) -> dict:
    provenance = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(provenance, dict) or not isinstance(provenance.get("files"), list):
        raise RefreshError(f"{path}: files must be an array")
    return provenance


def write_provenance(path: Path, provenance: dict) -> None:
    path.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )


def refresh_entry(entry: dict, directory: Path, checkouts: dict[str, Path], args) -> str:
    name = entry["file"]
    fixture = directory / name
    source_repo = entry["sourceRepo"]

    checkout = checkouts.get(source_repo)
    if checkout is None:
        return f"skipped {fixture.relative_to(REPO)} (no --repo {source_repo}=PATH given)"

    source_path = args.source_path or entry["sourcePath"]

    mode = entry.get("refreshMode")
    if mode != "copy":
        raise RefreshError(f"{name}: unknown refreshMode {mode!r}")
    payload = fetch_copy(checkout, source_path)

    # Parse JSON before installation. Preserve non-JSON fixtures byte-for-byte.
    if fixture.suffix == ".json":
        try:
            json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RefreshError(
                f"{fixture.relative_to(REPO)}: source content is not valid "
                f"JSON: {exc}"
            ) from exc

    digest = hashlib.sha256(payload).hexdigest()
    promoting = args.promote or args.source_path
    if not promoting and digest != entry.get("sha256"):
        raise RefreshError(
            f"refused {fixture.relative_to(REPO)}: source content differs from the "
            "recorded sha256 (pass --promote to accept the newer source state)")

    was_drifted = not fixture.is_file() or fixture.read_bytes() != payload
    fixture.write_bytes(payload)
    entry["sourcePath"] = source_path
    entry["sha256"] = digest

    verb = "promoted" if promoting else ("restored" if was_drifted else "unchanged")
    return f"{verb} {fixture.relative_to(REPO)} from {source_repo}:{source_path}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--repo", action="append", default=[], metavar="NAME=PATH",
        help="source checkout for sourceRepo NAME (repeatable; required per repo refreshed)",
    )
    ap.add_argument("--only", metavar="VENDOR_FILE", help="refresh a single vendored file")
    ap.add_argument("--promote", action="store_true",
                    help="accept a source state whose bytes differ from the recorded sha256")
    ap.add_argument("--source-path", metavar="PATH",
                    help="with --only: the file's new path in the source repository")
    args = ap.parse_args()

    if args.source_path and not args.only:
        ap.error("--source-path requires --only")

    checkouts: dict[str, Path] = {}
    for spec in args.repo:
        name, sep, path = spec.partition("=")
        if not sep or not name or not path:
            ap.error(f"--repo expects NAME=PATH, got {spec!r}")
        checkout = Path(path).resolve()
        if not (checkout / ".git").exists():
            ap.error(f"{checkout} is not a git checkout")
        checkouts[name] = checkout

    statuses: list[str] = []
    known: list[str] = []
    try:
        for provenance_path in sorted(VENDOR.glob("*/PROVENANCE.json")):
            provenance = load_provenance(provenance_path)
            directory = provenance_path.parent
            changed = False
            for entry in provenance["files"]:
                rel = str((directory / entry.get("file", "")).relative_to(REPO)).replace("\\", "/")
                known.append(rel)
                if args.only and rel != args.only.replace("\\", "/"):
                    continue
                before = json.dumps(entry, sort_keys=True)
                statuses.append(refresh_entry(entry, directory, checkouts, args))
                changed = changed or json.dumps(entry, sort_keys=True) != before
            if changed:
                write_provenance(provenance_path, provenance)
    except RefreshError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # A mistyped --only would otherwise refresh nothing and still exit 0.
    if args.only and args.only.replace("\\", "/") not in known:
        print(f"error: --only {args.only} matched no vendored file; declared "
              f"fixtures: {', '.join(sorted(known))}", file=sys.stderr)
        return 1

    for line in statuses:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
