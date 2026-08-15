from pathlib import Path
from typing import Any

from app.database import Database
from app.utils.logger import logger
from app.services.ollama import OllamaClient
from app.utils.config import PROMPTS_DIR


PROMPT_PATH = PROMPTS_DIR / "score_topic.txt"


SCORE_SCHEMA = {
    "type": "object",
    "properties": {
        "viral_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 40,
        },
        "originality_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 30,
        },
        "affiliate_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 30,
        },
        "final_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
        },
        "reason": {
            "type": "string",
        },
    },
    "required": [
        "viral_score",
        "originality_score",
        "affiliate_score",
        "final_score",
        "reason",
    ],
    "additionalProperties": False,
}


def load_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Prompt introuvable : {PROMPT_PATH}"
        )

    return PROMPT_PATH.read_text(encoding="utf-8")


def build_prompt(topic: dict[str, Any]) -> str:
    template = load_prompt()

    title = str(topic.get("title") or "")
    summary = str(topic.get("summary") or "")
    category = str(topic.get("category") or "")

    return (
        template
        .replace("{{TITLE}}", title)
        .replace("{{SUMMARY}}", summary)
        .replace("{{CATEGORY}}", category)
    )


def validate_scores(
    result: dict[str, Any],
) -> dict[str, Any]:
    required_fields = {
        "viral_score",
        "originality_score",
        "affiliate_score",
        "final_score",
        "reason",
    }

    missing_fields = required_fields.difference(result.keys())

    if missing_fields:
        raise ValueError(
            "Champs manquants dans la réponse Ollama : "
            f"{sorted(missing_fields)}"
        )

    try:
        viral_score = int(result["viral_score"])
        originality_score = int(
            result["originality_score"]
        )
        affiliate_score = int(result["affiliate_score"])
        final_score = int(result["final_score"])

    except (TypeError, ValueError) as error:
        raise ValueError(
            "Un ou plusieurs scores ne sont pas des nombres entiers."
        ) from error

    if not 0 <= viral_score <= 40:
        raise ValueError(
            "viral_score doit être compris entre 0 et 40."
        )

    if not 0 <= originality_score <= 30:
        raise ValueError(
            "originality_score doit être compris entre 0 et 30."
        )

    if not 0 <= affiliate_score <= 30:
        raise ValueError(
            "affiliate_score doit être compris entre 0 et 30."
        )

    calculated_total = (
        viral_score
        + originality_score
        + affiliate_score
    )

    if final_score != calculated_total:
        logger.warning(
            "Le score final fourni par Ollama est incorrect : "
            "%s. Il est remplacé par %s.",
            final_score,
            calculated_total,
        )

        final_score = calculated_total

    reason = str(result["reason"]).strip()

    if not reason:
        reason = "Aucune justification fournie."

    return {
        "viral_score": viral_score,
        "originality_score": originality_score,
        "affiliate_score": affiliate_score,
        "final_score": final_score,
        "reason": reason,
    }


def score_topic(topic_id: int) -> dict[str, Any]:
    with Database() as database:
        row = database.fetchone(
            """
            SELECT *
            FROM topics
            WHERE id = ?
            """,
            (topic_id,),
        )

        if row is None:
            raise ValueError(
                "Aucun sujet trouvé avec l'identifiant "
                f"{topic_id}."
            )

        topic = dict(row)

        logger.info(
            "Préparation du prompt pour le sujet %s : %s",
            topic_id,
            topic.get("title"),
        )

        prompt = build_prompt(topic)

        client = OllamaClient()

        raw_result = client.generate(
            prompt=prompt,
            temperature=0.1,
            json_schema=SCORE_SCHEMA,
        )

        logger.info(
            "Résultat brut de notation : %r",
            raw_result,
        )

        if not isinstance(raw_result, dict):
            raise TypeError(
                "Ollama devait retourner un objet JSON, "
                "mais a retourné un type "
                f"{type(raw_result).__name__} : {raw_result!r}"
            )

        result = validate_scores(raw_result)

        database.update_topic_score(
            topic_id=topic_id,
            viral_score=result["viral_score"],
            originality_score=result[
                "originality_score"
            ],
            affiliate_score=result["affiliate_score"],
            final_score=result["final_score"],
        )

        logger.info(
            "Sujet %s noté avec succès : %s/100",
            topic_id,
            result["final_score"],
        )

        logger.info(
            "Justification : %s",
            result["reason"],
        )

        return result
