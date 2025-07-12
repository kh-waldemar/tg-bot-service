from datetime import date, datetime
from urllib.parse import urlparse

from pathlib import Path

from telethon import events
from telethon.utils import pack_bot_file_id

from api_driver import GatewayAPIDriver
from config import bot, settings


MEDIA_DIR = Path(__file__).resolve().parents[1] / 'media'


def _build_media_url(filename: str) -> str:
    """Return public URL for a downloaded media file."""
    parsed = urlparse(settings.PUBLIC_BASE_URL)
    scheme = parsed.scheme or "http"
    port = settings.PUBLIC_MEDIA_PORT
    include_port = not (
        (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    )
    if include_port:
        return f"{scheme}://{settings.PUBLIC_MEDIA_HOST}:{port}/media/{filename}"
    return f"{scheme}://{settings.PUBLIC_MEDIA_HOST}/media/{filename}"


@bot.on(events.NewMessage)
async def forward_all_messages(event) -> None:
    """Forward every incoming message to the configured webhook."""
    if event.out:
        return

    sender = await event.get_sender()

    user_info = {
        "id": sender.id,
        "first_name": sender.first_name,
        "last_name": sender.last_name,
        "username": sender.username,
        "language_code": getattr(sender, "lang_code", None),
        "phone_number": getattr(sender, "phone", None),
    }

    msg = event.message

    media = None
    media_url = None
    if msg.media:
        media_type = None
        if msg.voice:
            media_type = "voice"
        elif msg.video:
            media_type = "video"
        elif msg.photo:
            media_type = "photo"
        elif msg.document:
            media_type = "document"
        else:
            media_type = msg.media.__class__.__name__.lower()

        try:
            file_id = pack_bot_file_id(msg.media)
        except Exception:
            file_id = None

        ext = msg.file.ext or '.bin'
        if not ext.startswith('.'):
            ext = '.' + ext
        filename = f"{msg.id}_{media_type}{ext}"
        MEDIA_DIR.mkdir(exist_ok=True)
        await msg.download_media(file=MEDIA_DIR / filename)
        media_url = _build_media_url(filename)

        media = {"type": media_type, "file_id": file_id}

    reply_to_message = None
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        reply_sender = await reply_msg.get_sender()

        r_media_type = None
        r_media_url = None
        if reply_msg.media:
            if reply_msg.voice:
                r_media_type = "voice"
            elif reply_msg.video:
                r_media_type = "video"
            elif reply_msg.photo:
                r_media_type = "photo"
            elif reply_msg.document:
                r_media_type = "document"
            else:
                r_media_type = reply_msg.media.__class__.__name__.lower()

            ext = reply_msg.file.ext or '.bin'
            if not ext.startswith('.'):
                ext = '.' + ext
            filename = f"{reply_msg.id}_{r_media_type}{ext}"
            MEDIA_DIR.mkdir(exist_ok=True)
            await reply_msg.download_media(file=MEDIA_DIR / filename)
            r_media_url = _build_media_url(filename)

        reply_to_message = {
            "message_id": reply_msg.id,
            "text": reply_msg.message,
            "media_url": r_media_url,
            "media_type": r_media_type,
            "sender_id": reply_sender.id,
            "sender_name": reply_sender.first_name,
            "date": reply_msg.date.isoformat(),
        }

    message_dict = {
        "message_id": msg.id,
        "chat": {"id": event.chat_id},
        "date": msg.date.isoformat(),
        "text": msg.message,
        "media": media,
        "media_url": media_url,
        "from": user_info,
        "reply_to_message": reply_to_message,
    }

    payload = {
        "account_phone_number": settings.TG_PHONE_NUMBER,
        "message": message_dict,
    }

    await GatewayAPIDriver.send_to_webhook(payload)
