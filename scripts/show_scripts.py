from app.database import Database


def main() -> None:
    with Database() as database:
        rows = database.fetchall(
            """
            SELECT
                id,
                topic_id,
                title,
                status,
                created_at
            FROM scripts
            ORDER BY id DESC
            """
        )

    print()
    print(
        f"{'ID':<5}"
        f"{'Topic':<7}"
        f"{'Statut':<12}"
        f"{'Créé le':<22}"
        f"Titre"
    )
    print("-" * 110)

    for row in rows:
        print(
            f"{row['id']:<5}"
            f"{row['topic_id']:<7}"
            f"{row['status']:<12}"
            f"{row['created_at']:<22}"
            f"{row['title']}"
        )


if __name__ == "__main__":
    main()