"""Greek spelling normalization applied before NLP so that one word keeps one form."""

import re
import unicodedata

_TONOS = "\u0301"
_POLYTONIC = re.compile(r"[\u1f00-\u1fff]")
# Breathings, circumflex, iota subscript and the like disappear in monotonic spelling;
# the grave and the circumflex become the single monotonic accent.
_DROP = {"\u0313", "\u0314", "\u0345", "\u0306", "\u0304"}
_TO_TONOS = {"\u0300", "\u0342"}
_GREEK_VOWELS = "αεηιουωΑΕΗΙΟΥΩ"
_ACCENTED_MONOSYLLABLES = {"ή", "πού", "πώς", "Ή", "Πού", "Πώς"}
_WORD = re.compile(r"[\w\u0300-\u036f]+")
# Unambiguous elisions only: τ' (το/τα) and στ' (στο/στα) cannot be expanded safely.
_ELISIONS = {"σ": "σε", "μ": "με", "ν": "να", "θ": "θα", "γι": "για", "απ": "από"}
_ELISION = re.compile(r"(?<![\w\u0300-\u036f])(" + "|".join(_ELISIONS) + r")['’‘]\s*(?=[\w\u0300-\u036f])", re.IGNORECASE)


def _restore_case(source: str, target: str) -> str:
    return target[0].upper() + target[1:] if source[0].isupper() else target


def _expand_elision(match: re.Match) -> str:
    text = match.group(1)
    return _restore_case(text, _ELISIONS[text.lower()]) + " "


def _vowel_groups(word: str) -> int:
    base = "".join(c for c in unicodedata.normalize("NFD", word) if not unicodedata.combining(c))
    return len(re.findall(f"[{_GREEK_VOWELS}]+", base))


def to_monotonic(word: str) -> str:
    chars = []
    for char in unicodedata.normalize("NFD", word):
        if char in _DROP:
            continue
        chars.append(_TONOS if char in _TO_TONOS else char)
    result = unicodedata.normalize("NFC", "".join(chars))
    if _vowel_groups(result) <= 1 and result not in _ACCENTED_MONOSYLLABLES:
        result = unicodedata.normalize(
            "NFC", unicodedata.normalize("NFD", result).replace(_TONOS, "")
        )
    return result


def drop_enclitic_accent(word: str) -> str:
    """η ένωσή του -> ένωση: the second accent only marks a following enclitic."""
    decomposed = unicodedata.normalize("NFD", word)
    if decomposed.count(_TONOS) < 2:
        return word
    index = decomposed.rindex(_TONOS)
    return unicodedata.normalize("NFC", decomposed[:index] + decomposed[index + 1 :])


def normalize_greek(text: str) -> str:
    # The micro sign often replaces μ in texts produced by legacy encoders.
    text = text.replace("\u00b5", "μ")
    if _POLYTONIC.search(text):
        text = _WORD.sub(lambda m: to_monotonic(m.group()), text)
    text = _WORD.sub(lambda m: drop_enclitic_accent(m.group()), text)
    return _ELISION.sub(_expand_elision, text)
