from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🐾 Мои питомцы", callback_data="my_pets")
    kb.button(text="💼 Работа", callback_data="work")
    kb.button(text="🏪 Магазин", callback_data="shop")
    kb.button(text="🎒 Инвентарь", callback_data="inventory")
    kb.button(text="🐣 Завести питомца", callback_data="adopt")
    kb.button(text="🌟 Ежедневный бонус", callback_data="daily")
    kb.adjust(2)
    return kb.as_markup()

def pet_types_keyboard():
    pets = [
        "Собачка", "Котик", "Попугайчик", "Лиса", "Пингвинчик", "Мишка",
        "Кенгуру", "Панда", "Зайчик", "Ежик", "Дракончик", "Пони", "Сова", "Хомяк"
    ]
    kb = InlineKeyboardBuilder()
    for pet in pets:
        kb.button(text=pet, callback_data=f"choose_pet:{pet}")
    kb.adjust(2)
    return kb.as_markup()

def shop_keyboard(items):
    kb = InlineKeyboardBuilder()
    for item in items:
        kb.button(text=f"{item.name} - {item.price}💰", callback_data=f"buy:{item.id}")
    kb.adjust(2)
    return kb.as_markup()

def pet_actions_keyboard(pet_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="🍖 Покормить", callback_data=f"feed:{pet_id}")
    kb.button(text="🔙 Назад", callback_data="my_pets")
    kb.adjust(1)
    return kb.as_markup()

def feed_choice_keyboard(pet_id: int, inventory_items):
    kb = InlineKeyboardBuilder()
    for inv in inventory_items:
        kb.button(
            text=f"{inv.shop_item.name} x{inv.quantity}",
            callback_data=f"use_food:{pet_id}:{inv.id}"
        )
    kb.button(text="❌ Отмена", callback_data=f"pet_info:{pet_id}")
    kb.adjust(1)
    return kb.as_markup()