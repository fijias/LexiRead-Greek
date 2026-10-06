"""Learner forms for Greek from Wiktionary principal parts: ο δρόμος, του δρόμου, οι δρόμοι."""

from .pos_mapping import parse_morph

# nominative singular, genitive singular, nominative plural
ARTICLES = {"m": ("ο", "του", "οι"), "f": ("η", "της", "οι"), "n": ("το", "του", "τα")}
GENDER_RU = {"m": "мужской", "f": "женский", "n": "средний"}
UD_GENDER = {"Masc": "m", "Fem": "f", "Neut": "n"}


def observed_gender(entry):
    genders = {UD_GENDER.get(parse_morph(m).get("Gender")) for m in entry["morph_variants"]} - {None}
    return next(iter(genders)) if len(genders) == 1 else ""


def enrich_greek(entry, info, lexicon):
    lemma, pos = entry["lemma"], entry["pos"]
    if pos not in {"NOUN", "VERB", "AUX", "ADJ"}:
        return
    head = lexicon.headword(lemma, pos)
    if head is None and lexicon.is_headword(lemma):
        # Known word under another POS (που, όλος tagged NOUN): no noun article or forms.
        info.review.append("Часть речи не совпадает со словарём Kaikki")
        return
    if head is None:
        info.review.append("Лемма не найдена в словаре Kaikki: проверить лемматизацию")
        head = {}
    if pos == "NOUN":
        gender = head.get("gender") or observed_gender(entry)
        if gender not in ARTICLES:
            info.review.append("Род неизвестен или неоднозначен")
            return
        if head.get("gender") and observed_gender(entry) not in {"", gender}:
            info.review.append("Род словаря противоречит наблюдаемой морфологии")
        nominative, genitive, plural = ARTICLES[gender]
        info.grammatical_gender = GENDER_RU[gender]
        info.learning_form = f"{nominative} {lemma}"
        forms = [info.learning_form]
        if head.get("genitive"):
            forms.append(f"{genitive} {head['genitive']}")
        if head.get("plural"):
            info.plural_form = f"{plural} {head['plural']}"
            forms.append(info.plural_form)
        info.grammar_forms = ", ".join(forms)
    elif pos == "ADJ":
        if head.get("feminine") and head.get("neuter"):
            info.grammar_forms = f"{lemma}, {head['feminine']}, {head['neuter']}"
    elif head.get("past"):
        info.grammar_forms = f"{lemma}, {head['past']}"
