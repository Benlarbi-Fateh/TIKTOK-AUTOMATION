from app.pipeline.stages.selection import SelectionStage
from app.pipeline.context import PipelineContext


def test_selection_stage_runs_and_stores_stats():
    ctx = PipelineContext()
    # ensure settings exist and run in dry_run mode to avoid DB mutations
    ctx.settings["dry_run"] = True

    stage = SelectionStage()
    stage.execute(ctx)

    assert "selection_stats" in ctx.settings
    stats = ctx.settings["selection_stats"]
    assert isinstance(stats, dict)
