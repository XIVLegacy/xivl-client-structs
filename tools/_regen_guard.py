"""Refuse-to-clobber guard for partial manifest generators.

Several manifests started life as the whole output of one generator and have
since grown: later phases append their own top-level blocks, and hand-curated
sections such as data_dependency_catalog.json's confirmedIndirectBindings are
extended well past what the generator's seed constant holds. Rerunning such a
generator reconstructs the original pilot schema and drops everything added
since -- thousands of lines of evidence, with nothing in the script to say so.

check_regen_safe() compares the on-disk top-level keys against the keys the
generator is about to write. Any key present on disk but absent from the new
document is accumulated evidence, so the write is refused. Passing --force
overrides, for the case where the caller genuinely wants the pilot schema back.

Stdlib only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def check_regen_safe(out_path: Path, new_doc: dict, force: bool = False) -> bool:
    """Return True if writing new_doc over out_path is non-destructive.

    Prints an explanation to stderr and returns False when the existing file
    carries top-level keys the generator does not emit. A missing or
    unparseable target is always safe to write.
    """
    if not out_path.is_file():
        return True
    try:
        with out_path.open(encoding="utf-8") as f:
            existing = json.load(f)
    except (json.JSONDecodeError, OSError):
        return True
    if not isinstance(existing, dict):
        return True

    dropped = [k for k in existing if k not in new_doc]
    if not dropped:
        return True

    verb = "OVERWRITING (--force)" if force else "REFUSING to overwrite"
    print(
        f"\n{verb} {out_path.name}: it carries {len(dropped)} top-level "
        f"key(s) this generator does not produce.",
        file=sys.stderr,
    )
    for k in dropped:
        val = existing[k]
        size = f" [{len(val)} entries]" if isinstance(val, (list, dict)) else ""
        print(f"    {k}{size}", file=sys.stderr)
    if not force:
        print(
            "\nThose blocks were appended by later phases and are not "
            "reconstructible from this script's inputs.\n"
            "Rerun with --force only if you deliberately want the original "
            "pilot schema back.",
            file=sys.stderr,
        )
    return force


def add_force_arg(ap) -> None:
    """Register the standard --force flag on an ArgumentParser."""
    ap.add_argument(
        "--force", action="store_true",
        help="overwrite the target even if it carries accumulated top-level "
             "blocks this generator cannot reproduce (data loss)",
    )
