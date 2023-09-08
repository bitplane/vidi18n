from redis import Redis
from vidi18n.common.cache import get_cache_name


def download_request(redis: Redis, queue, message):
    print(f"Received message on {queue}: {message}")
