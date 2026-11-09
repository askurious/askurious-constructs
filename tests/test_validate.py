import shutil

import common
import validate
from conftest import ROOT, edit_yaml, git


def test_the_catalogue_itself_is_valid():
    assert validate.validate(ROOT) == []


def test_small_copy_is_valid(catalogue):
    assert validate.validate(catalogue) == []


def test_licensed_construct_may_not_have_a_wording_folder(catalogue):
    shutil.copytree(catalogue / "constructs" / "kamb" / "wording", catalogue / "constructs" / "bfi10" / "wording")
    errors = validate.validate(catalogue)
    assert any("no wording/ folder allowed" in e for e in errors)


def test_distributable_must_match_the_licence_vocabulary(catalogue):
    edit_yaml(catalogue / "constructs" / "bfi10" / "construct.yaml",
              lambda c: c["licence"].update(distributable=True))
    assert any("distributable must be False" in e for e in validate.validate(catalogue))


def test_unknown_licence_key(catalogue):
    edit_yaml(catalogue / "constructs" / "kamb" / "construct.yaml", lambda c: c["licence"].update(wording="frei"))
    assert any("not in schema/vocab/licences.yaml" in e for e in validate.validate(catalogue))


def test_wording_must_name_exactly_the_item_codes(catalogue):
    edit_yaml(catalogue / "constructs" / "kamb" / "wording" / "de.yaml",
              lambda w: w["items"].update(KAMB_9=w["items"].pop("KAMB_8")))
    errors = validate.validate(catalogue)
    assert any("missing ['KAMB_8'], unknown ['KAMB_9']" in e for e in errors)


def test_option_codes_are_checked_too(catalogue):
    edit_yaml(catalogue / "constructs" / "ratswd_ges1" / "wording" / "en.yaml", lambda w: w["options"].pop("3"))
    assert any("options: missing ['3']" in e for e in validate.validate(catalogue))


def test_german_and_english_are_required(catalogue):
    edit_yaml(catalogue / "constructs" / "kamb" / "construct.yaml", lambda c: c["name"].update(en=""))
    assert any("name: German and English are required" in e for e in validate.validate(catalogue))


def test_unknown_tag_and_bad_doi(catalogue):
    def change(c):
        c["tags"]["thema"] = ["Gibtsnicht"]
        c["sources"][0]["doi"] = "doi:10.1/x"
    edit_yaml(catalogue / "constructs" / "kamb" / "construct.yaml", change)
    errors = validate.validate(catalogue)
    assert any("'Gibtsnicht' is not in" in e for e in errors)
    assert any("is not a DOI" in e for e in errors)


def test_overlay_language_needs_a_hash(catalogue):
    edit_yaml(catalogue / "constructs" / "bfi10" / "construct.yaml", lambda c: c["languages"]["de"].pop("sha256"))
    assert any("needs its sha256" in e for e in validate.validate(catalogue))


def test_schema_errors_are_reported(catalogue):
    edit_yaml(catalogue / "constructs" / "kamb" / "construct.yaml", lambda c: c.update(version="2"))
    assert any("version" in e and "does not match" in e for e in validate.validate(catalogue))


def test_examples_are_checked(catalogue):
    edit_yaml(catalogue / "examples" / "likert-offen" / "construct.yaml", lambda c: c.pop("name"))
    assert any("examples/likert-offen" in e for e in validate.validate(catalogue))


# ---- version rule ----

def _wording_change(root):
    edit_yaml(root / "constructs" / "kamb" / "wording" / "de.yaml",
              lambda w: w.update(question="Bewerten Sie das Video mithilfe der folgenden Begriffspaare."))


def _set_version(root, key, version):
    def change(c):
        c["version"] = version
        c["versions"].insert(0, {"version": version})
    edit_yaml(root / "constructs" / key / "construct.yaml", change)


def test_wording_change_needs_a_new_minor_number(repo):
    _wording_change(repo)
    assert any("wording changed" in e for e in validate.validate(repo, base="main"))
    _set_version(repo, "kamb", "2.1")
    assert validate.validate(repo, base="main") == []


def test_structure_change_needs_a_new_major_number(repo):
    edit_yaml(repo / "constructs" / "kamb" / "construct.yaml",
              lambda c: c["structure"]["config"]["pairs"][1].update(reverse=True))
    _set_version(repo, "kamb", "2.1")
    assert any("structure changed" in e for e in validate.validate(repo, base="main"))
    _set_version(repo, "kamb", "3.0")
    assert validate.validate(repo, base="main") == []


def test_overlay_hash_change_counts_as_wording_change(repo):
    edit_yaml(repo / "constructs" / "bfi10" / "construct.yaml",
              lambda c: c["languages"]["de"].update(sha256="sha256:" + "b" * 64))
    assert any("bfi10" in e and "wording changed" in e for e in validate.validate(repo, base="main"))


def test_metadata_change_needs_no_new_version(repo):
    edit_yaml(repo / "constructs" / "kamb" / "construct.yaml",
              lambda c: c["description"].update(de="Andere Beschreibung."))
    assert validate.validate(repo, base="main") == []


def test_a_construct_must_not_disappear(repo):
    shutil.rmtree(repo / "constructs" / "kamb")
    assert any("never disappear" in e for e in validate.validate(repo, base="main"))


def test_version_must_not_go_down(repo):
    _set_version(repo, "kamb", "1.0")
    assert any("version went down" in e for e in validate.validate(repo, base="main"))


def test_retiring_keeps_the_key(repo):
    edit_yaml(repo / "constructs" / "kamb" / "construct.yaml",
              lambda c: c.update(status="retired", retired_since="2026.12.0"))
    assert validate.validate(repo, base="main") == []


def test_unknown_base_revision(repo):
    assert any("not found" in e for e in validate.validate(repo, base="nichtda"))


def test_new_construct_passes_against_base(repo):
    shutil.copytree(ROOT / "constructs" / "age", repo / "constructs" / "age")
    git(repo, "status")
    assert validate.validate(repo, base="main") == []
    assert len(common.construct_dirs(repo)) == 5
