from time import sleep

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db_depart.new_module import get_vacancy_by_vacancy_id
from functions.special_functions import packer
from functions.vacancies_cards import message_creater
from settings import logging


async def inline_buttons_packed(update, context, result):

    vacancies_id = []
    vacancy_num = 0
    for vacancy_full in result:
        vacancy_num += 1
        vacancy = vacancy_full.vacancy_inf
        vacancy_id = vacancy_full.vacancy_id

        vacancy_text = await message_creater(vacancy)
        if vacancy_num < 6:
            await send_inline_buttons(update, context, message_text=vacancy_text, vacancy_id=vacancy_id)
            
        else:
            vacancies_id.append(vacancy_id)

    if vacancy_num > 5:
        packed_vacancies_id = await packer(vacancies_id)

        await next_or_stop(
            update,
            context,
            vacancy_count=vacancy_num,
            last_watched_count=0,
            new_watched_count=5,
            left_packing=packed_vacancies_id
        )


async def next_or_stop(update, context, vacancy_count, last_watched_count, new_watched_count, left_packing):
    summ_watched = last_watched_count+new_watched_count
    options_ask = [
        ['Продолжить', 'more_more'],
        ['Достаточно', 'main_menu'],
    ]
    ask_text = f'Всего вакансий: {vacancy_count}\n'
    if summ_watched < vacancy_count:
        ask_text += (
            f'Вы просмотрели {summ_watched} из них.\n'
            'Показать еще вакансии или остановиться ?'
            )

        
        context.user_data['vacancies_informations'] = [vacancy_count, summ_watched, left_packing]
        await set_inline_keyboard(update, context, options_ask, ask_text)


async def one_more_dose(update, context):

    vacancy_num, watched_num, packed_vacancies_id = context.user_data['vacancies_informations']
    next_pack = packed_vacancies_id.pop(-1)
    pack_size = len(next_pack)

    for vacancy_id in next_pack:
        vacancy_data = await get_vacancy_by_vacancy_id(vacancy_id)

        vacancy = vacancy_data.vacancy_inf
        vacancy_id = vacancy_data.vacancy_id

        vacancy_text = await message_creater(vacancy)
        await send_inline_buttons(update, context, message_text=vacancy_text, vacancy_id=vacancy_id)
    
    if packed_vacancies_id:
        await next_or_stop(
            update,
            context,
            vacancy_count=vacancy_num,
            last_watched_count=watched_num,
            new_watched_count=pack_size,
            left_packing=packed_vacancies_id
        )


async def send_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text, vacancy_id) -> None:
    logging.info('РЕГИСТРАЦИЯ КНОПОК')
    user_id = update.effective_user.id

    vacancy = await get_vacancy_by_vacancy_id(vacancy_id)
    # vacancy_url = vacancy.vacancy_inf['Ссылка на вакансию']
    # Создаем инлайн кнопки
    keyboard = [
        [
            InlineKeyboardButton("Откликнуться", callback_data=f'tq;{vacancy_id}')
        ],

        # [
        #     InlineKeyboardButton("Откликнуться через hhru", callback_data=f'{vacancy_id}')
        # ],
        [
            # InlineKeyboardButton("Ссылка на вакансию", callback_data='req_button', url=vacancy_url)
        ],

        [
            InlineKeyboardButton("Получить консультацию специалиста 📞", callback_data='get_spec')
        ],
    ]

    # Создаем разметку для кнопок
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=user_id, text=message_text, reply_markup=reply_markup, parse_mode='HTML')


async def set_inline_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, buttons_list: list, message_text: str) -> None:
    logging.info('РЕГИСТРАЦИЯ КНОПОК')
    # Создаем инлайн кнопки
    keyboard = []

    for button in buttons_list:
        logging.info(button)
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

    # Создаем разметку для кнопок
    reply_markup = InlineKeyboardMarkup(keyboard)

    user_id = update.effective_user.id
    await context.bot.send_message(chat_id=user_id, text=message_text, reply_markup=reply_markup, parse_mode='HTML')




async def extra_inline_button(update: Update, context: ContextTypes.DEFAULT_TYPE, inline_message_text, user_id = None, parse_mode=None) -> None:
    # Создаем инлайн кнопки
    keyboard = [
        [
            InlineKeyboardButton("Главное меню", callback_data=f'main_menu')
        ],

    ]
    # Создаем разметку для кнопок
    reply_markup = InlineKeyboardMarkup(keyboard)
    if user_id:
        await context.bot.send_message(chat_id=user_id, text=inline_message_text, reply_markup=reply_markup, parse_mode=parse_mode)
    else:
        await update.message.reply_text(inline_message_text, reply_markup=reply_markup, parse_mode=parse_mode)
