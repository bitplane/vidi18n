import asyncio
import json
from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.routing import APIRouter

from vidi18n.common.cache import get_cache_key
from vidi18n.common.redis import get_redis
from vidi18n.common.settings import (
    DATA_ROOT,
    STREAM_DOWNLOAD,
    caption_stream,
    job_key,
    video_key,
)
from vidi18n.common.workflow import load_json
from vidi18n.schemas.workflow import CreateVideoRequest, Event, now

router = APIRouter()
redis = get_redis()


def public_video(video: dict, job: dict) -> dict:
    video_id = video["video_id"]
    language = video["target_language"]
    return {
        **video,
        "job": job,
        "media_url": f"/api/video/{video_id}/media",
        "caption_events_url": f"/api/video/{video_id}/captions/{language}/events",
        "caption_url": f"/api/video/{video_id}/captions/{language}.vtt",
    }


@router.post("/", status_code=202)
async def create_video(request: CreateVideoRequest):
    if request.source_language != "en" or request.target_language != "fr":
        raise HTTPException(
            status_code=422, detail="The first slice supports en to fr only"
        )

    video_id = get_cache_key(f"{request.url}|{request.target_language}")
    existing = load_json(redis, video_key(video_id))
    if existing:
        job = load_json(redis, job_key(existing["job_id"])) or {}
        return public_video(existing, job)

    job_id = str(uuid4())
    video = {
        "video_id": video_id,
        "job_id": job_id,
        "url": request.url,
        "source_language": request.source_language,
        "target_language": request.target_language,
        "status": "requested",
        "translated_through_ms": 0,
        "created_at": now(),
    }
    job = {
        "job_id": job_id,
        "video_id": video_id,
        "status": "requested",
        "stage": "download",
        "progress": 0.0,
        "attempts": 0,
        "error": None,
        "created_at": now(),
    }
    event = Event(
        event_type="video.download.requested",
        job_id=job_id,
        video_id=video_id,
        source_language=request.source_language,
        target_language=request.target_language,
    )
    with redis.pipeline(transaction=True) as pipe:
        pipe.set(video_key(video_id), json.dumps(video))
        pipe.set(job_key(job_id), json.dumps(job))
        pipe.xadd(STREAM_DOWNLOAD, {"event": event.model_dump_json()})
        pipe.execute()
    return public_video(video, job)


@router.get("/{video_id}")
async def get_video(video_id: str):
    video = load_json(redis, video_key(video_id))
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    job = load_json(redis, job_key(video["job_id"])) or {}
    return public_video(video, job)


@router.get("/{video_id}/media")
async def proxy_media(video_id: str, request: Request):
    video = load_json(redis, video_key(video_id))
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    source = video.get("resolved_source")
    if not source:
        raise HTTPException(status_code=425, detail="Media source is not ready")

    headers = dict(source.get("headers", {}))
    if request.headers.get("range"):
        headers["Range"] = request.headers["range"]
    client = httpx.AsyncClient(follow_redirects=False, timeout=None)
    upstream_request = client.build_request("GET", source["url"], headers=headers)
    upstream = await client.send(upstream_request, stream=True)
    if upstream.status_code not in (200, 206):
        await upstream.aclose()
        await client.aclose()
        raise HTTPException(status_code=502, detail="Upstream media request failed")

    response_headers = {}
    for name in ("accept-ranges", "content-range", "content-length", "content-type"):
        if name in upstream.headers:
            response_headers[name] = upstream.headers[name]

    async def body():
        try:
            async for chunk in upstream.aiter_bytes():
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    return StreamingResponse(
        body(),
        status_code=upstream.status_code,
        headers=response_headers,
        media_type=upstream.headers.get("content-type"),
    )


@router.get("/{video_id}/captions/{language}/events")
async def caption_events(video_id: str, language: str, request: Request):
    if not load_json(redis, video_key(video_id)):
        raise HTTPException(status_code=404, detail="Video not found")
    stream = caption_stream(video_id, language)
    last_id = request.headers.get("last-event-id", "0-0")

    async def events():
        cursor = last_id
        while not await request.is_disconnected():
            result = await asyncio.to_thread(
                redis.xread, {stream: cursor}, count=100, block=15000
            )
            if not result:
                video = load_json(redis, video_key(video_id)) or {}
                if video.get("status") == "failed":
                    error = json.dumps({"error": video.get("error", "Job failed")})
                    yield f"event: error\ndata: {error}\n\n"
                    return
                yield ": heartbeat\n\n"
                continue
            for _, entries in result:
                for message_id, values in entries:
                    cursor = message_id.decode()
                    data = values[b"cue"].decode()
                    yield f"id: {cursor}\nevent: cue\ndata: {data}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{video_id}/captions/{language}.vtt")
async def captions(video_id: str, language: str):
    path = Path(DATA_ROOT) / video_id / "captions" / f"{language}.vtt"
    if not path.exists():
        raise HTTPException(status_code=425, detail="Captions are not ready")
    video = load_json(redis, video_key(video_id)) or {}
    return FileResponse(
        path,
        media_type="text/vtt",
        headers={
            "Cache-Control": (
                "public, max-age=31536000, immutable"
                if video.get("status") == "completed"
                else "no-store"
            )
        },
    )
