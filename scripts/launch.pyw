"""Stdlib launcher: missing imports get a native message."""
import ctypes
import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
os.chdir(root)
try:
    from src.gui.app import main
    raise SystemExit(main())
except Exception:
    if os.name == "nt":
        ctypes.windll.user32.MessageBoxW(None, "Could not start LexiRead Greek. Run INSTALL.bat to repair the installation.\n\n"
                                        "Не удалось запустить LexiRead Greek. Запустите INSTALL.bat для восстановления установки.",
                                        "LexiRead Greek", 0x10)
