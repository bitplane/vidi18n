import json
from datetime import datetime, timezone

from redis import Redis

from vidi18n.common.settings import metrics_key


def redis_now(redis: Redis) -> tuple[str, int]:
    seconds, microseconds = redis.time()
    milliseconds = seconds * 1000 + microseconds // 1000
    value = datetime.fromtimestamp(
        milliseconds / 1000, tz=timezone.utc
    ).isoformat()
    return value, milliseconds


def mark_once(redis: Redis, job_id: str, name: str) -> int:
    timestamp, milliseconds = redis_now(redis)
    redis.hsetnx(metrics_key(job_id), name, timestamp)
    return milliseconds


def record_stage(redis: Redis, job_id: str, stage: str, elapsed_ms: int) -> None:
    key = metrics_key(job_id)
    with redis.pipeline(transaction=True) as pipe:
        pipe.hincrby(key, f"stage:{stage}:count", 1)
        pipe.hincrby(key, f"stage:{stage}:total_ms", elapsed_ms)
        pipe.execute()
    redis.eval(
        """
        local current = redis.call('HGET', KEYS[1], ARGV[1])
        if not current or tonumber(ARGV[2]) > tonumber(current) then
            redis.call('HSET', KEYS[1], ARGV[1], ARGV[2])
        end
        """,
        1,
        key,
        f"stage:{stage}:max_ms",
        elapsed_ms,
    )


def public_metrics(redis: Redis, job_id: str, duration_ms: int | None) -> dict:
    raw = redis.hgetall(metrics_key(job_id))
    values = {
        key.decode() if isinstance(key, bytes) else key: (
            value.decode() if isinstance(value, bytes) else value
        )
        for key, value in raw.items()
    }
    result = {
        name: values.get(name)
        for name in (
            "submitted_at",
            "media_ready_at",
            "first_caption_at",
            "completed_at",
        )
    }
    if result["submitted_at"] and result["first_caption_at"]:
        result["first_caption_latency_ms"] = _difference_ms(
            result["submitted_at"], result["first_caption_at"]
        )
    else:
        result["first_caption_latency_ms"] = None
    if result["submitted_at"] and result["completed_at"]:
        elapsed = _difference_ms(result["submitted_at"], result["completed_at"])
        result["processing_elapsed_ms"] = elapsed
        result["realtime_factor"] = (
            round(elapsed / duration_ms, 4) if duration_ms else None
        )
    else:
        result["processing_elapsed_ms"] = None
        result["realtime_factor"] = None

    stages = {}
    for key, value in values.items():
        if not key.startswith("stage:"):
            continue
        _, stage, field = key.split(":", 2)
        stages.setdefault(stage, {})[field] = int(value)
    result["stages"] = stages
    processors = values.get("processors")
    result["processors"] = json.loads(processors) if processors else []
    return result


def _difference_ms(start: str, end: str) -> int:
    return round(
        (
            datetime.fromisoformat(end) - datetime.fromisoformat(start)
        ).total_seconds()
        * 1000
    )
