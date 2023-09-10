from fastapi import FastAPI
from vidi18n.services.manager.routes.file import router as file_router
from vidi18n.services.manager.routes.video import router as video_router

app = FastAPI()

app.include_router(video_router, prefix="/video", tags=["video"])
app.include_router(file_router, prefix="/file", tags=["file"])
