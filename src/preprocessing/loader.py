import logging
import codecs
from pathlib import Path

from charset_normalizer import from_bytes

from src.storage import atomic_path

from .normalizer import normalize
from .english_contractions import expand_contractions
from .greek import normalize_greek

logger = logging.getLogger(__name__)


# Single-byte code pages used by legacy TXT files, by source language.
LEGACY_ENCODINGS = {"el": "cp1253"}


def read_text_auto(source: Path, language: str = "es") -> tuple[str, str]:
    """Decode a TXT file and return Unicode text plus the detected source encoding."""
    data = source.read_bytes()
    for marker, encoding in (
        (codecs.BOM_UTF8, "utf-8-sig"),
        (codecs.BOM_UTF32_LE, "utf-32"),
        (codecs.BOM_UTF32_BE, "utf-32"),
        (codecs.BOM_UTF16_LE, "utf-16"),
        (codecs.BOM_UTF16_BE, "utf-16"),
    ):
        if data.startswith(marker):
            return data.decode(encoding), encoding
    try:
        return data.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        # Legacy English and Spanish TXT files most commonly use Windows-1252,
        # Greek ones Windows-1253; cp1252 would silently turn Greek into Latin-1 noise.
        encoding = LEGACY_ENCODINGS.get(language, "cp1252")
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            match = from_bytes(data).best()
        if match is None:
            raise UnicodeError("Не удалось определить кодировку TXT-файла")
        return str(match), match.encoding or "unknown"


def run(source: Path, target: Path, config, language: str = "es"):
    decoded, encoding = read_text_auto(source, language)
    text = normalize(decoded, config)
    if language == "en":
        text = expand_contractions(text)
    elif language == "el":
        text = normalize_greek(text)
    with atomic_path(target) as tmp:
        tmp.write_text(text, encoding="utf-8")
    logger.info("Исходный файл: %s; кодировка: %s; символов: %d", source, encoding, len(text))
