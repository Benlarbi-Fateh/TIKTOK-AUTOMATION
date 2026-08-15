from __future__ import annotations

from pathlib import Path
from app.pipeline.stage import PipelineStage
from app.pipeline.context import PipelineContext
from app.media.generator import (
    generate_audio,
    generate_images,
    generate_subtitles,
)
from app.utils.logger import logger


class MediaStage(PipelineStage):
    name = "media"

    def run(self, context: PipelineContext) -> None:
        script = context.current_script

        if not script:
            logger.info("No script available for media generation — skipping MediaStage.")
            return

        dry_run = bool(context.settings.get("dry_run", False))

        project = context.project_folder
        outputs = project / "outputs"

        scenes = script.get("scenes", [])

        if dry_run:
            # do not perform heavy work in dry-run; record intent
            context.settings["media_generated"] = True
            logger.info("Dry run: MediaStage skipped actual generation.")
            return

        # audio
        audio_path = outputs / f"script_{script.get('script_id', 'unknown')}.mp3"
        context.audio_path = generate_audio(script.get("script_text", ""), audio_path)

        # images
        images_folder = outputs / f"script_{script.get('script_id', 'unknown')}_images"
        context.images = generate_images(scenes, images_folder)

        # subtitles
        subtitle_path = outputs / f"script_{script.get('script_id', 'unknown')}.srt"
        context.subtitle_path = generate_subtitles(scenes, subtitle_path)

        context.settings["media_generated"] = True
