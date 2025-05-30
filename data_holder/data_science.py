import json
import os

from pwd_generator import get_current_directory
from settings import logging

vacancies_keys_file = "/data_holder/vacancies_keys.json"


async def load_vacancies_keys():

    project_folder = await get_current_directory()
    vacancies_keys_path = project_folder + vacancies_keys_file

    if os.path.exists(vacancies_keys_path):
        with open(vacancies_keys_path, "r") as file:
            vacancies_keys = json.load(file)
            # logging.info("Уведомления успешно загружены.")
            return vacancies_keys

    logging.warning("Файл уведомлений не найден, возвращается пустой словарь.")

    stat_bank = {
        "keys_word": {},
        "categories": {},
        "replies": {},
    }

    return stat_bank


async def save_vacancies_keys(vacancies_keys):
    # logging.info("Сохранение уведомлений в файл.")

    project_folder = await get_current_directory()
    vacancies_keys_path = project_folder + vacancies_keys_file

    with open(vacancies_keys_path, "w") as file:
        json.dump(vacancies_keys, file, ensure_ascii=True, indent=4)

    # logging.info("Уведомления успешно сохранены.")


async def key_keeper(parameter_name, parameter_value):
    keys_bank = await load_vacancies_keys()

    keys_words = keys_bank[parameter_name]

    if parameter_value not in keys_words:
        keys_bank[parameter_name][parameter_value] = 1
    else:
        keys_bank[parameter_name][parameter_value] += 1

    await save_vacancies_keys(keys_bank)


async def stat_collector(info_bank, parameter):

    keys_words = info_bank[parameter]
    popular_keys = 0
    answer = ""
    for key, count in keys_words.items():
        if count > 1:
            answer += f'"{key}": {count};\n'
            popular_keys += 1

    if popular_keys == 0:
        return False

    return answer


async def data_inf(update, context, admin_id):
    keys_pref = "Статистика по ключюевым словам, которые используют пользователи при поиске вакансий наиболее часто:\n"
    keys_stat = "На текущий момент нет вакансий, которые пользователь искал бы чаще одного раза.\n\n"

    categories_pref = (
        "Статистика по категориям, которые наиболее интересны пользователям:\n"
    )
    categories_stat = "На текущий момент нет категорий, которые наиболее интересных пользователям.\n\n"

    replies_pref = (
        "Статистика по вакансиям, на которые пользователи откликаются чаще всего:\n"
    )
    replies_stat = "На текущий момент нелья выделить ни одну из вакансий.\n\n"

    stat_collections = await load_vacancies_keys()

    keys_answer = await stat_collector(stat_collections, "keys_word")
    categories_answer = await stat_collector(stat_collections, "categories")
    replies_answer = await stat_collector(stat_collections, "replies")

    if keys_answer:
        keys_stat = keys_answer + "\n\n"
    if categories_answer:
        categories_stat = categories_answer + "\n\n"
    if replies_answer:
        replies_stat = replies_answer + "\n\n"

    keys_pref += keys_stat
    categories_pref += categories_stat
    replies_pref += replies_stat

    result_answer = f"{keys_pref}{categories_pref}{replies_pref}"

    project_folder = await get_current_directory()

    await create_text_file(project_folder, "statistic.txt", result_answer)

    full_path = f"{project_folder}/statistic.txt"
    with open(full_path, "rb") as txt_file:
        await context.bot.send_document(
            chat_id=admin_id, document=txt_file, filename="Метрика.txt"
        )


async def create_text_file(path, filename, content):
    full_path = f"{path}/{filename}"
    with open(full_path, "w", encoding="utf-8") as file:
        file.write(content)
