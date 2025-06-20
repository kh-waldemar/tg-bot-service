from datetime import date, datetime

from telethon import events

from api_driver import GatewayAPIDriver
from config import bot, settings


@bot.on(events.NewMessage)
async def forward_all_messages(event) -> None:
    if event.out:
        return

    payload = event.message.to_dict()
    payload['phone_number'] = settings.TG_PHONE_NUMBER

    def _convert(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert(v) for v in obj]
        return obj

    payload = _convert(payload)

    await GatewayAPIDriver.send_to_webhook(payload)
