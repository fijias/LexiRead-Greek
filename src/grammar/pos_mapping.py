POS_RU = {
    "NOUN": "существительное",
    "VERB": "глагол",
    "ADJ": "прилагательное",
    "ADV": "наречие",
    "PRON": "местоимение",
    "DET": "определитель / артикль",
    "ADP": "предлог",
    "AUX": "вспомогательный глагол",
    "PROPN": "имя собственное",
    "CCONJ": "сочинительный союз",
    "SCONJ": "подчинительный союз",
    "PART": "частица",
    "NUM": "числительное",
    "INTJ": "междометие",
    "SYM": "символ",
    "X": "неизвестно",
}

MORPH = {
    "Gender": {"Fem": "женский род", "Masc": "мужской род", "Neut": "средний род", "Com": "общий род"},
    "Case": {"Nom": "именительный", "Gen": "родительный", "Acc": "винительный", "Voc": "звательный", "Dat": "дательный"},
    "Aspect": {"Imp": "несовершенный вид", "Perf": "совершенный вид"},
    "Voice": {"Act": "действительный залог", "Pass": "страдательный залог"},
    "Number": {"Sing": "единственное число", "Plur": "множественное число"},
    "Person": {"1": "1 лицо", "2": "2 лицо", "3": "3 лицо"},
    "Mood": {"Ind": "Indicativo", "Sub": "Subjuntivo", "Imp": "Imperativo", "Cnd": "Condicional"},
    "Tense": {
        "Pres": "Presente",
        "Past": "Pretérito",
        "Imp": "Imperfecto",
        "Fut": "Futuro",
        "Pqp": "Pluscuamperfecto",
    },
    "VerbForm": {"Inf": "инфинитив", "Fin": "личная форма", "Ger": "герундий", "Part": "причастие"},
    "Definite": {"Def": "определённый", "Ind": "неопределённый"},
    "PronType": {
        "Art": "артикль",
        "Prs": "личное",
        "Rel": "относительное",
        "Int": "вопросительное",
        "Dem": "указательное",
        "Ind": "неопределённое",
        "Neg": "отрицательное",
        "Tot": "обобщающее",
    },
    "Polarity": {"Neg": "отрицание"},
    "Reflex": {"Yes": "возвратность"},
}


def parse_morph(raw):
    return dict(part.split("=", 1) for part in raw.split("|") if "=" in part)


# Spanish tense and mood names do not fit Greek verbs.
GREEK_MORPH = {
    **MORPH,
    "Mood": {"Ind": "изъявительное", "Sub": "сослагательное", "Imp": "повелительное"},
    "Tense": {"Pres": "настоящее", "Past": "прошедшее", "Fut": "будущее"},
    "VerbForm": {**MORPH["VerbForm"], "Conv": "деепричастие"},
}


# Feature names for result files in English.
MORPH_EN = {
    "Gender": {"Fem": "feminine", "Masc": "masculine", "Neut": "neuter", "Com": "common gender"},
    "Case": {"Nom": "nominative", "Gen": "genitive", "Acc": "accusative", "Voc": "vocative", "Dat": "dative"},
    "Aspect": {"Imp": "imperfective", "Perf": "perfective"},
    "Voice": {"Act": "active", "Pass": "passive"},
    "Number": {"Sing": "singular", "Plur": "plural"},
    "Person": {"1": "1st person", "2": "2nd person", "3": "3rd person"},
    "Mood": {"Ind": "indicative", "Sub": "subjunctive", "Imp": "imperative", "Cnd": "conditional"},
    "Tense": {"Pres": "present", "Past": "past", "Imp": "imperfect", "Fut": "future", "Pqp": "pluperfect"},
    "VerbForm": {"Inf": "infinitive", "Fin": "finite", "Ger": "gerund", "Part": "participle", "Conv": "converb"},
    "Definite": {"Def": "definite", "Ind": "indefinite"},
    "PronType": {
        "Art": "article", "Prs": "personal", "Rel": "relative", "Int": "interrogative",
        "Dem": "demonstrative", "Ind": "indefinite", "Neg": "negative", "Tot": "total",
    },
    "Polarity": {"Neg": "negative"},
    "Reflex": {"Yes": "reflexive"},
}


def format_morph(raw, language="es", output="ru"):
    names = MORPH_EN if output == "en" else GREEK_MORPH if language == "el" else MORPH
    result = []
    for key, values in parse_morph(raw).items():
        result.append(
            " / ".join(names.get(key, {}).get(value, f"{key}={value}") for value in values.split(","))
        )
    return ", ".join(result)
