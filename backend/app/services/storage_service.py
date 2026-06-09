import re
from pathlib import Path

from app.core.config import Settings, settings


class LocalTranscriptStorage:
    def __init__(self, config: Settings = settings) -> None:
        configured_dir = Path(config.transcript_storage_dir)
        if configured_dir.is_absolute():
            self.base_dir = configured_dir
        else:
            project_root = Path(__file__).resolve().parents[3]
            self.base_dir = project_root / configured_dir

    def raw_meeting_dir(self, meeting_id: str) -> Path:
        path = self.base_dir / "raw" / meeting_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def raw_transcript_path(self, *, meeting_id: str, filename: str) -> Path:
        safe_filename = sanitize_filename(filename)
        return self.raw_meeting_dir(meeting_id) / safe_filename


def sanitize_filename(filename: str) -> str:
    candidate = Path(filename).name.strip()
    candidate = re.sub(r"[^A-Za-z0-9._-]+", "_", candidate)
    candidate = candidate.strip("._")
    return candidate or "transcript.vtt"
