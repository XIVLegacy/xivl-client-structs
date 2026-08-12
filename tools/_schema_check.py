"""Minimal JSON Schema validator for the schemas/ directory.

Stdlib only, because the repo's CI installs no packages and the local gate
must run from a bare checkout. It supports exactly the draft 2020-12
keywords the in-repo schemas use, and raises on any keyword it does not
implement -- an unimplemented keyword must fail loudly rather than pass
silently, which is the failure mode that makes hand-rolled validators
worthless.

Where a real `jsonschema` install is available, `crosscheck()` runs it over
the same (schema, document) pair and reports disagreement. That is an
optional second opinion on this interpreter, never the gate itself.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterator

SUPPORTED = frozenset({
    "$schema", "$id", "$defs", "$ref", "title", "description", "examples",
    "type", "properties", "patternProperties", "required",
    "additionalProperties", "items", "enum", "const", "pattern",
    "minimum", "maximum", "minItems", "minLength", "uniqueItems", "oneOf",
    "dependentRequired",
})

_TYPES: dict[str, type | tuple[type, ...]] = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


class SchemaError(Exception):
    """The schema itself is malformed or uses an unsupported keyword."""


NAME_MAPS = ("properties", "$defs", "patternProperties", "dependentRequired")


def load_schema(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        schema = json.load(f)
    _assert_supported(schema, "#", in_name_map=False)
    return schema


def _assert_supported(node: Any, loc: str, in_name_map: bool) -> None:
    """Reject any keyword this module does not implement.

    An unimplemented keyword that validates silently is worse than no
    validator, so the guard runs once at load and covers every depth.
    `in_name_map` is threaded rather than recovered from `loc`, because a
    document property legitimately named "properties" would otherwise make
    its whole subtree look like a name map and skip the check.
    """
    if isinstance(node, dict):
        if not in_name_map:
            for key in node:
                if key not in SUPPORTED:
                    raise SchemaError(
                        f"{loc}: unsupported schema keyword {key!r}")
            if "type" in node:
                names = node["type"]
                for name in ([names] if isinstance(names, str) else names):
                    if name not in _TYPES:
                        raise SchemaError(f"{loc}/type: unknown type {name!r}")
        for key, val in node.items():
            _assert_supported(val, f"{loc}/{key}",
                              in_name_map=not in_name_map and key in NAME_MAPS)
    elif isinstance(node, list):
        for i, val in enumerate(node):
            _assert_supported(val, f"{loc}/{i}", in_name_map=False)


def _is_type(value: Any, name: str) -> bool:
    expected = _TYPES.get(name)
    if expected is None:
        raise SchemaError(f"unknown type {name!r}")
    if name == "integer":
        # JSON booleans are ints in Python. A bool is not an integer here.
        return isinstance(value, int) and not isinstance(value, bool)
    if name in ("number",):
        return isinstance(value, expected) and not isinstance(value, bool)
    if name == "boolean":
        return isinstance(value, bool)
    return isinstance(value, expected)


def validate(document: Any, schema: dict) -> list[str]:
    """Return human-readable violations. An empty list means valid."""
    return list(_validate(document, schema, schema, "$"))


def _resolve(ref: str, root: dict) -> dict:
    if not ref.startswith("#/"):
        raise SchemaError(f"only local $ref is supported, got {ref!r}")
    node: Any = root
    for part in ref[2:].split("/"):
        if not isinstance(node, dict) or part not in node:
            raise SchemaError(f"unresolvable $ref {ref!r}")
        node = node[part]
    return node


def _validate(value: Any, schema: dict, root: dict, loc: str) -> Iterator[str]:
    if "$ref" in schema:
        yield from _validate(value, _resolve(schema["$ref"], root), root, loc)
        return

    if "type" in schema:
        names = schema["type"]
        names = [names] if isinstance(names, str) else names
        if not any(_is_type(value, n) for n in names):
            yield f"{loc}: expected type {'|'.join(names)}, got {type(value).__name__}"
            return

    if "const" in schema and value != schema["const"]:
        yield f"{loc}: expected const {schema['const']!r}, got {value!r}"
    if "enum" in schema and value not in schema["enum"]:
        yield f"{loc}: {value!r} not in enum {schema['enum']!r}"

    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            yield f"{loc}: {value!r} does not match /{schema['pattern']}/"
        if "minLength" in schema and len(value) < schema["minLength"]:
            yield f"{loc}: shorter than minLength {schema['minLength']}"

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            yield f"{loc}: {value} < minimum {schema['minimum']}"
        if "maximum" in schema and value > schema["maximum"]:
            yield f"{loc}: {value} > maximum {schema['maximum']}"

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            yield f"{loc}: {len(value)} items < minItems {schema['minItems']}"
        if schema.get("uniqueItems") and len(
                {json.dumps(v, sort_keys=True) for v in value}) != len(value):
            yield f"{loc}: items are not unique"
        if "items" in schema:
            for i, item in enumerate(value):
                yield from _validate(item, schema["items"], root, f"{loc}[{i}]")

    if isinstance(value, dict):
        for name in schema.get("required", []):
            if name not in value:
                yield f"{loc}: missing required property {name!r}"
        for trigger, dependencies in schema.get("dependentRequired", {}).items():
            if trigger not in value:
                continue
            for dependency in dependencies:
                if dependency not in value:
                    yield (f"{loc}: property {trigger!r} requires "
                           f"property {dependency!r}")
        props = schema.get("properties", {})
        pattern_props = schema.get("patternProperties", {})
        for key, sub in value.items():
            matched = False
            if key in props:
                matched = True
                yield from _validate(sub, props[key], root, f"{loc}.{key}")
            for pat, pschema in pattern_props.items():
                if re.search(pat, key):
                    matched = True
                    yield from _validate(sub, pschema, root, f"{loc}.{key}")
            if not matched:
                extra = schema.get("additionalProperties", True)
                if extra is False:
                    yield f"{loc}: unexpected property {key!r}"
                elif isinstance(extra, dict):
                    yield from _validate(sub, extra, root, f"{loc}.{key}")

    if "oneOf" in schema:
        matches = [i for i, sub in enumerate(schema["oneOf"])
                   if not list(_validate(value, sub, root, loc))]
        if len(matches) != 1:
            yield (f"{loc}: matched {len(matches)} of {len(schema['oneOf'])} "
                   "oneOf branches, expected exactly 1")


def crosscheck(document: Any, schema: dict) -> str | None:
    """Second opinion from a real jsonschema install, when one exists.

    Returns None when unavailable or in agreement, otherwise a description
    of the disagreement. Callers report this. They must not gate on it.
    """
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return None
    ours = bool(validate(document, schema))
    try:
        jsonschema.validate(document, schema)
        theirs = False
    except jsonschema.ValidationError:
        theirs = True
    except jsonschema.SchemaError as e:
        return f"jsonschema rejects the schema itself: {e.message}"
    if ours != theirs:
        return (f"interpreter says {'invalid' if ours else 'valid'}, "
                f"jsonschema says {'invalid' if theirs else 'valid'}")
    return None
