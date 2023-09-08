from vidi18n.common.redis import consume_queue, get_redis, DOWNLOAD_REQUEST_QUEUE
from vidi18n.services.download.listeners import download_request


def main():
    redis = get_redis()
    consume_queue(redis, DOWNLOAD_REQUEST_QUEUE, download_request)


if __name__ == "__main__":
    main()
