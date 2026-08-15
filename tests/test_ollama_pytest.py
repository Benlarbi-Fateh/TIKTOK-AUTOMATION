import os
import pytest
from app.services.ollama import OllamaClient


@pytest.mark.skipif(os.environ.get("RUN_NETWORK_TESTS") != "1", reason="Network tests skipped by default")
def test_ollama_text_and_json():
    client = OllamaClient()
    text = client.generate(prompt="Que fait SQLite ?", temperature=0.2)
    assert isinstance(text, str)

    json_res = client.generate(
        prompt=(
            "Retourne un petit JSON: {\"score\": 0, \"reason\": \"ok\"}"
        ),
        temperature=0.2,
        json_format=True,
    )

    assert isinstance(json_res, dict)
