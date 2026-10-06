import json
import logging
from collections import defaultdict
from pathlib import Path

from src.models import GrammarInfo
from src.storage import read_rows, write_rows

from .adjectives import enrich_adjective
from .greek import enrich_greek
from .nouns import enrich_noun
from .pos_mapping import POS_RU, format_morph
from .verbs import enrich_verb

logger = logging.getLogger(__name__)


def load_lexicon(path=None):
    lexicon = json.loads(Path(__file__).with_name("lexicon.json").read_text(encoding="utf-8"))
    if path:
        custom = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        for section, entries in custom.items():
            if section not in lexicon or not isinstance(entries, dict):
                raise ValueError(f"Некорректный раздел словаря: {section}")
            lexicon[section].update(entries)
    return lexicon


def enrich(lemmas, forms, config, language="es", lexicon_path=None):
    if language == "en":
        from .english import enrich as enrich_english

        return enrich_english(lemmas, forms, config)
    greek = None
    if language == "el":
        from src.languages.greek_lexicon import GreekLexicon

        greek = GreekLexicon(lexicon_path)
    lexicon = None if greek else load_lexicon(config.lexicon)
    by_lemma = defaultdict(list)
    for f in forms:
        by_lemma[f["lemma"], f["pos"]].append(f)
    result = []
    for row in lemmas:
        info = GrammarInfo(row["id"], learning_form=row["lemma"])
        if config.enabled and greek:
            info.provenance = "Kaikki/Wiktionary principal parts + spaCy observed morphology"
            enrich_greek(row, info, greek)
        elif config.enabled:
            info.provenance = "spaCy observed morphology + conservative rules + lexicon"
            if row["pos"] == "NOUN":
                enrich_noun(row, info, lexicon, by_lemma[row["lemma"], row["pos"]])
            elif row["pos"] == "ADJ":
                enrich_adjective(row, info, lexicon)
            elif row["pos"] in {"VERB", "AUX"}:
                enrich_verb(row, info, lexicon)
        result.append(info)
    form_result = []
    for row in forms:
        info = GrammarInfo(row["id"])
        if config.enabled:
            info.morph_description = (
                POS_RU.get(row["pos"], row["pos"])
                + ": "
                + " | ".join(format_morph(m, language) for m in row["morph_variants"])
            )
            info.provenance = "observed UD morphology (variants separated by |)"
        form_result.append(info)
    if greek:
        greek.close()
    return result, form_result


def run(lemma_source, form_source, lemma_target, form_target, config, language="es", lexicon_path=None):
    lemmas, forms = enrich(read_rows(lemma_source), read_rows(form_source), config, language, lexicon_path)
    write_rows(lemma_target, lemmas)
    write_rows(form_target, forms)
    logger.info("Grammar enrichments: %d", len(lemmas) + len(forms))
