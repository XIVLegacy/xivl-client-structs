#!/usr/bin/env python3
"""Validate the tracked public repository boundary and public contracts."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

import _schema_check


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
PROVENANCE_FIELDS = (
    "file", "sourceRepo", "sourcePath", "sha256", "refreshMode",
    "evidenceTier", "transformation",
)


def tracked_paths() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return sorted(path for path in result.stdout.decode("utf-8").split("\0") if path)


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


def check_json_and_schemas(paths: list[str], errors: list[str]) -> int:
    documents: dict[str, object] = {}
    for path in paths:
        if not path.endswith(".json"):
            continue
        try:
            documents[path] = json.loads((ROOT / path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"invalid tracked JSON {path}: {exc}")

    pairs = (
        ("manifests/ir_catalog.json", "schemas/ir-v1.schema.json"),
        ("manifests/ir_overlay.json", "schemas/ir-overlay-v1.schema.json"),
    )
    for document_path, schema_path in pairs:
        if document_path not in documents:
            continue
        try:
            schema = _schema_check.load_schema(ROOT / schema_path)
            for finding in _schema_check.validate(documents[document_path], schema):
                errors.append(f"schema violation {document_path}: {finding}")
        except (OSError, ValueError, _schema_check.SchemaError) as exc:
            errors.append(f"invalid schema {schema_path}: {exc}")
    return len(documents)


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
    docs_tree = {
        path for path in paths
        if path.startswith("docs/") and path.endswith(".md") and path != "docs/README.md"
    }
    index = ROOT / "docs" / "README.md"
    indexed: set[str] = set()
    for raw in MARKDOWN_LINK_RE.findall(index.read_text(encoding="utf-8")):
        target = raw.strip().strip("<>").split()[0].split("#", 1)[0]
        if not target or re.match(r"^[a-z]+:", target, re.IGNORECASE):
            continue
        resolved = (index.parent / unquote(target)).resolve()
        try:
            relative = resolved.relative_to(ROOT).as_posix()
        except ValueError:
            continue
        if relative.startswith("docs/") and relative.endswith(".md"):
            indexed.add(relative)
    for path in sorted(docs_tree - indexed):
        errors.append(f"docs index missing: {path}")
    for path in sorted(indexed - docs_tree):
        errors.append(f"docs index extra: {path}")

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


def check_vendor(errors: list[str]) -> int:
    checked = 0
    vendor = ROOT / "data" / "vendor"
    for directory in sorted(path for path in vendor.iterdir() if path.is_dir()):
        provenance_path = directory / "PROVENANCE.json"
        label = provenance_path.relative_to(ROOT).as_posix()
        if not provenance_path.is_file():
            errors.append(f"vendor provenance missing: {label}")
            continue
        try:
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"invalid vendor provenance {label}: {exc}")
            continue
        entries = provenance.get("files") if isinstance(provenance, dict) else None
        if not isinstance(entries, list) or not entries:
            errors.append(f"vendor provenance has no files: {label}")
            continue
        declared: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                errors.append(f"vendor provenance entry is not an object: {label}")
                continue
            missing = [field for field in PROVENANCE_FIELDS if not entry.get(field)]
            if missing:
                errors.append(f"vendor provenance missing {','.join(missing)}: {label}")
                continue
            name = entry["file"]
            if Path(name).name != name or name == "PROVENANCE.json":
                errors.append(f"vendor provenance invalid file name {name}: {label}")
                continue
            declared.add(name)
            target = directory / name
            if not target.is_file():
                errors.append(f"vendor provenance file missing: {target.relative_to(ROOT)}")
                continue
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            if actual != entry["sha256"]:
                errors.append(f"vendor provenance hash mismatch: {target.relative_to(ROOT)}")
            checked += 1
        actual_files = {
            path.name for path in directory.iterdir()
            if path.is_file() and path.name != "PROVENANCE.json"
        }
        for name in sorted(actual_files - declared):
            errors.append(f"vendor file lacks provenance: {(directory / name).relative_to(ROOT)}")
    return checked


def main() -> int:
    errors: list[str] = []
    try:
        paths = tracked_paths()
        check_boundary(paths, errors)
        json_count = check_json_and_schemas(paths, errors)
        check_docs(paths, errors)
        vendor_count = check_vendor(errors)
    except (OSError, subprocess.SubprocessError, UnicodeError) as exc:
        print(f"repository boundary FAILED: {exc}", file=sys.stderr)
        return 1

    if errors:
        print(f"repository boundary FAILED ({len(errors)} problems):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(
        f"repository boundary OK ({len(paths)} tracked files, {json_count} JSON files, "
        f"2 schemas, docs-index/link sync, {vendor_count} provenance hashes)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
