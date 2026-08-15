from __future__ import annotations

from app.pipeline.stage import PipelineStage
from app.pipeline.context import PipelineContext
from app.selection import select_topics
from app.utils.logger import logger


class SelectionStage(PipelineStage):
    name = "selection"

    def run(self, context: PipelineContext) -> None:
        """Run topic selection using the migrated selection module.

        Stores the resulting statistics into `context.settings['selection_stats']`.
        """

        approval_threshold = int(context.settings.get("approval_threshold", 60))
        review_threshold = int(context.settings.get("review_threshold", 45))
        limit = context.settings.get("selection_limit")
        dry_run = bool(context.settings.get("dry_run", False))

        logger.info(
            "Running SelectionStage (approval=%s review=%s limit=%s)",
            approval_threshold,
            review_threshold,
            limit,
        )

        stats = select_topics(
            approval_threshold=approval_threshold,
            review_threshold=review_threshold,
            limit=limit,
            dry_run=dry_run,
        )

        # persist into context for downstream inspection
        context.settings["selection_stats"] = stats
        logger.info("SelectionStage completed: %s", stats)
