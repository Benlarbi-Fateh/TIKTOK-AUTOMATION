"""Compatibility wrapper for RSS reader during migration.

Existing scripts import ``from rss_reader import RSSReader, FeedArticle``. To
support a gradual migration we re-export these symbols from the new
``app.services.rss`` module.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
import sys


def _import_new() -> object:
    try:
        mod = import_module("app.services.rss")
        return mod
    except ModuleNotFoundError:
        # Ensure project root is on sys.path when running from scripts/
        current = Path(__file__).resolve()
        project_root = current.parents[1]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        return import_module("app.services.rss")


_mod = _import_new()

FeedArticle = _mod.FeedArticle
RSSReader = _mod.RSSReader

__all__ = ["FeedArticle", "RSSReader"]