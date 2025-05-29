import asyncio
import os

from settings import *


async def get_current_directory():
    """Возвращает текущую директорию, в которой находится исполняемый файл."""
    current_file_path = os.path.abspath(__file__)  # Получаем абсолютный путь к текущему файлу
    current_directory = os.path.dirname(current_file_path)  # Извлекаем директорию из полного пути
    logging.info(f"Текущая директория: {current_directory}")
    return current_directory


async def main():
    """Основная функция для получения текущей директории."""
    pwd = await get_current_directory()
    print(f"Текущая директория: {pwd}")

if __name__ == "__main__":
    asyncio.run(main())
