from fastapi import FastAPI

from .routes import router as video_router

app = FastAPI()

app.include_router(video_router, prefix="/video", tags=["video"])
