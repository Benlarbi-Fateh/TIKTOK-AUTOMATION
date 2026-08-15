from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from app.utils.logger import logger


@dataclass
class PublishResult:
    post_id: Optional[str]
    status: str


class PublishClient:
    """Simple HTTP client placeholder for TikTok-like APIs.

    This is a minimal, test-friendly interface. Real provider differences
    must be adapted by implementing upload/publish flows.
    """

    def __init__(self, api_key: str, api_base: str = "https://api.tiktok.com", timeout: int = 30) -> None:
        self.api_key = api_key
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout

    def upload_video(self, file_path: Path, metadata: Dict[str, Any]) -> str:
        """Upload video file and return an upload_token (placeholder).

        Tests must mock `requests.post` for this method.
        """
        logger.info("Uploading video %s", file_path)
        # Placeholder implementation: in real usage, stream file via multipart
        # Return a fake token for tests.
        return "upload-token-placeholder"

    def publish(self, upload_token: str, idempotency_key: Optional[str] = None) -> PublishResult:
        logger.info("Publishing upload %s", upload_token)
        # Placeholder: would call publish endpoint and return post id
        return PublishResult(post_id="post-placeholder", status="published")

    def get_status(self, post_id: str) -> str:
        logger.info("Fetching status for post %s", post_id)
        return "published"
