"""
Модуль конфигурации бота.
Здесь хранятся настройки и переменные окружения.
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота из переменных окружения
# Токен можно получить у @BotFather в Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Путь к файлу базы данных SQLite
DATABASE_PATH = "teamplay.db"

# Проверка наличия токена
if not BOT_TOKEN:
    raise ValueError(
        "Не найден BOT_TOKEN! "
        "Создайте файл .env и укажите в нём BOT_TOKEN=ваш_токен"
    )

