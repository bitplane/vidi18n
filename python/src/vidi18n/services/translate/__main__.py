from vidi18n.common.settings import STREAM_TRANSLATE
from vidi18n.common.workflow import run_worker
from vidi18n.services.translate.listeners import translate_chunk


def main():
    run_worker(STREAM_TRANSLATE, "translate", translate_chunk)


if __name__ == "__main__":
    main()
