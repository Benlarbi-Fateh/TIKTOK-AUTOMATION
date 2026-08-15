import os
import pytest
from app.services.rss import RSSReader


@pytest.mark.skipif(os.environ.get("RUN_NETWORK_TESTS") != "1", reason="Network tests skipped by default")
def test_rss_fetch_minimal():
    reader = RSSReader(timeout=10)
    articles = reader.fetch(
        feed_url="https://openai.com/news/rss.xml",
        source_name="OpenAI News",
        category="intelligence-artificielle",
        limit=1,
    )

    assert isinstance(articles, list)
    assert len(articles) <= 1
