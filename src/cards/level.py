"""Assumed vocabulary: the N most frequent lemmas of the language count as already known."""

from src.cards.formatter import normalize_card_form
from src.preprocessing.greek import drop_enclitic_accent

LEVELS = (0, 500, 1000, 2000, 3000)
# wordfreq lists word forms; several forms share a lemma, so read well past N forms.
FORMS_PER_LEMMA = 8


def frequent_lemmas(language, count, lexicon=None, lookup=None):
    """Lemmas of the ``count`` most frequent words; without a lexicon the forms stand for lemmas."""
    if not count:
        return set()
    if lookup is None:
        from wordfreq import top_n_list

        lookup = top_n_list
    known, lemmas_seen = set(), 0
    for form in lookup(language, count * FORMS_PER_LEMMA):
        # wordfreq keeps a medial sigma at the end of Greek words (τησ); fold() restores ς.
        form = normalize_card_form(form)
        if language == "el":
            # Web text keeps enclitic double accents (όνομά μου); the lemma has one accent.
            form = drop_enclitic_accent(form)
        if not form.isalpha():
            continue
        lemmas = {normalize_card_form(lemma) for lemma in lexicon.lemmas_of(form)} if lexicon else set()
        new = (lemmas or {form}) - known
        if new:
            lemmas_seen += 1
            known |= new
        if lemmas_seen >= count:
            break
    return known
