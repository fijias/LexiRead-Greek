"""Read worker events on a background thread; widgets are touched only by Tk."""

import json
import os
import queue
import subprocess
import sys
import threading

from src.i18n import ENV, get_language, t


class Controller:
    def __init__(self):
        self.events = queue.Queue()
        self.process = None
        self.thread = None

    @property
    def running(self):
        return self.thread is not None and self.thread.is_alive()

    def start(self, root, config, source, api_key=""):
        if self.running:
            raise RuntimeError(t("err.already_running"))
        env = dict(os.environ, PYTHONUTF8="1", **{ENV: get_language()})
        if api_key:
            env["OPENAI_API_KEY"] = api_key
        # Never put secrets in command-line arguments or runtime YAML.
        self.process = subprocess.Popen(
            [sys.executable, "-m", "src.gui.worker", "--config", str(config), "--source", str(source)],
            cwd=root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        self.thread = threading.Thread(target=self._read, daemon=True)
        self.thread.start()

    def _read(self):
        terminal = False
        try:
            with self.process.stdout:
                for line in self.process.stdout:
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    terminal |= event.get("type") in {"done", "error"}
                    self.events.put(event)
            self.process.wait()
        finally:
            if not terminal:
                self.events.put(
                    {
                        "type": "error",
                        "message": t("err.process_stopped"),
                    }
                )

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=3)
