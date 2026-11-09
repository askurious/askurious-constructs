import hash as hashing


def test_wording_hash_ignores_quotes_spaces_and_unicode_form():
    a = {"question": "Wie  finden Sie „das“ Video?\n", "items": {"X_1": "Café"}}
    b = {"question": 'Wie finden Sie "das" Video?', "items": {"X_1": "Café"}}
    assert hashing.wording_hash(a) == hashing.wording_hash(b)


def test_wording_hash_sees_a_changed_word():
    a = {"question": "Wie finden Sie das Video?"}
    b = {"question": "Wie fanden Sie das Video?"}
    assert hashing.wording_hash(a) != hashing.wording_hash(b)


def test_wording_hash_ignores_the_for_line_and_key_order():
    a = {"for": "ask:x@1.0", "question": "Q", "items": {"X_1": "a", "X_2": "b"}}
    b = {"items": {"X_2": "b", "X_1": "a"}, "question": "Q"}
    assert hashing.wording_hash(a) == hashing.wording_hash(b)


def test_structure_hash_changes_with_polarity():
    c = {"structure": {"type": "likert", "code": "X", "config": {"statements": [{"id": "s1", "code": "X_1", "reverse": False}]}}}
    d = {"structure": {"type": "likert", "code": "X", "config": {"statements": [{"id": "s1", "code": "X_1", "reverse": True}]}}}
    assert hashing.structure_hash(c) != hashing.structure_hash(d)
    assert hashing.structure_hash(c).startswith("sha256:") and len(hashing.structure_hash(c)) == 71


def test_overlay_languages_use_the_stored_hash():
    stored = "sha256:" + "a" * 64
    c = {"languages": {"de": {"wording": "overlay", "sha256": stored}, "en": {"wording": "repo"}}}
    out = hashing.wording_hashes(c, {"en": {"question": "Q"}})
    assert out == {"de": stored, "en": hashing.wording_hash({"question": "Q"})}
