import json

import build
import common
import hash as hashing
import new
import roundtrip
import validate
from conftest import ROOT


def test_manifest_of_the_catalogue(tmp_path, monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1762646400")
    out = tmp_path / "manifest.json"
    assert build.main(["--release", "2026.11.0", "--out", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["release"] == "2026.11.0" and data["generated"] == "2025-11-09T00:00:00Z"
    assert list(common.validator("manifest").iter_errors(data)) == []
    by_key = {c["key"]: c for c in data["constructs"]}
    assert len(by_key) == len(common.construct_dirs(ROOT))
    # licensed: no wording, but a hash per language; open: wording and its hash
    assert by_key["bfi10"]["wording"] == {} and set(by_key["bfi10"]["hash"]["wording"]) == {"de", "en"}
    assert by_key["kamb"]["wording"]["de"]["items"]["KAMB_1"] == {"left": "professionell", "right": "amateurhaft"}
    assert by_key["kamb"]["hash"]["wording"]["de"] == hashing.wording_hash(by_key["kamb"]["wording"]["de"])


def test_build_refuses_a_bad_release_name(capsys):
    try:
        build.main(["--release", "november"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("no error")


def test_release_notes_from_the_changelog(tmp_path):
    (tmp_path / "CHANGELOG.md").write_text("# C\n\n## 2026.11.0\n\n- neu: x\n\n## 2026.10.0\n\n- alt\n", encoding="utf-8")
    assert build.notes(tmp_path, "2026.11.0") == "- neu: x\n"
    assert build.notes(tmp_path, "2027.01.0") == "Release 2027.01.0\n"


def test_roundtrip_builds_the_open_constructs():
    specs, missing, differing = roundtrip.build_all(ROOT)
    assert "kamb" in specs and "bfi10" in missing and not differing
    kamb = specs["kamb"]
    assert kamb["type"] == "semantic" and kamb["code"] == "KAMB"
    assert kamb["texts"]["en"]["pairs"]["p1"] == {"left": "professional", "right": "amateur"}
    sorgfalt = specs["sorgfalt"]
    assert set(sorgfalt["texts"]) == {"de", "de-du", "en"}
    assert sorgfalt["texts"]["de"]["options"]["o2"].startswith("Nein")


def _licensed_example(tmp_path, statements):
    """The licensed example as a construct, with an invented overlay in the old instruments.json format."""
    construct = common.load_yaml(ROOT / "examples" / "likert-lizenziert" / "construct.yaml")
    overlay = tmp_path / "instruments.json"
    overlay.write_text(json.dumps({"format": 1, "instruments": {construct["key"]: {
        "question": {"de": "Frage"}, "statements": [{"de": s} for s in statements]}}}), encoding="utf-8")
    return construct, overlay


def test_overlay_from_instruments_json(tmp_path):
    construct, overlay = _licensed_example(tmp_path, ["a", "b", "c", "d"])
    wordings = roundtrip.overlay_wordings(overlay, construct)
    assert wordings == {"de": {"question": "Frage", "items": {"BLZ_1": "a", "BLZ_2": "b", "BLZ_3": "c", "BLZ_4": "d"}}}
    spec = roundtrip.to_spec(construct, wordings)
    assert spec["texts"]["de"]["labels"][0] == "trifft gar nicht zu"
    assert spec["texts"]["de"]["statements"]["s4"] == "d"


def test_overlay_with_the_wrong_number_of_items_is_ignored(tmp_path):
    construct, overlay = _licensed_example(tmp_path, ["a", "b"])
    assert roundtrip.overlay_wordings(overlay, construct) == {}


def test_overlay_folder_format(tmp_path):
    construct = common.load_yaml(ROOT / "examples" / "likert-lizenziert" / "construct.yaml")
    folder = tmp_path / "overlay" / construct["key"]
    folder.mkdir(parents=True)
    (folder / "de.yaml").write_text(common.dump_yaml({"question": "Q", "items": {"BLZ_1": "a"}}), encoding="utf-8")
    assert roundtrip.overlay_wordings(tmp_path / "overlay", construct) == {"de": {"question": "Q", "items": {"BLZ_1": "a"}}}


def test_compare_names_the_differences():
    assert roundtrip.compare({"a": {"x": 1}}, {"a": {"x": 1}}) == []
    assert roundtrip.compare({"a": {"x": 1}, "b": {}}, {"a": {"x": 2}}) == ["a: spec differs", "b: not in the comparison"]


def test_seed_metadata():
    construct = common.load_yaml(ROOT / "constructs" / "sorgfalt" / "construct.yaml")
    seed = roundtrip.to_seed(construct)
    assert seed["authors"] == "Meade & Craig; Aust, Diedenhofen, Ullrich & Musch"
    assert seed["seed_version"] == 1 and "status:Standardfrage" in seed["tags"]
    assert seed["en"]["name"] == "Care taken in participating (self-report)"


def test_new_construct_from_an_example(catalogue):
    target = new.create(catalogue, "likert-offen", "meinkey")
    construct = common.load_yaml(target / "construct.yaml")
    assert construct["key"] == "meinkey" and construct["id"] == "ask:meinkey"
    assert common.load_yaml(target / "wording" / "de.yaml")["for"] == "ask:meinkey@1.0"
    assert validate.validate(catalogue) == []


def test_new_refuses_bad_keys_and_existing_folders(catalogue):
    for example, key in (("likert-offen", "Mein-Key"), ("likert-offen", "kamb"), ("gibtsnicht", "x")):
        try:
            new.create(catalogue, example, key)
        except ValueError:
            continue
        raise AssertionError((example, key))


def test_manifest_names_the_commit_of_a_clean_checkout(repo):
    data = build.manifest(repo, "2026.11.0-dev")
    assert data["release"] == "2026.11.0-dev" and len(data["commit"]) == 40
    assert list(common.validator("manifest").iter_errors(data)) == []
    (repo / "constructs" / "kamb" / "construct.yaml").write_text("changed: true\n", encoding="utf-8")
    assert build.commit(repo) is None  # uncommitted changes: no commit named
