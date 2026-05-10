"""
Vercel FastAPI discovery: ``api/index.py`` with top-level ``app`` is a supported path.

See https://vercel.com/docs/frameworks/backend/fastapi
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from app.main import app  # noqa: E402

__all__ = ["app"]
