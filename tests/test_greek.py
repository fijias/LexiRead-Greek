import json

import pytest

from src.cards.formatter import extract_forms_from_front, normalize_card_form
from src.config import Preprocess
from src.grammar.greek import enrich_greek
from src.languages import get_profile
from src.languages.greek_lexicon import GreekLexicon, build
from src.models import GrammarInfo
from src.preprocessing.greek import normalize_greek
from src.preprocessing.loader import read_text_auto, run
from src.text import fold
from src.translation.kaikki import gloss_rows

ENTRIES = [
    {
        "word": "ρωτάω", "pos": "verb", "lang_code": "el",
        "senses": [{"glosses": ["to ask"]}],
        "forms": [{"form": "ρώτησα", "tags": ["past"]}, {"form": "rotáo", "tags": ["romanization"]}],
    },
    {
        "word": "ρώτησε", "pos": "verb", "lang_code": "el",
        "senses": [{"glosses": ["third-person singular simple past of ρωτάω"], "form_of": [{"word": "ρωτάω"}]}],
    },
    {"word": "ρωτώ", "pos": "verb", "lang_code": "el", "senses": [{"glosses": ["x"], "alt_of": [{"word": "ρωτάω"}]}]},
    {
        "word": "βρει", "pos": "verb", "lang_code": "el",
        # A form entry whose first sense is described only in its gloss.
        "senses": [{"glosses": ["active nonfinite form of βρίσκω"]}, {"glosses": ["y"], "form_of": [{"word": "βρίσκω"}]}],
    },
    {
        "word": "δρόμος", "pos": "noun", "lang_code": "el",
        "head_templates": [{"expansion": "δρόμος • (drómos) m (plural δρόμοι)"}],
        "senses": [{"glosses": ["roadway, road (paved), street"]}],
        "forms": [
            {"form": "δρόμου", "tags": ["genitive", "singular"]},
            {"form": "δρόμοι", "tags": ["nominative", "plural"]},
            {"form": "ΔΡΟΜΟΣ", "tags": ["no-table-tags"]},
        ],
    },
    {
        "word": "μεγάλος", "pos": "adj", "lang_code": "el",
        "senses": [{"glosses": ["big"]}],
        "forms": [
            {"form": "μεγάλη", "tags": ["feminine", "nominative", "singular"]},
            {"form": "μεγάλο", "tags": ["neuter", "nominative", "singular"]},
        ],
    },
]


@pytest.fixture
def lexicon(tmp_path):
    source = tmp_path / "el-extract.jsonl"
    source.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in ENTRIES), encoding="utf-8")
    target = tmp_path / "greek.sqlite"
    build(source, target)
    result = GreekLexicon(target)
    yield result
    result.close()


def test_fold_keeps_final_sigma():
    assert fold("ΛΌΓΟΣ λόγος σας") == "λόγος λόγος σας"
    assert fold("Casa ESTÁ") == "casa está"


def test_card_matching_keeps_final_sigma_and_strips_greek_articles():
    assert normalize_card_form("Δρόμος") == "δρόμος"
    assert extract_forms_from_front("ο δρόμος, του δρόμου, οι δρόμοι") == {"δρόμος", "δρόμου", "δρόμοι"}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("σ' αυτό, μ'αρέσει, Γι' αυτό", "σε αυτό, με αρέσει, Για αυτό"),
        ("τ' άσπρα στ' αυτιά", "τ' άσπρα στ' αυτιά"),
        ("η ένωσή του", "η ένωση του"),
        ("οµάδα", "ομάδα"),
        ("Ἐν ἀρχῇ ἦν ὁ λόγος, καὶ τὸ φῶς ἢ", "Εν αρχή ην ο λόγος, και το φως ή"),
    ],
)
def test_normalize_greek(raw, expected):
    assert normalize_greek(raw) == expected


def test_loader_reads_greek_windows_1253(tmp_path):
    source, target = tmp_path / "book.txt", tmp_path / "normalized.txt"
    expected = "Καλημέρα, τι κάνεις;"
    source.write_bytes(expected.encode("cp1253"))
    assert read_text_auto(source, "el") == (expected, "cp1253")
    run(source, target, Preprocess(), "el")
    assert target.read_text(encoding="utf-8") == expected + "\n"


def test_lexicon_corrects_lemmas(lexicon):
    assert lexicon.lemma("ρώτησε", "VERB", "ρώτησε") == "ρωτάω"
    assert lexicon.lemma("ρωτώ", "VERB", "ρωτώ") == "ρωτάω"
    assert lexicon.lemma("βρει", "VERB", "βρει") == "βρίσκω"
    # All-caps text has no tonos.
    assert lexicon.lemma("ΔΡΟΜΟΥ", "NOUN", "δρομου") == "δρόμος"
    # Unknown forms keep the analyzer's lemma.
    assert lexicon.lemma("ξένο", "NOUN", "ξένος") == "ξένος"


def test_greek_learning_forms(lexicon):
    noun = GrammarInfo("n", learning_form="δρόμος")
    enrich_greek({"lemma": "δρόμος", "pos": "NOUN", "morph_variants": ["Case=Nom|Gender=Masc"]}, noun, lexicon)
    assert noun.grammar_forms == "ο δρόμος, του δρόμου, οι δρόμοι"
    assert noun.grammatical_gender == "мужской" and not noun.review

    verb = GrammarInfo("v", learning_form="ρωτάω")
    enrich_greek({"lemma": "ρωτάω", "pos": "VERB", "morph_variants": []}, verb, lexicon)
    assert verb.grammar_forms == "ρωτάω, ρώτησα"

    adjective = GrammarInfo("a", learning_form="μεγάλος")
    enrich_greek({"lemma": "μεγάλος", "pos": "ADJ", "morph_variants": []}, adjective, lexicon)
    assert adjective.grammar_forms == "μεγάλος, μεγάλη, μεγάλο"

    unknown = GrammarInfo("u", learning_form="ξένος")
    enrich_greek({"lemma": "ξένος", "pos": "NOUN", "morph_variants": ["Gender=Masc"]}, unknown, lexicon)
    assert unknown.learning_form == "ο ξένος"
    assert "Лемма не найдена в словаре Kaikki: проверить лемматизацию" in unknown.review


def test_gloss_rows_by_edition():
    english = list(gloss_rows(ENTRIES[4], "el"))
    assert [row[4] for row in english] == ["roadway", "road", "street"]
    assert {row[3] for row in english} == {"en"}
    russian = {"word": "άλογο", "pos": "noun", "lang_code": "el", "senses": [{"glosses": ["зоол. лошадь, конь"]}]}
    assert [(r[3], r[4], r[5]) for r in gloss_rows(russian, "ru")] == [("ru", "лошадь", 2), ("ru", "конь", 2)]
    assert list(gloss_rows(ENTRIES[4], "es")) == []


def test_greek_profile():
    profile = get_profile("el")
    assert profile.translation_targets == ("ru", "en")
    assert profile.cards_show_english_translation


def test_mistagged_noun_gets_no_article(lexicon):
    info = GrammarInfo("m", learning_form="μεγάλος")
    enrich_greek({"lemma": "μεγάλος", "pos": "NOUN", "morph_variants": ["Gender=Neut"]}, info, lexicon)
    assert info.learning_form == "μεγάλος" and not info.grammar_forms
    assert "Часть речи не совпадает со словарём Kaikki" in info.review


def test_gloss_notes_are_skipped():
    entry = {
        "word": "έχω", "pos": "verb", "lang_code": "el",
        "senses": [{"glosses": ["to have, hold"]}, {"glosses": ["alternative of μου"]}, {"glosses": ["Plant and fruit senses"]}],
    }
    assert [row[4] for row in gloss_rows(entry, "el")] == ["to have", "hold"]


def test_particles_tagged_aux_are_not_flagged(lexicon):
    info = GrammarInfo("p", learning_form="να")
    enrich_greek({"lemma": "να", "pos": "AUX", "morph_variants": []}, info, lexicon)
    assert not info.review and not info.grammar_forms


def test_english_interface_puts_english_translation_first(monkeypatch):
    from src import i18n
    from src.cards.formatter import card_content
    from src.cards.models import CardEntry

    card = CardEntry(lemma="δρόμος", pos="NOUN", rank=1, grammatical_forms="", learning_form="ο δρόμος",
                     ipa="ˈðromos", translation_ru="дорога", translation_en="road", observed_forms={})
    assert card_content(card, language="el")[2] == ["дорога", "road"]
    monkeypatch.setattr(i18n, "_current", "en")
    assert card_content(card, language="el")[2] == ["road", "дорога"]
