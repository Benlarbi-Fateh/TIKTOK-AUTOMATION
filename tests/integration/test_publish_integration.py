import os
import tempfile
import time
import threading
import uuid
from pathlib import Path

import pytest

from app.publish.client import PublishClient
from tests.integration import mock_publish_server


def _make_dummy_video(path: Path) -> None:
    # Create a small placeholder file; sandbox should accept a binary blob for upload testing
    path.write_bytes(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41")


def test_publish_integration_gate():
    """Gated integration test for publish flow.

    Runs only when RUN_PUBLISH_TESTS=1 and `PUBLISH_SANDBOX_API_KEY` is set.
    The test performs: upload -> publish -> poll status. It attempts cleanup
    only when the client exposes a deletion API.
    """
    if os.getenv("RUN_PUBLISH_TESTS", "0") != "1":
        pytest.skip("Skipping gated publish integration tests (RUN_PUBLISH_TESTS!=1)")

    api_key = os.getenv("PUBLISH_SANDBOX_API_KEY") or os.getenv("TIKTOK_ACCESS_TOKEN")
    if not api_key:
        pytest.skip("No sandbox API key available in environment")

    # Optionally start a local mock publish server for deterministic testing
    use_mock = os.getenv("USE_MOCK_PUBLISH", "0") == "1"
    if use_mock:
        port = int(os.getenv("MOCK_PUBLISH_PORT", "8001"))
        t = threading.Thread(target=mock_publish_server.run, args=(port,), daemon=True)
        t.start()
        time.sleep(0.5)
        # When using the local mock, always target the mock server regardless
        # of any existing PUBLISH_SANDBOX_API_BASE value (avoid schemeless secrets)
        api_base = f"http://127.0.0.1:{port}"
    else:
        # Require an explicit sandbox base URL to avoid hitting production APIs by mistake
        api_base = os.getenv("PUBLISH_SANDBOX_API_BASE", "")
        if not api_base:
            pytest.skip("Skipping gated publish integration tests (PUBLISH_SANDBOX_API_BASE not set)")

    client = PublishClient(api_key=api_key, api_base=api_base)

    # create temp file
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / f"test_upload_{uuid.uuid4().hex}.mp4"
        _make_dummy_video(tmp)

        upload_token = client.upload_video(tmp, metadata={"title": "integration-test"})
        assert upload_token

        idempotency_key = f"test-{uuid.uuid4().hex}"
        result = client.publish(upload_token, idempotency_key=idempotency_key)
        assert result.status in ("published", "processing", "queued", "unknown")

        # If we received a post_id, poll status a few times
        if result.post_id:
            status = result.status
            deadline = time.time() + 30
            while status not in ("published", "failed") and time.time() < deadline:
                time.sleep(2)
                status = client.get_status(result.post_id)

            assert status in ("published", "processing", "queued", "unknown", "failed")

        # Attempt cleanup if client supports it (best-effort)
        if hasattr(client, "delete_video") and result.post_id:
            try:
                client.delete_video(result.post_id)
            except Exception:
                # best-effort cleanup; don't fail the test for cleanup issues
                pass

