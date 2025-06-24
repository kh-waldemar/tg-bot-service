import logging
from typing import Optional, Union
from json import JSONDecodeError

import httpx

from config import settings

from .logger import gateway_api_driver_logger_init


class GatewayAPIDriver:
    _webhook_url: str = settings.WEBHOOK_URL
    _api_key: str = settings.WEBHOOK_API_KEY

    logger: logging.Logger = gateway_api_driver_logger_init()

    class LoggerMsgTemplates:
        REQUEST: str = 'REQUEST: url: {url} headers: {headers} body: {body}'
        RESPONSE: str = (
            'RESPONSE: status_code: {status_code} url: {url} headers: {headers} '
            'body: {body} error: {error}'
        )

    @classmethod
    async def send_to_webhook(cls, payload: dict) -> httpx.Response:
        url = cls._webhook_url
        headers = {
            'x-api-key': cls._api_key,
            'Content-Type': 'application/json',
        }

        cls._log_request(url, headers, payload)

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)

        try:
            resp_body = resp.json()
            error = None
        except JSONDecodeError as exc:
            resp_body = None
            error = str(exc)

        cls._log_response(resp.url, resp.status_code, resp.headers, resp_body, error)

        return resp

    @classmethod
    def _log_request(cls, url: str, headers: dict[str, str], body: dict) -> None:
        cls.logger.info(
            msg=cls.LoggerMsgTemplates.REQUEST.format(
                url=url,
                headers=headers,
                body=body,
            )
        )

    @classmethod
    def _log_response(
            cls,
            url: Optional[httpx.URL],
            status_code: int,
            headers: dict[str, str],
            body: Union[None, dict, str] = None,
            error: Optional[str] = None,
    ) -> None:
        cls.logger.info(
            msg=cls.LoggerMsgTemplates.RESPONSE.format(
                url=url,
                status_code=status_code,
                headers=headers,
                body=body,
                error=error,
            )
        )
