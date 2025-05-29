import logging

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants.keyboards import admin_main_menu_keyboard
from constants.messages_text import welcome_text
from db_depart.user_db import get_all_users
from functions.inline_buttons import set_inline_keyboard
from pwd_generator import get_current_directory


async def send_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info('send process')
    # Запрос текста сообщения от пользователя
    message_creator = {
        'Creating' : message_text_getting,
        'Edited' : message_text_confirmation,
        'Completed' : message_text_sending
    }
    if 'message_state' not in context.user_data:
        context.user_data['message_state'] = 'Creating'
    current_message_state = context.user_data.get('message_state')

    current_step = message_creator[current_message_state]

    await current_step(update, context)


async def message_text_getting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    logging.info('edit process')
    context.user_data['message_text'] = None
    user_id = update.effective_user.id
    # await context.bot.send_message(chat_id=user_id, text='Пришлите мне сообщение, которое хотите разослать:', parse_mode='Markdown')

    keyboard = [
        ['Отмена']
        
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    
    await context.bot.send_message(chat_id=user_id, text='Пришлите мне сообщение, которое хотите разослать:', reply_markup=reply_markup)


    context.user_data['message_state'] = 'Edited'

async def message_text_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    logging.info('confirm process')
    user_id = update.effective_user.id
    message_text, image_path = await download_message_with_image(update, context)
    context.user_data['message_inf'] = (message_text, image_path)
    
    keyboard = [
        ['Да'],
        ['Нет'],
        ['Отмена']
        
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if message_text == 'Отмена':

        keyboard = [
        ['Главное меню']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        context.user_data.pop('message_state')
        context.user_data.pop('message_text')
        
        await context.bot.send_message(chat_id=user_id, text='Отмена рассылки. Возвращение в главное меню', reply_markup=reply_markup)
        await set_inline_keyboard(update, context, buttons_list = admin_main_menu_keyboard, message_text = welcome_text)
    
    else:

        await context.bot.send_message(chat_id=user_id, text='Вы хотите отправить следующее сообщение?', reply_markup=reply_markup)
        await forward_message_with_image(update, context, message_text, image_path, user_id)
        context.user_data['message_state'] = 'Completed'


async def message_text_sending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    keyboard = [
        ['Главное меню']
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
    main_id = update.effective_user.id

    message_text = update.message.text
    if message_text == 'Да':
        current_message_text, image_path = context.user_data.get('message_inf')
        users = await get_all_users()  # Получаем всех пользователей
        users_id = [user['telegram_id'] for user in users]

        for user_id in users_id:
            try:
                await forward_message_with_image(update, context, current_message_text, image_path, user_id)
            except Exception as error:
                logging.exception(f"Не удалось отправить сообщение пользователю {user_id}: {error}")

        context.user_data.pop('message_state')
        context.user_data.pop('message_text')
        
        await context.bot.send_message(chat_id=main_id, text='Рассылка завершена.', reply_markup=reply_markup)

    elif message_text == 'Нет':
        context.user_data['message_state'] = 'Creating'
        await message_text_getting(update, context)
    
    elif message_text == 'Отмена':
        context.user_data.pop('message_state')
        context.user_data.pop('message_text')
        
        await context.bot.send_message(chat_id=main_id, text='Отмена рассылки. Возвращение в главное меню', reply_markup=reply_markup)
        await set_inline_keyboard(update, context, buttons_list = admin_main_menu_keyboard, message_text = welcome_text)

    

async def download_message_with_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем текст сообщения
    # message_text = context.user_data.get('current_text')
    message_text = update.message.text
    file_path = None

    if update.message.photo:
        message_text = update.message.caption
        context.user_data['current_text'] = message_text
        photo = update.message.photo[-1]  # Получаем самое высокое качество изображения
        file = await photo.get_file()
        project_pwd = await get_current_directory()

        file_path = f"downloads/{photo.file_id}.jpg"
        context.user_data['photo_path'] = project_pwd+file_path  # Путь для сохранения изображения
        await file.download_to_drive(file_path)

        return message_text, file_path

    else:
        # Если изображения нет, просто отправляем текст
        return message_text, file_path


async def forward_message_with_image(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text, image_path, user_id) -> None:
    
    # Проверяем, есть ли вложение (изображение)
    if image_path:

        # Отправляем новое сообщение с изображением и текстом
        with open(image_path, 'rb') as img_file:
            await context.bot.send_photo(chat_id=user_id, photo=img_file, caption=message_text, parse_mode='Markdown')
    else:
        # Если изображения нет, просто отправляем текст
        await context.bot.send_message(chat_id=user_id, text=message_text, parse_mode='Markdown')

