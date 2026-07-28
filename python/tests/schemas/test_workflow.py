from vidi18n.schemas.workflow import CaptionCue, Event, ProcessorRef


def test_event_round_trip():
    event = Event(
        event_type="audio.chunk.ready",
        job_id="job",
        video_id="video",
        chunk_id="job:0",
        chunk_index=0,
        start_ms=0,
        duration_ms=10_000,
    )
    restored = Event.model_validate_json(event.model_dump_json())
    assert restored == event
    assert restored.schema_version == 1


def test_caption_cue_defaults_to_first_revision():
    cue = CaptionCue(
        segment_id="segment",
        chunk_index=0,
        start_ms=0,
        end_ms=1000,
        text="Bonjour",
        language="fr",
    )
    assert cue.revision == 1


def test_event_carries_processor_provenance():
    processor = ProcessorRef(
        stage="transcribe",
        engine="faster-whisper",
        engine_version="1.2.0",
        mode="local",
        model="tiny.en",
        compute_type="int8",
    )
    event = Event(
        event_type="transcription.chunk.completed",
        job_id="job",
        video_id="video",
        processors=[processor],
    )

    restored = Event.model_validate_json(event.model_dump_json())

    assert restored.processors == [processor]
