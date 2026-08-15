"""Compatibility wrapper for legacy imports.

Historic scripts import `from db import Database`. During the migration the
real implementation lives in `app.database.db.Database`. This module tries
to import the new implementation using absolute imports; if that fails
because the `app` package is not on `sys.path` (common when running files
directly from the `scripts/` folder), we add the project root to `sys.path`
and retry. This keeps backward compatibility while the codebase migrates.
"""

from __future__ import annotations

import importlib
import site
import sys
from pathlib import Path


def _import_database() -> type:
	try:
		mod = importlib.import_module("app.database.db")
		return mod.Database
	except ModuleNotFoundError:
		# Attempt to add project root to sys.path and retry. This makes running
		# scripts from the `scripts/` directory resilient during migration.
		current = Path(__file__).resolve()
		project_root = current.parents[1]

		if str(project_root) not in sys.path:
			sys.path.insert(0, str(project_root))

		mod = importlib.import_module("app.database.db")
		return mod.Database


Database = _import_database()

__all__ = ["Database"]