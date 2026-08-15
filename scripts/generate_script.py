from __future__ import annotations

import argparse
import json

from app.utils.logger import logger
from script_generator import generate_script


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Génère un script TikTok "
            "depuis un sujet approuvé."
        )
    )

    parser.add_argument(
        "topic_id",
        type=int,
        help="Identifiant du sujet à traiter.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Autorise la génération même si "
            "un script existe déjà."
        ),
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        result = generate_script(
            topic_id=args.topic_id,
            force=args.force,
        )

    except Exception:
        logger.exception(
            "Échec de la génération du script."
        )
        raise SystemExit(1)

    print()
    print("=" * 70)
    print(f"Script ID : {result['script_id']}")
    print(f"Sujet ID  : {result['topic_id']}")
    print(f"Titre     : {result['title']}")
    print()
    print("Accroche :")
    print(result["hook"])
    print()
    print("Script :")
    print(result["script_text"])
    print()
    print("Description :")
    print(result["description"])
    print()
    print("Hashtags :")
    print(" ".join(result["hashtags"]))
    print()
    print("Scènes :")
    print(
        json.dumps(
            result["scenes"],
            ensure_ascii=False,
            indent=2,
        )
    )
    print("=" * 70)


if __name__ == "__main__":
    main()