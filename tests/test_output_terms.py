import re

from src.export.review import _GRAMMAR, SCRIPT_RU, describe
from src.grammar.greek import GENDER_RU
from src.grammar.pos_mapping import POS_RU
from src.output_terms import OUTPUT_EN

CYRILLIC = re.compile("[А-Яа-яЁё]")
ISSUES = [
    ("grammar", "Неизвестный ID"), ("translation", "Дублирующиеся IDs"), ("ipa", "Отсутствующий ID"),
    ("ipa", "Подозрительная IPA"), ("ipa", "x"),
    ("translation", "Пустой ru"), ("translation", "Пустой en"),
    ("translation", "ru: Markdown или длинное объяснение"), ("translation", "en: Markdown или длинное объяснение"),
    ("translation", "ru: проверить язык перевода"), ("translation", "en: проверить язык перевода"),
    ("grammar", "что-то новое"), ("nlp", "Неизвестный POS X"), ("nlp", "Пустая лемма"), ("nlp", "x"), ("other", "x"),
    *(("grammar", message) for message in _GRAMMAR),
]


def test_every_result_label_has_an_english_equivalent():
    labels = {*POS_RU.values(), *GENDER_RU.values(), *SCRIPT_RU.values()} - {"—"}
    for category, message in ISSUES:
        labels.update(describe({"category": category, "message": message}))
    missing = sorted(label for label in labels if label not in OUTPUT_EN)
    assert not missing
    assert not [text for text in OUTPUT_EN.values() if CYRILLIC.search(text)]
