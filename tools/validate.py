"""Check the catalogue: schema, licence, languages, item codes, tags, sources and the version rule.

    python tools/validate.py                      everything, without the version rule
    python tools/validate.py --base origin/main   also the version rule against that git revision

Rules:
- every construct.yaml and wording file matches its JSON Schema; folder name = key, id = ask:<key>
- licence key from schema/vocab/licences.yaml; distributable: false and a wording/ folder exclude each other
- name, short, description, scoring and notes in German and English
- each wording file names exactly the item and option codes of the structure
- version rule: structure hash changed => major number up; wording hash changed => version up (minor);
  a key in the base revision must still exist (withdraw with status: retired)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import hash as hashing  # noqa: E402

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")


class Report:
    def __init__(self):
        self.errors: list[str] = []

    def error(self, where: str, message: str):
        self.errors.append(f"{where}: {message}")


def _schema_errors(validator, data, where, report):
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        path = "/".join(str(p) for p in err.path)
        report.error(where, f"{path or '(root)'}: {err.message}")


def check_construct(folder: Path, report: Report, ctx: dict) -> dict | None:
    where = f"{folder.parent.name}/{folder.name}"
    try:
        construct, wordings = common.load_construct(folder)
    except Exception as exc:  # unreadable YAML
        report.error(where, f"cannot read: {exc}")
        return None
    before = len(report.errors)
    _schema_errors(ctx["construct_schema"], construct, where + "/construct.yaml", report)
    for lang, w in wordings.items():
        _schema_errors(ctx["wording_schema"], w, f"{where}/wording/{lang}.yaml", report)
    if len(report.errors) > before:
        return None  # the rules below expect the shape the schema guarantees

    key = construct["key"]
    if folder.name != key and folder.parent.name == common.CONSTRUCTS:
        report.error(where, f"folder name must be the key {key!r}")
    if construct["id"] != f"ask:{key}":
        report.error(where, f"id must be ask:{key}")

    # licence
    lic = construct["licence"]
    known = ctx["licences"].get(lic["wording"])
    if known is None:
        report.error(where, f"licence {lic['wording']!r} is not in schema/vocab/licences.yaml")
    elif bool(known["distributable"]) != bool(lic["distributable"]):
        report.error(where, f"distributable must be {known['distributable']} for {lic['wording']}")
    has_dir = (folder / "wording").exists()
    langs = construct["languages"]
    if not lic["distributable"]:
        if has_dir:
            report.error(where, "distributable: false - no wording/ folder allowed")
        for lang, info in langs.items():
            if info["wording"] != "overlay":
                report.error(where, f"languages.{lang}: wording must be overlay (licence not distributable)")
    else:
        for lang, info in langs.items():
            if info["wording"] != "repo":
                report.error(where, f"languages.{lang}: wording must be repo (distributable licence)")
            if lang not in wordings:
                report.error(where, f"wording/{lang}.yaml is missing")
        for lang in wordings:
            if lang not in langs:
                report.error(where, f"wording/{lang}.yaml has no entry under languages")
    for lang, info in langs.items():
        if lang not in ctx["languages"]:
            report.error(where, f"language {lang!r} is not in schema/vocab/languages.yaml")
        if info["wording"] == "overlay" and not info.get("sha256"):
            report.error(where, f"languages.{lang}: an overlay wording needs its sha256")
        if info["wording"] == "repo" and lang in wordings and info.get("sha256"):
            if info["sha256"] != hashing.wording_hash(wordings[lang]):
                report.error(where, f"languages.{lang}: sha256 does not match wording/{lang}.yaml")

    # German and English
    for field in common.text_fields():
        value = construct[field]
        if field in ("name", "short", "description") and not (value.get("de") and value.get("en")):
            report.error(where, f"{field}: German and English are required")
        elif bool(value.get("de")) != bool(value.get("en")):
            report.error(where, f"{field}: give it in German and English (or leave both empty)")

    # item codes
    codes = common.item_codes(construct["structure"])
    for group, values in codes.items():
        if len(set(values)) != len(values):
            report.error(where, f"structure: {group} codes are not unique")
    for lang, w in wordings.items():
        for group, values in codes.items():
            named = list((w.get(group) or {}).keys())
            if set(named) != set(values):
                missing, extra = sorted(set(values) - set(named)), sorted(set(named) - set(values))
                report.error(where, f"wording/{lang}.yaml {group}: missing {missing}, unknown {extra}")
        if construct["structure"]["type"] == "semantic":
            for code, pair in (w.get("items") or {}).items():
                if not isinstance(pair, dict):
                    report.error(where, f"wording/{lang}.yaml items.{code}: needs left and right")
        elif any(isinstance(v, dict) for v in (w.get("items") or {}).values()):
            report.error(where, f"wording/{lang}.yaml: left/right only for a semantic differential")
        if w.get("for") and not str(w["for"]).startswith(construct["id"] + "@"):
            report.error(where, f"wording/{lang}.yaml: 'for' must name {construct['id']}@<version>")

    # tags, sources, family, versions
    for facet, names in construct["tags"].items():
        if facet not in ctx["facets"]:
            report.error(where, f"tags: unknown facet {facet!r}")
        for name in names if isinstance(names, list) else [names]:
            if name not in ctx["tags"]:
                report.error(where, f"tags.{facet}: {name!r} is not in schema/vocab/facets.yaml")
    for n, source in enumerate(construct["sources"]):
        if source.get("doi") and not DOI_RE.match(source["doi"]):
            report.error(where, f"sources[{n}].doi {source['doi']!r} is not a DOI (10.xxxx/...)")
    if construct.get("family") and construct["family"] not in ctx["families"]:
        report.error(where, f"family {construct['family']!r} has no file in families/")
    if construct["versions"][0]["version"] != construct["version"]:
        report.error(where, "versions: the first entry must be the current version")
    return {"construct": construct, "wordings": wordings}


def check_families(root: Path, report: Report, ctx: dict) -> dict[str, dict]:
    out = {}
    base = root / common.FAMILIES
    for path in sorted(base.glob("*.yaml")) if base.is_dir() else []:
        data = common.load_yaml(path)
        before = len(report.errors)
        _schema_errors(ctx["family_schema"], data, f"families/{path.name}", report)
        if len(report.errors) == before:
            if data["id"] != path.stem:
                report.error(f"families/{path.name}", f"id must be the file name {path.stem!r}")
            out[data["id"]] = data
    return out


# ---- version rule against a git revision ----

def _git(root: Path, *args: str) -> str | None:
    run = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8")
    return run.stdout if run.returncode == 0 else None


def base_constructs(root: Path, ref: str) -> dict[str, dict] | None:
    """{key: {"construct", "wordings"}} at git revision `ref`; None if the revision is unknown."""
    if _git(root, "rev-parse", "--verify", "--quiet", ref + "^{commit}") is None:
        return None
    listing = _git(root, "ls-tree", "-r", "--name-only", ref, "--", common.CONSTRUCTS) or ""
    out: dict[str, dict] = {}
    for path in listing.splitlines():
        parts = path.split("/")
        if len(parts) == 3 and parts[2] == "construct.yaml":
            out.setdefault(parts[1], {"wordings": {}})["construct"] = common.load_yaml_text(_git(root, "show", f"{ref}:{path}"))
        elif len(parts) == 4 and parts[2] == "wording" and parts[3].endswith(".yaml"):
            out.setdefault(parts[1], {"wordings": {}})["wordings"][parts[3][:-5]] = common.load_yaml_text(
                _git(root, "show", f"{ref}:{path}"))
    return {k: v for k, v in out.items() if "construct" in v}


def check_versions(current: dict[str, dict], base: dict[str, dict], report: Report):
    for key, old in base.items():
        where = f"constructs/{key}"
        new = current.get(key)
        if new is None:
            report.error(where, "a construct must never disappear; withdraw it with status: retired")
            continue
        try:
            old_v = common.parse_version(old["construct"]["version"])
            new_v = common.parse_version(new["construct"]["version"])
        except (KeyError, ValueError) as exc:
            report.error(where, str(exc))
            continue
        if new_v < old_v:
            report.error(where, f"version went down ({old_v[0]}.{old_v[1]} -> {new_v[0]}.{new_v[1]})")
        if hashing.structure_hash(new["construct"]) != hashing.structure_hash(old["construct"]):
            if new_v[0] <= old_v[0]:
                report.error(where, f"structure changed: the major number must go up (now {new_v[0]}.{new_v[1]})")
        elif (hashing.wording_hashes(new["construct"], new["wordings"])
              != hashing.wording_hashes(old["construct"], old["wordings"])):
            if new_v <= old_v:
                report.error(where, f"wording changed: the minor number must go up (now {new_v[0]}.{new_v[1]})")


def context(root: Path) -> dict:
    licences = common.vocab("licences")["licences"]
    facets = common.vocab("facets")
    return {
        "construct_schema": common.validator("construct"),
        "wording_schema": common.validator("wording"),
        "family_schema": common.validator("family"),
        "licences": licences,
        "languages": set(common.vocab("languages")["languages"]),
        "facets": set(facets["facets"]),
        "tags": set(facets["tags"]),
        "families": {},
    }


def validate(root: Path, base: str | None = None, examples: bool = True) -> list[str]:
    report = Report()
    ctx = context(root)
    ctx["families"] = check_families(root, report, ctx)
    current = {}
    for folder in common.construct_dirs(root):
        checked = check_construct(folder, report, ctx)
        if checked:
            current[checked["construct"]["key"]] = checked
        elif not (folder / "construct.yaml").exists():
            report.error(f"constructs/{folder.name}", "construct.yaml is missing")
    if examples:
        for folder in common.construct_dirs(root, common.EXAMPLES):
            check_construct(folder, report, ctx)
    if base:
        old = base_constructs(root, base)
        if old is None:
            report.error("version rule", f"git revision {base!r} not found (fetch it, e.g. git fetch origin main)")
        else:
            check_versions(current, old, report)
    return report.errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=common.ROOT)
    parser.add_argument("--base", help="git revision for the version rule, e.g. origin/main")
    parser.add_argument("--no-examples", action="store_true", help="leave examples/ out")
    args = parser.parse_args(argv)
    errors = validate(args.root, args.base, not args.no_examples)
    for e in errors:
        print(e)
    count = len(common.construct_dirs(args.root))
    print(f"{count} constructs checked, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
