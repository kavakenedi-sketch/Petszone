import datetime
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database import Pet, User, EvolutionStage, ShopItem, Inventory

# Уровни пользователя (опыт до следующего уровня)
LEVEL_EXP_REQUIREMENTS = {
    1: 0,
    2: 15,
    3: 30,
    4: 50,
    5: 80,
    6: 130,
    7: 190,
    8: 260,
    9: 340,
    10: 440,
    11: 560,
    12: 700
}

def get_level_from_exp(exp: int) -> int:
    level = 1
    for lvl, req in LEVEL_EXP_REQUIREMENTS.items():
        if exp >= req:
            level = lvl
        else:
            break
    return level

async def update_user_level(user: User, session: AsyncSession):
    new_level = get_level_from_exp(user.exp)
    if new_level != user.level:
        user.level = new_level
        await session.commit()

async def check_pet_evolution(pet: Pet, session: AsyncSession) -> bool:
    """Проверяет, нужно ли питомцу эволюционировать, и обновляет стадию."""
    # Получаем все стадии для этого вида
    result = await session.execute(
        select(EvolutionStage).where(EvolutionStage.pet_type == pet.pet_type).order_by(EvolutionStage.stage)
    )
    stages = result.scalars().all()
    if not stages:
        return False
    current_stage = pet.stage
    for stage in stages:
        if stage.stage > current_stage and pet.level >= stage.level_required:
            pet.stage = stage.stage
            if stage.stage == len(stages) - 1:  # последняя стадия
                pet.is_mature = True
            await session.commit()
            return True
    return False

async def apply_hunger_and_sickness(pet: Pet, session: AsyncSession):
    """Уменьшает сытость питомца на основе времени, прошедшего с последнего кормления.
       Если сытость упала до 0 и прошло более 24 часов с последнего кормления, питомец заболевает."""
    now = datetime.datetime.utcnow()
    if pet.last_fed:
        hours_passed = (now - pet.last_fed).total_seconds() / 3600
        # Уменьшаем сытость на 1 за каждый час (можно настроить)
        hunger_decrease = int(hours_passed)
        if hunger_decrease > 0:
            pet.hunger = max(0, pet.hunger - hunger_decrease)
            pet.last_fed = now  # обновляем, чтобы не уменьшать повторно каждый час
            # Болезнь: если сытость 0 и прошло больше 24 часов с последнего кормления
            if pet.hunger == 0 and hours_passed >= 24 and not pet.is_sick:
                pet.is_sick = True
            elif pet.hunger > 0 and pet.is_sick:
                pet.is_sick = False  # выздоровление, если поели
            await session.commit()

async def feed_pet(pet: Pet, food_item: ShopItem, user: User, session: AsyncSession):
    """Кормит питомца выбранным кормом."""
    # Восстанавливаем сытость (не более 100)
    pet.hunger = min(100, pet.hunger + food_item.hunger_restore)
    # Питомец получает опыт
    pet.exp += food_item.exp_bonus
    # Проверяем повышение уровня питомца (каждые 10 опыта = 1 уровень, например)
    new_pet_level = 1 + pet.exp // 10  # простая формула
    if new_pet_level > pet.level:
        pet.level = new_pet_level
    # Снимаем болезнь, если была
    if pet.is_sick and pet.hunger > 0:
        pet.is_sick = False
    pet.last_fed = datetime.datetime.utcnow()
    # Пользователь получает 3 exp
    user.exp += 3
    await update_user_level(user, session)
    await session.commit()

async def work_reward(user: User) -> int:
    """Возвращает количество монет за работу в зависимости от уровня."""
    if user.level <= 4:
        return random.randint(1, 45)
    elif user.level <= 7:
        return random.randint(45, 87)
    else:
        return random.randint(87, 120)

def work_exp_gain(user: User) -> int:
    """Опыт за работу: 2 + 2*(level-1)"""
    return 2 + 2 * (user.level - 1)

async def daily_reward(user: User, session: AsyncSession):
    """Начисляет ежедневный бонус (монеты + опыт)."""
    base_coins = 50
    base_exp = 10
    user.coins += base_coins
    user.exp += base_exp
    user.last_daily = datetime.datetime.utcnow()
    await update_user_level(user, session)
    await session.commit()
    return base_coins, base_exp