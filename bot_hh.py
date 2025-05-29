import asyncio
import logging
import os
from time import sleep
from unicodedata import category

import nest_asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, Update)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)

from constants.keyboards import (admin_main_menu_keyboard,
                                 user_main_menu_keyboard)
from constants.messages_text import (inf_contacts_text, welcome_text,
                                     welcome_two)
from constants.options_inline_list import but_opt
from constants.regions_data import region_list
from constants.some_constants import admins_id, group_id
from constants.vacancies_keys import (energy_vacancy_keys,
                                      ofice_request_translater,
                                      ofice_vacancy_keys,
                                      power_request_translater,
                                      vacancy_request_translater,
                                      categories_vacancy_keys)
from data_holder.data_science import data_inf, key_keeper
from db_depart.bd_update import create_rename_and_delete
from db_depart.new_module import get_vacancy_by_vacancy_id
from db_depart.user_db import (creat_user_in_db, get_user_from_db,
                               update_user_in_db)
from functions.inline_buttons import one_more_dose, set_inline_keyboard
from functions.tg_mailman import send_messages
from functions.user_data_form import (list_waiting,
                                      user_full_information_process)
from functions.user_reply_form import user_form_information_process
from functions.vacancies_getting import (get_all_company_vacancies,
                                         get_no_exp_vacancies,
                                         get_vacancies_by_key_word,
                                         get_vacancies_by_keys_list,)
from settings import logging


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = await get_user_from_db(user_id)
    user_inf = user['user_inf']
    if 'Регион поиска' in user['user_inf']:
        user_region = user['user_inf']['Регион поиска']
    user_name = user_inf['ФИО']
    
    buttons_calling_data = query.data


    # мы реагируем на нажатие определенной кнопки, а не сообщение, поэтому не важен порядок определения *на подумать
    if buttons_calling_data.__eq__('user_data'):
        await list_waiting(update, context)
    elif buttons_calling_data.__eq__('postman'):
        await send_messages(update, context)
    elif buttons_calling_data.__eq__("analiz"):
        await data_inf(update, context, admin_id=user_id)
    
    elif buttons_calling_data.__eq__('more_more'):
        await one_more_dose(update, context)

    elif buttons_calling_data in vacancy_request_translater.keys():
        first_key = vacancy_request_translater[buttons_calling_data]
        promt_keys = categories_vacancy_keys[first_key]
        await get_vacancies_by_keys_list(update, context, promt_keys, first_key, user_region)


    elif buttons_calling_data in power_request_translater.keys():
        first_key = power_request_translater[buttons_calling_data]
        promt_keys = energy_vacancy_keys[first_key]
        await get_vacancies_by_keys_list(update, context, promt_keys, first_key, user_region)

    elif buttons_calling_data in ofice_request_translater.keys():
        first_key = ofice_request_translater[buttons_calling_data]
        promt_keys = ofice_vacancy_keys[first_key]
        await get_vacancies_by_keys_list(update, context, promt_keys, first_key, user_region)
    
    elif buttons_calling_data.__eq__('no_exp'):
        await get_no_exp_vacancies(update, context, user_region)

    elif buttons_calling_data.__eq__('duty_vacancies'):
        await get_vacancies_by_key_word(update, context, key_word='Стажер', user_region=user_region)

    elif buttons_calling_data.__eq__('show_all'):
        await get_all_company_vacancies(update, context, user_region)


    elif buttons_calling_data in but_opt.keys() or buttons_calling_data in region_list:
        if buttons_calling_data in region_list:
            await update_user_in_db(user_id, user_inf={'Регион поиска':buttons_calling_data})
            buttons_calling_data = 'vacancies'


        menu = buttons_calling_data == 'main_menu'
        message_text, buttons_set = but_opt[buttons_calling_data]
        if menu and 'admin_status' in context.user_data:
            buttons_set = buttons_set[1]
        elif menu:
            buttons_set = buttons_set[0]

        if buttons_set:
            keyboard = []
            for button in buttons_set:
                
                if all(isinstance(element, str) for element in button):
                    button_name, button_data = button
                    keyboard.append(
                        [InlineKeyboardButton(text = button_name, callback_data = button_data)]
                    )
                else:
                    
                    next_button_row = []
                    for element in button:
                        button_name, button_data = element
                        next_button_row.append(
                            InlineKeyboardButton(text = button_name, callback_data = button_data)
                        )
                    keyboard.append(next_button_row)
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=message_text, reply_markup=reply_markup)
        else:
            current_keyboard = query.message.reply_markup
            await query.edit_message_text(text=message_text, reply_markup=current_keyboard)

    elif 'tq' in buttons_calling_data:
        vac_id = query.data.split(';')[1]
        int_id = int(vac_id)
        vacancy = await get_vacancy_by_vacancy_id(int_id)
        vacancy_name = vacancy.vacancy_inf['Вакансия']
        vacancy_url = vacancy.vacancy_inf['Ссылка на вакансию']

        employer_url = vacancy.vacancy_inf['Ссылка на работодателя']
        employer_id = int(employer_url.split('/')[-1])
        context.user_data['employer_id'] = employer_id

        context.user_data['vacancy_name'] = vacancy_name
        context.user_data['Запрос анкетных данных'] = 'Запуск анкетирования'

        await key_keeper("replies", vacancy_name)

        await user_form_information_process(update, context)

    elif not user_inf['ФИО'] or not user_inf['Номер телефона']:
        context.user_data['Запрос анкетных данных'] = 'Запуск анкетирования'
        await user_full_information_process(update, context)

    elif buttons_calling_data.__eq__('get_spec'):
        await context.bot.send_message(chat_id=user_id, text=inf_contacts_text, parse_mode='Markdown')

    else:
        
        int_id = int(buttons_calling_data)
        vacancy = await get_vacancy_by_vacancy_id(int_id)
        vacancy_url = vacancy.vacancy_inf['Ссылка на вакансию']
        vacancy_name = vacancy.vacancy_inf['Вакансия']

        user_send_req_text = (
            f'Пользователь: {user_name}\n'
            f'Откликнулся на вакансию: {vacancy_name}'
        )

        await key_keeper("replies", vacancy_name)

        await context.bot.send_message(chat_id=group_id, text=user_send_req_text)

        keyboard = [
        [
            InlineKeyboardButton("Откликнуться", callback_data=f'tq;{int_id}')
        ],
        [
            InlineKeyboardButton("Ссылка на вакансию", callback_data='req_button', url=vacancy_url)
        ],
        [
            InlineKeyboardButton("Получить консультацию специалиста 📞", callback_data='get_spec')
        ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id, reply_markup=reply_markup)

        vacancion_name = query.data.split(';')[1]
        user = await get_user_from_db(user_id)
        user_inf = user['user_inf']
        user_name = user_inf['ФИО']
        logging.info(f'IMPOOOOORTANT {vacancion_name}')
        note_text = f'Пользователь: {user_name}\nОткликнулся на вакансию: {vacancion_name}'
        if 'ФИО' and 'Образование' in user_inf:
            await context.bot.send_message(chat_id=group_id, text=note_text, parse_mode='HTML')


# Функция для обработки нажатий кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    list_keys = [
    'Запрос full данных',
    'Запрос анкетных данных',
    'information_form',
    'message_inf',
    'message_state',
    'current_text',
    'photo_path',
    'pdf_path',
    'vacancy_name',

]

    user_id = update.effective_user.id
    current_text = update.message.text

    
    admin_check = user_id in admins_id
    if admin_check:
        context.user_data['admin_status'] = True

    if update.message.photo:
        if 'message_state' in context.user_data:
            await send_messages(update, context)
    elif update.message.document:
        if 'Запрос анкетных данных' in context.user_data:
            await user_form_information_process(update, context)


    elif current_text.__eq__('Главное меню'):

        for key in list_keys:
            if key in context.user_data:
                context.user_data.pop(key)

        if admin_check:
            await set_inline_keyboard(update, context, buttons_list = admin_main_menu_keyboard, message_text = welcome_text)

        else:
            await set_inline_keyboard(update, context, buttons_list = user_main_menu_keyboard, message_text = welcome_text)
    
    elif 'message_state' in context.user_data:
            await send_messages(update, context)

    elif 'Запрос full данных' in context.user_data:
        await list_waiting(update, context)

    elif 'Запрос анкетных данных' in context.user_data:
        await user_form_information_process(update, context)

    elif current_text.lower().__eq__('без опыта'):
        logging.info('БЕЗ ОПЫТА')

        user = await get_user_from_db(user_id)
        if 'Регион поиска' in user['user_inf']:
            user_region = user['user_inf']['Регион поиска']

        else:
            message_text, buttons_set = but_opt['region']

            keyboard = []
            for button in buttons_set:
                
                button_name, button_data = button
                keyboard.append(
                    [InlineKeyboardButton(text = button_name, callback_data = button_data)]
                )
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(chat_id=user_id, text=message_text, parse_mode='Markdown', reply_markup=reply_markup)


        await get_no_exp_vacancies(update, context, user_region)
    else:
        user = await get_user_from_db(user_id)
        if 'Регион поиска' in user['user_inf']:
            user_region = user['user_inf']['Регион поиска']
            # # 1. Создать словарь, в котором будут хранится ключи и вакансии к ним
            # if current_text in 'some_list_with_keys':
            #     pass
            #     # 2. Обращаться к этому словарю с ключем и получать пакет ключей для запросы, после чего отправлять его в функцию получения вакансий по списку ключей
            #     pack_of_keys = 'keys_vocabular'[current_text]
            #     await get_vacancies_by_keys_list(update, context, pack_of_keys, user_region)
            # else:
            await get_vacancies_by_key_word(update, context, current_text, user_region)
        else:
            message_text, buttons_set = but_opt['region']

            keyboard = []
            for button in buttons_set:
                
                button_name, button_data = button
                keyboard.append(
                    [InlineKeyboardButton(text = button_name, callback_data = button_data)]
                )
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(chat_id=user_id, text=message_text, parse_mode='Markdown', reply_markup=reply_markup)

        


# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    
    # await start_create_table()
    if 'Запрос full данных' in context.user_data:
        context.user_data.pop('Запрос full данных')

    if 'Запрос анкетных данных' in context.user_data:
        context.user_data.pop('Запрос анкетных данных')

    user_id = update.effective_user.id
    user = await get_user_from_db(user_id)
    if not user:
        await creat_user_in_db(user_id)
    
    keyboard = [
        ['Главное меню'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    text = welcome_text 
    # if admin_authenticated.get(user_id, False):
    if user_id in admins_id:
        await update_user_in_db(user_id, menu_state='Меню администратора')
        
        context.user_data['admin_status'] = True
        await set_inline_keyboard(update, context, buttons_list = admin_main_menu_keyboard, message_text = text)

        sleep(0.5)
        
        await context.bot.send_message(chat_id=user_id, text=welcome_two, parse_mode='Markdown', reply_markup=reply_markup)

    else:
        await update_user_in_db(user_id, menu_state='Меню пользователя')

        await set_inline_keyboard(update, context, buttons_list = user_main_menu_keyboard, message_text = text)

        sleep(0.5)
        await context.bot.send_message(chat_id=user_id, text=welcome_two, parse_mode='Markdown', reply_markup=reply_markup)

async def db_update_task(update, context):

    user_id = update.effective_user.id
    if str(user_id).__eq__('2091023767'):
        logging.info('ЗАПУСКАЕМ расписание обновления БД')
        
        await create_rename_and_delete()
        
        scheduler = AsyncIOScheduler()
        scheduler.add_job(create_rename_and_delete, 'cron', hour=0, minute=0)  # Запрашиваем события каждую полночь
        scheduler.start()

        logging.info('ЗАПУСТИЛИ расписание обновления БД')

        await context.bot.send_message(chat_id=user_id, text='БД обновлена\nТаймер на обновления запущен')


async def main(telegram_bot_token) -> None:
    
    nest_asyncio.apply()

    application = Application.builder().token(telegram_bot_token).build()

    # Регистрируем обработчики команд и сообщений
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('developer_hand', db_update_task))
    # application.add_handler(CommandHandler('buttons', send_inline_buttons))
    application.add_handler(CallbackQueryHandler(button_callback))  # Добавляем обработчик для инлайн кнопок
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND | filters.PHOTO | filters.Document.ALL, button_handler))
      # Обработчик для инлайн кнопок

    # Запускаем бота
    logging.info('Бот запущен')
    try:
        # Запускаем бота
        await application.run_polling()
    except (KeyboardInterrupt, SystemExit):
        # Обрабатываем исключения, чтобы избежать вывода в терминал
        logging.error(f"Бот остановлен", exc_info=True)
        await application.stop()
    

if __name__ == '__main__':
    
    try:
        load_dotenv()
        telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    except Exception as er:
        logging.error(f'Не получилось получить токен телеграм бота.\n{er}\nПроверьте наличие .env')

    asyncio.run(main(telegram_bot_token))
        