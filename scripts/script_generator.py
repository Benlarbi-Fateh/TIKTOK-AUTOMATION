from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.database import Database
from app.utils.logger import logger
from app.services.ollama import OllamaClient


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROMPT_PATH = (
    PROJECT_ROOT
    / "prompts"
    / "generate_tiktok_script.txt"
)


SCRIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
        },
        "hook": {
            "type": "string",
        },
        "script_text": {
            "type": "string",
        },
        "description": {
            "type": "string",
        },
        "hashtags": {
            "type": "array",
            "items": {
                "type": "string",
            },
        from app.generator.generator import *
