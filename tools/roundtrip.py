"""Build the Askurious item template ("spec": type, code, config, texts) of each construct from construct.yaml and
its wording, so the main repository can check that the catalogue gives exactly the spec it has today.

Licensed constructs keep their wording out of this repository; pass an instance's private overlay with --overlay
(a folder with <key>/<lang>.yaml or wordings/<key>/<lang>.yaml, or the older instruments.json). Without it they are
left out. A wording from the overlay whose hash differs from the documented one is reported.

    python tools/roundtrip.py --out specs.json
    python tools/roundtrip.py --overlay ../instance/overlay/instruments.json --compare askurious-specs.json
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import hash as hashing  # noqa: E402

TEXT_FIELDS = ("prefix", "suffix", "validation_message")


def to_spec(construct: dict, wordings: dict[str, dict]) -> dict:
    """The Askurious spec of one construct with the given wording per language."""
    s = construct["structure"]
    config = copy.deepcopy(s.get("config") or {})
    labels = s.get("labels") or {}
    order = list((construct.get("languages") or {}).keys())
    langs = [lang for lang in order if lang in wordings] + [lang for lang in wordings if lang not in order]
    texts = {}
    for lang in langs:
        w = wordings[lang]
        if s["type"] == "likert" and labels and lang not in labels and "labels" not in w:
            continue  # a scale of others offers only the languages its response labels are documented in
        t = {}
        if "question" in w:
            t["question"] = w["question"]
        if "labels" in w:
            t["labels"] = list(w["labels"])
        elif lang in labels:
            t["labels"] = list(labels[lang])
        items = w.get("items") or {}
        if config.get("statements"):
            t["statements"] = {st["id"]: items[st["code"]] for st in config["statements"]}
        if config.get("pairs"):
            t["pairs"] = {p["id"]: {"left": items[p["code"]]["left"], "right": items[p["code"]]["right"]}
                          for p in config["pairs"]}
        if config.get("options"):
            options = w.get("options") or {}
            t["options"] = {o["id"]: options[o["code"]] for o in config["options"]}
        for field in TEXT_FIELDS:
            if field in w:
                t[field] = w[field]
        texts[lang] = t
    return {"type": s["type"], "code": s["code"], "config": config, "texts": texts}


def authors_text(construct: dict) -> str:
    """The authors as one line: "A", "A & B", "A, B & C" (or authors_text where that differs)."""
    if construct.get("authors_text"):
        return construct["authors_text"]
    names = [a.get("family") or a.get("name") for a in construct.get("authors") or []]
    if not names:
        return ""
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " & " + names[-1]


def to_seed(construct: dict) -> dict:
    """The metadata of a construct in the shape of an Askurious seed (app/constructs.py SEEDS), German, plus "en"
    with the English texts (SEEDS_EN)."""
    source = (construct.get("sources") or [{}])[0]
    tags = []
    for facet, names in (construct.get("tags") or {}).items():
        tags += [f"{facet}:{n}" for n in (names if isinstance(names, list) else [names])]
    seed = {"key": construct["key"], "seed_version": common.parse_version(construct["version"])[0],
            "status": construct["status"], "authors": authors_text(construct), "year": construct.get("year"),
            "citation": source.get("citation", ""), "doi": source.get("doi", ""), "tags": tags}
    for field in common.text_fields():
        seed[field] = construct[field]["de"]
    seed["en"] = {field: construct[field]["en"] for field in common.text_fields() if construct[field]["en"]}
    return seed


def overlay_wordings(overlay: Path | None, construct: dict) -> dict[str, dict]:
    """{language: wording} of a licensed construct from an instance's overlay; {} if it has none."""
    if overlay is None:
        return {}
    key = construct["key"]
    if overlay.is_file():  # instruments.json: {"instruments": {key: {"question": {lang}, "statements": [{lang}]}}}
        entry = (common.load_json(overlay).get("instruments") or {}).get(key)
        if not isinstance(entry, dict):
            return {}
        codes = common.item_codes(construct["structure"])["items"]
        statements = entry.get("statements") or []
        if len(statements) != len(codes):
            return {}
        out = {}
        for lang, question in (entry.get("question") or {}).items():
            if all(isinstance(s, dict) and isinstance(s.get(lang), str) for s in statements):
                out[lang] = {"question": question, "items": {c: s[lang] for c, s in zip(codes, statements)}}
        return out
    for base in (overlay / "wordings" / key, overlay / key):
        if base.is_dir():
            return {p.stem: common.load_yaml(p) for p in sorted(base.glob("*.yaml"))}
    return {}


def build_all(root: Path, overlay: Path | None = None) -> tuple[dict[str, dict], list[str], list[str]]:
    """({key: spec}, licensed keys without overlay wording, keys whose overlay wording differs from the hash)."""
    specs, missing, differing = {}, [], []
    for folder in common.construct_dirs(root):
        construct, wordings = common.load_construct(folder)
        if construct.get("status") == "retired":
            continue
        langs = construct.get("languages") or {}
        if any(info.get("wording") == "overlay" for info in langs.values()):
            private = overlay_wordings(overlay, construct)
            for lang, w in private.items():
                expected = (langs.get(lang) or {}).get("sha256")
                if expected and hashing.wording_hash(w) != expected:
                    differing.append(f"{construct['key']}/{lang}")
            private = {lang: w for lang, w in private.items() if (langs.get(lang) or {}).get("wording") == "overlay"}
            if not private:
                missing.append(construct["key"])
                continue
            wordings = {**wordings, **private}
        specs[construct["key"]] = to_spec(construct, wordings)
    return specs, missing, differing


def compare(built: dict[str, dict], expected: dict[str, dict]) -> list[str]:
    """Differences between the built specs and the ones of the main repository."""
    problems = []
    for key in sorted(set(built) | set(expected)):
        if key not in built:
            problems.append(f"{key}: not built from the catalogue")
        elif key not in expected:
            problems.append(f"{key}: not in the comparison")
        elif hashing.canonical(built[key]) != hashing.canonical(expected[key]):
            problems.append(f"{key}: spec differs")
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=common.ROOT)
    parser.add_argument("--overlay", type=Path, help="private overlay of an instance (folder or instruments.json)")
    parser.add_argument("--out", type=Path, help="write {key: spec} as JSON")
    parser.add_argument("--compare", type=Path, help="JSON {key: spec} to compare with")
    args = parser.parse_args(argv)
    specs, missing, differing = build_all(args.root, args.overlay)
    if args.out:
        args.out.write_text(json.dumps(specs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(specs)} specs built")
    if missing:
        print(f"without overlay wording: {', '.join(missing)}")
    status = 0
    for item in differing:
        print(f"overlay wording differs from the documented hash: {item}")
        status = 1
    if args.compare:
        expected = common.load_json(args.compare)
        if args.overlay is None:
            expected = {k: v for k, v in expected.items() if k not in missing}
        problems = compare(specs, expected)
        for p in problems:
            print(p)
        print("roundtrip: " + ("equal" if not problems else f"{len(problems)} differences"))
        status = status or (1 if problems else 0)
    return status


if __name__ == "__main__":
    sys.exit(main())
