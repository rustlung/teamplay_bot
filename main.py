"""
Главный файл приложения - точка входа для Telegram-бота.
Здесь происходит инициализация бота и запуск polling.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import init_db
from handlers import router


async def main():
    """
    Главная асинхронная функция.
    Инициализирует бота, базу данных и запускает polling.
    """
    # Настройка логирования для отслеживания работы бота
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Запуск бота...")
    
    # Инициализация базы данных
    init_db()
    
    # Создание экземпляра бота
    # DefaultBotProperties позволяет установить настройки по умолчанию
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Создание диспетчера для обработки обновлений
    dp = Dispatcher()
    
    # Регистрация роутера с обработчиками команд
    dp.include_router(router)
    
    logger.info("✅ Бот успешно запущен!")
    logger.info("📝 Для остановки нажмите Ctrl+C")
    
    try:
        # Удаление всех ожидающих обновлений (чистый старт)
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Запуск polling - бот начинает получать и обрабатывать сообщения
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка при работе бота: {e}")
    finally:
        # Закрытие сессии бота при завершении работы
        await bot.session.close()
        logger.info("👋 Бот остановлен")


if __name__ == "__main__":
    """
    Точка входа в программу.
    Запускает асинхронную функцию main().
    """
    try:
        # Запуск асинхронной функции main()
        asyncio.run(main())
    except KeyboardInterrupt:
        # Обработка прерывания (Ctrl+C)
        print("\n👋 Бот остановлен пользователем")

