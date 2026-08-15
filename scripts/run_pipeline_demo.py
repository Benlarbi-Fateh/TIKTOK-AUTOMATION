from pathlib import Path

from app.pipeline.engine import PipelineEngine
from app.pipeline.context import PipelineContext
from app.pipeline.stages.scoring import ScoringStage
from app.pipeline.stages.selection import SelectionStage
from app.pipeline.stages.generator import GeneratorStage
from app.pipeline.stages.media import MediaStage
from app.pipeline.stages.render import RenderStage
from app.pipeline.stage import PipelineStage
from app.utils.logger import logger


def main():
    # Demo pipeline: scoring stage requires a current_topic with an id
    project_root = Path(__file__).resolve().parents[1]
    context = PipelineContext(project_folder=project_root)

    # choose a topic id that exists in the demo DB (23 used during tests)
    context.current_topic = {"id": 23, "title": "Demo topic"}

    engine = PipelineEngine()
    engine.register(ScoringStage())
    engine.register(SelectionStage())
    engine.register(GeneratorStage())
    engine.register(MediaStage())
    engine.register(RenderStage())

    try:
        engine.run(context)
        logger.info("Pipeline demo completed.")
    except Exception:
        logger.exception("Pipeline demo failed.")


if __name__ == '__main__':
    main()
