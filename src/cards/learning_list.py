from src.cards.formatter import card_content
from src.config import Export
from src.export.excel_exporter import translation_credit, write_excel


def list_filename(language):
    return {"en": "english_list.xlsx", "es": "spanish_list.xlsx", "el": "greek_list.xlsx"}[language]


def render_learning_list(cards, target, cards_config, language="es", machine_translation=False):
    rows = []
    for card in cards:
        front, ipa, translations, forms = card_content(card, cards_config.max_forms, language)
        # Lemma identifies the word; a mark in Known adds it to the known-words list on the next run.
        rows.append([front, ipa, "\n".join(translations), forms, card.lemma, ""])
    write_excel(
        target,
        [("Список для изучения", ["Слово", "Транскрипция", "Перевод", "Словоформы", "Лемма", "Знаю"], rows)],
        Export(),
        description=None if machine_translation else translation_credit(),
    )
