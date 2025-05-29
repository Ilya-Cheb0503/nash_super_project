import json
from time import sleep

import requests

from constants.some_constants import ACCESS_TOKEN
from data_holder.data_science import key_keeper
from db_depart.new_module import (filling_vacancies_to_db,
                                  get_all_vacancies_module,
                                  get_no_exp_vacancies_module,
                                  get_vacancies_by_key_word_module,
                                  get_vacancies_by_keys_list_module)
from functions.inline_buttons import inline_buttons_packed
from functions.special_functions import check_for_empty_list
from functions.vacancies_cards import inf_taker
from settings import logging

unfortunately_text = (
    'Если вы пока не нашли нужную вакансию, пожалуйста, оставьте свои контакты в разделе «Отправить анкету».\n'
    'С Вами обязательно свяжутся, когда появится подходящая вакансия.'
)

async def get_vacancies_by_keys_list(update, context, keywords, first_key, user_region):

    await key_keeper('categories', first_key)

    try:
        result = await get_vacancies_by_keys_list_module(keywords, user_region)
    
    except Exception as error:
        sleep(5)
        result = await get_vacancies_by_keys_list_module(keywords, user_region)
    
    else:
        empty_list = await check_for_empty_list(result)
        if empty_list:
            user_id = update.effective_user.id
            await context.bot.send_message(chat_id=user_id, text=unfortunately_text)
            return

        await inline_buttons_packed(update, context, result)


async def get_no_exp_vacancies(update, context, user_region):
    try:
        result = await get_no_exp_vacancies_module(user_region)

    except Exception as error:
        sleep(5)
        result = await get_no_exp_vacancies_module(user_region)

    else:
        empty_list = await check_for_empty_list(result)
        if empty_list:
            user_id = update.effective_user.id
            await context.bot.send_message(chat_id=user_id, text=unfortunately_text)
            return

        await inline_buttons_packed(update, context, result)


async def get_vacancies_by_key_word(update, context, key_word, user_region):

    await key_keeper('keys_word', key_word)
    print('start vac')
    try:
        print('try')
        result = await get_vacancies_by_key_word_module(key_word, user_region)

    except Exception as error:
        sleep(5)
        result = await get_vacancies_by_key_word_module(key_word, user_region)

    else:
        print('else')
        empty_list = await check_for_empty_list(result)
        if empty_list:
            user_id = update.effective_user.id
            await context.bot.send_message(chat_id=user_id, text=unfortunately_text)
            return

        await inline_buttons_packed(update, context, result)
            

async def get_all_company_vacancies(update, context, user_region):
    try:
        result = await get_all_vacancies_module(user_region)

    except Exception as error:
        sleep(5)
        result = await get_all_vacancies_module(user_region)

    else:
        empty_list = await check_for_empty_list(result)
        if empty_list:
            user_id = update.effective_user.id
            await context.bot.send_message(chat_id=user_id, text=unfortunately_text)
            return

        await inline_buttons_packed(update, context, result)


EMPLOYER_IDS = [5436353, 10696710, 3147445, 538640, 2763248]
#  3451509, 3421843, 2029438,  9985959, 11733401

async def update_vacancies_db(per_page=100):
    for employer_id in EMPLOYER_IDS:
        page = 0
        logging.info(f'Токен доступа = {ACCESS_TOKEN}')
    
        vacancies_url = "https://api.hh.ru/vacancies"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        while True:
            params = {
                "employer_id": employer_id,
                "page": page,
                "per_page": per_page
            }
            response = requests.get(vacancies_url, headers=headers, params=params)
            if response.status_code != 200:
                logging.error(f"Ошибка при получении вакансий для работодателя {employer_id}: {response.status_code}")
                break
            data = response.json()
            items = data.get("items", [])
            if not items:
                break
            formatted_json = json.dumps(items, ensure_ascii=False, indent=4)
            logging.info(f'formatted_json для employer_id {employer_id} = {formatted_json}')
            tight_inf = await inf_taker(items)
            await filling_vacancies_to_db(tight_inf)
            if page >= data.get("pages", 1) - 1:
                break
            page += 1
