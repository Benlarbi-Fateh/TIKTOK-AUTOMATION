from __future__ import annotations

from typing import List

from app.pipeline.stage import PipelineStage


class PipelineRegistry:
    """Simple registry to hold pipeline stages in order."""

    def __init__(self) -> None:
        self._stages: List[PipelineStage] = []

    def register(self, stage: PipelineStage) -> None:
        self._stages.append(stage)

    def get_stages(self) -> List[PipelineStage]:
        return list(self._stages)
