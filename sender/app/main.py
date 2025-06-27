from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.v1.api import api_router
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f'{settings.API_V1_STR}/openapi.json',
)

media_path = Path(settings.MEDIA_DIR)
app.mount("/media", StaticFiles(directory=str(media_path), html=False), name="media")

app.include_router(api_router, prefix=settings.API_V1_STR)
