import asyncio
import os

from db_depart.vacancies_get_to_db import start_create_table
from functions.vacancies_getting import update_vacancies_db
from settings import *


async def create_rename_and_delete():
    """
    Асинхронно переименовывает один файл и удаляет другой.

    :param old_file_name: Имя файла, который нужно переименовать.
    :param new_file_name: Новое имя для файла.
    :param file_to_delete: Имя файла, который нужно удалить.
    """
    DATABASE_URL_CREATE = 'sqlite:///./db_depart/vacancies_upd.db'
    await start_create_table(DATABASE_URL_CREATE)
    await update_vacancies_db()

    old_file_name: str = 'db_depart/vacancies_upd.db'
    new_file_name: str = 'db_depart/vacancies.db'
    file_to_delete: str = 'db_depart/vacancies.db'
    try:

        os.remove(file_to_delete)
        logging.info('БД умешно обновлена')
        os.rename(old_file_name, new_file_name)

    except Exception as e:
        print(f"Произошла ошибка: {e}")

async def main():
    await create_rename_and_delete()


if __name__ == "__main__":
    asyncio.run(main())
