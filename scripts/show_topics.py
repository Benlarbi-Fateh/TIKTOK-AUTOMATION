from app.database import Database


def main() -> None:
    with Database() as database:
        rows = database.fetchall(
            """
            SELECT
                id,
                title,
                final_score,
                status
            FROM topics
            ORDER BY final_score DESC, id DESC
            """
        )

    print()
    print(
        f"{'ID':<4} "
        f"{'Score':<7} "
        f"{'Statut':<10} "
        f"Titre"
    )
    print("-" * 100)

    for row in rows:
        print(
            f"{row['id']:<4} "
            f"{row['final_score']:<7} "
            f"{row['status']:<10} "
            f"{row['title']}"
        )


if __name__ == "__main__":
    main()
    