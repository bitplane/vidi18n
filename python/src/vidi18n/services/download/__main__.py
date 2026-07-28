from vidi18n.common.settings import STREAM_DOWNLOAD
from vidi18n.common.workflow import run_worker
from vidi18n.services.download.listeners import download_requested


def main():
    run_worker(
        STREAM_DOWNLOAD,
        "download",
        download_requested,
        readiness={"status": "ready"},
    )


if __name__ == "__main__":
    main()
