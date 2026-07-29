from __future__ import annotations

import argparse
import time
from typing import Any

from db import Database
from logger import logger
from topic_scorer import score_topic


def get_pending_topics(
    limit: int | None = None,
) -> list[dict[str, Any]]:
    with Database() as database:
        rows = database.fetchall(
            """
            SELECT *
            FROM topics
            WHERE status IN ('pending', 'new')
            ORDER BY collected_at DESC
            """
        )

    topics = [dict(row) for row in rows]

    if limit is not None:
        topics = topics[:limit]

    return topics

def score_pending_topics(
    limit: int | None = None,
    delay: float = 1.0,
) -> dict[str, int]:
    """
    Note les sujets en attente un par un avec Ollama.

    Une erreur sur un sujet n'interrompt pas tout le traitement.
    """

    topics = get_pending_topics(limit=limit)

    statistics = {
        "total": len(topics),
        "scored": 0,
        "failed": 0,
    }

    logger.info(
        "%s sujet(s) en attente de notation.",
        statistics["total"],
    )

    if not topics:
        logger.info("Aucun sujet à noter.")
        return statistics

    for position, topic in enumerate(topics, start=1):
        topic_id = int(topic["id"])
        title = str(topic.get("title") or "Sans titre")

        logger.info(
            "Notation %s/%s — sujet %s : %s",
            position,
            statistics["total"],
            topic_id,
            title,
        )

        try:
            result = score_topic(topic_id)

            statistics["scored"] += 1

            logger.info(
                "Sujet %s terminé avec un score de %s/100.",
                topic_id,
                result["final_score"],
            )

        except KeyboardInterrupt:
            logger.warning(
                "Traitement interrompu manuellement."
            )
            raise

        except Exception as error:
            statistics["failed"] += 1

            logger.exception(
                "Échec de la notation du sujet %s : %s",
                topic_id,
                error,
            )

        if delay > 0 and position < statistics["total"]:
            time.sleep(delay)

    return statistics


def display_statistics(
    statistics: dict[str, int],
) -> None:
    logger.info("=" * 60)
    logger.info("Résumé de la notation automatique")
    logger.info("Sujets sélectionnés : %s", statistics["total"])
    logger.info("Sujets notés : %s", statistics["scored"])
    logger.info("Échecs : %s", statistics["failed"])
    logger.info("=" * 60)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Note automatiquement les sujets pending avec Ollama."
        )
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Nombre maximal de sujets à traiter. "
            "Sans cette option, tous les sujets pending sont traités."
        ),
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help=(
            "Temps d'attente en secondes entre deux sujets. "
            "Valeur par défaut : 1 seconde."
        ),
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.limit is not None and args.limit <= 0:
        parser.error("--limit doit être supérieur à 0.")

    if args.delay < 0:
        parser.error("--delay ne peut pas être négatif.")

    statistics = score_pending_topics(
        limit=args.limit,
        delay=args.delay,
    )

    display_statistics(statistics)


if __name__ == "__main__":
    main()