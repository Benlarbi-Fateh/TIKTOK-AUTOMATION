"""SQLite Database access layer moved to application package.

This module provides a thin, safe wrapper around sqlite3 used across
the project. It aims to preserve the previous public API so existing
modules continue to work while the codebase migrates to the new
architecture under `app/`.
"""
from __future__ import annotations

import sqlite3
from typing import Any

from app.utils.config import DATABASE_PATH


class Database:
    """Small SQLite helper preserving the legacy API.

    Methods mirror the original `scripts/db.py` implementation so
    existing imports like ``from db import Database`` will continue
    to work when a compatibility wrapper points here.
    """

    def __init__(self) -> None:
        self.connection: sqlite3.Connection = sqlite3.connect(str(DATABASE_PATH))
        self.connection.row_factory = sqlite3.Row
        # ensure foreign keys are enforced
        self.connection.execute("PRAGMA foreign_keys = ON;")

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        """Execute a query and commit the transaction.

        Returns the sqlite3.Cursor for convenience (e.g. to read lastrowid).
        """
        cursor = self.connection.execute(query, params)
        self.connection.commit()
        return cursor

    def fetchone(self, query: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
        """Execute a query and return a single row or None."""
        cursor = self.connection.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        """Execute a query and return all rows as a list."""
        cursor = self.connection.execute(query, params)
        return cursor.fetchall()

    # --- sources -------------------------------------------------
    def add_source(
        self,
        name: str,
        url: str,
        source_type: str,
        language: str = "fr",
        category: str | None = None,
    ) -> int:
        """Insert a new source and return its id."""
        cursor = self.execute(
            """
            INSERT INTO sources (
                name,
                url,
                source_type,
                language,
                category
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, url, source_type, language, category),
        )
        return int(cursor.lastrowid)

    def get_sources(self, active_only: bool = True) -> list[sqlite3.Row]:
        """Return sources; by default only active ones."""
        if active_only:
            return self.fetchall(
                """
                SELECT *
                FROM sources
                WHERE active = 1
                ORDER BY name
                """
            )

        return self.fetchall(
            """
            SELECT *
            FROM sources
            ORDER BY name
            """
        )

    def source_exists(self, url: str) -> bool:
        """Return True when a source with the given URL exists."""
        row = self.fetchone(
            """
            SELECT id
            FROM sources
            WHERE url = ?
            """,
            (url,),
        )
        return row is not None

    # --- topics --------------------------------------------------
    def add_topic(
        self,
        title: str,
        normalized_title: str,
        summary: str | None,
        source_url: str,
        source_name: str,
        category: str | None,
        fingerprint: str,
        published_at: str | None = None,
    ) -> int:
        """Insert a new topic and return its id."""
        cursor = self.execute(
            """
            INSERT INTO topics (
                title,
                normalized_title,
                summary,
                source_url,
                source_name,
                published_at,
                category,
                fingerprint
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                normalized_title,
                summary,
                source_url,
                source_name,
                published_at,
                category,
                fingerprint,
            ),
        )
        return int(cursor.lastrowid)

    def get_topics_by_status(self, status: str) -> list[sqlite3.Row]:
        """Return topics matching a given status."""
        return self.fetchall(
            """
            SELECT *
            FROM topics
            WHERE status = ?
            ORDER BY collected_at DESC
            """,
            (status,),
        )

    def get_topic_by_id(self, topic_id: int) -> sqlite3.Row | None:
        """Retrieve a single topic by id."""
        return self.fetchone(
            """
            SELECT *
            FROM topics
            WHERE id = ?
            """,
            (topic_id,),
        )

    def update_topic_score(
        self,
        topic_id: int,
        viral_score: int,
        originality_score: int,
        affiliate_score: int,
        final_score: int,
    ) -> None:
        """Update score fields and mark topic as scored."""
        self.execute(
            """
            UPDATE topics
            SET viral_score = ?,
                originality_score = ?,
                affiliate_score = ?,
                final_score = ?,
                status = 'scored'
            WHERE id = ?
            """,
            (
                viral_score,
                originality_score,
                affiliate_score,
                final_score,
                topic_id,
            ),
        )

    def update_topic_status(self, topic_id: int, status: str) -> None:
        """Set the `status` column for a topic."""
        self.execute(
            """
            UPDATE topics
            SET status = ?
            WHERE id = ?
            """,
            (status, topic_id),
        )

    # --- scripts -------------------------------------------------
    def script_exists_for_topic(self, topic_id: int) -> bool:
        """Return True if a script exists for the given topic id."""
        row = self.fetchone(
            """
            SELECT id
            FROM scripts
            WHERE topic_id = ?
            LIMIT 1
            """,
            (topic_id,),
        )
        return row is not None

    def add_script(
        self,
        topic_id: int,
        title: str,
        hook: str,
        script_text: str,
        description: str,
        hashtags: str,
        scenes_json: str,
        sources_json: str,
        uncertainties_json: str,
        status: str = "draft",
    ) -> int:
        """Insert a script record and return its id."""
        cursor = self.execute(
            """
            INSERT INTO scripts (
                topic_id,
                title,
                hook,
                script_text,
                description,
                hashtags,
                scenes_json,
                sources_json,
                uncertainties_json,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                topic_id,
                title,
                hook,
                script_text,
                description,
                hashtags,
                scenes_json,
                sources_json,
                uncertainties_json,
                status,
            ),
        )
        return int(cursor.lastrowid)

    def get_scripts_by_status(self, status: str) -> list[sqlite3.Row]:
        """Return scripts filtered by `status`."""
        return self.fetchall(
            """
            SELECT *
            FROM scripts
            WHERE status = ?
            ORDER BY created_at DESC
            """,
            (status,),
        )

    # --- videos --------------------------------------------------
    def add_video(
        self,
        script_id: int,
        project_folder: str | None = None,
        audio_path: str | None = None,
        subtitle_path: str | None = None,
        final_video_path: str | None = None,
        status: str = "prepared",
    ) -> int:
        cursor = self.execute(
            """
            INSERT INTO videos (
                script_id,
                project_folder,
                audio_path,
                subtitle_path,
                final_video_path,
                status
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (script_id, project_folder, audio_path, subtitle_path, final_video_path, status),
        )
        return int(cursor.lastrowid)

    def get_video_by_script(self, script_id: int) -> sqlite3.Row | None:
        return self.fetchone(
            """
            SELECT *
            FROM videos
            WHERE script_id = ?
            LIMIT 1
            """,
            (script_id,),
        )

    def update_video_publication(self, video_id: int, platform_id: str | None, status: str = "published") -> None:
        self.execute(
            """
            UPDATE videos
            SET platform_id = ?, status = ?, published_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (platform_id, status, video_id),
        )

    # --- lifecycle ----------------------------------------------
    def close(self) -> None:
        """Close the underlying SQLite connection."""
        try:
            self.connection.close()
        except Exception:
            # best-effort close
            pass

    def __enter__(self) -> "Database":
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        self.close()
