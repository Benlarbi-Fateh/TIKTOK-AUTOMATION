from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from db import Database
from logger import logger
from ollama_client import OllamaClient


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROMPT_PATH = (
    PROJECT_ROOT
    / "prompts"
    / "generate_tiktok_script.txt"
)


SCRIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
        },
        "hook": {
            "type": "string",
        },
        "script_text": {
            "type": "string",
        },
        "description": {
            "type": "string",
        },
        "hashtags": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "scene_number": {
                        "type": "integer",
                    },
                    "duration_seconds": {
                        "type": "integer",
                    },
                    "voice_text": {
                        "type": "string",
                    },
                    "visual_instruction": {
                        "type": "string",
                    },
                    "screen_text": {
                        "type": "string",
                    },
                },
                "required": [
                    "scene_number",
                    "duration_seconds",
                    "voice_text",
                    "visual_instruction",
                    "screen_text",
                ],
                "additionalProperties": False,
            },
        },
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                    },
                    "url": {
                        "type": "string",
                    },
                },
                "required": [
                    "name",
                    "url",
                ],
                "additionalProperties": False,
            },
        },
        "uncertainties": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "title",
        "hook",
        "script_text",
        "description",
        "hashtags",
        "scenes",
        "sources",
        "uncertainties",
    ],
    "additionalProperties": False,
}


def load_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Prompt introuvable : {PROMPT_PATH}"
        )

    return PROMPT_PATH.read_text(encoding="utf-8")


def build_prompt(
    topic: dict[str, Any],
) -> str:
    template = load_prompt()

    replacements = {
        "{{TITLE}}": str(topic.get("title") or ""),
        "{{SUMMARY}}": str(topic.get("summary") or ""),
        "{{CATEGORY}}": str(topic.get("category") or ""),
        "{{SOURCE_NAME}}": str(
            topic.get("source_name") or ""
        ),
        "{{SOURCE_URL}}": str(
            topic.get("source_url") or ""
        ),
    }

    for placeholder, value in replacements.items():
        template = template.replace(
            placeholder,
            value,
        )

    return template


def validate_result(
    result: dict[str, Any],
) -> dict[str, Any]:
    text_fields = [
        "title",
        "hook",
        "script_text",
        "description",
    ]

    for field in text_fields:
        value = str(result.get(field) or "").strip()

        if not value:
            raise ValueError(
                f"Le champ {field} est vide."
            )

        result[field] = value

    hashtags = result.get("hashtags")

    if not isinstance(hashtags, list):
        raise ValueError(
            "hashtags doit être une liste."
        )

    cleaned_hashtags = []

    for hashtag in hashtags:
        hashtag = str(hashtag).strip()

        if not hashtag:
            continue

        if not hashtag.startswith("#"):
            hashtag = f"#{hashtag}"

        cleaned_hashtags.append(hashtag)

    if not cleaned_hashtags:
        raise ValueError(
            "Aucun hashtag valide n'a été généré."
        )

    result["hashtags"] = cleaned_hashtags[:6]

    scenes = result.get("scenes")

    if not isinstance(scenes, list) or not scenes:
        raise ValueError(
            "Aucune scène n'a été générée."
        )

    sources = result.get("sources")

    if not isinstance(sources, list):
        result["sources"] = []

    uncertainties = result.get("uncertainties")

    if not isinstance(uncertainties, list):
        result["uncertainties"] = []

    word_count = len(
        result["script_text"].split()
    )

    if word_count < 80:
        logger.warning(
            "Le script est assez court : %s mots.",
            word_count,
        )

    if word_count > 180:
        logger.warning(
            "Le script est assez long : %s mots.",
            word_count,
        )

    return result


def generate_script(
    topic_id: int,
    force: bool = False,
) -> dict[str, Any]:
    with Database() as database:
        row = database.get_topic_by_id(topic_id)

        if row is None:
            raise ValueError(
                f"Sujet {topic_id} introuvable."
            )

        topic = dict(row)

        if topic["status"] != "approved":
            raise ValueError(
                f"Le sujet {topic_id} n'est pas approuvé. "
                f"Statut actuel : {topic['status']}."
            )

        if (
            not force
            and database.script_exists_for_topic(
                topic_id
            )
        ):
            raise ValueError(
                "Un script existe déjà pour "
                f"le sujet {topic_id}."
            )

        prompt = build_prompt(topic)

        logger.info(
            "Génération du script pour le sujet %s : %s",
            topic_id,
            topic["title"],
        )

        client = OllamaClient()

        raw_result = client.generate(
            prompt=prompt,
            temperature=0.4,
            json_schema=SCRIPT_SCHEMA,
        )

        if not isinstance(raw_result, dict):
            raise TypeError(
                "Ollama devait retourner un objet JSON, "
                f"mais a retourné : {type(raw_result).__name__}"
            )

        result = validate_result(raw_result)

        hashtags_text = " ".join(
            result["hashtags"]
        )

        scenes_json = json.dumps(
            result["scenes"],
            ensure_ascii=False,
            indent=2,
        )

        sources_json = json.dumps(
            result["sources"],
            ensure_ascii=False,
            indent=2,
        )

        uncertainties_json = json.dumps(
            result["uncertainties"],
            ensure_ascii=False,
            indent=2,
        )

        script_id = database.add_script(
            topic_id=topic_id,
            title=result["title"],
            hook=result["hook"],
            script_text=result["script_text"],
            description=result["description"],
            hashtags=hashtags_text,
            scenes_json=scenes_json,
            sources_json=sources_json,
            uncertainties_json=uncertainties_json,
            status="draft",
        )

        database.update_topic_status(
            topic_id=topic_id,
            status="scripted",
        )

        result["script_id"] = script_id
        result["topic_id"] = topic_id

        logger.info(
            "Script %s créé avec succès.",
            script_id,
        )

        return result