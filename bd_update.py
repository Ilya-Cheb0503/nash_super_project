import asyncio
import os

from functions import update_vacancies_db
from vacancies_get_to_db import start_create_table

from settings import *


async def create_rename_and_delete():
    """
    Асинхронно переименовывает один файл и удаляет другой.

    :param old_file_name: Имя файла, который нужно переименовать.
    :param new_file_name: Новое имя для файла.
    :param file_to_delete: Имя файла, который нужно удалить.
    """
    DATABASE_URL_CREATE = 'sqlite:///./vacancies_upd.db'
    await start_create_table(DATABASE_URL_CREATE)
    await update_vacancies_db()

    old_file_name: str = 'vacancies_upd.db'
    new_file_name: str = 'vacancies.db'
    file_to_delete: str = 'vacancies.db'
    try:

        # Удаление файла
        os.remove(file_to_delete)
        logging.info('БД умешно обновлена')
        # Переименование файла
        os.rename(old_file_name, new_file_name)

        # Использовать данную ошибку в кастомном виде: когда пользователь оптарвляет запрос на поиск вакансии во время обновления БД
        # мы делаем задержку в секунд 5 и повторяем его запрос.
    # except FileNotFoundError as e:
    #     print(f"Ошибка: {e}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Пример использования
async def main():
    await create_rename_and_delete()
# Запуск асинхронного кода
if __name__ == "__main__":
    asyncio.run(main())