"""Case folding that keeps visible word forms correct in every supported language."""

import re
import unicodedata

# str.casefold() turns Greek final sigma into a medial one: λόγος -> λόγοσ.
_FINAL_SIGMA = re.compile(r"(?<=[\u0370-\u03ff\u1f00-\u1fff])σ(?![\w\u0300-\u036f])")


def fold(text: str) -> str:
    return _FINAL_SIGMA.sub("ς", text.casefold())


SCRIPTS = {"GREEK": "greek", "LATIN": "latin", "CYRILLIC": "cyrillic"}


def script(word: str) -> str:
    """Alphabet of a word: greek, latin, cyrillic, mixed or other (no letters / another script)."""
    found = {
        SCRIPTS.get(unicodedata.name(char, "").split(" ")[0], "other") for char in word if char.isalpha()
    }
    if len(found) > 1:
        return "mixed"
    return found.pop() if found else "other"
