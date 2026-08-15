import json
from pathlib import Path

import pytest

from app.publish.client import PublishClient, PublishResult, PublishError


class DummyResponse:
    def __init__(self, status_code=200, content=b"", json_data=None, text=""):
        self.status_code = status_code
        # expose some content when json_data is provided so client.json() is used
        self._content = content if content else (b"{" if json_data else b"")
        self._json = json_data
        self.text = text

    @property
    def content(self):
        return self._content

    def json(self):
        return self._json or {}


class DummySession:
    def __init__(self, responses):
        self.responses = responses
        self.posts = []

    def post(self, url, headers=None, data=None, files=None, json=None, timeout=None):
        self.posts.append((url, headers, data, files, json))
        return self.responses.pop(0)

    def get(self, url, headers=None, timeout=None):
        return self.responses.pop(0)


def test_upload_and_publish_success(monkeypatch, tmp_path):
    # Create a small temp file to act as video
    p = tmp_path / "video.mp4"
    p.write_bytes(b"fake")

    upload_resp = DummyResponse(status_code=200, json_data={"upload_id": "upl-123"})
    publish_resp = DummyResponse(status_code=200, json_data={"post_id": "post-456", "status": "published"})

    session = DummySession([upload_resp, publish_resp])
    client = PublishClient(api_key="key", session=session)

    upload_token = client.upload_video(file_path=p, metadata={"foo": "bar"})
    assert upload_token == "upl-123"

    result = client.publish(upload_token=upload_token, idempotency_key="id-1")
    assert isinstance(result, PublishResult)
    assert result.post_id == "post-456"
    assert result.status == "published"


def test_upload_400_raises(monkeypatch, tmp_path):
    p = tmp_path / "video.mp4"
    p.write_bytes(b"fake")

    bad = DummyResponse(status_code=400, content=b"", json_data={})
    session = DummySession([bad])
    client = PublishClient(api_key="key", session=session)

    with pytest.raises(PublishError):
        client.upload_video(file_path=p, metadata={})
