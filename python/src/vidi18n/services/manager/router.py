from fastapi import HTTPException
from fastapi.routing import APIRouter
from vidi18n.services.manager.schemas import GetVideoByUrlRequest, VideoDetails
from vidi18n.common.redis import get_redis
from vidi18n.common.cache import get_cache_name


router = APIRouter()


@router.post("/video/", response_model=VideoDetails)
async def get_video_by_url(request: GetVideoByUrlRequest):
    cache = get_cache_name(request.url)

    redis = get_redis()
    if redis.exists(cache):
        data = redis.get(cache)
        return VideoDetails.model_validate_json(data.decode("utf-8"))

    raise HTTPException(status_code=404, detail="Video not found")
