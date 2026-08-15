# Publish Integration Playbook (Sandbox)

Purpose: describe steps and security controls for running gated publish integration tests.

1. Prepare sandbox credentials
   - Create sandbox API key and secret with limited scope (uploads only).
   - Store credentials in CI secrets: `PUBLISH_SANDBOX_API_KEY`, `PUBLISH_SANDBOX_SECRET`.

2. CI gating
   - Integration job only runs when `PUBLISH_SANDBOX_API_KEY` secret is present.
   - Set environment `RUN_PUBLISH_TESTS=1` for the job.

3. Local developer guidance
   - Do not store sandbox credentials in plaintext. Use a local `.env` excluded from VCS.
   - To run locally: set `RUN_PUBLISH_TESTS=1` and set `PUBLISH_SANDBOX_API_KEY` in env.

4. Test hygiene
   - Tests should clean up uploaded artifacts after run if sandbox supports deletion.
   - Rate-limit and backoff: respect platform rate limits; use retries for transient errors.

4.1 Cleanup guidance
   - Prefer a server-side sandbox deletion API. If present, CI should call this in a finalizer step.
   - If no delete API is available, tag uploaded artifacts with a test-only prefix and document retention policies.
   - Always attempt best-effort cleanup in tests but do not fail the test solely for cleanup errors.

5. Logging and secrets
   - Avoid printing secrets or full request bodies in logs.
   - Redact or mask IDs and tokens in CI logs.

6. Rollback and post-run
   - If artifacts are published to a public view, ensure sandbox mode or cleanup exists.
