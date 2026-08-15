from __future__ import annotations

from pathlib import Path
from app.pipeline.stage import PipelineStage
from app.pipeline.context import PipelineContext
from app.media.renderer import render_video
from app.utils.logger import logger


class RenderStage(PipelineStage):
    name = "render"

    def run(self, context: PipelineContext) -> None:
        if not context.current_script:
            logger.info("No script for rendering — skipping RenderStage.")
            return

        dry_run = bool(context.settings.get("dry_run", False))

        if dry_run:
            context.settings["rendered"] = True
            logger.info("Dry run: RenderStage skipped actual rendering.")
            return

        audio = context.audio_path
        images = context.images
        subs = context.subtitle_path

        output = context.project_folder / "outputs" / f"video_{context.current_script.get('script_id', 'unknown')}.mp4"

        result = render_video(audio, images, subs, output)
        context.current_video = {"path": result}
        context.settings["rendered"] = True
