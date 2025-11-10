"""
Модуль с inline-клавиатурами для бота.
Содержит клавиатуры для выбора категорий задач.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Список доступных категорий задач
CATEGORIES = [
    "💼 Работа",
    "🏠 Дом",
    "📚 Обучение",
    "💪 Спорт",
    "🎯 Личное",
    "📞 Встречи",
]

# Список статусов задач
STATUSES = {
    "new": "🆕 Новая",
    "in_progress": "⚙️ В работе",
    "done": "✅ Выполнена"
}


def get_categories_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт inline-клавиатуру с категориями задач.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками категорий
    """
    # Создаём список кнопок
    buttons = []
    
    # Добавляем кнопку для каждой категории
    # Размещаем по 2 кнопки в ряд
    for i in range(0, len(CATEGORIES), 2):
        row = []
        # Добавляем первую кнопку в ряду
        row.append(
            InlineKeyboardButton(
                text=CATEGORIES[i],
                callback_data=f"category:{CATEGORIES[i]}"
            )
        )
        # Добавляем вторую кнопку, если она есть
        if i + 1 < len(CATEGORIES):
            row.append(
                InlineKeyboardButton(
                    text=CATEGORIES[i + 1],
                    callback_data=f"category:{CATEGORIES[i + 1]}"
                )
            )
        buttons.append(row)
    
    # Создаём клавиатуру из кнопок
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    return keyboard

