import sqlite3
from typing import Any

from config import DATABASE_PATH


class Database:
    def __init__(self) -> None:
        self.connection = sqlite3.connect(DATABASE_PATH)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON;")

    def execute(
        self,
        query: str,
        params: tuple[Any, ...] = (),
    ) -> sqlite3.Cursor:
        cursor = self.connection.execute(query, params)
        self.connection.commit()
        return cursor

    def fetchone(
        self,
        query: str,
        params: tuple[Any, ...] = (),
    ) -> sqlite3.Row | None:
        cursor = self.connection.execute(query, params)
        return cursor.fetchone()

    def fetchall(
        self,
        query: str,
        params: tuple[Any, ...] = (),
    ) -> list[sqlite3.Row]:
        cursor = self.connection.execute(query, params)
        return cursor.fetchall()

    def add_source(
        self,
        name: str,
        url: str,
        source_type: str,
        language: str = "fr",
        category: str | None = None,
    ) -> int:
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
            (
                name,
                url,
                source_type,
                language,
                category,
            ),
        )

        return cursor.lastrowid

    def get_sources(
        self,
        active_only: bool = True,
    ) -> list[sqlite3.Row]:
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
        row = self.fetchone(
            """
            SELECT id
            FROM sources
            WHERE url = ?
            """,
            (url,),
        )

        return row is not None

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

        return cursor.lastrowid

    def get_topics_by_status(
        self,
        status: str,
    ) -> list[sqlite3.Row]:
        return self.fetchall(
            """
            SELECT *
            FROM topics
            WHERE status = ?
            ORDER BY collected_at DESC
            """,
            (status,),
        )

    def get_topic_by_id(
        self,
        topic_id: int,
    ) -> sqlite3.Row | None:
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

    def update_topic_status(
        self,
        topic_id: int,
        status: str,
    ) -> None:
        self.execute(
            """
            UPDATE topics
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                topic_id,
            ),
        )

    def script_exists_for_topic(
        self,
        topic_id: int,
    ) -> bool:
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

        return cursor.lastrowid

    def get_scripts_by_status(
        self,
        status: str,
    ) -> list[sqlite3.Row]:
        return self.fetchall(
            """
            SELECT *
            FROM scripts
            WHERE status = ?
            ORDER BY created_at DESC
            """,
            (status,),
        )

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        self.close()