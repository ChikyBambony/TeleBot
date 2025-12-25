# TeleBot

Простой Telegram-бот на **pyTelegramBotAPI**:

- парсит нужные данные с сайта и выдаёт по запросу;
- выдаёт по запросу ответы из БД (**Excel**, **SQL**).

## Режимы работы

- **Админский режим** — доступны все функции чата.
- **Пользовательский режим** — не-админы получают ответ из БД (Excel-файла), также пишутся логи действий и `chat_id`.

## Структура проекта

- `TeleBot.py` — основной файл бота
- `config.py` — загрузка `.env` и настройки
- `loging.py` — подключение и парсинг сервиса
- `requirements.txt` — зависимости
- `.env.example` — пример переменных окружения

## Установка зависимостей

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
