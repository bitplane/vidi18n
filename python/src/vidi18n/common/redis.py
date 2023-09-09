import os
from functools import partial
from threading import Thread

from redis import Redis

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))


def get_redis():
    return Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


def listen_for_events(redis: Redis, channels, callback):
    """
    Calls callback(redis, channel, message) for each message received on
    the given channels.
    """
    pubsub = redis.pubsub()
    pubsub.subscribe(channels)

    for message in pubsub.listen():
        if message["type"] == "message":
            callback(redis, message["channel"], message["data"])


def queue_worker(subscriptions, callback):
    redis = get_redis()
    listener = partial(listen_for_events, redis, subscriptions, callback)
    thread = Thread(target=listener)

    return thread.start()
