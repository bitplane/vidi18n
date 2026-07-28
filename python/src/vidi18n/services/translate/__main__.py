from vidi18n.common.settings import STREAM_TRANSLATE
from vidi18n.common.workflow import run_worker
from vidi18n.services.translate.listeners import create_translator, translate_chunk


def main():
    processor = create_translator()
    run_worker(
        STREAM_TRANSLATE,
        "translate",
        lambda redis, event: translate_chunk(redis, event, processor),
        readiness={"status": "ready", "processor": processor.provenance.model_dump()},
    )


if __name__ == "__main__":
    main()
