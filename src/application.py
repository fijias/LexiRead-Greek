"""The same entry point is used by the CLI and the GUI worker."""

from src.pipeline import Pipeline
from src.runtime import prepare_environment


def run_pipeline(config_path, source=None, stage="run-all", force=False, on_progress=None, import_marked=False):
    prepare_environment()
    pipeline = Pipeline(config_path, source)
    pipeline.imported_known = 0
    cfg = pipeline.config
    if import_marked and cfg.known_dictionary.enabled and cfg.cards.enabled:
        # Words marked "Known" in the previous study list join the known-words workbook first,
        # so translation and cards are rebuilt without them.
        from src.cards.known_words import import_marked_words

        pipeline.imported_known = import_marked_words(pipeline.outputs["cards"][1], pipeline.known_dictionary_path)
    pipeline.run(stage, force, on_progress=on_progress)
    return pipeline
