from uvicorn import run
from vidi18n.common.redis import DOWNLOAD_RESPONSE_QUEUE, queue_worker

from .listeners import download_response


def main():
    queue_worker(DOWNLOAD_RESPONSE_QUEUE, download_response)

    run("vidi18n.services.manager:app", host="0.0.0.0", port=8081, reload=True)


if __name__ == "__main__":
    main()
