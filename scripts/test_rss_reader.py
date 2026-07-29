from logger import logger
from rss_reader import RSSReader


TEST_FEED_URL = "https://openai.com/news/rss.xml"


def test_rss_reader() -> None:
    reader = RSSReader(
        timeout=30,
    )

    articles = reader.fetch(
        feed_url=TEST_FEED_URL,
        source_name="OpenAI News",
        category="intelligence-artificielle",
        limit=5,
    )

    if not articles:
        raise RuntimeError(
            "Aucun article n’a été récupéré."
        )

    logger.info(
        "Nombre d’articles récupérés : %s",
        len(articles),
    )

    for index, article in enumerate(
        articles,
        start=1,
    ):
        logger.info(
            "Article %s | %s",
            index,
            article.title,
        )

        logger.info(
            "URL : %s",
            article.url,
        )

        logger.info(
            "Date : %s",
            article.published_at or "non disponible",
        )

        logger.info(
            "Résumé : %s",
            article.summary[:200],
        )


if __name__ == "__main__":
    try:
        test_rss_reader()
        logger.info("Test RSS réussi.")

    except Exception as error:
        logger.exception(
            "Échec du test RSS : %s",
            error,
        )
        raise