from app.scoring.topic_scorer import build_prompt, load_prompt, validate_scores
from app.scoring.topic_scorer import SCORE_SCHEMA


def test_validate_scores_basic():
    sample = {
        "viral_score": 10,
        "originality_score": 10,
        "affiliate_score": 10,
        "final_score": 30,
        "reason": "ok",
    }

    out = validate_scores(sample)
    assert out["final_score"] == 30
