from app.pipeline.stages.generator import GeneratorStage
from app.pipeline.context import PipelineContext


def test_generator_stage_no_topic_noop():
    ctx = PipelineContext()
    stage = GeneratorStage()
    # should not raise when no current_topic is set
    stage.execute(ctx)
    assert ctx.current_script is None
