from typing import Optional
import base64
import mimetypes
import uuid
from pathlib import Path

import httpx
from fastapi import APIRouter, status, Depends, HTTPException

from app import schemas
from app.api.deps import verify_api_key
from app.config import bot_init, settings

TMP_DIR = Path("/tmp/userbot-api")
TMP_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(dependencies=[Depends(verify_api_key)])


def _serialize_message(msg) -> dict:
    return {
        "message_id": msg.id,
        "chat": {"id": msg.chat_id},
        "date": msg.date.isoformat(),
        "text": msg.text or msg.message,
    }


async def _download_file(src: str) -> Path:
    if src.startswith("http://") or src.startswith("https://"):
        async with httpx.AsyncClient() as client:
            resp = await client.get(src)
            resp.raise_for_status()
            data = resp.content
            ext = mimetypes.guess_extension(resp.headers.get("content-type", "")) or ".bin"
    else:
        if src.startswith("data:") and ";base64," in src:
            header, b64 = src.split(",", 1)
            mime = header[5: header.index(";")]
            ext = mimetypes.guess_extension(mime) or ".bin"
            data = base64.b64decode(b64)
        else:
            data = base64.b64decode(src)
            ext = ".bin"
    filename = TMP_DIR / f"{uuid.uuid4().hex}{ext}"
    filename.write_bytes(data)
    return filename


@router.post("/sendMessage")
async def send_message(payload: schemas.SendMessage):
    async with await bot_init() as bot:
        msg = await bot.send_message(payload.chat_id, payload.text, parse_mode=payload.parse_mode)
    return {"ok": True, "result": _serialize_message(msg)}


async def _send_media(chat_id: int, file_src: str, caption: Optional[str]) -> dict:
    file_path = await _download_file(file_src)
    async with await bot_init() as bot:
        msg = await bot.send_file(chat_id, file_path, caption=caption)
    return _serialize_message(msg) | {
        "file_name": file_path.name,
        "file_url": f"{settings.PUBLIC_BASE_URL}/media/{file_path.name}"
    }


@router.post("/sendPhoto")
async def send_photo(payload: schemas.SendPhoto):
    msg = await _send_media(payload.chat_id, payload.photo, payload.caption)
    msg["file_type"] = "photo"
    return {"ok": True, "result": msg}


@router.post("/sendDocument")
async def send_document(payload: schemas.SendDocument):
    msg = await _send_media(payload.chat_id, payload.document, payload.caption)
    msg["file_type"] = "document"
    return {"ok": True, "result": msg}


@router.post("/sendAudio")
async def send_audio(payload: schemas.SendAudio):
    msg = await _send_media(payload.chat_id, payload.audio, payload.caption)
    msg["file_type"] = "audio"
    return {"ok": True, "result": msg}


@router.post("/sendVoice")
async def send_voice(payload: schemas.SendVoice):
    msg = await _send_media(payload.chat_id, payload.voice, payload.caption)
    msg["file_type"] = "voice"
    return {"ok": True, "result": msg}


@router.post("/sendVideo")
async def send_video(payload: schemas.SendVideo):
    msg = await _send_media(payload.chat_id, payload.video, payload.caption)
    msg["file_type"] = "video"
    return {"ok": True, "result": msg}


@router.post("/editMessageText")
async def edit_message_text(payload: schemas.EditMessageText):
    async with await bot_init() as bot:
        msg = await bot.edit_message(entity=payload.chat_id, message=payload.message_id, text=payload.text, parse_mode=payload.parse_mode)
    return {"ok": True, "result": _serialize_message(msg)}


@router.post("/deleteMessage")
async def delete_message(payload: schemas.DeleteMessage):
    async with await bot_init() as bot:
        await bot.delete_messages(entity=payload.chat_id, message_ids=payload.message_id)
    return {"ok": True, "result": "Message deleted"}
