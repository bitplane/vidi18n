import json
from importlib.metadata import version
from pathlib import Path

from redis import Redis

from vidi18n.common.artifacts import artifacts
from vidi18n.common.settings import PROCESSOR_MODE, STREAM_PACKAGE
from vidi18n.common.workflow import enqueue
from vidi18n.schemas.workflow import Event, ProcessorRef


class DeterministicTranslator:
    provenance = ProcessorRef(
        stage="translate",
        engine="vidi18n-deterministic",
        engine_version="1",
        mode="deterministic",
        model="fixture-en-fr",
    )

    def translate(self, text: str) -> str:
        return text


class ArgosTranslator:
    def __init__(self):
        import argostranslate.package
        import argostranslate.translate

        installed = argostranslate.translate.get_installed_languages()
        source = next(language for language in installed if language.code == "en")
        target = next(language for language in installed if language.code == "fr")
        self.translation = source.get_translation(target)
        package = next(
            item
            for item in argostranslate.package.get_installed_packages()
            if item.from_code == "en" and item.to_code == "fr"
        )
        self.provenance = ProcessorRef(
            stage="translate",
            engine="argostranslate",
            engine_version=version("argostranslate"),
            mode="local",
            model=f"translate-en_fr-{package.package_version}",
        )

    def translate(self, text: str) -> str:
        return self.translation.translate(text)


def create_translator():
    return ArgosTranslator() if PROCESSOR_MODE == "local" else DeterministicTranslator()


def translate_chunk(redis: Redis, event: Event, processor=None):
    processor = processor or create_translator()
    segments = json.loads(Path(event.input_artifact["path"]).read_text())
    if PROCESSOR_MODE == "local":
        for segment in segments:
            segment["text"] = processor.translate(segment["text"])
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
            processors=[*event.processors, processor.provenance],
        ),
    )
