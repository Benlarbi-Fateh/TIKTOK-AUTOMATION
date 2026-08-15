from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import timezone
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Any, List, Optional

import feedparser
import requests

from app.utils.logger import logger


@dataclass
class FeedArticle:
    title: str
    url: str
    summary: str
    published_at: str | None
    source_name: str
    source_url: str
    category: str | None


class RSSReader:
    """Télécharge et analyse des flux RSS ou Atom.

    API compatible avec l'ancienne implémentation afin de permettre une
    migration progressive.
    """

    def __init__(self, timeout: int = 30, user_agent: str = "TikTok-Automation/1.0") -> None:
        self.timeout = timeout
        self.headers = {
            "User-Agent": user_agent,
            "Accept": (
                "application/rss+xml,"
                "application/atom+xml,"
                "application/xml,"
                "text/xml;q=0.9,"
                "*/*;q=0.8"
            ),
        }

    def fetch(self, feed_url: str, source_name: str, category: str | None = None, limit: int = 10) -> List[FeedArticle]:
        """Télécharge un flux RSS et retourne ses articles.

        L'interface reprend celle utilisée par `scripts/collect_topics.py`.
        """
        if not feed_url.strip():
            raise ValueError("L’URL du flux RSS est vide.")

        if limit <= 0:
            raise ValueError("La limite d’articles doit être supérieure à zéro.")

        logger.info("Téléchargement du flux RSS : %s", feed_url)

        try:
            response = requests.get(feed_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.Timeout as error:
            raise RuntimeError(f"Délai dépassé pour le flux : {feed_url}") from error
        except requests.ConnectionError as error:
            raise RuntimeError(f"Connexion impossible au flux : {feed_url}") from error
        except requests.HTTPError as error:
            raise RuntimeError("Erreur HTTP pendant la lecture du flux " f"{feed_url} : {response.status_code}") from error
        except requests.RequestException as error:
            raise RuntimeError(f"Erreur réseau pour le flux {feed_url} : {error}") from error

        parsed_feed = feedparser.parse(response.content)

        if parsed_feed.bozo:
            logger.warning("Le flux %s contient une anomalie : %s", feed_url, parsed_feed.get("bozo_exception"))

        entries = parsed_feed.entries[:limit]

        logger.info("%s article(s) trouvé(s) dans %s", len(entries), source_name)

        articles: List[FeedArticle] = []

        for entry in entries:
            article = self._parse_entry(entry=entry, source_name=source_name, source_url=feed_url, category=category)
            if article is not None:
                articles.append(article)

        return articles

    def _parse_entry(self, entry: Any, source_name: str, source_url: str, category: str | None) -> Optional[FeedArticle]:
        title = self._clean_text(str(entry.get("title", "")))
        article_url = str(entry.get("link", "")).strip()

        if not title:
            logger.warning("Article ignoré : titre manquant dans %s", source_name)
            return None

        if not article_url:
            logger.warning("Article ignoré : URL manquante pour '%s'", title)
            return None

        summary_value = entry.get("summary") or entry.get("description") or self._extract_content(entry) or ""
        summary = self._clean_text(str(summary_value))
        published_at = self._extract_publication_date(entry)

        return FeedArticle(
            title=title,
            url=article_url,
            summary=summary,
            published_at=published_at,
            source_name=source_name,
            source_url=source_url,
            category=category,
        )

    @staticmethod
    def _extract_content(entry: Any) -> str:
        contents = entry.get("content", [])
        if not contents:
            return ""
        first_content = contents[0]
        if isinstance(first_content, dict):
            return str(first_content.get("value", ""))
        return str(first_content)

    @staticmethod
    def _clean_text(text: str) -> str:
        decoded_text = unescape(text)
        without_html = re.sub(r"<[^>]+>", " ", decoded_text)
        normalized = re.sub(r"\s+", " ", without_html)
        return normalized.strip()

    @staticmethod
    def _extract_publication_date(entry: Any) -> str | None:
        date_candidates = [entry.get("published"), entry.get("updated"), entry.get("created")]
        for date_value in date_candidates:
            if not date_value:
                continue
            try:
                parsed_date = parsedate_to_datetime(str(date_value))
                if parsed_date.tzinfo is None:
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                return parsed_date.isoformat()
            except Exception:
                continue
        return None
