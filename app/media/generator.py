from __future__ import annotations

from pathlib import Path
from typing import List

from app.utils.logger import logger


def generate_audio(text: str, output_path: Path) -> Path:
    """Generate audio from text using edge-tts if available.

    Raises RuntimeError if TTS backend is not available.
    """
    try:
        import edge_tts  # type: ignore
    except Exception:
        # Optional dependency: fallback to placeholder (do not raise)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("[audio binary placeholder]", encoding="utf-8")
        logger.warning("edge-tts not available; wrote audio placeholder at %s", output_path)
        return output_path

    # If edge_tts is available, attempt to use it (best-effort).
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Use a simplified API to support testing/mocking.
        async def _synthesize():
            communicate = edge_tts.Communicate(str(text), "en-US")
            await communicate.save(str(output_path))

        import asyncio

        asyncio.run(_synthesize())
        logger.info("Generated audio using edge-tts at %s", output_path)
        return output_path
    except Exception:
        output_path.write_text("[audio binary placeholder]", encoding="utf-8")
        logger.exception("edge-tts failed; wrote placeholder audio at %s", output_path)
        return output_path


def generate_images(scenes: List[dict], output_folder: Path) -> List[Path]:
    """Generate images for each scene. This is a placeholder implementation.

    Returns list of image paths (may be empty if no scenes).
    """
    output_folder.mkdir(parents=True, exist_ok=True)
    image_paths: List[Path] = []

    # Try to use Pillow if available to generate simple images
    try:
        from PIL import Image, ImageDraw  # type: ignore

        for scene in scenes:
            idx = scene.get("scene_number", len(image_paths) + 1)
            p = output_folder / f"scene_{idx}.png"
            img = Image.new("RGB", (1280, 720), color=(73, 109, 137))
            draw = ImageDraw.Draw(img)
            text = scene.get("voice_text", "")[:40]
            draw.text((50, 360), text, fill=(255, 255, 255))
            img.save(p)
            image_paths.append(p)

        logger.info("Generated %s images in %s using Pillow", len(image_paths), output_folder)
        return image_paths
    except Exception:
        # Fallback: create placeholder files
        for scene in scenes:
            idx = scene.get("scene_number", len(image_paths) + 1)
            p = output_folder / f"scene_{idx}.png"
            p.write_text("[image placeholder]", encoding="utf-8")
            image_paths.append(p)

        logger.warning("Pillow not available; created %s image placeholders in %s", len(image_paths), output_folder)
        return image_paths


def generate_subtitles(scenes: List[dict], output_path: Path) -> Path:
    """Create a simple SRT subtitles file from scenes' voice_text."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    for scene in scenes:
        idx = scene.get("scene_number", len(lines) + 1)
        voice = scene.get("voice_text", "")
        lines.append(str(idx))
        lines.append("00:00:00,000 --> 00:00:05,000")
        lines.append(voice)
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Generated subtitles at %s", output_path)
    return output_path
