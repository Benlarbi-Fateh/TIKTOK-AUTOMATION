from app.database import Database
from app.utils.text import normalize_text, create_fingerprint


def test_database_add_and_query():
    title = "Test article for pytest"
    normalized = normalize_text(title)
    fingerprint = create_fingerprint(title)

    with Database() as db:
        # ensure we can add a temporary source and topic (may already exist)
        url = "https://example.com/feed"
        if not db.source_exists(url):
            src_id = db.add_source(
                name="pytest-source",
                url=url,
                source_type="rss",
                language="en",
                category="test",
            )
        else:
            row = db.fetchone("SELECT id FROM sources WHERE url = ?", (url,))
            src_id = int(row["id"]) if row else None

        # only add the topic if its fingerprint is not already present
        existing = db.fetchone("SELECT id FROM topics WHERE fingerprint = ?", (fingerprint,))
        if existing:
            topic_id = int(existing["id"])
        else:
            topic_id = db.add_topic(
                title=title,
                normalized_title=normalized,
                summary="pytest summary",
                source_url="https://example.com/article",
                source_name="pytest-source",
                category="test",
                fingerprint=fingerprint,
            )

        assert topic_id is not None
