import json
import os

from redis import Redis

from vidi18n.common.artifacts import artifacts
from vidi18n.common.settings import PROCESSOR_MODE, STREAM_TRANSLATE
from vidi18n.common.workflow import enqueue
from vidi18n.schemas.workflow import Event


def deterministic_segments(event: Event) -> list[dict]:
    return [
        {
            "start_ms": event.start_ms,
            "end_ms": event.start_ms + event.duration_ms,
            "text": f"Hello from chunk {event.chunk_index}.",
        }
    ]


def local_segments(event: Event) -> list[dict]:
    from faster_whisper import WhisperModel

    model_name = os.environ.get("VIDI18N_WHISPER_MODEL", "tiny.en")
    model_root = os.environ.get("VIDI18N_MODEL_ROOT", "/models")
    model = WhisperModel(model_name, download_root=model_root, device="cpu")
    segments, _ = model.transcribe(
        event.input_artifact["path"],
        language=event.source_language,
        word_timestamps=True,
    )
    return [
        {
            "start_ms": event.start_ms + round(segment.start * 1000),
            "end_ms": event.start_ms + round(segment.end * 1000),
            "text": segment.text.strip(),
        }
        for segment in segments
        if segment.text.strip()
    ]


def transcribe_chunk(redis: Redis, event: Event):
    segments = (
        local_segments(event)
        if PROCESSOR_MODE == "local"
        else deterministic_segments(event)
    )
    artifact = artifacts.put(
        json.dumps(segments, sort_keys=True).encode(), ".transcript.json"
    )
    enqueue(
        redis,
        STREAM_TRANSLATE,
        Event(
            event_type="transcription.chunk.completed",
            job_id=event.job_id,
            video_id=event.video_id,
            chunk_id=event.chunk_id,
            chunk_index=event.chunk_index,
            start_ms=event.start_ms,
            duration_ms=event.duration_ms,
            input_artifact=artifact,
            source_language=event.source_language,
            target_language=event.target_language,
        ),
    )
