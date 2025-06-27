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


## Deployment

To start the service simply run:
```bash
docker compose up -d --build
```

1. Copy `.env.example` to `.env` and fill in your Telegram credentials.
2. Access the API at `http://localhost:8001`.
3. Media files are served at `http://localhost:8002/media/`.

Example request:
```bash
curl -X POST http://localhost:8001/api_v1/sendMessage \
  -H "x-api-key: <your_key>" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": 123456789, "text": "Привіт!"}'
```

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
      "media_url": "http://example.com:8002/media/1234_photo.jpg",
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
