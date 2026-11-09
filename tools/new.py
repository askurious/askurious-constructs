"""Start a new construct from one of the examples.

    python tools/new.py likert-lizenziert meinkey
    python tools/new.py --list

Copies examples/<example>/ to constructs/<key>/ and puts the new key and id in. Then fill in the metadata, the
structure and (open licence) the wording, and run python tools/validate.py.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

KEY_RE = re.compile(r"^[a-z][a-z0-9_]{0,33}$")


def create(root: Path, example: str, key: str) -> Path:
    source = root / common.EXAMPLES / example
    if not (source / "construct.yaml").is_file():
        raise ValueError(f"no example {example!r} (python tools/new.py --list)")
    if not KEY_RE.match(key):
        raise ValueError("the key takes small letters, digits and _, starts with a letter, at most 34 characters")
    target = root / common.CONSTRUCTS / key
    if target.exists():
        raise ValueError(f"{target} exists already")
    old_key = common.load_yaml(source / "construct.yaml")["key"]
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("README*"))
    for path in target.rglob("*.yaml"):
        text = path.read_text(encoding="utf-8")
        text = re.sub(rf"\b{re.escape(old_key)}\b", key, text)
        path.write_text(text, encoding="utf-8")
    return target


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("example", nargs="?")
    parser.add_argument("key", nargs="?")
    parser.add_argument("--list", action="store_true", help="list the examples")
    parser.add_argument("--root", type=Path, default=common.ROOT)
    args = parser.parse_args(argv)
    if args.list or not (args.example and args.key):
        for folder in common.construct_dirs(args.root, common.EXAMPLES):
            print(folder.name)
        return 0 if args.list else 2
    try:
        target = create(args.root, args.example, args.key)
    except ValueError as exc:
        print(exc)
        return 1
    print(f"{target} created; next: edit it, then python tools/validate.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
