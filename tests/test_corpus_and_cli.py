import json
from pathlib import Path

import pytest

from kkspell.__main__ import main
from kkspell.corpus import build_splits, read_blocks, split_of
from kkspell.evaluate import evaluate

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample_corpus_kk.txt"


def test_split_of_is_deterministic_and_covers_all_parts():
    parts = {split_of(i) for i in range(500)}
    assert parts == {"train", "dev", "test"}
    assert split_of(12345) == split_of(12345)


def test_split_proportions_are_roughly_80_10_10():
    parts = [split_of(i) for i in range(5000)]
    assert 0.75 < parts.count("train") / 5000 < 0.85
    assert 0.07 < parts.count("test") / 5000 < 0.13


def test_read_blocks_block_format(tmp_path):
    f = tmp_path / "c.txt"
    f.write_text("#7\nМен барамын.\nСен келдің.\n\n#9\nОл кетті.\n", encoding="utf-8")
    assert read_blocks(f) == [(7, ["Мен барамын.", "Сен келдің."]), (9, ["Ол кетті."])]


def test_read_blocks_plain_text_groups_lines(tmp_path):
    f = tmp_path / "plain.txt"
    f.write_text("\n".join(f"Сөйлем {i} бар." for i in range(7)), encoding="utf-8")
    blocks = read_blocks(f, block_size=3)
    assert [len(s) for _, s in blocks] == [3, 3, 1]


def test_build_splits_drops_short_and_duplicate_sentences():
    train_id = next(i for i in range(100) if split_of(i) == "train")
    blocks = [(train_id, ["Мен бардым.", "Мен бардым.", "Ия.", "Біз келдік үйге.", "Біз келдік үйге."])]
    splits = build_splits(blocks)
    all_sentences = [s for part in splits.values() for s in part]
    assert ["ия"] not in all_sentences
    assert all_sentences.count(["біз", "келдік", "үйге"]) == 1  # duplicate removed
    assert ["мен", "бардым"] not in all_sentences  # only two tokens: shorter than min_tokens


def test_build_splits_test_sentences_never_occur_in_train():
    splits = build_splits(read_blocks(SAMPLE, block_size=5))
    train = {" ".join(s) for s in splits["train"]}
    assert all(" ".join(s) not in train for s in splits["test"] + splits["dev"])


def test_evaluate_on_sample_corpus_returns_all_methods():
    splits = build_splits(read_blocks(SAMPLE, block_size=5))
    result = evaluate(splits, n_eval=80, seed=0, bootstrap=50)
    assert set(result["methods"]) == {"vocabulary", "suffix-strip", "char-LM"}
    for metrics in result["methods"].values():
        lo, hi = metrics["f1_ci95"]
        assert 0 <= metrics["f1"] <= 1 and lo <= hi


def test_evaluate_reports_empty_splits():
    with pytest.raises(ValueError, match="empty"):
        evaluate({"train": [["а", "б", "в"]], "dev": [], "test": []})


def test_cli_evaluate_prints_a_table(capsys):
    assert main(["evaluate", str(SAMPLE), "--n-eval", "60", "--bootstrap", "50"]) == 0
    out = capsys.readouterr().out
    assert "vocabulary" in out and "char-LM" in out


def test_cli_evaluate_json_is_valid_json(capsys):
    main(["evaluate", str(SAMPLE), "--n-eval", "60", "--bootstrap", "50", "--json"])
    assert "methods" in json.loads(capsys.readouterr().out)


def test_cli_check_prints_a_verdict_per_word(capsys):
    assert main(["check", str(SAMPLE), "мектепке", "ъъъъ"]) == 0
    assert "мектепке" in capsys.readouterr().out
