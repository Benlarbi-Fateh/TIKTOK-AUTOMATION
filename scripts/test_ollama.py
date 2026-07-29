from logger import logger
from ollama_client import OllamaClient


def test_text_generation() -> None:
    client = OllamaClient()

    response = client.generate(
        prompt=(
            "Réponds en français en une seule phrase : "
            "à quoi sert SQLite ?"
        ),
        temperature=0.2,
    )

    logger.info("Réponse texte : %s", response)


def test_json_generation() -> None:
    client = OllamaClient()

    response = client.generate(
        prompt="""
Analyse ce sujet :

Titre : Un nouvel outil d'intelligence artificielle est disponible.

Retourne uniquement un JSON valide avec cette structure :

{
  "score": 0,
  "category": "",
  "reason": ""
}

Le score doit être compris entre 0 et 100.
""",
        temperature=0.2,
        json_format=True,
    )

    logger.info("Réponse JSON : %s", response)


if __name__ == "__main__":
    try:
        test_text_generation()
        test_json_generation()
        logger.info("Tous les tests Ollama sont réussis.")

    except Exception as error:
        logger.exception("Échec du test Ollama : %s", error)
        raise