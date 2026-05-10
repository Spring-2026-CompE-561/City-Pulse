"""
Vercel ASGI entrypoint: exposes the FastAPI app with ``src`` on ``sys.path``.

Create a **second** Vercel project for the API (repo root, Framework: Other / FastAPI).
The Next.js app should stay in a project with Root Directory ``frontend``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from app.main import app  # noqa: E402

__all__ = ["app"]
