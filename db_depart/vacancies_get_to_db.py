import asyncio
import json
import logging
from typing import Dict, Optional

import sqlalchemy
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

DATABASE_URL_CREATE = "sqlite:///./vacancies_upd.db"
DATABASE_URL = "sqlite:///./vacancies.db"
database = Database(DATABASE_URL)


async def save_vacancy(vacancy_id: int, region_name: str, vacancy_inf: dict = None):
    existing_vacancy = await get_vacancy_by_id(vacancy_id)
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
    await database.execute(query, values)


async def update_vacancy(vacancy_id: int, **kwargs):
    set_clause = ", ".join([f"{key} = :{key}" for key in kwargs.keys()])
    query = f"UPDATE vacancies SET {set_clause} WHERE vacancy_id = :vacancy_id"
    values = {"vacancy_id": vacancy_id, **kwargs}
    await database.execute(query, values)


async def update_vacancy_info(vacancy_id: int, vacancy_inf: Optional[dict] = None):
    updates = {}
    
    if vacancy_inf is not None:
        updates['vacancy_inf'] = json.dumps(vacancy_inf)
    
    if updates:
        await update_vacancy(vacancy_id, **updates)


async def get_vacancy_by_id(vacancy_id: int):
    query = "SELECT * FROM vacancies WHERE vacancy_id = :vacancy_id"
    vacancy = await database.fetch_one(query, values={"vacancy_id": vacancy_id})
    
    if vacancy:
        vacancy_dict = dict(vacancy)
        vacancy_dict['vacancy_inf'] = json.loads(vacancy_dict['vacancy_inf']) if vacancy_dict['vacancy_inf'] else None
        return vacancy_dict
    return None


async def get_vacancy_by_parameter(parameter, parameter_value):
    query = "SELECT * FROM vacancies WHERE properties LIKE ?"
    vacancy = await database.fetch_one(query, values={parameter: parameter_value})
    
    if vacancy:
        vacancy_dict = dict(vacancy)
        vacancy_dict['vacancy_inf'] = json.loads(vacancy_dict['vacancy_inf']) if vacancy_dict['vacancy_inf'] else None
        return vacancy_dict
    return None


async def get_all_vacancies_by_parameter(parameter, parameter_value):
    query = f"SELECT * FROM vacancies WHERE vacancy_inf->>{parameter} = :parameter_value"
    vacancies = await database.fetch_all(query, values={"parameter_value": parameter_value})
    
    result = []
    for vacancy in vacancies:
        vacancy_dict = dict(vacancy)
        vacancy_dict['vacancy_inf'] = json.loads(vacancy_dict['vacancy_inf']) if vacancy_dict['vacancy_inf'] else None
        result.append(vacancy_dict)
    
    return result


async def get_all_vacancys():
    query = "SELECT * FROM vacancies"
    vacancies = await database.fetch_all(query)
    
    vacancy_list = []
    for vacancy in vacancies:
        vacancy_dict = dict(vacancy)
        vacancy_dict['vacancy_inf'] = json.loads(vacancy_dict['vacancy_inf']) if vacancy_dict['vacancy_inf'] else None
        vacancy_list.append(vacancy_dict)
    
    return vacancy_list


async def start_create_table(DATABASE_URL):
    await database.connect()
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    await database.disconnect()

async def get_vacancy_from_db_by_id(vacancy_id):
    await database.connect()
    vacancy = await get_vacancy_by_id(vacancy_id)
    await database.disconnect()
    return vacancy


async def get_vacancy_from_db_by_parameter(parameter, par_value):
    await database.connect()
    vacancy = await get_vacancy_by_parameter(parameter, par_value)
    await database.disconnect()
    return vacancy

async def create_vacancy_in_db(vacancy_id, vacancy_inf):
    
    await database.connect()
    await save_vacancy(vacancy_id=vacancy_id, vacancy_inf=vacancy_inf)
    
    await database.disconnect()


async def create_vacancies_in_db(vacancies_data):
    await database.connect()
    
    for vacancy in vacancies_data:
        vacancy_id = vacancy.pop('id Вакансии')
        # vacancy_id, vacancy_inf = vacancy
        await save_vacancy(vacancy_id=vacancy_id, vacancy_inf=vacancy)
    
    await database.disconnect()

# подумать о ДЕКОРАТОРЕ, чтобы строки с подключением и отключеним от таблицы прописать лишь раз


async def update_vacancy_in_db(vacancy_id, menu_state=None, vacancy_inf=None):
    await database.connect()

    if vacancy_inf:
        vacancy = await get_vacancy_by_id(vacancy_id)
        vacancy_upd_inf = vacancy['vacancy_inf']
        for key, value in vacancy_inf.items():
            vacancy_upd_inf[key] = value
        logging.info(f'ОБНОВЛЕНИЕ ДАННЫХ {vacancy_upd_inf}')
        await update_vacancy_info(vacancy_id, vacancy_inf=vacancy_upd_inf)

    await database.disconnect()


async def get_vacancies_by_vacancy_id(vacancy_id: int):
    """
    Асинхронно извлекает вакансии, содержащие определенные значения в словаре информации.
    
    Args:
        experience_value (str): Значение для фильтрации по ключу 'опыт работы'.
    
    Returns:
        list: Список вакансий, соответствующих критериям.
    """
    query = select(Vacancy_hh).where(Vacancy_hh.vacancy_id == vacancy_id)
    results = await database.fetch_all(query)
    that = results
    return results


async def get_vacancies_by_option(option_name: str, option_value:str):
    """
    Асинхронно извлекает вакансии, содержащие определенные значения в словаре информации.
    
    Args:
        experience_value (str): Значение для фильтрации по ключу 'опыт работы'.
    
    Returns:
        list: Список вакансий, соответствующих критериям.
    """
    # query = select(Vacancy_hh).where(Vacancy_hh.vacancy_id[option_name] == option_value)
    # results = await database.fetch_all(query)
    # that = results
    # print(that)
    # return results

    query = select(Vacancy_hh)
    result_list = []
    results = await database.fetch_all(query)
    for vac in results:
        if vac.vacancy_inf[option_name] == option_value:
            result_list.append(vac)
    return results


async def main():
    from functions.vacancies_getting import update_vacancies_db
    await start_create_table(DATABASE_URL)
    await update_vacancies_db()
    # await create_vacancies_in_db(vac_list)
    # result = await get_vacancies_by_option('name', 'проверка123')
    # print(result)
    # vacancy = await get_vacancy_from_db_by_parameter('Наличие опыта', 'От 1 года до 3 лет')
    # # print(vacancy)

# Запуск асинхронного кода
if __name__ == "__main__":
    asyncio.run(main())
