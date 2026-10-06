import re
from collections import Counter
from dataclasses import dataclass

from src.cards.formatter import normalize_card_form
from src.cards.models import CardEntry
from src.languages import get_profile
from src.lemma_groups import group_lemmas
from src.text import script
from src.translation.selection import TranslationSelection, select_lemmas_by_cumulative_coverage


FUNCTION_POS = frozenset({"PRON", "ADP", "DET", "CCONJ", "SCONJ", "PART", "AUX", "INTJ"})
# Alphabet of the text language: words in another alphabet are names, brands or quotes.
ALPHABETS = {"el": "greek", "en": "latin", "es": "latin"}
FORECAST_COVERAGES = (70, 80, 85, 90, 95)


@dataclass(frozen=True)
class CardPolicy:
    exclude_function_words: bool = False
    exclude_proper_nouns: bool = False
    exclude_numbers: bool = False
    text_alphabet_only: bool = False
    max_cards: int = 0
    assumed_known: frozenset = frozenset()

    @classmethod
    def from_config(cls, cards_config, assumed_known=frozenset()):
        return cls(
            cards_config.exclude_function_words,
            cards_config.exclude_proper_nouns,
            cards_config.exclude_numbers,
            cards_config.text_alphabet_only,
            cards_config.max_cards,
            frozenset(assumed_known),
        )

    def excluded_pos(self):
        return (
            (FUNCTION_POS if self.exclude_function_words else frozenset())
            | ({"PROPN"} if self.exclude_proper_nouns else frozenset())
            | ({"NUM"} if self.exclude_numbers else frozenset())
        )

    def skips(self, group, language):
        """True when a lemma group gets no card; a group is excluded only if all its POS are."""
        poses = {row["pos"] for row in group["rows"]}
        if poses and poses <= self.excluded_pos():
            return "category"
        if self.text_alphabet_only and script(group["lemma"]) != ALPHABETS.get(language, script(group["lemma"])):
            return "alphabet"
        if normalize_card_form(group["lemma"]) in self.assumed_known:
            return "level"
        return None


def select_cards(
    data: dict[str, list[dict]],
    coverage_limit: float,
    specificity_threshold: float = 2.0,
    min_book_occurrences: int = 3,
    language="es",
    known_words: set[str] | None = None,
    policy: CardPolicy | None = None,
) -> tuple[list[CardEntry], TranslationSelection]:
    lemmas = data["lemmas"]
    selection = select_lemmas_by_cumulative_coverage(
        lemmas, data["forms"], coverage_limit, specificity_threshold, min_book_occurrences
    )
    grammar = {row["id"]: row for row in data["lemma_grammar"]}
    ipa = {row["text"]: row.get("ipa", "") for row in data["ipa"]}
    translations = {row["id"]: row for row in data["translations"]}
    cards = []
    missing = {"IPA": 0, "Russian translations": 0, "observed forms": 0}
    show_english = get_profile(language).cards_show_english_translation
    if show_english:
        missing["English translations"] = 0

    def joined(values, separator=", "):
        unique = {}
        for value in values:
            for part in re.split(r"[,;/|]", value or ""):
                part = part.strip()
                if part and part not in {"—", "-"}:
                    unique.setdefault(normalize_card_form(part), part)
        return separator.join(unique.values())

    for group in group_lemmas(lemmas, data["forms"]):
        rows = group["rows"]
        if not any(r["id"] in selection.eligible_lemma_ids for r in rows) or normalize_card_form(
            group["lemma"]
        ) in (known_words or set()):
            continue
        if policy and policy.skips(group, language):
            continue
        gs = [grammar.get(r["id"], {}) for r in rows]
        ts = [translations.get(r["id"], {}) for r in rows]
        observed = Counter()
        for row in rows:
            for form, count in (row.get("observed_forms") or {}).items():
                observed[normalize_card_form(form)] += count
        value = CardEntry(
            lemma=group["lemma"],
            pos=", ".join(r["pos"] for r in rows),
            rank=group["rank"],
            grammatical_forms=(
                gs[0].get("grammar_forms", "")
                if len(rows) == 1
                else joined(g.get("grammar_forms", "") for g in gs)
            ),
            learning_form=(
                gs[0].get("learning_form", "")
                if len(rows) == 1
                else group["lemma"]
                if language == "en"
                else joined(g.get("learning_form", "") for g in gs)
            ),
            ipa=ipa.get(group["lemma"]) or "-",
            translation_ru=joined(t.get("ru") for t in ts) or "—",
            translation_en=joined(t.get("en") for t in ts) or "—",
            observed_forms=dict(observed),
        )
        if value.ipa == "-":
            missing["IPA"] += 1
        if value.translation_ru == "—":
            missing["Russian translations"] += 1
        if show_english and value.translation_en == "—":
            missing["English translations"] += 1
        if not value.observed_forms:
            missing["observed forms"] += 1
        cards.append(value)
    if policy and policy.max_cards and len(cards) > policy.max_cards:
        # Groups come in frequency order, so the cap keeps the most important words.
        cards = cards[: policy.max_cards]
    nonzero = {name: count for name, count in missing.items() if count}
    if nonzero:
        import logging

        logging.getLogger(__name__).info(
            "Карточки с заглушками/пропусками: %s.",
            ", ".join(f"{name}: {count}" for name, count in nonzero.items()),
        )
    return cards, selection


def forecast(data, translation_config, language, known_words, policy):
    """How many cards each coverage level would give with the same filters and no cap."""
    uncapped = CardPolicy(**{**policy.__dict__, "max_cards": 0}) if policy else None
    return {
        coverage: len(
            select_cards(
                data,
                coverage,
                translation_config.specificity_threshold,
                translation_config.min_book_occurrences,
                language,
                known_words,
                uncapped,
            )[0]
        )
        for coverage in FORECAST_COVERAGES
    }
