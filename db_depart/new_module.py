import asyncio
import json

from databases import Database
from sqlalchemy import JSON, Column, Integer, String, create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Vacancy_hh(Base):
    __tablename__ = 'vacancies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vacancy_id = Column(Integer, unique=True)
    region_name = Column(String)
    vacancy_inf = Column(JSON, nullable=True)

DATABASE_URL_CREATE = "sqlite:///./db_depart/vacancies_upd.db"
DATABASE_URL = "sqlite:///./db_depart/vacancies.db"
database = Database(DATABASE_URL)
database_update = Database(DATABASE_URL_CREATE)


async def save_vacancy(vacancy_id: int, region_name: str, vacancy_inf: dict = None):
    existing_vacancy = await get_vacancy_by_vacancy_id(vacancy_id, database_update)
    if existing_vacancy:
        print(f"Вакансия с vacancy_id {vacancy_id} уже существует.")
        return

    query = """
    INSERT INTO vacancies (vacancy_id, region_name, vacancy_inf)
    VALUES (:vacancy_id, :region_name, :vacancy_inf)
    """
    values = {
        "vacancy_id": vacancy_id,
        "region_name": region_name,
        "vacancy_inf": json.dumps(vacancy_inf)
    }
    await database_update.execute(query, values)


async def filling_vacancies_to_db(vacancies_data):
    await database_update.connect()
    # for vacancies in vacancies_data:

    for vacancy in vacancies_data:
        region = vacancy['Регион']
        await save_vacancy(vacancy_id=vacancy['id Вакансии'], region_name=region, vacancy_inf=vacancy)
    
    await database_update.disconnect()


async def get_vacancy_by_vacancy_id(vacancy_id: int, db=database):
    await db.connect()

    query = select(Vacancy_hh).where(Vacancy_hh.vacancy_id == vacancy_id)
    vacancy = await db.fetch_one(query)
    
    await db.disconnect()

    return vacancy


async def get_vacancies_by_key_word_module(key_word, user_region):
    await database.connect()
    

    select_region_name = user_region.lower()
    # Добавить функцию чтения названия региона из карточки пользователя
    query = select(Vacancy_hh)
    result_list = []
    results = await database.fetch_all(query)
    try:
        for vac in results:
            vacancy_region_name = vac.region_name.lower() if vac.region_name else ''
            vacancy_name = vac.vacancy_inf.get('Вакансия', '').lower()
            vacancy_req = vac.vacancy_inf.get('Требования', '').lower()
            vacancy_resp = vac.vacancy_inf.get('Обязанности', '').lower()
            if key_word.lower() in (vacancy_name or vacancy_req or vacancy_resp) and select_region_name in vacancy_region_name:
                result_list.append(vac)
    except Exception as ex:
        print(ex)

    await database.disconnect()

    return result_list


async def get_vacancies_by_keys_list_module(key_words_list, user_region):
    await database.connect()
    
    select_region_name = user_region.lower()
    # Добавить функцию чтения названия региона из карточки пользователя

    query = select(Vacancy_hh)
    result_list = []
    results = await database.fetch_all(query)
    for vac in results:
        for key_word in key_words_list:

            vacancy_region_name = vac.region_name.lower() if vac.region_name else ''
            vacancy_name = vac.vacancy_inf.get('Вакансия', '').lower() if vac.vacancy_inf.get('Вакансия') else ''
            vacancy_req = vac.vacancy_inf.get('Требования', '').lower() if vac.vacancy_inf.get('Требования') else ''
            vacancy_resp = vac.vacancy_inf.get('Обязанности', '').lower() if vac.vacancy_inf.get('Обязанности') else ''


            if key_word.lower() in (vacancy_name or vacancy_req or vacancy_resp) and select_region_name in vacancy_region_name:
                result_list.append(vac)

    await database.disconnect()

    return result_list


# Функция временно будет недоступна, поскольку на сайте нет такого пункта в карточках вакансий
async def get_no_exp_vacancies_module(user_region):
    await database.connect()

    select_region_name = user_region.lower()

    option_name = "Наличие опыта"
    option_value = "Нет опыта"

    query = select(Vacancy_hh)
    result_list = []
    results = await database.fetch_all(query)
    for vac in results:
        vacancy_region_name = vac.region_name.lower() if vac.region_name else ''
        if vac.vacancy_inf[option_name] == option_value and select_region_name in vacancy_region_name:
            result_list.append(vac)

    await database.disconnect()

    return result_list


async def get_all_vacancies_module(user_region):
    await database.connect()

    query = select(Vacancy_hh)
    results = await database.fetch_all(query)
    result_list = []

    select_region_name = user_region.lower() 
    # Добавить функцию чтения названия региона из карточки пользователя

    for vac in results:
        
        vacancy_region_name = vac.region_name.lower()

        if select_region_name in vacancy_region_name:
            result_list.append(vac)

    await database.disconnect()

    return result_list


async def start_create_table(DATABASE_URL):
    await database.connect()
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    await database.disconnect()


async def main():
    await start_create_table(DATABASE_URL)


if __name__ == '__main__':
    asyncio.run(main())

    