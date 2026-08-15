from datetime import datetime, timezone
from typing import Any

from app.database import Database


class SourceManager:
    def get_active_sources(self) -> list[Any]:
        with Database() as database:
            return database.fetchall(
                """
                SELECT *
                FROM sources
                WHERE active = 1
                ORDER BY priority ASC, name ASC
                """
            )

    def mark_checked(self, source_id: int) -> None:
        now = datetime.now(timezone.utc).isoformat()

        with Database() as database:
            database.execute(
                """
                UPDATE sources
                SET last_checked = ?
                WHERE id = ?
                """,
                (now, source_id),
            )

    def mark_success(self, source_id: int) -> None:
        now = datetime.now(timezone.utc).isoformat()

        with Database() as database:
            database.execute(
                """
                UPDATE sources
                SET
                    last_checked = ?,
                    last_success = ?,
                    last_error = NULL
                WHERE id = ?
                """,
                (now, now, source_id),
            )

    def mark_error(
        self,
        source_id: int,
        error: Exception | str,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()

        with Database() as database:
            database.execute(
                """
                UPDATE sources
                SET
                    last_checked = ?,
                    last_error = ?
                WHERE id = ?
                """,
                (now, str(error), source_id),
            )

    def update_priority(
        self,
        source_id: int,
        priority: int,
    ) -> None:
        if not 1 <= priority <= 10:
            raise ValueError(
                "La priorité doit être comprise entre 1 et 10."
            )

        with Database() as database:
            database.execute(
                """
                UPDATE sources
                SET priority = ?
                WHERE id = ?
                """,
                (priority, source_id),
            )

    def enable_source(self, source_id: int) -> None:
        with Database() as database:
            database.execute(
                """
                UPDATE sources
                SET active = 1
                WHERE id = ?
                """,
                (source_id,),
            )

    def disable_source(self, source_id: int) -> None:
        with Database() as database:
            database.execute(
                """
                UPDATE sources
                SET active = 0
                WHERE id = ?
                """,
                (source_id,),
            )