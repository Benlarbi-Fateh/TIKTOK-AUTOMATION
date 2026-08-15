from pathlib import Path
import shutil
import subprocess

def test_render_video_with_images_and_audio(monkeypatch, tmp_path):
    audio = tmp_path / "audio.mp3"
    audio.write_bytes(b"audio")

    img1 = tmp_path / "i1.png"
    img1.write_bytes(b"i1")
    img2 = tmp_path / "i2.png"
    img2.write_bytes(b"i2")

    out = tmp_path / "out.mp4"

    # mock shutil.which to return a fake path
    monkeypatch.setattr(shutil, "which", lambda name: "ffmpeg")

    # mock subprocess.run to simulate success
    class DummyCompleted:
        def __init__(self):
            self.returncode = 0

    def fake_run(cmd, check, capture_output):
        return DummyCompleted()

    monkeypatch.setattr(subprocess, "run", fake_run)

    from app.media.renderer import render_video

    result = render_video(audio_path=audio, images=[img1, img2], subtitles_path=None, output_path=out)

    assert result == out
    assert out.exists()
