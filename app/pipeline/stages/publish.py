from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.pipeline.stage import PipelineStage
from app.pipeline.context import PipelineContext
from app.publish.client import PublishClient
from app.utils.logger import logger


class PublishStage(PipelineStage):
    name = "publish"

    def run(self, context: PipelineContext) -> None:
        if not context.current_video:
            logger.info("No video present — skipping PublishStage.")
            return

        dry_run = bool(context.settings.get("dry_run", False))

        if dry_run:
            context.settings["published"] = True
            logger.info("Dry run: PublishStage skipped actual publish.")
            return

        api_key = context.settings.get("tiktok_api_key")
        client = PublishClient(api_key=api_key)

        video_path = context.current_video.get("path")
        file_path = Path(str(video_path))

        # idempotency: use script_id if available
        script = context.current_script or {}
        script_id = script.get("script_id")
        idempotency_key = f"script-{script_id}-{script.get('topic_id')}"

        # Prefer provided database handle in context for testability
        db = context.database

        if db is None:
            from app.database.db import Database

            db = Database()

        # Check if a video already exists and has a platform_id (already published)
        existing = None
        if script_id is not None:
            existing = db.get_video_by_script(script_id)

        if existing and existing.get("platform_id"):
            # Already published — set context and return
            context.settings["published"] = True
            context.current_video = dict(existing)
            logger.info("Video for script %s already published as %s", script_id, existing.get("platform_id"))
            return

        # Ensure a video record exists (create if missing)
        video_id = None
        if existing:
            video_id = existing["id"]
        else:
            video_id = db.add_video(
                script_id=script_id or 0,
                project_folder=str(context.project_folder),
                audio_path=str(context.audio_path) if context.audio_path else None,
                subtitle_path=str(context.subtitle_path) if context.subtitle_path else None,
                final_video_path=str(file_path),
                status="prepared",
            )

        upload_token = None
        result = None
        try:
            upload_token = client.upload_video(file_path=file_path, metadata={"script": script})
            result = client.publish(upload_token=upload_token, idempotency_key=idempotency_key)

            # update DB with published info
            db.update_video_publication(video_id=video_id, platform_id=result.post_id, status="published")

            context.settings["published"] = True
            context.current_video = {"id": video_id, "path": file_path, "post_id": result.post_id}
            logger.info("Published post %s for video %s", result.post_id, video_id)
        finally:
            # Test-only cleanup: perform server-side deletion when running gated tests
            # Controlled by two env vars to avoid accidental deletion in production
            try:
                import os

                if (
                    os.getenv("RUN_PUBLISH_TESTS", "0") == "1"
                    and os.getenv("ALLOW_REMOTE_CLEANUP", "0") == "1"
                    and result is not None
                    and result.post_id
                ):
                    try:
                        client.delete_video(result.post_id)
                        logger.info("Test cleanup: deleted remote post %s", result.post_id)
                        # Optionally record cleanup in DB
                        try:
                            db.update_video_publication(video_id=video_id, platform_id=result.post_id, status="deleted")
                        except Exception:
                            pass
                    except Exception as e:
                        logger.warning("Test cleanup failed for post %s: %s", getattr(result, "post_id", "?"), str(e))
            except Exception:
                # Swallow any unexpected errors in finalizer
                pass
