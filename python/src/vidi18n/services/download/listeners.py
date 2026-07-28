import ipaddress
import json
import math
import os
import socket
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from redis import Redis

from vidi18n.common.artifacts import artifacts
from vidi18n.common.metrics import mark_once
from vidi18n.common.settings import CHUNK_SECONDS, STREAM_TRANSCRIBE, job_key, video_key
from vidi18n.common.workflow import enqueue, get_job, get_video, save_json
from vidi18n.schemas.workflow import Event


def validate_remote_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Only HTTP(S) video URLs are supported")
    if os.environ.get("VIDI18N_ALLOW_PRIVATE_URLS") == "1":
        return
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    for result in socket.getaddrinfo(parsed.hostname, port):
        address = ipaddress.ip_address(result[4][0])
        if (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_reserved
        ):
            raise ValueError("Private and local media addresses are not allowed")


def resolve_source(url: str) -> dict:
    validate_remote_url(url)
    command = [
        "python",
        "-m",
        "yt_dlp",
        "--dump-single-json",
        "--no-playlist",
        "--no-warnings",
        "--format",
        "best[acodec!=none][vcodec!=none]/best",
        url,
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "yt-dlp failed")
    info = json.loads(result.stdout)
    requested = info.get("requested_downloads") or []
    selected = next(
        (item for item in requested if item.get("vcodec") != "none"),
        requested[0] if requested else info,
    )
    media_url = selected.get("url") or info.get("url")
    if not media_url:
        raise ValueError("No playable media format was found")
    validate_remote_url(media_url)
    return {
        "url": media_url,
        "headers": selected.get("http_headers") or info.get("http_headers") or {},
        "duration_ms": (
            int(float(info["duration"]) * 1000) if info.get("duration") else None
        ),
        "title": info.get("title") or info.get("fulltitle"),
        "extractor": info.get("extractor_key"),
        "format_id": selected.get("format_id"),
    }


def ffmpeg_headers(headers: dict) -> str:
    return "".join(f"{name}: {value}\r\n" for name, value in headers.items())


def probe_duration_ms(url: str, headers: dict) -> int:
    command = ["ffprobe", "-v", "error"]
    if headers:
        command.extend(["-headers", ffmpeg_headers(headers)])
    command.extend(
        [
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            url,
        ]
    )
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "FFprobe failed")
    return int(float(result.stdout.strip()) * 1000)


def download_requested(redis: Redis, event: Event):
    video = get_video(redis, event.video_id)
    if video.get("download_complete"):
        return
    job = get_job(redis, event.job_id)
    source = resolve_source(video["url"])
    duration_ms = source["duration_ms"] or probe_duration_ms(
        source["url"], source["headers"]
    )
    source["duration_ms"] = duration_ms
    total_chunks = math.ceil(duration_ms / (CHUNK_SECONDS * 1000))

    video.update(
        {
            "resolved_source": source,
            "duration_ms": duration_ms,
            "chunk_duration_ms": CHUNK_SECONDS * 1000,
            "total_chunks": total_chunks,
            "status": "processing",
        }
    )
    job.update(
        {
            "status": "processing",
            "stage": "download",
            "total_chunks": total_chunks,
            "completed_chunks": 0,
        }
    )
    save_json(redis, video_key(event.video_id), video)
    save_json(redis, job_key(event.job_id), job)
    mark_once(redis, event.job_id, "media_ready_at")

    with tempfile.TemporaryDirectory(dir=artifacts.root) as temporary:
        for index in range(total_chunks):
            start_ms = index * CHUNK_SECONDS * 1000
            duration = min(CHUNK_SECONDS * 1000, duration_ms - start_ms)
            output = Path(temporary) / f"{index:08}.wav"
            command = ["ffmpeg", "-nostdin", "-loglevel", "error"]
            if source["headers"]:
                command.extend(["-headers", ffmpeg_headers(source["headers"])])
            command.extend(
                [
                    "-ss",
                    str(start_ms / 1000),
                    "-i",
                    source["url"],
                    "-t",
                    str(duration / 1000),
                    "-vn",
                    "-ac",
                    "1",
                    "-ar",
                    "16000",
                    "-c:a",
                    "pcm_s16le",
                    "-y",
                    str(output),
                ]
            )
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(result.stderr.strip() or "FFmpeg failed")
            artifact = artifacts.put_file(str(output), ".wav")
            enqueue(
                redis,
                STREAM_TRANSCRIBE,
                Event(
                    event_type="audio.chunk.ready",
                    job_id=event.job_id,
                    video_id=event.video_id,
                    chunk_id=f"{event.job_id}:{index}",
                    chunk_index=index,
                    start_ms=start_ms,
                    duration_ms=duration,
                    input_artifact=artifact,
                    source_language=event.source_language,
                    target_language=event.target_language,
                ),
            )
            job = get_job(redis, event.job_id)
            job.setdefault("stages", {})["download"] = (index + 1) / total_chunks
            job["completed_chunks"] = index + 1
            save_json(redis, job_key(event.job_id), job)
    video = get_video(redis, event.video_id)
    video["download_complete"] = True
    save_json(redis, video_key(event.video_id), video)
