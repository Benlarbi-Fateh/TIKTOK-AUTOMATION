import sqlite3

from app.database import Database
from app.utils.logger import logger
from app.utils.text import create_fingerprint, normalize_text


def test_database_service() -> None:
    source_url = "https://example.com/technology-feed"

    title = "Un nouvel outil d'intelligence artificielle est disponible"

    normalized_title = normalize_text(title)
    fingerprint = create_fingerprint(title)

    with Database() as database:
        if not database.source_exists(source_url):
            source_id = database.add_source(
                name="Source technologique de test",
                url=source_url,
                source_type="rss",
                language="fr",
                category="intelligence-artificielle",
            )

            logger.info(
                "Source créée avec l'identifiant %s",
                source_id,
            )
        else:
            logger.info("La source existe déjà")

        try:
            topic_id = database.add_topic(
                title=title,
                normalized_title=normalized_title,
                summary="Présentation d'un nouvel outil IA.",
                source_url=source_url,
                source_name="Source technologique de test",
                category="intelligence-artificielle",
                fingerprint=fingerprint,
            )

            logger.info(
                "Sujet créé avec l'identifiant %s",
                topic_id,
            )

        except sqlite3.IntegrityError:
            logger.info(
                "Le sujet existe déjà : le doublon a été bloqué"
            )

        topics = database.get_topics_by_status("new")

        logger.info(
            "Nombre de nouveaux sujets : %s",
            len(topics),
        )

        for topic in topics:
            logger.info(
                "Sujet %s : %s",
                topic["id"],
                topic["title"],
            )


if __name__ == "__main__":
    test_database_service()