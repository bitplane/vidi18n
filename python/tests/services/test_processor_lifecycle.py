from vidi18n.schemas.workflow import Event, ProcessorRef


class Processor:
    provenance = ProcessorRef(
        stage="transcribe",
        engine="test",
        engine_version="1",
        mode="local",
        model="test",
    )


def event():
    return Event(event_type="test", job_id="job", video_id="video")


def test_transcribe_main_reuses_processor(monkeypatch):
    from vidi18n.services.transcribe import __main__ as service

    processor = Processor()
    seen = []
    monkeypatch.setattr(service, "create_transcriber", lambda: processor)
    monkeypatch.setattr(
        service,
        "transcribe_chunk",
        lambda redis, item, current: seen.append(current),
    )

    def run_worker(stream, group, handler, readiness):
        handler(None, event())
        handler(None, event())

    monkeypatch.setattr(service, "run_worker", run_worker)
    service.main()
    assert seen == [processor, processor]


def test_translate_main_reuses_processor(monkeypatch):
    from vidi18n.services.translate import __main__ as service

    processor = Processor()
    seen = []
    monkeypatch.setattr(service, "create_translator", lambda: processor)
    monkeypatch.setattr(
        service,
        "translate_chunk",
        lambda redis, item, current: seen.append(current),
    )

    def run_worker(stream, group, handler, readiness):
        handler(None, event())
        handler(None, event())

    monkeypatch.setattr(service, "run_worker", run_worker)
    service.main()
    assert seen == [processor, processor]
