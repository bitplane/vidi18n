from vidi18n.common.redis import DOWNLOAD_REQUEST_QUEUE, consume_queue, get_redis
from vidi18n.services.download.listeners import download_request


def main():
    redis = get_redis()
    consume_queue(redis, DOWNLOAD_REQUEST_QUEUE, download_request)


if __name__ == "__main__":
    main()
