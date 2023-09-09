from fastapi import HTTPException
from fastapi.routing import APIRouter
from vidi18n.common.cache import get_cache_key
from vidi18n.common.redis import get_redis
from vidi18n.schemas.video import Video
from vidi18n.services.manager.schemas import GetVideoByUrlRequest

router = APIRouter()
redis = get_redis()


@router.post("/video/", response_model=Video)
async def get_video_by_url(request: GetVideoByUrlRequest):
    uid = get_cache_key(request.url)
    video = Video.load(uid=uid)

    if not video:
        video = Video(uid=uid, url=request.url)
        video.save(redis=redis)

    return video


@router.get("/video/{uid}", response_model=Video)
async def get_video_by_url(uid: str):
    video = Video.load(uid=uid)

    if video:
        return video

    raise HTTPException(status_code=404, detail="Video not found")
