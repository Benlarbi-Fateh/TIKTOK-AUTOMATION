from config import OLLAMA_MODEL
from db import Database
from logger import logger


def test_core() -> None:
    logger.info("Test du Core Python")
    logger.info("Modèle IA : %s", OLLAMA_MODEL)

    with Database() as database:
        rows = database.fetchall(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name;
            """
        )

        for row in rows:
            logger.info(row["name"])

    logger.info("Test terminé")


if __name__ == "__main__":
    test_core()