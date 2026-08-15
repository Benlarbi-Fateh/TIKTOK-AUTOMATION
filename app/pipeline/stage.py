from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Optional

from app.utils.logger import logger
from app.pipeline.context import PipelineContext


class PipelineStage:
    """Base class for pipeline stages.

    Subclasses should implement ``run(context)`` and may
    override ``name`` for logging purposes.
    """

    name: str = "base"

    def run(self, context: PipelineContext) -> None:  # pragma: no cover - abstract
        """Execute stage logic. Must be implemented by subclasses."""
        raise NotImplementedError

    def execute(self, context: PipelineContext) -> None:
        """Wrapper that runs the stage with timing, logging and error handling."""
        logger.info("Stage %s - start", self.name)
        start = time.perf_counter()

        try:
            self.run(context)

        except Exception:
            logger.exception("Stage %s - failed", self.name)
            raise

        finally:
            elapsed = time.perf_counter() - start
            logger.info("Stage %s - finished (%.2fs)", self.name, elapsed)
