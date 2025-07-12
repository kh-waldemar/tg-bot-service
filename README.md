# Telegram Bot Microservice
Basis for extendable, high-performance Telegram Bot microservice.

For instructions in Ukrainian see [docs/setup_uk.md](docs/setup_uk.md).

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/kh-waldemar/tg-bot-service.git
   cd tg-bot-service
   ```

2. **Copy and edit the environment file**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Fill in your Telegram `API ID`, `API HASH`, phone number, webhook URL and other settings.

3. **Create the required directories**
   ```bash
   mkdir -p sessions
   mkdir -p userbot_media
   ```

4. **Build the Docker images**
   ```bash
   docker compose build
   ```

5. **Authorize Telegram**
   Run the **receiver** container interactively and follow the login prompts:
   ```bash
   docker run -it --rm \
     -v $(pwd)/sessions:/sessions \
     -v $(pwd)/userbot_media:/userbot_media \
     --env-file .env \
     tg-bot-service-receiver \
     python3 main.py
   ```
   Enter the verification code and 2FA password if asked. When `Bot is running!` appears, press `Ctrl+C` to stop the container.

6. **Start all services in the background**
   ```bash
   docker compose up -d
   ```

7. **Check container status**
   ```bash
   docker compose ps
   ```

8. **Follow the logs**
   ```bash
   docker compose logs -f
   ```

After successful login the session is saved inside `sessions/`. Delete the files in that directory if you ever need to re-authorize or switch accounts.

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
If you modify `pyproject.toml` in either service, run `poetry lock` in that
directory before rebuilding so the lock file matches the dependencies.
And start up services:
```shell
docker-compose up
```

On the first run the **receiver** container will prompt for your Telegram login
code (and 2FA password if enabled). Enter the values directly in the container
when prompted.

The receiver will serve downloaded files on `<scheme>://<PUBLIC_MEDIA_HOST>[:<PUBLIC_MEDIA_PORT>]/media`. The port is omitted when it matches the default for the chosen scheme (80 for HTTP, 443 for HTTPS). Media links in webhook payloads are generated automatically using these variables.

### Configuration

1.  Copy `.env.example` to `.env`, populate your Telegram API credentials, session name, phone number, webhook information and public domain settings (`PUBLIC_MEDIA_HOST`, `PUBLIC_MEDIA_PORT`). Keep the file in the repository root next to `docker-compose.yml`.
2.  Create an empty `sessions/` directory next to the compose file. Docker Compose mounts this path into both services so they share one Telethon session.
   In your `.env` set `TG_SESSION_NAME=/sessions/tg_userbot` (or any name inside `/sessions`).
3.  Ensure the `userbot_media` directory exists. Docker Compose mounts this path
   into both services so that downloaded files persist and can be served over HTTP
   at `<scheme>://<PUBLIC_MEDIA_HOST>[:<PUBLIC_MEDIA_PORT>]/media/<filename>`.
4.  Docker Compose loads the `.env` file automatically for both services (see
   `env_file` in `docker-compose.yml`).
5.  Set `X_API_TOKEN` in `.env` and include this token in the `x-api-key` header when calling the sender API.
6.  Run the services with `docker-compose up`. When `receiver` starts for the first time it will prompt for the Telegram code (and 2FA password if enabled).
   Enter the values directly in the compose terminal. Subsequent runs will reuse the saved session file from `sessions/`.
7.  Ensure `TG_API_ID` and `TG_API_HASH` are taken from a **user** application created on [my.telegram.org](https://my.telegram.org) and not from a bot. Otherwise login will fail.
8.  During image build the latest Telethon is installed automatically. If you build images manually, update Telethon with `pip install -U telethon`.
9.  Media files are served directly by the receiver service on port `8181`, making
   any downloaded files reachable as
   `<scheme>://<PUBLIC_MEDIA_HOST>[:<PUBLIC_MEDIA_PORT>]/media/<filename>` without any
   extra web server.

Use the **sender** service endpoints to send messages from your server to Telegram.

## API Reference

The sender service exposes a small HTTP API on port `8001`.
The base URL for all endpoints is:

```
http://<HOST>:8001/api_v1
```

Every request must include the header `x-api-key` with the value
set in `X_API_TOKEN` inside your `.env` file.  All methods accept and
return JSON.

### Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/sendMessage` | Send a plain text message |
| `POST` | `/sendPhoto` | Send an image file |
| `POST` | `/sendDocument` | Send a document file |
| `POST` | `/sendAudio` | Send an audio file |
| `POST` | `/sendVoice` | Send a voice message |
| `POST` | `/sendVideo` | Send a video file |
| `POST` | `/editMessageText` | Edit a previously sent text |
| `POST` | `/deleteMessage` | Delete a message |

Below are the request payloads for each endpoint:

`POST /sendMessage`
```json
{
  "chat_id": 123456789,
  "text": "Hello",
  "parse_mode": "HTML"
}
```

`POST /sendPhoto`
```json
{
  "chat_id": 123456789,
  "photo": "<file url or base64>",
  "caption": "optional caption"
}
```

`POST /sendDocument`
```json
{
  "chat_id": 123456789,
  "document": "<file url or base64>",
  "caption": "optional caption"
}
```

`POST /sendAudio`
```json
{
  "chat_id": 123456789,
  "audio": "<file url or base64>",
  "caption": "optional caption"
}
```

`POST /sendVoice`
```json
{
  "chat_id": 123456789,
  "voice": "<file url or base64>",
  "caption": "optional caption"
}
```

`POST /sendVideo`
```json
{
  "chat_id": 123456789,
  "video": "<file url or base64>",
  "caption": "optional caption"
}
```

`POST /editMessageText`
```json
{
  "chat_id": 123456789,
  "message_id": 1,
  "text": "Updated text",
  "parse_mode": "HTML"
}
```

`POST /deleteMessage`
```json
{
  "chat_id": 123456789,
  "message_id": 1
}
```

Successful responses include `{"ok": true, "result": ...}` where `result`
contains the sent Telegram message data.  Media uploads return the file
name and a public `file_url` that can be fetched from
`http://<HOST>:8001/media/<file_name>`.

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
      "media_url": "https://example.com/media/1234_photo.jpg",
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
