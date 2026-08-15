from __future__ import annotations

from pathlib import Path
import os

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

# load environment variables if present
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(PROJECT_ROOT / "database" / "content.db")))

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

LOG_DIR = Path(os.getenv("LOG_DIR", str(PROJECT_ROOT / "logs")))
LOG_DIR.mkdir(parents=True, exist_ok=True)

PROMPTS_DIR = PROJECT_ROOT / "prompts"
