from fastapi import FastAPI
import json

from vidi18n.common.redis import get_redis
from vidi18n.common.settings import worker_key
from vidi18n.services.manager.routes.file import router as file_router
from vidi18n.services.manager.routes.video import router as video_router

app = FastAPI()

app.include_router(video_router, prefix="/video", tags=["video"])
app.include_router(file_router, prefix="/file", tags=["file"])


@app.get("/health")
async def health():
    redis = get_redis()
    workers = {}
    for name in ("download", "transcribe", "translate", "package"):
        value = redis.get(worker_key(name))
        workers[name] = json.loads(value) if value else {"status": "unavailable"}
    ready = all(worker["status"] == "ready" for worker in workers.values())
    return {"status": "ok" if ready else "degraded", "workers": workers}
