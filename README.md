# Telegram Bot Microservice
Basis for extendable, high-performance Telegram Bot microservice.


## Tech Stack
- FastAPI
- Telethon
- AsyncIO
- Docker & docker-compose


## Features

### Receiver Service
- Updates Receiver [Telethon / MTProto] - receive updates on any action made by user directed to Telegram Bot/Account. Similar to Webhook Server or Long Polling, but faster and more stable due to use of MTProto protocol which is Telegram Native. [More on this topic](https://docs.telethon.dev/en/latest/concepts/botapi-vs-mtproto.html#advantages-of-mtproto-over-bot-api).
- Basic event handler - currently to stay as generic as possible service implements basic conversation. Functionality can be extended by adding new handlers.
- Async API Driver [HTTPX] - HTTP/REST API Driver to interact with other services.
- Logger for API Driver [Native Python Logger] - to monitor and log each request and response. Additionally, keeps logs in files to use with monitoring tools, such as ELK, Prometheus+Grafana, etc.

### Sender Service
- REST API built with FastAPI. Methods mimic the [Telegram Bot API](https://core.telegram.org/bots/api):
    * `POST /api_v1/sendMessage`
    * `POST /api_v1/sendPhoto`
    * `POST /api_v1/sendDocument`
    * `POST /api_v1/sendAudio`
    * `POST /api_v1/sendVoice`
    * `POST /api_v1/sendVideo`
    * `POST /api_v1/editMessageText`
    * `POST /api_v1/deleteMessage`
- Each request must include `x-api-key` header matching `X_API_TOKEN` from `.env`.
- Sender uses Telethon to act as a user account.


## Whole Service Workflow
As it can be understood, this microservice is not "killer-beast" and is not suitable for all use-cases. It is mostly oriented for offload, high-speed interaction with users through Telegram.

Ideal workflow of service is following:
- user sends update to Telegram Bot/Account, which is received by specific event handler of **Receiver**
- event handler processes received data, adjusts it if needed and sends this data to **Other Microservice** through **API Driver**, note that you can implement as many API Drivers as you need to interact with your services.
- **Other Microservice** processes and executes its own business logic and sends result of processing to **API**.
- **API** receives the data from other service and transfers it Telegram through **Sender**, which is Telegram Client provided by Telethon.

Thus, we have fully autonomous, loosely-coupled microservice.

### Workflow Scheme

![workflow_scheme](diagrams/architecture.jpg)


## How to Use

Root directory has docker-compose file through which whole microservice can be started. But firstly, build images:
```shell
docker-compose build
```
The Dockerfiles run `poetry install` during build and automatically generate `poetry.lock` inside the containers. This prevents errors about a missing or outdated lock file when you clone the repository.
And start up services:
```shell
docker-compose up
```

The receiver will serve downloaded files on `http://<PUBLIC_MEDIA_HOST>:<PUBLIC_MEDIA_PORT>/media`. Media links in webhook payloads are generated automatically using these variables.

### Configuration

1.  Copy `.env.example` to `.env`, populate your Telegram API credentials, session name, phone number, webhook information and public domain settings (`PUBLIC_MEDIA_HOST`, `PUBLIC_MEDIA_PORT`). Keep the file in the repository root next to `docker-compose.yml`.
2.  Create an empty `sessions/` directory next to the compose file. Docker Compose mounts this path into both services so they share one Telethon session.
   In your `.env` set `TG_SESSION_NAME=/sessions/tg_userbot` (or any name inside `/sessions`).
3.  Ensure the `userbot_media` directory exists. Docker Compose mounts this path
   into both services so that downloaded files persist and can be served over HTTP
   at `http://<PUBLIC_MEDIA_HOST>:<PUBLIC_MEDIA_PORT>/media/<filename>`.
4.  Docker Compose loads the `.env` file automatically for both services (see
   `env_file` in `docker-compose.yml`).
5.  Set `X_API_TOKEN` in `.env` and include this token in the `x-api-key` header when calling the sender API.
6.  You can pre-create a session by running `python init_session.py` once
    outside of Docker.  The script reads credentials from `.env` and always
    stores the session file inside `sessions/` in the repository so it will be
    mounted into the containers.  Any absolute `/sessions/<name>` path from the
    environment is rewritten automatically to this local directory.
7.  Start the services with `docker-compose up`. If the session file is missing
    the receiver will prompt for the login code and create it automatically on
    the first run.
8.  Ensure `TG_API_ID` and `TG_API_HASH` are taken from a **user** application created on [my.telegram.org](https://my.telegram.org) and not from a bot. Otherwise login will fail.
9.  During image build the latest Telethon is installed automatically. If you build images manually, update Telethon with `pip install -U telethon`.

10.  Media files are served directly by the receiver service on port `8181`, making
    any downloaded files reachable as
    `http://<PUBLIC_MEDIA_HOST>:<PUBLIC_MEDIA_PORT>/media/<filename>` without any
    extra web server.

### Viewing incoming messages

The receiver prints every message it receives to STDOUT. When running via
Docker Compose you can follow the output with:

```shell
docker-compose logs -f receiver
```

This works even if no webhook is configured and helps to verify that the bot is
receiving events.

Use the **sender** service endpoints to send messages from your server to Telegram.

**Sender** service API can be found on http://0.0.0.0:8001 and docs on http://0.0.0.0:8001/docs

### Example webhook payload

When a user replies to a message, the receiver forwards the update to the configured webhook with the following structure:

```json
{
  "account_phone_number": "+10000000000",
  "message": {
    "message_id": 2345,
    "chat": {"id": 1111111},
    "date": "2023-01-01T12:00:00",
    "text": "Це відповідь",
    "media": null,
    "media_url": null,
    "from": {
      "id": 777000,
      "first_name": "User",
      "last_name": null,
      "username": "user",
      "language_code": "en",
      "phone_number": null
    },
    "reply_to_message": {
      "message_id": 1234,
      "text": "Оригінальне повідомлення",
      "media_url": "http://example.com:8181/media/1234_photo.jpg",
      "media_type": "photo",
      "sender_id": 1111111,
      "sender_name": "Other",
      "date": "2023-01-01T11:59:00"
    }
  }
}
```


## Enhancement, contribution, and feedback
Any feedback or contribution to the project is eagerly welcomed. Just create an issue or contact me on ki.xbozz@gmail.com.


## Recommended for reading:
- https://docs.telethon.dev/en/latest/quick-references/faq.html


## Todo:
- [ ] logging for FastAPI
- [ ] logging for Telethon event handlers
