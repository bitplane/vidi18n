from uvicorn import run

from .listeners import download_response
from vidi18n.common.redis import queue_worker, DOWNLOAD_RESPONSE_QUEUE


def main():
    queue_worker(DOWNLOAD_RESPONSE_QUEUE, download_response)

    run("vidi18n.services.manager:app", host="0.0.0.0", port=8081, reload=True)


if __name__ == "__main__":
    main()
