"""Case folding that keeps visible word forms correct in every supported language."""

import re

# str.casefold() turns Greek final sigma into a medial one: λόγος -> λόγοσ.
_FINAL_SIGMA = re.compile(r"(?<=[\u0370-\u03ff\u1f00-\u1fff])σ(?![\w\u0300-\u036f])")


def fold(text: str) -> str:
    return _FINAL_SIGMA.sub("ς", text.casefold())
