import hashlib
import json
import os
from pathlib import Path

from redis import Redis

from vidi18n.common.artifacts import artifacts
from vidi18n.common.metrics import redis_now
from vidi18n.common.settings import (
    DATA_ROOT,
    caption_stream,
    job_key,
    metrics_key,
    video_key,
)
from vidi18n.common.workflow import get_job, get_video
from vidi18n.schemas.workflow import CaptionCue, Event


def timestamp(milliseconds: int) -> str:
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{millis:03}"


def render_vtt(cues: list[dict]) -> str:
    output = ["WEBVTT", ""]
    for cue in sorted(cues, key=lambda item: (item["start_ms"], item["segment_id"])):
        output.extend(
            [
                cue["segment_id"],
                f"{timestamp(cue['start_ms'])} --> {timestamp(cue['end_ms'])}",
                cue["text"].replace("-->", "→"),
                "",
            ]
        )
    return "\n".join(output)


def contiguous_frontier(packaged: set[int]) -> int:
    frontier = 0
    while frontier in packaged:
        frontier += 1
    return frontier


def package_chunk(redis: Redis, event: Event):
    video = get_video(redis, event.video_id)
    job = get_job(redis, event.job_id)
    packaged = set(video.get("packaged_chunks", []))
    if event.chunk_index in packaged:
        return

    segments = json.loads(Path(event.input_artifact["path"]).read_text())
    cues = video.get("cues", [])
    existing = {cue["segment_id"] for cue in cues}
    new_cues = []
    for sequence, segment in enumerate(segments):
        identity = (
            f"{event.video_id}:{event.target_language}:{event.chunk_index}:{sequence}:"
            f"{segment['start_ms']}:{segment['end_ms']}:{segment['text']}"
        )
        segment_id = hashlib.sha256(identity.encode()).hexdigest()
        cue = CaptionCue(
            segment_id=segment_id,
            chunk_index=event.chunk_index,
            start_ms=segment["start_ms"],
            end_ms=segment["end_ms"],
            text=segment["text"],
            language=event.target_language,
        ).model_dump()
        if segment_id not in existing:
            cues.append(cue)
            new_cues.append(cue)

    packaged.add(event.chunk_index)
    frontier = contiguous_frontier(packaged)
    video["cues"] = cues
    video["packaged_chunks"] = sorted(packaged)
    video["translated_through_ms"] = min(
        frontier * video["chunk_duration_ms"], video["duration_ms"]
    )
    processor_data = [processor.model_dump() for processor in event.processors]
    video["processors"] = processor_data

    caption_dir = Path(DATA_ROOT) / event.video_id / "captions"
    caption_dir.mkdir(parents=True, exist_ok=True)
    target = caption_dir / f"{event.target_language}.vtt"
    temporary = target.with_suffix(".vtt.tmp")
    vtt = render_vtt(cues)
    temporary.write_text(vtt)
    os.replace(temporary, target)

    complete = len(packaged) == video["total_chunks"]
    if complete:
        final_artifact = artifacts.put(vtt.encode(), ".vtt")
        video["caption_artifact"] = final_artifact
        video["status"] = "completed"
        job.update({"status": "completed", "stage": "completed", "progress": 1.0})
    else:
        job.update(
            {
                "status": "processing",
                "stage": "package",
                "progress": len(packaged) / video["total_chunks"],
            }
        )

    stream = caption_stream(event.video_id, event.target_language)
    event_time, _ = redis_now(redis)
    with redis.pipeline(transaction=True) as pipe:
        pipe.set(video_key(event.video_id), json.dumps(video))
        pipe.set(job_key(event.job_id), json.dumps(job))
        pipe.hset(
            metrics_key(event.job_id),
            "processors",
            json.dumps(processor_data, separators=(",", ":"), sort_keys=True),
        )
        if new_cues:
            pipe.hsetnx(
                metrics_key(event.job_id), "first_caption_at", event_time
            )
        if complete:
            pipe.hsetnx(metrics_key(event.job_id), "completed_at", event_time)
        for cue in new_cues:
            pipe.xadd(stream, {"cue": json.dumps(cue, separators=(",", ":"))})
        pipe.execute()
