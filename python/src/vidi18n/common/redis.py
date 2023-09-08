import os
from redis import Redis
from functools import partial

from threading import Thread


REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))


DOWNLOAD_REQUEST_QUEUE = "download:request"
DOWNLOAD_RESPONSE_QUEUE = "download:request"


def get_redis():
    return Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


def consume_queue(redis: Redis, queues, callback):
    """
    Calls callback(redis, queue_name, message), consuming messages until
    callback returns False.
    """
    keep_processing = True
    while keep_processing:
        queue, message = redis.blpop(queues)
        callback(redis, queue, message)


def queue_worker(queue_pattern, callback):
    """
    Calls callback(redis, queue_name, message) in a new thread, consuming
    messages until callback returns False.
    """
    redis = get_redis()

    consume = partial(consume_queue, redis, queue_pattern, callback)

    thread = Thread(target=consume)
    return thread.start()
