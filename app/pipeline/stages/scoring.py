from __future__ import annotations

from app.pipeline.stage import PipelineStage
from app.pipeline.context import PipelineContext
import app.scoring.topic_scorer as scorer
from app.utils.logger import logger


class ScoringStage(PipelineStage):
    name = "scoring"

    def run(self, context: PipelineContext) -> None:
        """Score the current topic via the scoring module.

        Expects `context.current_topic` to be a mapping with an `id` key.
        Stores the scoring result under `context.current_topic['score_result']`.
        """

        topic = context.current_topic

        if not topic or "id" not in topic:
            logger.info("Aucun sujet courant à noter — saut de la stage scoring.")
            return

        topic_id = int(topic["id"])

        logger.info("Scoring du sujet %s via ScoringStage", topic_id)

        result = scorer.score_topic(topic_id)

        # attach result to context for downstream stages
        topic["score_result"] = result
        context.current_topic = topic
