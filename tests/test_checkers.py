from collections import Counter

import pytest

from kkspell.checkers import CharLM, SuffixStrip, VocabLookup

COUNTS = Counter({"мектеп": 5, "бару": 3, "кітап": 1})


def test_vocab_lookup_respects_min_freq():
    assert VocabLookup(COUNTS, 1).is_valid("кітап")
    assert not VocabLookup(COUNTS, 2).is_valid("кітап")
    assert not VocabLookup(COUNTS).is_valid("мектэп")


def test_vocab_lookup_rejects_bad_min_freq():
    with pytest.raises(ValueError):
        VocabLookup(COUNTS, 0)


def test_suffix_strip_accepts_known_stem_plus_suffix():
    checker = SuffixStrip(COUNTS)
    assert checker.is_valid("мектептер")   # мектеп + тер
    assert checker.is_valid("мектеп")
    assert not checker.is_valid("мектэптер")


def test_suffix_strip_does_not_strip_the_whole_word():
    # "ме" is itself a suffix, but nothing would be left as a stem
    assert not SuffixStrip(Counter({"мектеп": 9})).is_valid("ме")


WORDS = ["мектеп", "мектепке", "кітап", "кітаптар", "бардым", "барамыз", "оқыдым", "оқиды", "қалаға", "қалада"] * 3


def test_charlm_scores_real_words_higher_than_garbage():
    lm = CharLM(WORDS, order=3)
    assert lm.score("мектепке") > lm.score("ъъфцйк")


def test_charlm_threshold_must_be_set_before_use():
    with pytest.raises(RuntimeError):
        CharLM(WORDS).is_valid("мектеп")


def test_charlm_fit_threshold_separates_valid_from_garbage():
    lm = CharLM(WORDS, order=3)
    labelled = [(w, 0) for w in set(WORDS)] + [(w, 1) for w in ("ъъфцйк", "жшщъь", "ццццц", "мктпк")]
    lm.fit_threshold(labelled)
    assert lm.is_valid("мектепке") and not lm.is_valid("ъъфцйк")


def test_charlm_needs_training_data_and_valid_order():
    with pytest.raises(ValueError):
        CharLM([])
    with pytest.raises(ValueError):
        CharLM(["сөз"], order=1)
