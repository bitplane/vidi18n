import json
from pathlib import Path

from redis import Redis

from vidi18n.common.artifacts import artifacts
from vidi18n.common.settings import PROCESSOR_MODE, STREAM_PACKAGE
from vidi18n.common.workflow import enqueue
from vidi18n.schemas.workflow import Event


def translate_chunk(redis: Redis, event: Event):
    segments = json.loads(Path(event.input_artifact["path"]).read_text())
    if PROCESSOR_MODE == "local":
        import argostranslate.translate

        for segment in segments:
            segment["text"] = argostranslate.translate.translate(
                segment["text"], event.source_language, event.target_language
            )
    else:
        for segment in segments:
            segment["text"] = f"Bonjour du segment {event.chunk_index}."

    artifact = artifacts.put(
        json.dumps(segments, sort_keys=True).encode(), ".translation.json"
    )
    enqueue(
        redis,
        STREAM_PACKAGE,
        Event(
            event_type="translation.chunk.completed",
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
