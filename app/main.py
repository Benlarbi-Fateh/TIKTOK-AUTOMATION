from __future__ import annotations

from pathlib import Path

from app.pipeline.engine import PipelineEngine
from app.pipeline.context import PipelineContext
from app.pipeline.stage import PipelineStage
from app.pipeline.stages.scoring import ScoringStage
from app.utils.logger import logger


class ExampleStage(PipelineStage):
    name = "example"

    def run(self, context: PipelineContext) -> None:
        logger.info("ExampleStage: processing context %r", context.to_dict())
        # perform a tiny mutation to demonstrate flow
        context.add_log("example-stage-completed")


def build_pipeline() -> PipelineEngine:
    engine = PipelineEngine()
    # Register scoring stage first (it will noop if no current_topic)
    engine.register(ScoringStage())
    from app.pipeline.stages.selection import SelectionStage
    engine.register(SelectionStage())
    from app.pipeline.stages.generator import GeneratorStage
    engine.register(GeneratorStage())
    from app.pipeline.stages.media import MediaStage
    engine.register(MediaStage())
    from app.pipeline.stages.render import RenderStage
    engine.register(RenderStage())
    engine.register(ExampleStage())
    return engine


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    context = PipelineContext(project_folder=project_root)

    engine = build_pipeline()

    try:
        engine.run(context)
        logger.info("Pipeline completed successfully.")
    except Exception:
        logger.exception("Pipeline execution failed.")


if __name__ == "__main__":
    main()
