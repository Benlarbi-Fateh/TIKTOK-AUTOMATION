import argparse

from app.database import Database
from app.utils.logger import logger


class SourceCLI:

    def list_sources(self):
        with Database() as db:

            rows = db.fetchall("""
                SELECT
                    id,
                    name,
                    source_type,
                    category,
                    active,
                    priority
                FROM sources
                ORDER BY priority, name
            """)

            logger.info("")

            logger.info(
                "%-3s %-30s %-8s %-20s %-8s %-8s",
                "ID",
                "Nom",
                "Type",
                "Catégorie",
                "Actif",
                "Priorité",
            )

            logger.info("-" * 90)

            for row in rows:

                logger.info(
                    "%-3s %-30s %-8s %-20s %-8s %-8s",
                    row["id"],
                    row["name"],
                    row["source_type"],
                    row["category"] or "-",
                    "Oui" if row["active"] else "Non",
                    row["priority"],
                )

    def enable(self, source_id):

        with Database() as db:

            db.execute("""
                UPDATE sources
                SET active = 1
                WHERE id = ?
            """, (source_id,))

        logger.info("Source activée.")

    def disable(self, source_id):

        with Database() as db:

            db.execute("""
                UPDATE sources
                SET active = 0
                WHERE id = ?
            """, (source_id,))

        logger.info("Source désactivée.")

    def priority(self, source_id, priority):

        with Database() as db:

            db.execute("""
                UPDATE sources
                SET priority = ?
                WHERE id = ?
            """, (
                priority,
                source_id,
            ))

        logger.info("Priorité mise à jour.")

    def add(
        self,
        name,
        url,
        source_type,
        language,
        category,
    ):

        with Database() as db:

            db.add_source(
                name=name,
                url=url,
                source_type=source_type,
                language=language,
                category=category,
            )

        logger.info("Source ajoutée.")


def build_parser():

    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list")

    enable = sub.add_parser("enable")
    enable.add_argument("id", type=int)

    disable = sub.add_parser("disable")
    disable.add_argument("id", type=int)

    priority = sub.add_parser("priority")
    priority.add_argument("id", type=int)
    priority.add_argument("value", type=int)

    add = sub.add_parser("add")

    add.add_argument("--name", required=True)
    add.add_argument("--url", required=True)
    add.add_argument("--type", default="rss")
    add.add_argument("--lang", default="en")
    add.add_argument("--category", default="technology")

    return parser


def main():

    cli = SourceCLI()

    parser = build_parser()

    args = parser.parse_args()

    if args.command == "list":

        cli.list_sources()

    elif args.command == "enable":

        cli.enable(args.id)

    elif args.command == "disable":

        cli.disable(args.id)

    elif args.command == "priority":

        cli.priority(
            args.id,
            args.value,
        )

    elif args.command == "add":

        cli.add(
            args.name,
            args.url,
            args.type,
            args.lang,
            args.category,
        )

    else:

        parser.print_help()


if __name__ == "__main__":

    main()