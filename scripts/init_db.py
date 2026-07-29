from pathlib import Path
import sqlite3
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "content.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"


def initialize_database() -> None:
    """Crée la base SQLite et exécute le schéma SQL."""

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Le fichier schema.sql est introuvable : {SCHEMA_PATH}"
        )

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.executescript(schema)
        connection.commit()

    print("Base de données créée avec succès.")
    print(f"Emplacement : {DATABASE_PATH}")


def list_tables() -> None:
    """Affiche les tables présentes dans la base."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
            """
        )

        tables = [row[0] for row in cursor.fetchall()]

    print("\nTables disponibles :")

    for table in tables:
        print(f"- {table}")


if __name__ == "__main__":
    try:
        initialize_database()
        list_tables()

    except Exception as error:
        print(f"Erreur : {error}")
        sys.exit(1)