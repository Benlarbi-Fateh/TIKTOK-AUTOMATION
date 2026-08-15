from app.pipeline.stages.media import MediaStage
from app.pipeline.context import PipelineContext


def test_media_stage_dry_run_sets_flag():
    ctx = PipelineContext()
    ctx.current_script = {
        "script_id": 1,
        "script_text": "Bonjour",
        "scenes": [{"scene_number": 1, "voice_text": "hello"}],
    }
    ctx.settings["dry_run"] = True

    stage = MediaStage()
    stage.execute(ctx)

    assert ctx.settings.get("media_generated") is True
