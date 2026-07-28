import json
import os
from importlib.metadata import version

from redis import Redis

from vidi18n.common.artifacts import artifacts
from vidi18n.common.settings import PROCESSOR_MODE, STREAM_TRANSLATE
from vidi18n.common.workflow import enqueue
from vidi18n.schemas.workflow import Event, ProcessorRef


class DeterministicTranscriber:
    provenance = ProcessorRef(
        stage="transcribe",
        engine="vidi18n-deterministic",
        engine_version="1",
        mode="deterministic",
        model="fixture",
    )

    def segments(self, event: Event) -> list[dict]:
        return [
            {
                "start_ms": event.start_ms,
                "end_ms": event.start_ms + event.duration_ms,
                "text": f"Hello from chunk {event.chunk_index}.",
            }
        ]


class WhisperTranscriber:
    def __init__(self):
        from faster_whisper import WhisperModel

        model_name = os.environ.get("VIDI18N_WHISPER_MODEL", "tiny.en")
        model_root = os.environ.get("VIDI18N_MODEL_ROOT", "/models")
        device = os.environ.get("VIDI18N_WHISPER_DEVICE", "cpu")
        compute_type = os.environ.get(
            "VIDI18N_WHISPER_COMPUTE_TYPE",
            "float16" if device == "cuda" else "int8",
        )
        cpu_threads = int(os.environ.get("VIDI18N_WHISPER_CPU_THREADS", "4"))
        self.model = WhisperModel(
            model_name,
            download_root=model_root,
            device=device,
            compute_type=compute_type,
            cpu_threads=cpu_threads,
            local_files_only=True,
        )
        self.provenance = ProcessorRef(
            stage="transcribe",
            engine="faster-whisper",
            engine_version=version("faster-whisper"),
            mode="local",
            model=model_name,
            device=device,
            compute_type=compute_type,
        )

    def segments(self, event: Event) -> list[dict]:
        segments, _ = self.model.transcribe(
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


def create_transcriber():
    return (
        WhisperTranscriber()
        if PROCESSOR_MODE == "local"
        else DeterministicTranscriber()
    )


def transcribe_chunk(redis: Redis, event: Event, processor=None):
    processor = processor or create_transcriber()
    segments = processor.segments(event)
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
            processors=[*event.processors, processor.provenance],
        ),
    )
