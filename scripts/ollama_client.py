import json
from typing import Any

import requests

from config import OLLAMA_MODEL, OLLAMA_URL
from logger import logger


class OllamaClient:
    def __init__(
        self,
        base_url: str = OLLAMA_URL,
        model: str = OLLAMA_MODEL,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(
        self,
        prompt: str,
        temperature: float = 0.5,
        json_format: bool = False,
        json_schema: dict[str, Any] | None = None,
    ) -> str | dict[str, Any] | list[Any]:
        if not prompt.strip():
            raise ValueError("Le prompt ne peut pas être vide.")

        url = f"{self.base_url}/api/generate"

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "2m",
            "options": {
                "num_ctx": 4096,
                "temperature": temperature,
                "top_p": 0.9,
            },
        }

        if json_schema is not None:
            payload["format"] = json_schema
        elif json_format:
            payload["format"] = "json"

        logger.info(
            "Envoi d'une requête à Ollama avec le modèle %s",
            self.model,
        )

        response = None

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=180,
            )

            response.raise_for_status()

        except requests.ConnectionError as error:
            raise RuntimeError(
                "Connexion à Ollama impossible. "
                "Vérifie qu'Ollama est démarré."
            ) from error

        except requests.Timeout as error:
            raise RuntimeError(
                "Ollama a dépassé le délai de réponse."
            ) from error

        except requests.HTTPError as error:
            status_code = (
                response.status_code
                if response is not None
                else "inconnu"
            )

            response_text = (
                response.text
                if response is not None
                else ""
            )

            raise RuntimeError(
                f"Erreur HTTP Ollama {status_code} : "
                f"{response_text}"
            ) from error

        except requests.RequestException as error:
            raise RuntimeError(
                f"Erreur pendant l'appel à Ollama : {error}"
            ) from error

        try:
            data = response.json()
        except ValueError as error:
            raise RuntimeError(
                "La réponse HTTP d'Ollama n'est pas un JSON valide."
            ) from error

        generated_text = data.get("response", "").strip()

        if not generated_text:
            raise RuntimeError(
                "Ollama a renvoyé une réponse vide."
            )

        if json_format or json_schema is not None:
            try:
                parsed_result = json.loads(generated_text)

            except json.JSONDecodeError as error:
                logger.error(
                    "Réponse brute Ollama : %s",
                    generated_text,
                )

                raise RuntimeError(
                    "Le contenu généré par Ollama "
                    "n'est pas un JSON valide."
                ) from error

            logger.info(
                "Type JSON retourné par Ollama : %s",
                type(parsed_result).__name__,
            )

            return parsed_result

        return generated_text