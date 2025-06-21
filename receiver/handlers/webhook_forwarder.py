from datetime import date, datetime

from pathlib import Path

from telethon import events
from telethon.utils import pack_bot_file_id

from api_driver import GatewayAPIDriver
from config import bot, settings



MEDIA_DIR = Path(__file__).resolve().parents[1] / 'media'


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
        media_url = f"{settings.PUBLIC_BASE_URL.rstrip('/')}/media/{filename}"

        media = {"type": media_type, "file_id": file_id}

    message_dict = {
        "message_id": msg.id,
        "chat": {"id": event.chat_id},
        "date": msg.date.isoformat(),
        "text": msg.message,
        "media": media,
        "media_url": media_url,
        "from": user_info,
    }

    payload = {
        "account_phone_number": settings.TG_PHONE_NUMBER,
        "message": message_dict,
    }

    await GatewayAPIDriver.send_to_webhook(payload)
