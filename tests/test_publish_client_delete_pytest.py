import pytest

from types import SimpleNamespace

from app.publish.client import PublishClient, PublishTransientError, PublishError


class DummyResponse:
    def __init__(self, status_code=200, text="", content=b""):
        self.status_code = status_code
        self.text = text
        self.content = content


class DummySession:
    def __init__(self, resp):
        self._resp = resp

    def delete(self, url, headers=None, timeout=None):
        return self._resp


def test_delete_success_204():
    client = PublishClient(api_key="key", session=DummySession(DummyResponse(status_code=204)))
    assert client.delete_video("post123") is True


def test_delete_not_found_404():
    client = PublishClient(api_key="key", session=DummySession(DummyResponse(status_code=404)))
    assert client.delete_video("post123") is True


def test_delete_server_error_raises_transient():
    client = PublishClient(api_key="key", session=DummySession(DummyResponse(status_code=500)))
    with pytest.raises(PublishTransientError):
        client.delete_video("post123")


def test_delete_client_error_raises():
    client = PublishClient(api_key="key", session=DummySession(DummyResponse(status_code=400, text="bad")))
    with pytest.raises(PublishError):
        client.delete_video("post123")
