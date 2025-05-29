import asyncio
import json
import logging
from typing import Dict, Optional

from databases import Database
from sqlalchemy import JSON, Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

# Импортируем declarative_base из sqlalchemy.orm
Base = declarative_base()

class User_tg(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True)
    menu_state = Column(String, nullable=True)
    user_inf = Column(JSON, nullable=True)  # Добавлено новое свойство

DATABASE_URL = "sqlite:///./db_depart/users.db"
database = Database(DATABASE_URL)

async def create_user(telegram_id: int, menu_state: str = None):
    existing_user = await get_user(telegram_id)
    if existing_user:
        print(f"Пользователь с telegram_id {telegram_id} уже существует.")
        return

    query = """
    INSERT INTO users (telegram_id, menu_state, user_inf)
    VALUES (:telegram_id, :menu_state, :user_inf)
    """
    values = {
        "telegram_id": telegram_id,
        "menu_state": menu_state,
        "user_inf": json.dumps({'ФИО': None, 'Номер телефона': None})
    }
    await database.execute(query, values)

async def update_user(telegram_id: int, **kwargs):
    set_clause = ", ".join([f"{key} = :{key}" for key in kwargs.keys()])
    query = f"UPDATE users SET {set_clause} WHERE telegram_id = :telegram_id"
    values = {"telegram_id": telegram_id, **kwargs}
    await database.execute(query, values)

async def update_user_info(telegram_id: int, menu_state: Optional[str] = None, 
                            user_inf: Optional[dict] = None):
    updates = {}
    
    if menu_state is not None:
        updates['menu_state'] = menu_state
    if user_inf is not None:
        updates['user_inf'] = json.dumps(user_inf)
    
    if updates:
        await update_user(telegram_id, **updates)

async def get_user(telegram_id: int):
    query = "SELECT * FROM users WHERE telegram_id = :telegram_id"
    user = await database.fetch_one(query, values={"telegram_id": telegram_id})
    
    if user:
        user_dict = dict(user)
        user_dict['user_inf'] = json.loads(user_dict['user_inf']) if user_dict['user_inf'] else None
        return user_dict
    return None

async def get_all_users():
    query = "SELECT * FROM users"
    users = await database.fetch_all(query)
    
    user_list = []
    for user in users:
        user_dict = dict(user)
        user_dict['user_inf'] = json.loads(user_dict['user_inf']) if user_dict['user_inf'] else None
        user_list.append(user_dict)
    
    return user_list


async def start_create_table(DATABASE_URL):
    await database.connect()
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    await database.disconnect()

async def get_user_from_db(telegram_id):
    await database.connect()
    user = await get_user(telegram_id)
    await database.disconnect()
    return user

async def creat_user_in_db(telegram_id):
    await database.connect()
    await create_user(telegram_id=telegram_id)
    await database.disconnect()

# подумать о ДЕКОРАТОРЕ, чтобы строки с подключением и отключеним от таблицы прописать лишь раз
async def get_user_from_db(telegram_id):
    await database.connect()

    user = await get_user(telegram_id)

    await database.disconnect()

    return user


async def update_user_in_db(telegram_id, menu_state=None, user_inf=None):
    await database.connect()

    if menu_state:
        await update_user(telegram_id, menu_state=menu_state)
    if user_inf:
        user = await get_user(telegram_id)
        user_upd_inf = user['user_inf']
        for key, value in user_inf.items():
            user_upd_inf[key] = value
        logging.info(f'ОБНОВЛЕНИЕ ДАННЫХ {user_upd_inf}')
        await update_user_info(telegram_id, user_inf=user_upd_inf)

    await database.disconnect()


async def main():
    await start_create_table(DATABASE_URL)  # Создание таблицы
    # await create_user(5346)
    # user = await get_user(5346)
    # print(user)

# Запуск асинхронного кода
if __name__ == "__main__":
    asyncio.run(main())
