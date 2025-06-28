from pathlib import Path
import asyncio

from config import bot, settings

from handlers import register_handlers


def _ask_code() -> str:
    """Prompt the user for the login code when Telegram requests it."""
    print("[!] Telegram requires a login code. Enter it below:")
    return input('>>> ')


def _ask_password() -> str:
    """Prompt the user for the 2FA password if enabled."""
    return input('[!] Enter 2FA password:\n>>> ')


async def main() -> None:
    """Start the Telegram client and run until disconnected."""
    session_file = Path(settings.TG_SESSION_NAME).with_suffix('.session')
    if not session_file.exists():
        print(f'[!] Session file {session_file} not found. Run init_session.py first.')
        raise SystemExit(1)

    await bot.start(
        phone=settings.TG_PHONE_NUMBER,
        code_callback=_ask_code,
        password=_ask_password,
    )
    print(f'[+] Using session {session_file}')

    # Import handlers after the client has started to ensure they register
    register_handlers()
    print("Bot is fully running and listening for messages!")

    print('Bot is running!')
    await bot.run_until_disconnected()


if __name__ == '__main__':
    asyncio.run(main())
