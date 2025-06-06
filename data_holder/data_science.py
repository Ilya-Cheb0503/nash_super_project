import json
import os
from datetime import datetime

from pwd_generator import get_current_directory
from settings import logging

from constants.constants import stat_bank


async def load_json_file(pattern_dict, file_path):

    project_folder = await get_current_directory()
    json_file_path = project_folder + file_path

    if os.path.exists(json_file_path):
        with open(json_file_path, "r", encoding='utf-8') as file:
            json_file = json.load(file)
            # logging.info("Уведомления успешно загружены.")
            return json_file

    logging.warning("Файл уведомлений не найден, возвращается пустой словарь.")

    return pattern_dict


async def save_json_file(json_file, file_path):
    # logging.info("Сохранение уведомлений в файл.")

    project_folder = await get_current_directory()
    json_file_path = project_folder + file_path

    with open(json_file_path, "w", encoding='utf-8') as file:
        json.dump(json_file, file, ensure_ascii=False, indent=4)

    # logging.info("Уведомления успешно сохранены.")


async def get_current_month():

    months_dict = {
        1: "Январь",
        2: "Февраль",
        3: "Март",
        4: "Апрель",
        5: "Май",
        6: "Июнь",
        7: "Июль",
        8: "Август",
        9: "Сентябрь",
        10: "Октябрь",
        11: "Ноябрь",
        12: "Декабрь",
    }

    current_month_number = datetime.now().month
    return months_dict[current_month_number]


async def key_keeper(parameter_name, parameter_value):
    keys_bank = await load_json_file(pattern_dict=stat_bank, file_path='/data_holder/vacancies_keys.json')

    keys_words = keys_bank[parameter_name]

    if parameter_value not in keys_words:
        keys_bank[parameter_name][parameter_value] = 1
    else:
        keys_bank[parameter_name][parameter_value] += 1

    await save_json_file(json_file=keys_bank, file_path='/data_holder/vacancies_keys.json')


async def change_json_file(json_file, key, value):
    json_file[key] = value
    return json_file


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

    stat_collections = await load_json_file(pattern_dict=stat_bank, file_path='/data_holder/vacancies_keys.json')

    keys_answer = await stat_collector(stat_collections, "keys_word")
    categories_answer = await stat_collector(stat_collections, "categories")
    replies_answer = await stat_collector(stat_collections, "replies")
    year_answer = stat_collections['year']

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

    result_answer += '\nСтатистика по новым пользователям за год:\n'

    for month, value in year_answer.items():
        result_answer += f'{month}: {value}\n'

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
