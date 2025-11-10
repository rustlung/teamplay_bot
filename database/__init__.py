"""
Пакет для работы с базой данных.
Здесь находятся функции для инициализации БД и работы с задачами.
"""

from .db_manager import init_db, add_task, get_all_tasks

__all__ = ["init_db", "add_task", "get_all_tasks"]

