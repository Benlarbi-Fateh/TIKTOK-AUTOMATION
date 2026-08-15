from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from app.pipeline.context import PipelineContext
from app.pipeline.stage import PipelineStage
from app.utils.logger import logger


class PipelineEngine:
    """Orchestrates execution of registered pipeline stages.

    The engine supports saving state on failure so the pipeline can be resumed.
    """

    def __init__(self, state_folder: Path | None = None) -> None:
        self.stages: List[PipelineStage] = []
        self.state_folder = (
            Path(state_folder) if state_folder is not None else Path.cwd() / ".pipeline"
        )
        self.state_folder.mkdir(parents=True, exist_ok=True)
        self._state_file = self.state_folder / "state.json"

    def register(self, stage: PipelineStage) -> None:
        self.stages.append(stage)

    def run(self, context: PipelineContext, resume: bool = False) -> None:
        """Execute stages in order. On exception save state for resume."""
        start_index = 0

        if resume and self._state_file.exists():
            try:
                data = json.loads(self._state_file.read_text(encoding="utf-8"))
                start_index = int(data.get("last_stage", 0))
                logger.info("Resuming pipeline from stage index %s", start_index)
            except Exception:
                logger.exception("Impossible de lire l'état du pipeline, démarrage depuis 0.")
                start_index = 0

        for index, stage in enumerate(self.stages[start_index:], start=start_index):
            try:
                logger.info("Running stage %s (index=%s)", stage.name, index)
                stage.execute(context)
                # update state after successful stage
                self._save_state(index + 1, context)

            except Exception:
                logger.exception("Pipeline failed on stage %s (index=%s)", stage.name, index)
                self._save_state(index, context, failed=True)
                raise

        # finished successfully -> remove state
        if self._state_file.exists():
            try:
                self._state_file.unlink()
            except Exception:
                logger.warning("Impossible de supprimer le fichier d'état du pipeline.")

    def _save_state(self, last_stage: int, context: PipelineContext, failed: bool = False) -> None:
        payload = {
            "last_stage": last_stage,
            "failed": bool(failed),
            "context": context.to_dict(),
        }

        try:
            self._state_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.info("Pipeline state saved to %s", self._state_file)
        except Exception:
            logger.exception("Failed to save pipeline state.")

    def resume(self, context: PipelineContext) -> None:
        """Resume pipeline using saved state (if any)."""
        self.run(context, resume=True)
