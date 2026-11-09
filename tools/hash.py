"""Structure and wording hashes of a construct.

SHA-256 over canonical JSON (keys sorted, no spaces, UTF-8). The wording is normalised first: Unicode NFC,
typographic quotation marks as plain ones, runs of white space as one space, no space at either end. So a wording
that differs only in such details has the same hash, and an instance can check its private wording against the
public hash without the text ever being public.

    python tools/hash.py constructs/kamb              structure and wording hashes of a construct
    python tools/hash.py --wording overlay/x/de.yaml  hash of one wording file (e.g. of a private overlay)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

QUOTES = str.maketrans({
    "„": '"', "“": '"', "”": '"', "‟": '"', "«": '"', "»": '"', "″": '"',
    "‚": "'", "‘": "'", "’": "'", "‛": "'", "‹": "'", "›": "'", "′": "'",
})
# keys of a wording file that say what it belongs to, not what it says
WORDING_META = ("for",)


def normalise_text(value: str) -> str:
    value = unicodedata.normalize("NFC", value).translate(QUOTES)
    return " ".join(value.split())


def normalise(obj):
    if isinstance(obj, str):
        return normalise_text(obj)
    if isinstance(obj, list):
        return [normalise(v) for v in obj]
    if isinstance(obj, dict):
        return {str(k): normalise(v) for k, v in obj.items()}
    return obj


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha256(obj) -> str:
    return "sha256:" + hashlib.sha256(canonical(obj)).hexdigest()


def structure_hash(construct: dict) -> str:
    return sha256(construct["structure"])


def wording_hash(wording: dict) -> str:
    return sha256(normalise({k: v for k, v in wording.items() if k not in WORDING_META}))


def wording_hashes(construct: dict, wordings: dict[str, dict]) -> dict[str, str]:
    """{language: hash}: computed from the wording files in the repository, stored for overlay wordings."""
    out = {}
    for lang, info in (construct.get("languages") or {}).items():
        if info.get("wording") == "repo":
            if lang in wordings:
                out[lang] = wording_hash(wordings[lang])
        elif info.get("sha256"):
            out[lang] = info["sha256"]
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", type=Path, help="construct folder, or a wording file with --wording")
    parser.add_argument("--wording", action="store_true", help="hash one wording file")
    args = parser.parse_args(argv)
    if args.wording:
        print(wording_hash(common.load_yaml(args.path)))
        return 0
    construct, wordings = common.load_construct(args.path)
    print(f"structure: {structure_hash(construct)}")
    for lang, value in wording_hashes(construct, wordings).items():
        print(f"wording {lang}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
