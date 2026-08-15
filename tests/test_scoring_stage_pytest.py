import app.scoring.topic_scorer as scorer
from app.pipeline.context import PipelineContext
from app.pipeline.stages.scoring import ScoringStage


def test_scoring_stage_monkeypatch(monkeypatch):
    # Arrange: prepare fake score result and monkeypatch the scorer
    fake_result = {
        "viral_score": 1,
        "originality_score": 2,
        "affiliate_score": 3,
        "final_score": 6,
        "reason": "unit-test",
    }

    monkeypatch.setattr(scorer, "score_topic", lambda topic_id: fake_result)

    context = PipelineContext(current_topic={"id": 123, "title": "Test"})
    stage = ScoringStage()

    # Act
    stage.execute(context)

    # Assert
    assert context.current_topic is not None
    assert context.current_topic.get("score_result") == fake_result
