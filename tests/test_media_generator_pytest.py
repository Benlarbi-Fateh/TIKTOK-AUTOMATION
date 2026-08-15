from pathlib import Path
import asyncio

def test_generate_audio_fallback(tmp_path, monkeypatch):
    out = tmp_path / "audio.mp3"

    # Simulate absence of edge-tts by ensuring import raises
    monkeypatch.setitem(__import__('sys').modules, 'edge_tts', None)

    from app.media.generator import generate_audio

    res = generate_audio("hello", out)
    assert res == out
    assert out.exists()


def test_generate_images_pillow_and_fallback(tmp_path, monkeypatch):
    scenes = [{"scene_number": 1, "voice_text": "Hello world"}, {"scene_number": 2, "voice_text": "Bye"}]
    outdir = tmp_path / "images"

    # First, simulate Pillow not available
    monkeypatch.setitem(__import__('sys').modules, 'PIL', None)
    from app.media.generator import generate_images

    imgs = generate_images(scenes, outdir)
    assert len(imgs) == 2
    for p in imgs:
        assert p.exists()
