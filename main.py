"""Run entrypoint so `fastapi run main.py` finds the app from project root."""

import sys
from pathlib import Path

# Ensure src is on path so "app" package resolves
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / "src"))

from app.main import app  # noqa: E402

__all__ = ["app"]
