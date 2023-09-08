from fastapi import FastAPI

from .router import router as video_router

app = FastAPI()

app.include_router(video_router, prefix="/video", tags=["video"])
