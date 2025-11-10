"""
Модуль с обработчиками команд бота.
Обрабатывает команды: /start, /add, /list, /list_csv
"""

import csv
import os
from collections import defaultdict
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import add_task, get_all_tasks
from keyboards import get_categories_keyboard
from keyboards.inline import STATUSES

# Создаём роутер для регистрации обработчиков
router = Router()


# Определяем состояния для FSM (Finite State Machine - конечный автомат)
class TaskStates(StatesGroup):
    """Состояния для добавления задачи"""
    waiting_for_category = State()  # Ожидание выбора категории
    waiting_for_task = State()  # Ожидание ввода текста задачи


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start.
    Приветствует пользователя и показывает доступные команды.
    """
    welcome_text = (
        "👋 Привет! Я бот для командной работы с задачами.\n\n"
        "📋 Доступные команды:\n"
        "/add - Добавить новую задачу\n"
        "/list - Показать все задачи\n"
        "/list_csv - Получить список задач в формате CSV\n"
        "/start - Показать это сообщение"
    )
    
    await message.answer(welcome_text)


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    """
    Обработчик команды /add.
    Запускает процесс добавления новой задачи.
    Сначала предлагает выбрать категорию.
    """
    await state.set_state(TaskStates.waiting_for_category)
    
    # Отправляем сообщение с inline-клавиатурой для выбора категории
    await message.answer(
        "📂 Выберите категорию для новой задачи:",
        reply_markup=get_categories_keyboard()
    )


@router.callback_query(F.data.startswith("category:"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора категории через inline-кнопку.
    После выбора категории запрашивает текст задачи.
    """
    # Извлекаем название категории из callback_data
    category = callback.data.split(":", 1)[1]
    
    # Сохраняем выбранную категорию в состояние FSM
    await state.update_data(category=category)
    
    # Переходим к следующему состоянию - ожидание текста задачи
    await state.set_state(TaskStates.waiting_for_task)
    
    # Отвечаем на callback (убирает "часики" на кнопке)
    await callback.answer()
    
    # Редактируем сообщение - убираем клавиатуру
    await callback.message.edit_text(
        f"✅ Выбрана категория: {category}\n\n"
        f"📝 Теперь отправьте текст задачи.\n"
        f"Для отмены отправьте /cancel"
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """
    Обработчик команды /cancel.
    Отменяет текущее действие (например, добавление задачи).
    """
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer("❌ Нечего отменять.")
        return
    
    await state.clear()
    await message.answer("✅ Действие отменено.")


@router.message(TaskStates.waiting_for_task)
async def process_task_text(message: Message, state: FSMContext):
    """
    Обработчик текста задачи.
    Сохраняет задачу в базу данных с выбранной категорией.
    """
    # Получаем текст задачи
    task_text = message.text
    
    # Получаем сохранённые данные из состояния (категорию)
    data = await state.get_data()
    category = data.get("category", "🎯 Личное")
    
    # Получаем информацию о пользователе
    # Используем username, если есть, иначе - имя пользователя
    user_name = message.from_user.username or message.from_user.full_name
    
    # Добавляем задачу в базу данных
    task_id = add_task(task_text, user_name, category)
    
    # Очищаем состояние (завершаем процесс добавления задачи)
    await state.clear()
    
    # Отправляем подтверждение
    await message.answer(
        f"✅ Задача #{task_id} успешно добавлена!\n\n"
        f"📂 Категория: {category}\n"
        f"📝 {task_text}\n"
        f"🆕 Статус: Новая\n"
        f"👤 Автор: {user_name}"
    )


@router.message(Command("list"))
async def cmd_list(message: Message):
    """
    Обработчик команды /list.
    Выводит список всех задач из базы данных, сгруппированных по категориям.
    """
    # Получаем все задачи из базы данных
    tasks = get_all_tasks()
    
    # Если задач нет
    if not tasks:
        await message.answer("📋 Список задач пуст. Добавьте первую задачу командой /add")
        return
    
    # Группируем задачи по категориям
    tasks_by_category = defaultdict(list)
    for task in tasks:
        task_id, text, category, status, user, created_at = task
        tasks_by_category[category].append((task_id, text, status, user, created_at))
    
    # Формируем текст со списком задач
    response = f"📋 Всего задач: {len(tasks)}\n\n"
    
    # Выводим задачи, сгруппированные по категориям
    for category, category_tasks in tasks_by_category.items():
        response += f"{'=' * 40}\n"
        response += f"📂 {category} ({len(category_tasks)})\n"
        response += f"{'=' * 40}\n\n"
        
        for task_id, text, status, user, created_at in category_tasks:
            # Получаем иконку статуса
            status_text = STATUSES.get(status, "❓ Неизвестно")
            
            response += (
                f"#{task_id} | {status_text}\n"
                f"📝 {text}\n"
                f"👤 {user} | {created_at}\n"
                f"{'-' * 40}\n"
            )
        
        response += "\n"
    
    # Отправляем список задач
    # Telegram ограничивает длину сообщения 4096 символами
    if len(response) > 4000:
        # Если сообщение слишком длинное, разбиваем на части
        parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for part in parts:
            await message.answer(part)
    else:
        await message.answer(response)


@router.message(Command("list_csv"))
async def cmd_list_csv(message: Message):
    """
    Обработчик команды /list_csv.
    Создаёт CSV-файл со всеми задачами и отправляет его пользователю.
    """
    # Получаем все задачи из базы данных
    tasks = get_all_tasks()
    
    # Если задач нет
    if not tasks:
        await message.answer("📋 Список задач пуст. Нечего экспортировать.")
        return
    
    # Имя файла
    filename = "tasks.csv"
    
    # Создаём CSV-файл
    with open(filename, "w", encoding="utf-8-sig", newline="") as csvfile:
        # Создаём writer для записи в CSV
        writer = csv.writer(csvfile)
        
        # Записываем заголовки
        writer.writerow(["ID", "Задача", "Категория", "Статус", "Автор", "Дата создания"])
        
        # Записываем данные задач
        for task_id, text, category, status, user, created_at in tasks:
            # Преобразуем статус в читаемый вид
            status_text = STATUSES.get(status, "Неизвестно")
            writer.writerow([task_id, text, category, status_text, user, created_at])
    
    # Отправляем файл пользователю
    file = FSInputFile(filename)
    await message.answer_document(
        file,
        caption=f"📊 Экспорт {len(tasks)} задач(и) в формате CSV"
    )
    
    # Удаляем временный файл
    os.remove(filename)

