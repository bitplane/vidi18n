from vidi18n.common.cache import get_cache_name
from redis import Redis


def download_response(redis: Redis, queue, message):
    print(f"Received message on {queue}: {message}")
