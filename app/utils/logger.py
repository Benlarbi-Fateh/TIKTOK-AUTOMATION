from __future__ import annotations

import logging
from pathlib import Path

from app.utils.config import LOG_DIR


LOG_FILE = LOG_DIR / "project.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("TikTokAutomation")
