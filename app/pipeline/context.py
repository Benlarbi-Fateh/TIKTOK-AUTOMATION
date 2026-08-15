from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PipelineContext:
    """Shared context object passed to each pipeline stage.

    Attributes:
        current_topic: Optional[Dict[str, Any]]: raw topic data or model.
        current_script: Optional[Dict[str, Any]]: generated script data.
        current_video: Optional[Dict[str, Any]]: video metadata.
        audio_path: Optional[Path]: path to generated audio file.
        subtitle_path: Optional[Path]: path to subtitle file.
        images: List[Path]: generated image file paths per scene.
        project_folder: Path: workspace folder for the current production.
        logs: List[str]: lightweight per-context log entries.
        settings: Dict[str, Any]: runtime settings and thresholds.
        database: Any: database handle or service.
    """

    current_topic: Optional[Dict[str, Any]] = None
    current_script: Optional[Dict[str, Any]] = None
    current_video: Optional[Dict[str, Any]] = None

    audio_path: Optional[Path] = None
    subtitle_path: Optional[Path] = None
    images: List[Path] = field(default_factory=list)

    project_folder: Path = field(default_factory=lambda: Path.cwd())
    logs: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)

    database: Any = None

    def add_log(self, message: str) -> None:
        self.logs.append(message)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize a minimal representation of the context for diagnostics."""
        return {
            "current_topic": bool(self.current_topic),
            "current_script": bool(self.current_script),
            "current_video": bool(self.current_video),
            "audio_path": str(self.audio_path) if self.audio_path else None,
            "subtitle_path": str(self.subtitle_path) if self.subtitle_path else None,
            "images_count": len(self.images),
            "project_folder": str(self.project_folder),
        }
