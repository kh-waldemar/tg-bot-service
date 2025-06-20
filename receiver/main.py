from config import bot, settings

from handlers import *


def _ask_code() -> str:
    print("[!] Telegram requires a login code. Enter it below:")
    return input('>>> ')


def _ask_password() -> str:
    return input('[!] Enter 2FA password:\n>>> ')


if __name__ == '__main__':
    bot.start(
        phone=settings.TG_PHONE_NUMBER,
        code_callback=_ask_code,
        password=_ask_password,
    )
    print('Bot is running!')
    bot.run_until_disconnected()
