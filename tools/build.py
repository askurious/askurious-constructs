"""Build dist/manifest.json, the one file Askurious instances read.

    python tools/build.py --release 2026.11.0
    python tools/build.py --notes 2026.11.0     print the CHANGELOG section of a release (release notes)

Each construct carries its structure and wording hashes and, where the licence allows, its wording. Withdrawn
constructs (status: retired) stay in the list and are named under "retired" as well. The time stamp comes from
SOURCE_DATE_EPOCH if set, so a rebuild of the same commit gives the same file.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import hash as hashing  # noqa: E402
import validate  # noqa: E402

SOURCE = "https://github.com/askurious/askurious-constructs"
RELEASE_RE = re.compile(r"^\d{4}\.\d{2}\.\d+$")


def generated() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    moment = datetime.fromtimestamp(int(epoch), timezone.utc) if epoch else datetime.now(timezone.utc)
    return moment.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def manifest(root: Path, release: str) -> dict:
    constructs, retired = [], []
    for folder in common.construct_dirs(root):
        construct, wordings = common.load_construct(folder)
        repo_langs = [lang for lang, info in construct["languages"].items() if info["wording"] == "repo"]
        entry = dict(construct)
        entry["hash"] = {"structure": hashing.structure_hash(construct),
                         "wording": hashing.wording_hashes(construct, wordings)}
        entry["wording"] = {lang: {k: v for k, v in wordings[lang].items() if k != "for"}
                            for lang in repo_langs if lang in wordings}
        constructs.append(entry)
        if construct["status"] == "retired":
            retired.append({"id": construct["id"], **({"since": construct["retired_since"]}
                                                       if construct.get("retired_since") else {})})
    families = [common.load_yaml(p) for p in sorted((root / common.FAMILIES).glob("*.yaml"))]
    return {"format": 1, "release": release, "generated": generated(), "source": SOURCE,
            "constructs": constructs, "families": families, "retired": retired}


def notes(root: Path, release: str) -> str:
    """The CHANGELOG.md section "## <release>", or a short line if there is none."""
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8") if (root / "CHANGELOG.md").exists() else ""
    m = re.search(rf"^## {re.escape(release)}\b.*?$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() + "\n" if m else f"Release {release}\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=common.ROOT)
    parser.add_argument("--release", help="release name YYYY.MM.N")
    parser.add_argument("--out", type=Path, help="default: <root>/dist/manifest.json")
    parser.add_argument("--notes", metavar="RELEASE", help="print the release notes from CHANGELOG.md")
    args = parser.parse_args(argv)
    if args.notes:
        sys.stdout.write(notes(args.root, args.notes))
        return 0
    if not args.release or not RELEASE_RE.match(args.release):
        parser.error("--release YYYY.MM.N is required")
    errors = validate.validate(args.root, examples=False)
    if errors:
        print("\n".join(errors))
        print("not built: fix the errors above first")
        return 1
    data = manifest(args.root, args.release)
    problems = [e.message for e in common.validator("manifest").iter_errors(data)]
    if problems:
        print("\n".join(problems))
        return 1
    out = args.out or args.root / "dist" / "manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{out}: {len(data['constructs'])} constructs, release {args.release}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
