#!/usr/bin/env python3
"""End-to-end .le.lpb -> .luac -> .lua pipeline.

Wraps `decode_lpb.py` (this directory) and an external unluac.jar to turn
shipped client/script/*.le.lpb files into greppable Lua source. This is
the repository's Lua-name -> opcode bridge foundation.

External dependencies (the caller provides these; neither is vendored):
    UNLUAC_JAR env var (or --unluac-jar) - path to unluac.jar.
        Download from:
            https://sourceforge.net/projects/unluac/files/latest/download
    java on PATH - JDK 8 or later is sufficient for unluac.

Stages:
    1. .le.lpb -> .luac : decode_lpb.decode_lpb() (rlu/rle wrappers)
    2. .luac   -> .lua  : `java -jar unluac.jar <file>` -> stdout

Usage:
    # bulk:
    python tools/lpb_pipeline.py <install_root>

    # single source:
    python tools/lpb_pipeline.py <install_root> --source Man0g0

    # only decode stage 1 (skip unluac):
    python tools/lpb_pipeline.py <install_root> --no-decompile

    # only run stage 2 against an existing build/lpb tree:
    python tools/lpb_pipeline.py --lpb-dir build/lpb --no-decode

Outputs use the repository build layout:
    build/lpb/<ciphered>/<source>.luac
    build/lua/<ciphered>/<source>.lua
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from decode_lpb import decode_tree  # noqa: E402


def _resolve_unluac_jar(arg: Path | None) -> Path | None:
    if arg is not None:
        return arg
    env = os.environ.get("UNLUAC_JAR")
    return Path(env) if env else None


def _ensure_java_unluac(unluac_jar: Path) -> int:
    """Return 0 on success, nonzero with error printed otherwise."""
    if not unluac_jar.is_file():
        print(f"error: unluac.jar not found at {unluac_jar}", file=sys.stderr)
        print("       download from:", file=sys.stderr)
        print("         https://sourceforge.net/projects/unluac/files/latest/download",
              file=sys.stderr)
        print("       then set UNLUAC_JAR=<path> or pass --unluac-jar.", file=sys.stderr)
        return 2
    try:
        subprocess.run(["java", "-version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("error: 'java' not on PATH (unluac requires JDK 8+)", file=sys.stderr)
        return 3
    return 0


def _decompile_one(unluac_jar: Path, luac: Path, out_lua: Path) -> tuple[Path, bool, str]:
    out_lua.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            ["java", "-jar", str(unluac_jar), str(luac)],
            capture_output=True,
        )
    except FileNotFoundError as exc:
        return luac, False, f"java not found: {exc}"
    if result.returncode != 0:
        return luac, False, result.stderr.decode("utf-8", errors="replace").strip()
    out_lua.write_bytes(result.stdout)
    return luac, True, ""


def _decompile_stage(lpb_dir: Path, lua_dir: Path, unluac_jar: Path,
                     parallel_jobs: int, source_name: str | None) -> int:
    """Decompile .luac -> .lua into lua_dir using unluac."""
    rc = _ensure_java_unluac(unluac_jar)
    if rc != 0:
        return rc

    if source_name:
        luac = lpb_dir / f"{source_name}.luac"
        if not luac.is_file():
            print(f"error: {luac} not present - run decode stage first", file=sys.stderr)
            return 1
        out_lua = lua_dir / f"{source_name}.lua"
        _, ok, err = _decompile_one(unluac_jar, luac, out_lua)
        if not ok:
            print(f"error: unluac failed on {luac}: {err}", file=sys.stderr)
            return 1
        print(f"decompiled {source_name}: {luac} -> {out_lua}")
        return 0

    if not lpb_dir.is_dir():
        print(f"error: {lpb_dir} missing - run decode stage first", file=sys.stderr)
        return 1

    luacs = sorted(lpb_dir.rglob("*.luac"))
    n_ok = n_fail = 0
    jobs = []
    with ThreadPoolExecutor(max_workers=max(parallel_jobs, 1)) as ex:
        for luac in luacs:
            rel = luac.relative_to(lpb_dir)
            out_lua = lua_dir / rel.with_suffix(".lua")
            jobs.append(ex.submit(_decompile_one, unluac_jar, luac, out_lua))
        for fut in as_completed(jobs):
            _, ok, err = fut.result()
            if ok:
                n_ok += 1
            else:
                n_fail += 1
    print(f"decompiled {n_ok}/{len(luacs)} luac files to {lua_dir}/ ({n_fail} failed)")
    return 0 if n_fail == 0 else 4


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("install_root", type=Path, nargs="?",
                    help="FFXIV install root (the dir containing client/script/). "
                         "Required unless --no-decode is set.")
    ap.add_argument("--source", default=None,
                    help="Single source name (e.g. 'Man0g0' or 'OpeningDirector'). "
                         "If omitted, processes the entire script tree.")
    ap.add_argument("--lpb-dir", type=Path, default=Path("build/lpb"),
                    help="Output dir for stage-1 .luac files. Default: build/lpb")
    ap.add_argument("--lua-dir", type=Path, default=Path("build/lua"),
                    help="Output dir for stage-2 .lua files. Default: build/lua")
    ap.add_argument("--unluac-jar", type=Path, default=None,
                    help="Path to unluac.jar. Defaults to $UNLUAC_JAR env var.")
    ap.add_argument("--parallel-jobs", type=int, default=8,
                    help="unluac worker count (default: 8)")
    ap.add_argument("--no-decode", action="store_true",
                    help="Skip stage 1 (.le.lpb -> .luac). --lpb-dir must already exist.")
    ap.add_argument("--no-decompile", action="store_true",
                    help="Skip stage 2 (.luac -> .lua via unluac).")
    args = ap.parse_args()

    if not args.no_decode:
        if args.install_root is None:
            print("error: install_root is required unless --no-decode is set",
                  file=sys.stderr)
            return 1
        rc = decode_tree(args.install_root, args.lpb_dir, args.source)
        if rc != 0:
            return rc

    if not args.no_decompile:
        unluac_jar = _resolve_unluac_jar(args.unluac_jar)
        if unluac_jar is None:
            print("error: --unluac-jar or $UNLUAC_JAR required for decompile stage. "
                  "Use --no-decompile to skip.", file=sys.stderr)
            return 1
        rc = _decompile_stage(args.lpb_dir, args.lua_dir, unluac_jar,
                              args.parallel_jobs, args.source)
        if rc != 0:
            return rc

    return 0


if __name__ == "__main__":
    sys.exit(main())
