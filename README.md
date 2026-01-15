# tg-d

## Запуск

1. Создайте файл окружения:

```bash
cp .env.example .env
```

2. Укажите переменные:

- `BOT_TOKEN` — токен Telegram-бота.
- `BOT_SALT` — соль для хеширования идентификаторов (опционально).

3. Установите зависимости и запустите:

```bash
pip install -r requirements.txt
python main.py
```
