import pytest

from kkspell.metrics import bootstrap_f1_ci, prf


def test_prf_perfect_prediction():
    m = prf([True, False, True, False], [1, 0, 1, 0])
    assert m == {"precision": 1.0, "recall": 1.0, "f1": 1.0, "fpr": 0.0}


def test_prf_counts_false_alarms_and_misses():
    m = prf([True, True, False, False], [1, 0, 1, 0])
    assert m["precision"] == 0.5 and m["recall"] == 0.5 and m["fpr"] == 0.5 and m["f1"] == 0.5


def test_prf_handles_no_predicted_positives():
    assert prf([False, False], [1, 0])["f1"] == 0.0


def test_prf_length_mismatch_raises():
    with pytest.raises(ValueError):
        prf([True], [1, 0])


def test_bootstrap_interval_contains_point_estimate():
    pred = [True] * 40 + [False] * 10 + [True] * 5 + [False] * 45
    labels = [1] * 50 + [0] * 50
    lo, hi = bootstrap_f1_ci(pred, labels, n_resamples=300, seed=1)
    assert lo <= prf(pred, labels)["f1"] <= hi and 0 <= lo <= hi <= 1


def test_bootstrap_is_reproducible():
    pred, labels = [True, False, True, False] * 10, [1, 0, 0, 1] * 10
    assert bootstrap_f1_ci(pred, labels, 100, seed=3) == bootstrap_f1_ci(pred, labels, 100, seed=3)


def test_bootstrap_rejects_empty_input():
    with pytest.raises(ValueError):
        bootstrap_f1_ci([], [])
