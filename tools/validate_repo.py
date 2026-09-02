#!/usr/bin/env python3
"""Validate the tracked public repository boundary and public contracts."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
PERMITTED_TOP_LEVEL_GROUPS = {
    "root",
    ".github",
    "data",
    "docs",
    "ghidra",
    "manifests",
    "schemas",
    "signatures",
    "structs",
    "tools",
}
REQUIRED_AGENT_TOOLING_IGNORE_LINES = {
    "# Agent / AI tooling",
    ".claude/",
    ".agents/",
    "AGENTS.md",
    "CLAUDE.md",
    "docs/ai_agents/local/",
}
ABSOLUTE_MAINTAINER_PATH_RE = re.compile(
    rb"(?:[A-Za-z]:\\" + rb"Users\\|/" + rb"Users/|/" + rb"home/)",
    re.IGNORECASE,
)
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")
def tracked_paths() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return sorted(
        path for path in result.stdout.decode("utf-8").split("\0")
        if path and (ROOT / path).is_file()
    )


def forbidden_category(path: str) -> str | None:
    lower = path.lower()
    parts = lower.split("/")
    name = parts[-1]
    suffix = Path(name).suffix

    if name in {".ds_store", "thumbs.db"} or suffix in {".log", ".tmp"}:
        return "editor/OS noise"
    if suffix in {".gpr", ".rep", ".lock", ".bak"} or ".ghidra" in parts:
        return "Ghidra project state"
    if any(part in {"artifacts", "out", "tmp", "temp", "build"} for part in parts):
        return "generated/scratch output"
    if lower.startswith("tools/ghidra/logs/"):
        return "Ghidra decomp logs"
    if lower == "manifests/rtti_extraction_our.txt":
        return "raw RTTI extraction"
    if name == ".mcp.json" or ".ghidra-mcp" in parts:
        return "local MCP material"
    if "__pycache__" in parts or suffix == ".pyc":
        return "Python cache files"
    if (
        ".claude" in parts
        or ".agents" in parts
        or name in {"agents.md", "claude.md"}
        or lower.startswith("docs/ai_agents/local/")
    ):
        return "agent/AI material"
    return None


def private_tokens() -> tuple[bytes, ...]:
    slash = b"/"
    return (
        b"docs" + slash + b"ai_agents" + slash + b"local" + slash,
        b"." + b"claude" + slash,
        b"." + b"agents" + slash,
        b"AGENTS" + b".md",
        b"CLAUDE" + b".md",
        b"." + b"mcp" + b".json",
        b"." + b"ghidra-mcp" + slash,
    )


def check_boundary(paths: list[str], errors: list[str]) -> None:
    for path in paths:
        group = path.split("/", 1)[0] if "/" in path else "root"
        if group not in PERMITTED_TOP_LEVEL_GROUPS:
            errors.append(f"unexpected top-level tracked group: {path}")

    token_exclusions = {".gitignore", "tools/validate_repo.py"}
    tokens = private_tokens()
    for path in paths:
        category = forbidden_category(path)
        if category:
            errors.append(f"forbidden {category}: {path}")
        data = (ROOT / path).read_bytes()
        if data[:2] == b"MZ":
            errors.append(f"PE MZ magic in tracked file: {path}")
        if ABSOLUTE_MAINTAINER_PATH_RE.search(data):
            errors.append(f"absolute maintainer path in tracked file: {path}")
        if path not in token_exclusions:
            lowered = data.lower()
            for token in tokens:
                if token.lower() in lowered:
                    errors.append(
                        f"private-reference token {token.decode('ascii')} in tracked file: {path}"
                    )

    ignore_text = (
        (ROOT / ".gitignore").read_text(encoding="utf-8")
        .replace("\r\n", "\n")
    )
    ignore_lines = set(ignore_text.split("\n"))
    for required in sorted(REQUIRED_AGENT_TOOLING_IGNORE_LINES):
        if required not in ignore_lines:
            errors.append(f".gitignore missing required line: {required}")


def markdown_code_stripped(text: str) -> str:
    lines: list[str] = []
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            lines.append("".join(re.split(r"`[^`]*`", line)))
    return "\n".join(lines)


def check_docs(paths: list[str], errors: list[str]) -> None:
    for path in paths:
        if not path.endswith(".md"):
            continue
        full = ROOT / path
        text = markdown_code_stripped(full.read_text(encoding="utf-8"))
        for raw in MARKDOWN_LINK_RE.findall(text):
            target = raw.strip().strip("<>")
            if re.match(r"^(?:[a-z]+:|#)", target, re.IGNORECASE):
                continue
            target = target.split()[0].split("#", 1)[0]
            if not target:
                continue
            resolved = (full.parent / unquote(target)).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(f"relative link escapes repository: {path} -> {raw}")
                continue
            if not resolved.exists():
                errors.append(f"unresolved relative link: {path} -> {raw}")


def main() -> int:
    errors: list[str] = []
    try:
        paths = tracked_paths()
        check_boundary(paths, errors)
        check_docs(paths, errors)
    except (OSError, subprocess.SubprocessError, UnicodeError) as exc:
        print(f"repository boundary FAILED: {exc}", file=sys.stderr)
        return 1

    if errors:
        print(f"repository boundary FAILED ({len(errors)} problems):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"repository boundary OK ({len(paths)} tracked files, documentation links).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
