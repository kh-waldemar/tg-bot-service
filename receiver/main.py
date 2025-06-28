from pathlib import Path

from config import bot, settings

from handlers import *


def _ask_code() -> str:
    print("[!] Telegram requires a login code. Enter it below:")
    return input('>>> ')


def _ask_password() -> str:
    return input('[!] Enter 2FA password:\n>>> ')


if __name__ == '__main__':
    session_file = Path(settings.TG_SESSION_NAME).with_suffix('.session')
    if not session_file.exists():
        print(f'[!] Session file {session_file} not found. Run init_session.py first.')
        raise SystemExit(1)

    bot.connect()

    if not bot.is_user_authorized():
        bot.start(
            phone=settings.TG_PHONE_NUMBER,
            code_callback=_ask_code,
            password=_ask_password,
        )
    else:
        print(f'[+] Reusing existing session {session_file}')

    print('Bot is running!')
    bot.run_until_disconnected()
