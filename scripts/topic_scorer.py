"""Compatibility wrapper for topic scoring moved under `app.scoring`.

Exports the original `score_topic` function so existing callers keep working.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from app.scoring.topic_scorer import (
        score_topic,
        build_prompt,
        load_prompt,
        validate_scores,
        SCORE_SCHEMA,
    )

except Exception:  # pragma: no cover - fallback when running scripts directly
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from app.scoring.topic_scorer import (
        score_topic,
        build_prompt,
        load_prompt,
        validate_scores,
        SCORE_SCHEMA,
    )

__all__ = [
    "score_topic",
    "build_prompt",
    "load_prompt",
    "validate_scores",
    "SCORE_SCHEMA",
]