from app.pipeline.stages.render import RenderStage
from app.pipeline.context import PipelineContext


def test_render_stage_dry_run_sets_flag():
    ctx = PipelineContext()
    ctx.current_script = {"script_id": 1}
    ctx.settings["dry_run"] = True

    stage = RenderStage()
    stage.execute(ctx)

    assert ctx.settings.get("rendered") is True
