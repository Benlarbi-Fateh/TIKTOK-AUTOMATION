"""Compatibility wrapper for the migrated Ollama client.

Keeps the previous import path `scripts.ollama_client.OllamaClient`
while delegating implementation to `app.services.ollama`.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    # Prefer the app package
    from app.services.ollama import OllamaClient

except Exception:  # pragma: no cover - fallback for direct script execution
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from app.services.ollama import OllamaClient  # type: ignore

__all__ = ["OllamaClient"]