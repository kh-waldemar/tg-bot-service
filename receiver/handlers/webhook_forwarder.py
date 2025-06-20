from telethon import events

from api_driver import GatewayAPIDriver
from config import bot, settings


@bot.on(events.NewMessage)
async def forward_all_messages(event) -> None:
    if event.out:
        return

    payload = event.message.to_dict()
    payload['phone_number'] = settings.TG_PHONE_NUMBER

    await GatewayAPIDriver.send_to_webhook(payload)
