import json
import logging
import os
import socket
import time
from typing import Callable

from redis import Redis
from redis.exceptions import ResponseError

from vidi18n.common.redis import get_redis
from vidi18n.common.metrics import record_stage
from vidi18n.common.settings import MAX_ATTEMPTS, job_key, video_key, worker_key
from vidi18n.schemas.workflow import Event

logger = logging.getLogger(__name__)


def load_json(redis: Redis, key: str) -> dict | None:
    value = redis.get(key)
    return json.loads(value) if value else None


def save_json(redis: Redis, key: str, value: dict) -> None:
    redis.set(key, json.dumps(value, separators=(",", ":"), sort_keys=True))


def transition(redis: Redis, state_key: str, state: dict, stream: str, event: Event):
    payload = event.model_dump_json()
    with redis.pipeline(transaction=True) as pipe:
        pipe.set(state_key, json.dumps(state, separators=(",", ":"), sort_keys=True))
        pipe.xadd(stream, {"event": payload})
        return pipe.execute()[1]


def enqueue(redis: Redis, stream: str, event: Event):
    return redis.xadd(stream, {"event": event.model_dump_json()})


def ensure_group(redis: Redis, stream: str, group: str):
    try:
        redis.xgroup_create(stream, group, id="0-0", mkstream=True)
    except ResponseError as error:
        if "BUSYGROUP" not in str(error):
            raise


def run_worker(
    stream: str,
    group: str,
    handler: Callable[[Redis, Event], None],
    *,
    redis: Redis | None = None,
    readiness: dict | None = None,
):
    redis = redis or get_redis()
    ensure_group(redis, stream, group)
    consumer = f"{socket.gethostname()}-{os.getpid()}"

    while True:
        if readiness is not None:
            redis.set(
                worker_key(group),
                json.dumps({"consumer": consumer, **readiness}),
                ex=60,
            )
        messages = redis.xreadgroup(
            group,
            consumer,
            {stream: ">"},
            count=1,
            block=5000,
        )
        if not messages:
            continue
        for _, entries in messages:
            for message_id, values in entries:
                event = None
                try:
                    event = Event.model_validate_json(values[b"event"])
                    started = time.monotonic()
                    handler(redis, event)
                    record_stage(
                        redis,
                        event.job_id,
                        group,
                        round((time.monotonic() - started) * 1000),
                    )
                    redis.xack(stream, group, message_id)
                except Exception as error:
                    logger.exception(
                        "Worker failed handling %s message %s", stream, message_id
                    )
                    attempt_id = event.event_id if event else message_id.decode()
                    attempts = redis.hincrby(
                        f"vidi18n:attempts:{stream}", attempt_id, 1
                    )
                    job = None
                    if event:
                        try:
                            job = load_json(redis, job_key(event.job_id))
                        except Exception:
                            pass
                    if job is not None:
                        job["error"] = str(error)
                        job["attempts"] = attempts
                        job["status"] = (
                            "failed" if attempts >= MAX_ATTEMPTS else "retryable"
                        )
                        save_json(redis, job_key(event.job_id), job)
                        if attempts >= MAX_ATTEMPTS:
                            video = get_video(redis, event.video_id)
                            video["status"] = "failed"
                            video["error"] = str(error)
                            save_json(redis, video_key(event.video_id), video)
                    if attempts >= MAX_ATTEMPTS:
                        redis.xack(stream, group, message_id)
                    else:
                        time.sleep(min(attempts, 5))
                        redis.xadd(stream, values)
                        redis.xack(stream, group, message_id)


def get_video(redis: Redis, video_id: str) -> dict:
    return load_json(redis, video_key(video_id)) or {}


def get_job(redis: Redis, job_id: str) -> dict:
    return load_json(redis, job_key(job_id)) or {}
