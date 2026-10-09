import random

import pytest

from kkspell.errors import ERROR_TYPES, corrupt, make_eval_set


def test_diacritic_loss_replaces_kazakh_letter_with_look_alike():
    assert corrupt("қалай", "diacritic", random.Random(0)) == "калай"


def test_diacritic_not_applicable_without_kazakh_letters():
    assert corrupt("мектеп", "diacritic", random.Random(0)) is None


def test_harmony_swaps_a_vowel_in_the_ending():
    bad = corrupt("мектепке", "harmony", random.Random(0))
    assert bad is not None and bad != "мектепке" and bad[:4] == "мект"


def test_delete_needs_four_letters():
    assert corrupt("үй", "delete", random.Random(0)) is None
    assert len(corrupt("мектеп", "delete", random.Random(0))) == 5


def test_insert_adds_exactly_one_letter():
    assert len(corrupt("мектеп", "insert", random.Random(1))) == 7


def test_transpose_keeps_letters():
    bad = corrupt("барды", "transpose", random.Random(2))
    assert sorted(bad) == sorted("барды") and bad != "барды"


def test_unknown_error_type_raises():
    with pytest.raises(ValueError):
        corrupt("сөз", "nonsense", random.Random(0))


@pytest.mark.parametrize("etype", ERROR_TYPES)
def test_every_error_type_changes_the_word_when_applicable(etype):
    rng = random.Random(3)
    word = "қазақстанда"  # contains Kazakh-specific letters and a harmony vowel in the ending
    results = [corrupt(word, etype, rng) for _ in range(30)]
    assert any(r is not None and r != word for r in results)


SENTENCES = [["мен", "мектепке", "бардым"], ["біз", "қалаға", "барамыз"], ["ол", "кітап", "оқиды"]]


def test_make_eval_set_has_requested_balance():
    items = make_eval_set(SENTENCES, n_valid=20, n_error=10, seed=1)
    assert sum(i.label for i in items) == 10 and len(items) == 30


def test_make_eval_set_is_deterministic_for_a_seed():
    a = make_eval_set(SENTENCES, 15, 15, seed=7)
    b = make_eval_set(SENTENCES, 15, 15, seed=7)
    assert a == b
    assert a != make_eval_set(SENTENCES, 15, 15, seed=8)


def test_make_eval_set_valid_items_are_untouched_and_errors_differ_from_original():
    for item in make_eval_set(SENTENCES, 20, 20, seed=2):
        assert (item.word == item.original) == (item.label == 0)


def test_make_eval_set_rejects_empty_input():
    with pytest.raises(ValueError):
        make_eval_set([], 1, 1)
