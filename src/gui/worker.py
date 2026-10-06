"""Child process protocol: JSON progress on stdout, private logs on disk."""

import argparse
import contextlib
import json
import logging
import sys

from src.i18n import t
from src.runtime import configure_logging


def friendly_error(stage, exc):
    from src.preprocessing.formats import SourceFormatError

    if isinstance(exc, SourceFormatError):
        return str(exc)
    if isinstance(exc, ModuleNotFoundError):
        return t("err.missing_module", module=exc.name)
    if isinstance(exc, UnicodeError):
        return t("err.encoding")
    if stage == "nlp":
        return t("err.nlp")
    if stage == "ipa":
        return t("err.ipa")
    if stage == "translate":
        return t("err.translate")
    if isinstance(exc, PermissionError):
        return t("err.permission")
    return t("err.generic")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--source", required=True)
    args = parser.parse_args(argv)
    handler = configure_logging()
    protocol = sys.stdout

    def send(event):
        protocol.write(json.dumps(event, ensure_ascii=True) + "\n")
        protocol.flush()

    active = ""

    def progress(stage, completed, total):
        nonlocal active
        active = stage
        send({"type": "progress", "stage": stage, "completed": completed, "total": total})

    try:
        from src.application import run_pipeline

        # tqdm and third-party prints must not corrupt the JSON channel.
        with contextlib.redirect_stdout(handler.stream), contextlib.redirect_stderr(handler.stream):
            pipeline = run_pipeline(args.config, args.source, on_progress=progress, import_marked=True)
            files = {"folder": str(pipeline.output)}
            if pipeline.config.cards.enabled:
                files["cards"], files["list"] = map(str, pipeline.outputs["cards"])
            if pipeline.config.export.xlsx:
                files["table"] = str(pipeline.output / pipeline.profile.export_filename)
            elif pipeline.config.export.csv:
                files["table"] = str(pipeline.output / "lemmas.csv")
            from src.storage import read_rows

            lemmas = read_rows(pipeline.outputs["postprocess"][0])
            summary = {
                "lemmas": len({row["lemma"] for row in lemmas}),
                "cards": pipeline.manifest.data["stages"].get("cards", {}).get("selected_cards"),
                "forecast": pipeline.manifest.data["stages"].get("cards", {}).get("forecast"),
                "imported": pipeline.imported_known,
            }
        send({"type": "done", "files": files, "summary": summary})
        return 0
    except Exception as exc:
        logging.getLogger(__name__).exception("Pipeline failed at %s", active)
        send({"type": "error", "message": friendly_error(active, exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
