import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, select, update

# Используем SQLite (aiosqlite)
DATABASE_URL = "sqlite+aiosqlite:///pets_bot.db"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)  # Telegram ID
    username = Column(String, nullable=True)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    coins = Column(Integer, default=0)
    last_work = Column(DateTime, nullable=True)
    last_daily = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    pets = relationship("Pet", back_populates="owner", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="user", cascade="all, delete-orphan")

class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    pet_type = Column(String)          # вид: собачка, котик, ...
    name = Column(String)
    stage = Column(Integer, default=0)  # 0 - детёныш, 1 - подросток, 2 - взрослый
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    hunger = Column(Integer, default=100)  # 0-100
    is_mature = Column(Boolean, default=False)
    is_sick = Column(Boolean, default=False)
    last_fed = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="pets")

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer)   # id товара из shop
    quantity = Column(Integer, default=0)

    user = relationship("User", back_populates="inventory")

class ShopItem(Base):
    __tablename__ = "shop"
    id = Column(Integer, primary_key=True)  # 1-15
    name = Column(String)
    description = Column(String)
    price = Column(Integer)
    hunger_restore = Column(Integer)   # сколько сытости восстанавливает
    exp_bonus = Column(Integer)        # опыт питомцу за кормление

class EvolutionStage(Base):
    __tablename__ = "evolution_stages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pet_type = Column(String)
    stage = Column(Integer)            # 0,1,2
    level_required = Column(Integer)   # уровень питомца для перехода на эту стадию
    name = Column(String)              # название стадии

# Функция для создания таблиц
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Функция для получения пользователя (если нет - создаёт)
async def get_user(session: AsyncSession, tg_id: int, username: str = None):
    result = await session.execute(select(User).where(User.id == tg_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(id=tg_id, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user