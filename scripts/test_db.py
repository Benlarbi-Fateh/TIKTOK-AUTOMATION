from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "content.db"


def test_database() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")

        connection.execute(
            """
            INSERT OR IGNORE INTO sources (
                name,
                url,
                source_type,
                language,
                category
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "Source de test",
                "https://example.com/rss",
                "rss",
                "fr",
                "technologie",
            ),
        )

        connection.commit()

        cursor = connection.execute(
            """
            SELECT id, name, url, source_type, language, category
            FROM sources
            """
        )

        rows = cursor.fetchall()

    print("Sources enregistrées :")

    for row in rows:
        print(row)


if __name__ == "__main__":
    test_database()