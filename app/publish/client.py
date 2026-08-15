from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import os
import requests
from requests.adapters import HTTPAdapter, Retry

from app.utils.logger import logger


@dataclass
class PublishResult:
    post_id: Optional[str]
    status: str


class PublishError(Exception):
    pass


class PublishTransientError(PublishError):
    pass


class PublishClient:
    def __init__(self, api_key: Optional[str] = None, api_base: str = "https://api.tiktok.com", timeout: int = 30, max_retries: int = 3, session: Optional[requests.Session] = None) -> None:
        self.api_key = api_key or os.environ.get("TIKTOK_ACCESS_TOKEN")
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout

        if session is None:
            session = requests.Session()
            retries = Retry(total=max_retries, backoff_factor=0.5, status_forcelist=(500, 502, 503, 504), allowed_methods=frozenset(["GET", "POST"]))
            adapter = HTTPAdapter(max_retries=retries)
            session.mount("https://", adapter)
            session.mount("http://", adapter)

        self.session = session

    def upload_video(self, file_path: Path, metadata: Dict[str, Any]) -> str:
        logger.info("PublishClient.upload_video: %s", file_path)
        # Placeholder: real implementation should stream multipart file upload
        # For testability, we simulate a POST to /upload returning an upload_id
        url = f"{self.api_base}/upload/video"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

        files = {"file": (file_path.name, file_path.open("rb"))} if file_path.exists() else None

        resp = self.session.post(url, headers=headers, data={"meta": metadata}, files=files, timeout=self.timeout)

        if resp.status_code >= 500:
            raise PublishTransientError("Server error during upload")

        if resp.status_code >= 400:
            raise PublishError(f"Upload failed: {resp.status_code} {resp.text}")

        data = resp.json() if resp.content else {"upload_id": "upload-placeholder"}
        return data.get("upload_id") or data.get("upload_token") or "upload-placeholder"

    def publish(self, upload_token: str, idempotency_key: Optional[str] = None) -> PublishResult:
        logger.info("PublishClient.publish: %s", upload_token)
        url = f"{self.api_base}/video/publish"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        resp = self.session.post(url, headers=headers, json={"upload_token": upload_token}, timeout=self.timeout)

        if resp.status_code >= 500:
            raise PublishTransientError("Server error during publish")

        if resp.status_code >= 400:
            raise PublishError(f"Publish failed: {resp.status_code} {resp.text}")

        data = resp.json() if resp.content else {"post_id": "post-placeholder", "status": "published"}
        return PublishResult(post_id=data.get("post_id"), status=data.get("status", "unknown"))

    def get_status(self, post_id: str) -> str:
        url = f"{self.api_base}/video/status/{post_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        resp = self.session.get(url, headers=headers, timeout=self.timeout)

        if resp.status_code >= 500:
            raise PublishTransientError("Server error during status check")

        if resp.status_code >= 400:
            raise PublishError(f"Status check failed: {resp.status_code} {resp.text}")

        data = resp.json() if resp.content else {"status": "unknown"}
        return data.get("status", "unknown")

    def delete_video(self, post_id: str) -> bool:
        """Delete a published video (best-effort).

        Returns True when deletion confirmed or resource not found (404).
        Raises PublishTransientError on 5xx errors and PublishError on other 4xx.
        """
        url = f"{self.api_base}/video/{post_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

        resp = self.session.delete(url, headers=headers, timeout=self.timeout)

        if resp.status_code >= 500:
            raise PublishTransientError("Server error during delete")

        # Treat 200/204 as success, 404 as already-deleted (idempotent success)
        if resp.status_code in (200, 204) or resp.status_code == 404:
            return True

        if resp.status_code >= 400:
            raise PublishError(f"Delete failed: {resp.status_code} {resp.text}")

        return True
