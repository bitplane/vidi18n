from vidi18n.common.settings import STREAM_TRANSCRIBE
from vidi18n.common.workflow import run_worker
from vidi18n.services.transcribe.listeners import create_transcriber, transcribe_chunk


def main():
    processor = create_transcriber()
    run_worker(
        STREAM_TRANSCRIBE,
        "transcribe",
        lambda redis, event: transcribe_chunk(redis, event, processor),
        readiness={"status": "ready", "processor": processor.provenance.model_dump()},
    )


if __name__ == "__main__":
    main()
