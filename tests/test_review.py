from src.export.review import make_review_rows


def test_normal_homonymy_does_not_require_user_attention():
    data = {
        "lemmas": [],
        "forms": [],
        "validation": [
            {"id": "x", "category": "ambiguity", "severity": "info", "message": "watch: lemma/POS"}
        ],
    }
    assert make_review_rows(data)[0][5] == "Замечаний нет"
    data["validation"] = []
    assert make_review_rows(data)[0][5] == "Замечаний нет"


def test_review_localizes_prioritizes_and_deduplicates():
    data = {
        "lemmas": [{"id": "lemma", "lemma": "watch", "pos": "VERB"}],
        "forms": [{"id": "form", "lemma": "watch", "form": "watch", "pos": "VERB"}],
        "validation": [
            {"id": "lemma", "category": "ipa", "severity": "review", "message": "unsupported input"},
            {"id": "form", "category": "ipa", "severity": "review", "message": "unsupported input"},
            {"id": "lemma", "category": "translation", "severity": "error", "message": "Пустой ru"},
        ],
    }
    rows = make_review_rows(data)
    assert len(rows) == 2
    assert rows[0][:3] == ["watch", "Латиница", "глагол"]
    assert rows[0][5:7] == ["Ошибка", "Отсутствует перевод на русский"]
    assert rows[1][6] == "Не удалось получить транскрипцию"
    assert all(row[7] for row in rows)


def test_integrity_errors_remain_visible_without_technical_ids():
    rows = make_review_rows(
        {
            "lemmas": [],
            "forms": [],
            "validation": [
                {
                    "id": "internal-hash",
                    "category": "grammar",
                    "severity": "error",
                    "message": "Неизвестный ID",
                }
            ],
        }
    )
    assert rows[0][0] == "Весь словарь"
    assert rows[0][5] == "Ошибка"
    assert "разработчику" in rows[0][7]
    assert "internal-hash" not in str(rows)


def test_review_shows_alphabet_and_puts_card_words_first():
    data = {
        "lemmas": [
            {"id": "a", "lemma": "rotation", "pos": "X", "count": 9, "contexts": ["Το rotation άλλαξε."]},
            {"id": "b", "lemma": "δρόμος", "pos": "NOUN", "count": 3, "contexts": ["Ο δρόμος."]},
            {"id": "c", "lemma": "λόγοσ1", "pos": "NOUN", "count": 50, "contexts": []},
        ],
        "forms": [],
        "translations": [
            {"id": "a", "translation_eligible": False},
            {"id": "b", "translation_eligible": True},
            {"id": "c", "translation_eligible": True, "error": "known word excluded"},
        ],
        "validation": [
            {"id": i, "category": "nlp", "severity": "review", "message": "Неизвестный POS"} for i in "abc"
        ],
    }
    rows = make_review_rows(data)
    assert [(r[0], r[1], r[3], r[4]) for r in rows] == [
        ("δρόμος", "Греческий", 3, "Да"),
        ("λόγοσ1", "Греческий", 50, "Нет"),
        ("rotation", "Латиница", 9, "Нет"),
    ]
    assert rows[0][8] == "Ο δρόμος."
