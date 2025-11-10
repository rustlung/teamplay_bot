"""
Модуль для работы с базой данных SQLite.
Содержит функции для создания таблиц и выполнения операций с задачами.
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple
from config import DATABASE_PATH


def init_db() -> None:
    """
    Инициализация базы данных.
    Создаёт таблицу tasks, если её ещё нет.
    
    Структура таблицы:
    - id: уникальный идентификатор (автоинкремент)
    - text: текст задачи
    - category: категория задачи
    - status: статус задачи (new, in_progress, done)
    - user: имя пользователя, создавшего задачу
    - created_at: дата и время создания задачи
    """
    # Подключаемся к базе данных (файл создастся автоматически, если его нет)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # SQL-запрос для создания таблицы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT '🎯 Личное',
            status TEXT NOT NULL DEFAULT 'new',
            user TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """)
    
    # Миграция: добавляем новые поля, если таблица уже существует без них
    # Проверяем наличие столбца category
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'category' not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN category TEXT NOT NULL DEFAULT '🎯 Личное'")
        print("✅ Добавлено поле category")
    
    if 'status' not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN status TEXT NOT NULL DEFAULT 'new'")
        print("✅ Добавлено поле status")
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    
    print("✅ База данных инициализирована")


def add_task(text: str, user: str, category: str) -> int:
    """
    Добавляет новую задачу в базу данных.
    
    Args:
        text: Текст задачи
        user: Имя пользователя, создающего задачу
        category: Категория задачи
        
    Returns:
        ID добавленной задачи
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Получаем текущее время
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Статус по умолчанию - "new" (Новая)
    status = "new"
    
    # Добавляем задачу в базу данных
    cursor.execute(
        "INSERT INTO tasks (text, category, status, user, created_at) VALUES (?, ?, ?, ?, ?)",
        (text, category, status, user, created_at)
    )
    
    # Получаем ID последней добавленной записи
    task_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return task_id


def get_all_tasks() -> List[Tuple[int, str, str, str, str, str]]:
    """
    Получает все задачи из базы данных.
    
    Returns:
        Список кортежей (id, text, category, status, user, created_at)
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Получаем все задачи, отсортированные сначала по категории, затем по времени создания
    cursor.execute(
        "SELECT id, text, category, status, user, created_at FROM tasks ORDER BY category, created_at DESC"
    )
    
    tasks = cursor.fetchall()
    conn.close()
    
    return tasks

