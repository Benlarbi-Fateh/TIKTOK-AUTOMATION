from __future__ import annotations

import argparse
from typing import Any

from db import Database
from logger import logger


def get_scored_topics(
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """
    Récupère tous les sujets déjà notés afin de pouvoir
    recalculer leur classification.
    """

    query = """
        SELECT *
        FROM topics
        WHERE status IN (
            'scored',
            'review',
            'approved',
            'rejected'
        )
        ORDER BY final_score DESC, collected_at DESC
    """

    params: tuple[Any, ...] = ()

    if limit is not None:
        query += " LIMIT ?"
        params = (limit,)

    with Database() as database:
        rows = database.fetchall(query, params)

    return [dict(row) for row in rows]

def classify_score(
    final_score: int,
    approval_threshold: int,
    review_threshold: int,
) -> str:
    """
    Détermine le nouveau statut selon le score final.
    """

    if final_score >= approval_threshold:
        return "approved"

    if final_score >= review_threshold:
        return "review"

    return "rejected"


def select_topics(
    approval_threshold: int = 70,
    review_threshold: int = 50,
    limit: int | None = None,
    dry_run: bool = False,
) -> dict[str, int]:
    """
    Classe les sujets scored selon leur score final.
    """

    topics = get_scored_topics(limit=limit)

    statistics = {
        "total": len(topics),
        "approved": 0,
        "review": 0,
        "rejected": 0,
    }

    logger.info(
        "%s sujet(s) noté(s) à classer.",
        statistics["total"],
    )

    if not topics:
        logger.info("Aucun sujet scored à classer.")
        return statistics

    with Database() as database:
        for topic in topics:
            topic_id = int(topic["id"])
            title = str(topic["title"])
            final_score = int(topic["final_score"] or 0)

            new_status = classify_score(
                final_score=final_score,
                approval_threshold=approval_threshold,
                review_threshold=review_threshold,
            )

            statistics[new_status] += 1

            logger.info(
                "Sujet %s | %s/100 | %s | %s",
                topic_id,
                final_score,
                new_status,
                title,
            )

            if not dry_run:
                database.update_topic_status(
                    topic_id=topic_id,
                    status=new_status,
                )

    return statistics


def display_statistics(
    statistics: dict[str, int],
    dry_run: bool,
) -> None:
    logger.info("=" * 60)
    logger.info("Résumé de la sélection")
    logger.info("Sujets examinés : %s", statistics["total"])
    logger.info("Approuvés : %s", statistics["approved"])
    logger.info("À vérifier : %s", statistics["review"])
    logger.info("Rejetés : %s", statistics["rejected"])

    if dry_run:
        logger.info(
            "Mode simulation : aucun statut n'a été modifié."
        )

    logger.info("=" * 60)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classe les sujets notés selon leur score."
    )

    parser.add_argument(
        "--approval-threshold",
        type=int,
        default=70,
        help="Score minimal pour approuver un sujet.",
    )

    parser.add_argument(
        "--review-threshold",
        type=int,
        default=50,
        help="Score minimal pour placer un sujet en vérification.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Nombre maximal de sujets à traiter.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche le classement sans modifier SQLite.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not 0 <= args.review_threshold <= 100:
        parser.error(
            "--review-threshold doit être compris entre 0 et 100."
        )

    if not 0 <= args.approval_threshold <= 100:
        parser.error(
            "--approval-threshold doit être compris entre 0 et 100."
        )

    if args.review_threshold >= args.approval_threshold:
        parser.error(
            "--review-threshold doit être inférieur "
            "à --approval-threshold."
        )

    if args.limit is not None and args.limit <= 0:
        parser.error("--limit doit être supérieur à 0.")

    statistics = select_topics(
        approval_threshold=args.approval_threshold,
        review_threshold=args.review_threshold,
        limit=args.limit,
        dry_run=args.dry_run,
    )

    display_statistics(
        statistics=statistics,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()