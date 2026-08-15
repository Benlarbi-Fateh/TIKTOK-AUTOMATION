"""Database package for the application.

This package provides the new location for the SQLite Database class.
"""

from .db import Database  # re-export for convenience

__all__ = ["Database"]
