from vidi18n.common.settings import STREAM_TRANSCRIBE
from vidi18n.common.workflow import run_worker
from vidi18n.services.transcribe.listeners import transcribe_chunk


def main():
    run_worker(STREAM_TRANSCRIBE, "transcribe", transcribe_chunk)


if __name__ == "__main__":
    main()
