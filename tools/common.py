"""Shared helpers of the tools: paths, reading construct folders, item codes, versions."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schema"
CONSTRUCTS = "constructs"
FAMILIES = "families"
EXAMPLES = "examples"

VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class _Loader(yaml.SafeLoader):
    """Safe YAML without timestamps: a date stays the text it is written as (2026-11-09), JSON can carry it."""


_Loader.yaml_implicit_resolvers = {
    first: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml_text(text: str):
    return yaml.load(text, Loader=_Loader)  # noqa: S506 - _Loader is a SafeLoader


def load_yaml(path: Path):
    with open(path, encoding="utf-8") as f:
        return load_yaml_text(f.read())


def dump_yaml(data) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100, default_flow_style=False)


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def schema(name: str) -> dict:
    return load_json(SCHEMA / f"{name}.schema.json")


def validator(name: str):
    """A JSON Schema 2020-12 validator for schema/<name>.schema.json that resolves the other schemas."""
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource

    resources = []
    for path in sorted(SCHEMA.glob("*.schema.json")):
        data = load_json(path)
        resources.append((data["$id"], Resource.from_contents(data)))
    return Draft202012Validator(schema(name), registry=Registry().with_resources(resources),
                                format_checker=Draft202012Validator.FORMAT_CHECKER)


def vocab(name: str):
    return load_yaml(SCHEMA / "vocab" / f"{name}.yaml")


def construct_dirs(root: Path, folder: str = CONSTRUCTS) -> list[Path]:
    base = root / folder
    if not base.is_dir():
        return []
    return sorted(p for p in base.iterdir() if p.is_dir())


def load_construct(folder: Path) -> tuple[dict, dict[str, dict]]:
    """(construct.yaml, {language: wording}) of one construct folder."""
    construct = load_yaml(folder / "construct.yaml")
    wordings = {}
    wdir = folder / "wording"
    if wdir.is_dir():
        for path in sorted(wdir.glob("*.yaml")):
            wordings[path.stem] = load_yaml(path)
    return construct, wordings


def item_codes(structure: dict) -> dict[str, list[str]]:
    """The codes a wording file must name: items (statements, pairs) and answer options."""
    config = structure.get("config") or {}
    rows = config.get("statements") or config.get("pairs") or []
    return {"items": [r["code"] for r in rows], "options": [o["code"] for o in config.get("options") or []]}


def parse_version(value: str) -> tuple[int, int]:
    m = VERSION_RE.match(str(value))
    if not m:
        raise ValueError(f"version {value!r} is not MAJOR.MINOR")
    return int(m.group(1)), int(m.group(2))


def text_fields() -> tuple[str, ...]:
    """Fields every construct carries in German and English."""
    return ("name", "short", "description", "scoring", "notes")
