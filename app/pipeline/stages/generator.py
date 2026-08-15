from __future__ import annotations

from app.pipeline.stage import PipelineStage
from app.pipeline.context import PipelineContext
from app.generator.generator import generate_script
from app.utils.logger import logger


class GeneratorStage(PipelineStage):
    name = "generator"

    def run(self, context: PipelineContext) -> None:
        """Generate a script for the current topic and attach it to context.current_script."""

        topic = context.current_topic

        if not topic or "id" not in topic:
            logger.info("Aucun sujet courant pour la génération — saut de la stage generator.")
            return

        topic_id = int(topic["id"])

        logger.info("GeneratorStage: generating script for topic %s", topic_id)

        result = generate_script(topic_id=topic_id, force=context.settings.get("force_generate", False))

        context.current_script = result
        logger.info("GeneratorStage completed, script id %s", result.get("script_id"))
