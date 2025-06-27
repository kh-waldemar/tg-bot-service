import logging
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = 'tg-bot-service-receiver'

    TG_API_ID: int = 0
    TG_API_HASH: str = 'tg-api-hash'
    TG_SESSION_NAME: str = 'tg_session_receiver'
    TG_PHONE_NUMBER: str = '+10000000000'

    WEBHOOK_URL: str = 'https://some.host/webhook'
    WEBHOOK_API_KEY: str = 'secret-api-key'
    PUBLIC_BASE_URL: str = 'https://example.com'
    PUBLIC_MEDIA_HOST: str = 'userbot.zhito-systems.work'
    PUBLIC_MEDIA_PORT: int = 8181


    LOGS_DIR: str = 'logs/'

    class GatewayAPIDriverLogger:
        FILENAME: str = 'gateway_api_driver.log'
        MAX_BYTES: int = 5 * (1024 * 1024)
        BACKUP_COUNT: int = 10
        FORMATTER: logging.Formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    class Config:
        env_file = Path(__file__).resolve().parents[2] / '.env'
        case_sensitive = True


settings = Settings()
