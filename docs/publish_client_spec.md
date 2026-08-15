# Publish Client Specification

Purpose: define the `PublishClient` interface and runtime behavior for publishing videos to TikTok-like APIs.

1) Public API
- `class PublishClient(api_key: str, api_base: str, timeout: int = 30, max_retries: int = 3)`
- `upload_video(file_path: Path, metadata: dict) -> str` : upload and return an `upload_token` or `upload_id`.
- `publish(upload_token: str, idempotency_key: Optional[str] = None) -> PublishResult` : request publish, return `post_id` and status.
- `get_status(post_id: str) -> str` : return publish status.

2) Behavior
- Use an internal `requests.Session` with a retry policy for idempotent requests and safe retries for 5xx.
- Include `Idempotency-Key` header when provided.
- Timeouts: default per-call timeout; configurable in constructor.
- Errors: raise `PublishError` for client errors (4xx) and `PublishTransientError` for retryable server errors.

3) Testing
- Unit tests must mock HTTP calls (`requests.Session`) to verify headers, retries, and idempotency behavior.
- Integration tests gated by `RUN_PUBLISH_TESTS=1`.

4) Security
- Do not log API keys; allow passing pre-configured `requests.Session` for advanced usage.
