import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import init_db, AsyncSessionLocal, ShopItem, EvolutionStage
from handlers import router

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def on_startup():
    # Инициализация базы данных
    await init_db()
    # Заполняем таблицы начальными данными, если они пусты
    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли товары в магазине
        from sqlalchemy import select
        result = await session.execute(select(ShopItem))
        if not result.scalars().first():
            # Добавляем 15 товаров
            shop_items = [
                ShopItem(id=1, name="Морковка", description="", price=10, hunger_restore=10, exp_bonus=5),
                ShopItem(id=2, name="Рыбка", description="", price=15, hunger_restore=15, exp_bonus=7),
                ShopItem(id=3, name="Зёрнышки", description="", price=8, hunger_restore=8, exp_bonus=4),
                ShopItem(id=4, name="Мясо", description="", price=25, hunger_restore=25, exp_bonus=12),
                ShopItem(id=5, name="Бамбук", description="", price=20, hunger_restore=20, exp_bonus=10),
                ShopItem(id=6, name="Мёд", description="", price=18, hunger_restore=18, exp_bonus=9),
                ShopItem(id=7, name="Трава", description="", price=5, hunger_restore=5, exp_bonus=2),
                ShopItem(id=8, name="Ягоды", description="", price=12, hunger_restore=12, exp_bonus=6),
                ShopItem(id=9, name="Орехи", description="", price=22, hunger_restore=22, exp_bonus=11),
                ShopItem(id=10, name="Семечки", description="", price=7, hunger_restore=7, exp_bonus=3),
                ShopItem(id=11, name="Жёлудь", description="", price=9, hunger_restore=9, exp_bonus=4),
                ShopItem(id=12, name="Червячок", description="", price=6, hunger_restore=6, exp_bonus=3),
                ShopItem(id=13, name="Молоко", description="", price=14, hunger_restore=14, exp_bonus=7),
                ShopItem(id=14, name="Сыр", description="", price=16, hunger_restore=16, exp_bonus=8),
                ShopItem(id=15, name="Фруктовый микс", description="", price=30, hunger_restore=30, exp_bonus=15),
            ]
            session.add_all(shop_items)
            await session.commit()

        # Стадии эволюции для каждого вида (для примера одинаковые для всех)
        result = await session.execute(select(EvolutionStage))
        if not result.scalars().first():
            pet_types = [
                "Собачка", "Котик", "Попугайчик", "Лиса", "Пингвинчик", "Мишка",
                "Кенгуру", "Панда", "Зайчик", "Ежик", "Дракончик", "Пони", "Сова", "Хомяк"
            ]
            stages = []
            for pet in pet_types:
                stages.append(EvolutionStage(pet_type=pet, stage=0, level_required=1, name="Детёныш"))
                stages.append(EvolutionStage(pet_type=pet, stage=1, level_required=6, name="Подросток"))
                stages.append(EvolutionStage(pet_type=pet, stage=2, level_required=13, name="Взрослый"))
            session.add_all(stages)
            await session.commit()

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(on_startup)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())