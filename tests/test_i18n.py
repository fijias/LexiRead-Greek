import string

import pytest

from src import i18n
from src.gui.worker import friendly_error


def placeholders(text):
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def test_every_message_has_both_languages_with_same_placeholders():
    for key, (english, russian) in i18n.TEXT.items():
        assert english and russian, key
        assert placeholders(english) == placeholders(russian), key
    assert set(i18n.HELP) == set(i18n.LANGUAGES)


def test_switch_language_and_persist(tmp_path, monkeypatch):
    monkeypatch.setattr(i18n, "SETTINGS", tmp_path / "settings.json")
    i18n.set_language("en")
    assert i18n.t("btn.start") == "Start analysis"
    assert friendly_error("nlp", RuntimeError()).startswith("Text analysis failed")
    assert i18n.language_forms("el")["acc"] == "Greek"
    monkeypatch.delenv(i18n.ENV)
    monkeypatch.setattr(i18n, "_current", None)
    assert i18n.get_language() == "en"
    i18n.set_language("ru")
    assert i18n.t("btn.start") == "Начать анализ"
    assert i18n.t("install.title", **i18n.language_forms("el")) == "Установка греческого языка"


def test_unknown_language_is_rejected():
    with pytest.raises(ValueError):
        i18n.set_language("de", save=False)
