import sqlite3

from config import DATABASE_PATH


def show_table_structure(
    database: sqlite3.Connection,
    table_name: str,
) -> None:
    print(f"\nStructure de la table {table_name} :")

    columns = database.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    if not columns:
        print("Table introuvable.")
        return

    for column in columns:
        print(column)


def main() -> None:
    database = sqlite3.connect(DATABASE_PATH)

    tables = database.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """
    ).fetchall()

    print("Tables présentes :")

    for table in tables:
        print("-", table[0])

    show_table_structure(database, "topics")
    show_table_structure(database, "scripts")
    show_table_structure(database, "videos")

    database.close()


if __name__ == "__main__":
    main()