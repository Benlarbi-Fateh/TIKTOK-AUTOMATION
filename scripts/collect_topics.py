from __future__ import annotations

import sqlite3
from typing import Any

from db import Database
from logger import logger
from rss_reader import FeedArticle, RSSReader
from utils import create_fingerprint, normalize_text


DEFAULT_SOURCES = [
    {
        "name": "OpenAI News",
        "url": "https://openai.com/news/rss.xml",
        "source_type": "rss",
        "language": "en",
        "category": "intelligence-artificielle",
    },
    {
        "name": "Google Blog",
        "url": "https://blog.google/feed/",
        "source_type": "rss",
        "language": "en",
        "category": "technologie",
    },
    {
        "name": "GitHub Changelog",
        "url": "https://github.blog/changelog/feed/",
        "source_type": "rss",
        "language": "en",
        "category": "developpement",
    },
]


def ensure_default_sources(
    database: Database,
) -> None:
    """
    Ajoute les sources RSS initiales si elles n’existent pas.
    """

    for source in DEFAULT_SOURCES:
        source_url = source["url"]

        if database.source_exists(source_url):
            logger.info(
                "Source déjà présente : %s",
                source["name"],
            )
            continue

        source_id = database.add_source(
            name=source["name"],
            url=source_url,
            source_type=source["source_type"],
            language=source["language"],
            category=source["category"],
        )

        logger.info(
            "Source ajoutée : %s avec l’identifiant %s",
            source["name"],
            source_id,
        )


def get_rss_sources(
    database: Database,
) -> list[dict[str, Any]]:
    """
    Récupère les sources RSS actives depuis SQLite.
    """

    rows = database.fetchall(
        """
        SELECT
            id,
            name,
            url,
            source_type,
            language,
            category,
            active
        FROM sources
        WHERE active = 1
          AND source_type = 'rss'
        ORDER BY name
        """
    )

    return [
        dict(row)
        for row in rows
    ]


def save_article(
    database: Database,
    article: FeedArticle,
) -> bool:
    """
    Enregistre un article dans topics.

    Retourne True si l’article est ajouté,
    False s’il s’agit d’un doublon.
    """

    normalized_title = normalize_text(
        article.title
    )

    fingerprint_source = (
        f"{normalized_title}|{article.url}"
    )

    fingerprint = create_fingerprint(
        fingerprint_source
    )

    try:
        topic_id = database.add_topic(
            title=article.title,
            normalized_title=normalized_title,
            summary=article.summary,
            source_url=article.url,
            source_name=article.source_name,
            category=article.category,
            fingerprint=fingerprint,
            published_at=article.published_at,
        )

        logger.info(
            "Nouveau sujet enregistré %s : %s",
            topic_id,
            article.title,
        )

        return True

    except sqlite3.IntegrityError:
        logger.info(
            "Doublon ignoré : %s",
            article.title,
        )

        return False


def collect_topics(
    articles_per_source: int = 10,
) -> dict[str, int]:
    """
    Collecte les articles de toutes les sources RSS actives.
    """

    reader = RSSReader(
        timeout=30,
    )

    statistics = {
        "sources_total": 0,
        "sources_success": 0,
        "sources_failed": 0,
        "articles_found": 0,
        "topics_added": 0,
        "duplicates": 0,
    }

    with Database() as database:
        ensure_default_sources(database)

        sources = get_rss_sources(database)

        statistics["sources_total"] = len(sources)

        logger.info(
            "%s source(s) RSS active(s) à traiter",
            len(sources),
        )

        for source in sources:
            logger.info(
                "Traitement de la source : %s",
                source["name"],
            )

            try:
                articles = reader.fetch(
                    feed_url=source["url"],
                    source_name=source["name"],
                    category=source["category"],
                    limit=articles_per_source,
                )

                statistics["sources_success"] += 1
                statistics["articles_found"] += len(articles)

                for article in articles:
                    added = save_article(
                        database=database,
                        article=article,
                    )

                    if added:
                        statistics["topics_added"] += 1
                    else:
                        statistics["duplicates"] += 1

            except Exception as error:
                statistics["sources_failed"] += 1

                logger.exception(
                    "Échec de la source %s : %s",
                    source["name"],
                    error,
                )

    return statistics


def display_statistics(
    statistics: dict[str, int],
) -> None:
    logger.info("Résumé de la collecte RSS")
    logger.info(
        "Sources totales : %s",
        statistics["sources_total"],
    )
    logger.info(
        "Sources réussies : %s",
        statistics["sources_success"],
    )
    logger.info(
        "Sources échouées : %s",
        statistics["sources_failed"],
    )
    logger.info(
        "Articles trouvés : %s",
        statistics["articles_found"],
    )
    logger.info(
        "Nouveaux sujets : %s",
        statistics["topics_added"],
    )
    logger.info(
        "Doublons ignorés : %s",
        statistics["duplicates"],
    )


if __name__ == "__main__":
    try:
        collection_statistics = collect_topics(
            articles_per_source=10,
        )

        display_statistics(
            collection_statistics
        )

        logger.info(
            "Collecte RSS terminée avec succès."
        )

    except Exception as error:
        logger.exception(
            "Échec général de la collecte RSS : %s",
            error,
        )
        raise