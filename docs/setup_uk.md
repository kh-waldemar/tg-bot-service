# Інструкція запуску Tg-Bot Service

Цей документ описує послідовність дій для першого запуску сервісу.

## 1️⃣ Клонування репозиторію
```bash
git clone https://github.com/kh-waldemar/tg-bot-service.git
cd tg-bot-service
```

## 2️⃣ Налаштування середовища
Скопіюйте приклад файлу оточення та заповніть необхідні значення:
```bash
cp .env.example .env
nano .env
```
У `.env` потрібно вказати `API ID`, `API HASH`, номер телефону, URL вебхука та інші параметри.

## 3️⃣ Створення директорій
```bash
mkdir -p sessions
mkdir -p userbot_media
```

## 4️⃣ Збірка Docker-образів
```bash
docker compose build
```

## 5️⃣ Авторизація в Telegram
Запустіть контейнер **Receiver** в інтерактивному режимі та пройдіть авторизацію:
```bash
docker run -it --rm \
  -v $(pwd)/sessions:/sessions \
  -v $(pwd)/userbot_media:/userbot_media \
  --env-file .env \
  tg-bot-service-receiver \
  python3 main.py
```
Після запуску введіть код підтвердження, а також пароль 2FA (якщо увімкнено). Після появи повідомлення `Bot is running!` натисніть `Ctrl+C` для зупинки контейнера.

## ✅ Запуск сервісу

6️⃣ Запустіть усі сервіси у фоні:
```bash
docker compose up -d
```

7️⃣ Перевірте статус контейнерів:
```bash
docker compose ps
```

8️⃣ Перегляньте логи, щоб переконатися у коректній роботі:
```bash
docker compose logs -f
```

🟢 **Готово!** Після успішної авторизації сесія зберігається у папці `sessions/`,
тому повторне введення коду не потрібне. Якщо потрібно змінити акаунт або
авторизуватись заново, видаліть файли у `sessions/` і повторіть кроки
авторизації.
