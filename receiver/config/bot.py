from telethon import TelegramClient

from .settings import settings

bot = TelegramClient(
    session=settings.TG_SESSION_NAME,
    api_id=settings.TG_API_ID,
    api_hash=settings.TG_API_HASH,
)

# `start` is called explicitly in `receiver/main.py` so that the login prompts
# appear in the container's console when the service launches.
