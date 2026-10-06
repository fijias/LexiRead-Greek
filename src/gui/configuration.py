"""Build a per-book runtime config without changing the demo YAML files."""

import hashlib
import re
from pathlib import Path

import yaml

from src.config import Config, load_config
from src.i18n import t
from src.preprocessing.formats import SUPPORTED_SUFFIXES, suffix

LANGUAGES = {"English": "en", "Español": "es", "Ελληνικά": "el"}
# Languages installed on demand and their installers.
OPTIONAL_LANGUAGES = {"en": "INSTALL_ENGLISH.bat", "es": "INSTALL_SPANISH.bat", "el": "INSTALL_GREEK.bat"}


def restore_empty_default(entry, variable, default):
    """Keep an empty edit until focus leaves or the user clicks elsewhere."""
    def restore(*_):
        if variable.get() == "":
            variable.set(str(default))

    def clicked(event):
        target = str(event.widget)
        if target != str(entry) and not target.startswith(str(entry) + "."):
            restore()

    entry.bind("<FocusOut>", restore, add="+")
    entry.winfo_toplevel().bind("<Button-1>", clicked, add="+")
    return restore


def valid_numeric_edit(value, maximum, decimal=False, minimum=0):
    """Allow temporary empty edits, but reject nonnumeric and excessive input."""
    if value == "":
        return True
    pattern = r"[0-9]+(?:[.,][0-9]*)?" if decimal else r"[0-9]+"
    if not re.fullmatch(pattern, value):
        return False
    try:
        return minimum <= float(value.replace(",", ".")) <= maximum
    except ValueError:
        return False


def build_config(root, source, language, options):
    source = Path(source).expanduser().resolve()
    if suffix(source) not in SUPPORTED_SUFFIXES or not source.is_file():
        raise ValueError(t("cfg.choose_file", formats=", ".join(s[1:].upper() for s in SUPPORTED_SUFFIXES)))
    if source.stat().st_size == 0:
        raise ValueError(t("cfg.empty_file"))
    if language not in LANGUAGES.values():
        raise ValueError(t("cfg.choose_language"))
    demo = root / "config" / f"demo_{language}.yaml"
    cfg = load_config(demo)
    cfg.cards.enabled = bool(options["cards"])
    cfg.machine_translation.enabled = bool(options["machine"])
    cfg.known_dictionary.enabled = bool(options["known"])
    cfg.pronunciation.enabled = bool(options["ipa"])
    cfg.translation.cumulative_coverage_limit = int(options["coverage"])
    cfg.translation.specificity_threshold = float(options["specificity"])
    cfg.translation.min_book_occurrences = int(options["occurrences"])
    cfg.cards.exclude_function_words = bool(options["skip_function"])
    cfg.cards.exclude_proper_nouns = bool(options["skip_names"])
    cfg.cards.exclude_numbers = bool(options["skip_numbers"])
    cfg.cards.text_alphabet_only = bool(options["skip_alphabet"])
    cfg.cards.known_level = int(options["known_level"])
    cfg.cards.max_cards = int(options["max_cards"] or 0)
    # Revalidate assignments before any files are written.
    cfg = Config.model_validate(cfg.model_dump())
    for name in ("cache",):
        setattr(cfg.paths, name, str((demo.parent / getattr(cfg.paths, name)).resolve()))
    cfg.cards.template = str((demo.parent / cfg.cards.template).resolve())
    known = cfg.known_dictionary.path or f"../my_dictionary_{language}.xlsx"
    cfg.known_dictionary.path = str((demo.parent / known).resolve())
    if cfg.grammar.lexicon:
        cfg.grammar.lexicon = str((demo.parent / cfg.grammar.lexicon).resolve())
    if cfg.cards.enabled and not Path(cfg.cards.template).is_file():
        raise ValueError(t("cfg.no_template"))
    if cfg.known_dictionary.enabled and not Path(cfg.known_dictionary.path).is_file():
        raise ValueError(t("cfg.no_known"))
    book = hashlib.sha256(str(source).encode()).hexdigest()[:12] + "-" + language
    cfg.paths.work = str(root / "data" / "work" / "gui" / book)
    cfg.paths.output = str(root / "data" / "output" / "gui" / book)
    config_path = Path(cfg.paths.work) / "run.yaml"
    return source, config_path, cfg


def known_dictionary_path(root, language):
    """The user's known-words workbook for a text language, as the demo config names it."""
    demo = root / "config" / f"demo_{language}.yaml"
    known = load_config(demo).known_dictionary.path or f"../my_dictionary_{language}.xlsx"
    return (demo.parent / known).resolve()


def save_config(path, cfg):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        yaml.safe_dump(cfg.model_dump(), allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    temporary.replace(path)
