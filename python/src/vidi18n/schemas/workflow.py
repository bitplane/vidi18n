from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    schema_version: int = 1
    job_id: str
    video_id: str
    chunk_id: str | None = None
    chunk_index: int | None = None
    start_ms: int | None = None
    duration_ms: int | None = None
    input_artifact: dict[str, Any] | None = None
    source_language: str = "en"
    target_language: str = "fr"
    created_at: str = Field(default_factory=now)


class CreateVideoRequest(BaseModel):
    url: str
    source_language: str = "en"
    target_language: str = "fr"


class CaptionCue(BaseModel):
    segment_id: str
    chunk_index: int
    start_ms: int
    end_ms: int
    text: str
    language: str
    revision: int = 1
