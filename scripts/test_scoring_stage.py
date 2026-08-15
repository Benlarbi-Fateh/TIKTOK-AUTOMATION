from app.pipeline.context import PipelineContext
from app.pipeline.stages.scoring import ScoringStage


def fake_score(topic_id: int):
    return {"viral_score": 10, "originality_score": 5, "affiliate_score": 5, "final_score": 20, "reason": "ok"}


if __name__ == "__main__":
    # Prepare context with a fake topic
    context = PipelineContext(current_topic={"id": 1, "title": "Test"})

    # Monkeypatch the scorer
    import app.scoring.topic_scorer as scorer

    scorer.score_topic = fake_score

    stage = ScoringStage()
    stage.execute(context)

    print("Score result:", context.current_topic.get("score_result"))
