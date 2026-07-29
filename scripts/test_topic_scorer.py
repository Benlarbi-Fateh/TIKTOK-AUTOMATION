from db import Database
from logger import logger
from topic_scorer import score_topic


def test_topic_scorer() -> None:
    with Database() as database:
        topic = database.fetchone(
            """
            SELECT id, title
            FROM topics
            WHERE status = 'new'
            ORDER BY id
            LIMIT 1
            """
        )

    if topic is None:
        logger.warning(
            "Aucun sujet avec le statut 'new' n'a été trouvé."
        )
        return

    topic_id = topic["id"]

    logger.info(
        "Notation du sujet %s : %s",
        topic_id,
        topic["title"],
    )

    result = score_topic(topic_id)

    logger.info("Résultat : %s", result)

    with Database() as database:
        updated_topic = database.fetchone(
            """
            SELECT
                id,
                viral_score,
                originality_score,
                affiliate_score,
                final_score,
                status
            FROM topics
            WHERE id = ?
            """,
            (topic_id,),
        )

    logger.info(
        "Sujet enregistré dans SQLite : %s",
        dict(updated_topic),
    )


if __name__ == "__main__":
    try:
        test_topic_scorer()

    except Exception as error:
        logger.exception(
            "Échec du test de notation : %s",
            error,
        )
        raise