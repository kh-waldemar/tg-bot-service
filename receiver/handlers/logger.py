from telethon import events

from config import bot


@bot.on(events.NewMessage)
async def log_message(event) -> None:
    """Print every incoming message to stdout."""
    if event.out:
        return

    sender = await event.get_sender()
    text = event.raw_text or "<non-text message>"
    print(f"[TG LOG] Message from {sender.id}: {text}")
