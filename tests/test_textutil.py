from kkspell.textutil import KK_ALPHABET, split_sentences, tokenize


def test_tokenize_lowercases_and_drops_punctuation_and_digits():
    assert tokenize("Мен, мектепке 2 рет БАРДЫМ!") == ["мен", "мектепке", "рет", "бардым"]


def test_tokenize_keeps_kazakh_specific_letters():
    assert tokenize("Қазақстан әдемі өлке") == ["қазақстан", "әдемі", "өлке"]


def test_tokenize_ignores_latin_text():
    assert tokenize("Python және Git") == ["және"]


def test_split_sentences_requires_capital_after_terminator():
    text = "Мен барамын. Сен қайдасың? Ол кетті."
    assert split_sentences(text) == ["Мен барамын.", "Сен қайдасың?", "Ол кетті."]


def test_split_sentences_empty_input():
    assert split_sentences("") == []


def test_alphabet_has_all_kazakh_specific_letters():
    assert all(letter in KK_ALPHABET for letter in "әғқңөұүһі")
