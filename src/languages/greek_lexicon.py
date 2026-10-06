"""Greek lemmas and learner grammar from the Kaikki (English Wiktionary) Greek extract.

spaCy's Greek model leaves many verb forms unlemmatized (ρώτησε, πήρε, ήρθε). Wiktionary
lists form-of entries and full inflection tables, so the installer indexes them once and
the pipeline looks up (form, POS) -> lemma, plus gender and principal forms for cards.
"""

import json
import re
import sqlite3
import unicodedata
import uuid
from contextlib import closing
from functools import lru_cache

from tqdm import tqdm

from src.text import fold

SCHEMA_VERSION = "1"
FILENAME = "greek.sqlite"
SKIP_FORM_TAGS = {"romanization", "inflection-template", "table-tags", "class"}
# Some form entries describe themselves only in the gloss: "active nonfinite form of βρίσκω".
FORM_GLOSS = re.compile(r"(?<![a-z])(form|participle|plural|singular|tense|case) of(?![a-z])")
GENDER = re.compile(r"\)\s+(m|f|n)\b")
# The analyzer's own POS first; neighbouring POS (participle as adjective etc.) only as a fallback.
UD_TO_KAIKKI = {
    "NOUN": ("noun",),
    "PROPN": ("name", "noun"),
    "VERB": ("verb", "adj"),
    "AUX": ("verb",),
    "ADJ": ("adj", "verb"),
    "ADV": ("adv", "adj"),
    "PRON": ("pron",),
    "DET": ("article", "det", "pron"),
    "ADP": ("prep",),
    "NUM": ("num", "adj"),
}
PRINCIPAL_FORMS = {
    "genitive": {"genitive", "singular"},
    "plural": {"nominative", "plural"},
    "feminine": {"feminine", "nominative", "singular"},
    "neuter": {"neuter", "nominative", "singular"},
    "past": {"past"},
}


def bare(word):
    """Accent-free key: all-caps text is written without tonos (ΛΟΓΟΣ)."""
    return "".join(c for c in unicodedata.normalize("NFD", fold(word)) if not unicodedata.combining(c))


def clean_form(form):
    form = re.sub(r"\(.*?\)|[→*]", "", form).strip()
    return fold(form) if form and " " not in form and not form.startswith("-") else None


def defined_senses(entry):
    return [
        sense
        for sense in entry.get("senses", [])
        if not sense.get("form_of")
        and not sense.get("alt_of")
        and sense.get("glosses")
        and not FORM_GLOSS.search(sense["glosses"][0])
    ]


def principal_forms(entry):
    result = {}
    for item in entry.get("forms", []):
        tags = set(item.get("tags", []))
        form = clean_form(item["form"])
        for name, required in PRINCIPAL_FORMS.items():
            if form and name not in result and required <= tags and (name != "past" or len(tags) == 1):
                result[name] = form
    return result


def gender(entry):
    for template in entry.get("head_templates", []):
        match = GENDER.search(template.get("expansion", ""))
        if match:
            return match.group(1)
    return ""


def build(source, target):
    """Stream the Greek JSONL into a compact index; replace the old one only on success."""
    temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
    try:
        with closing(sqlite3.connect(temporary)) as db:
            db.execute("CREATE TABLE forms (form TEXT, bare TEXT, pos TEXT, lemma TEXT, UNIQUE(form, pos, lemma))")
            db.execute("CREATE TABLE alternatives (word TEXT, pos TEXT, main TEXT, PRIMARY KEY(word, pos))")
            db.execute(
                "CREATE TABLE headwords (lemma TEXT, pos TEXT, gender TEXT, genitive TEXT, plural TEXT, "
                "feminine TEXT, neuter TEXT, past TEXT, PRIMARY KEY(lemma, pos))"
            )
            with open(source, encoding="utf-8") as stream:
                for line in tqdm(stream, desc=source.name, unit=" entries"):
                    if line.strip():
                        _index_entry(db, json.loads(line))
            db.execute("CREATE INDEX forms_lookup ON forms(form, pos)")
            db.execute("CREATE INDEX forms_bare ON forms(bare, pos)")
            db.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT)")
            db.execute("INSERT INTO metadata VALUES ('schema_version', ?)", (SCHEMA_VERSION,))
            total = db.execute("SELECT COUNT(*) FROM forms").fetchone()[0]
            if not total:
                raise ValueError("В греческих данных Kaikki не найдено словоформ")
            db.commit()
        temporary.replace(target)
        return total
    finally:
        temporary.unlink(missing_ok=True)


def _index_entry(db, entry):
    if entry.get("lang_code") != "el" or not entry.get("word") or not entry.get("pos"):
        return
    word, pos = fold(entry["word"]), entry["pos"]
    senses = entry.get("senses", [])
    rows = [(word, lemma) for sense in senses for lemma in (fold(t["word"]) for t in sense.get("form_of", []))]
    alternatives = [fold(t["word"]) for sense in senses for t in sense.get("alt_of", [])]
    if defined_senses(entry):
        rows.append((word, word))
        rows.extend((form, word) for form in filter(None, map(clean_form, (f["form"] for f in entry.get("forms", [])
                     if not SKIP_FORM_TAGS & set(f.get("tags", []))))))
        forms = principal_forms(entry)
        db.execute(
            "INSERT OR IGNORE INTO headwords VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (word, pos, gender(entry), *(forms.get(name, "") for name in PRINCIPAL_FORMS)),
        )
    elif alternatives:
        db.execute("INSERT OR IGNORE INTO alternatives VALUES (?, ?, ?)", (word, pos, alternatives[0]))
    db.executemany(
        "INSERT OR IGNORE INTO forms VALUES (?, ?, ?, ?)", [(form, bare(form), pos, lemma) for form, lemma in rows]
    )


def is_healthy(path):
    if not path.is_file():
        return False
    try:
        with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)) as db:
            version = db.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
            return version == (SCHEMA_VERSION,) and db.execute("SELECT 1 FROM forms LIMIT 1").fetchone() is not None
    except (OSError, sqlite3.Error):
        return False


class GreekLexicon:
    def __init__(self, path):
        self.db = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=5, check_same_thread=False)
        self.lemma = lru_cache(maxsize=200_000)(self._lemma)

    def close(self):
        self.db.close()

    def canonical(self, lemma, upos):
        """Map alternative spellings (λέγω, ρωτώ) to the main Wiktionary headword."""
        for _ in range(3):
            row = next(
                (
                    row
                    for pos in UD_TO_KAIKKI.get(upos, ())
                    if (row := self.db.execute(
                        "SELECT main FROM alternatives WHERE word=? AND pos=?", (lemma, pos)
                    ).fetchone())
                ),
                None,
            )
            if not row or row[0] == lemma:
                break
            lemma = row[0]
        return lemma

    def _candidates(self, column, key, upos):
        for pos in UD_TO_KAIKKI.get(upos, ()):
            rows = self.db.execute(f"SELECT DISTINCT lemma FROM forms WHERE {column}=? AND pos=?", (key, pos))
            found = {self.canonical(lemma, upos) for (lemma,) in rows}
            if found:
                return found
        return set()

    def _lemma(self, form, upos, analyzer_lemma):
        """Correct the analyzer's lemma when Wiktionary knows the form; keep it otherwise."""
        form, base = fold(form), self.canonical(fold(analyzer_lemma), upos)
        candidates = self._candidates("form", form, upos)
        if not candidates and form == bare(form):
            candidates = self._candidates("bare", form, upos)
        if not candidates or base in candidates:
            return base
        if len(candidates) == 1:
            return next(iter(candidates))
        # Several readings: keep the one closest to the analyzer's guess.
        def shared_prefix(candidate):
            return next((i for i, (a, b) in enumerate(zip(candidate, base)) if a != b), min(len(candidate), len(base)))

        return max(sorted(candidates), key=shared_prefix)

    def is_headword(self, lemma):
        return self.db.execute("SELECT 1 FROM headwords WHERE lemma=? LIMIT 1", (lemma,)).fetchone() is not None

    def headword(self, lemma, upos):
        for pos in UD_TO_KAIKKI.get(upos, ())[:1]:
            row = self.db.execute(
                "SELECT gender, genitive, plural, feminine, neuter, past FROM headwords WHERE lemma=? AND pos=?",
                (lemma, pos),
            ).fetchone()
            if row:
                return dict(zip(("gender", *PRINCIPAL_FORMS), row))
        return None
