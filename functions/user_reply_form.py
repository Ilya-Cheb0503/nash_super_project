import logging

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants.keyboards import (admin_main_menu_keyboard,
                                 user_main_menu_keyboard)
from constants.messages_text import welcome_text
from constants.some_constants import admins_id, group_id
from db_depart.user_db import get_user, update_user_in_db
from functions.inline_buttons import extra_inline_button, set_inline_keyboard
from functions.mail_sender import send_email
from pwd_generator import get_current_directory


async def user_form_information_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = await get_user(user_id)
    user_inf_db = user['user_inf']
    

    if 'Запрос full данных' in context.user_data:
        context.user_data.pop('Запрос full данных')
        warning_text = 'Вы не закончили заполнять пользовательские данные, прежде, чем откликнуться на вакансию.\nПроцесс был прерван.\nДанные не сохранены.'
        await context.bot.send_message(chat_id=user_id, text=warning_text)

    # на случай, если пользователь перед тем, как откликнуться на вакансию заполнял анкету и не закончил ее заполнять
    # тогда мы прерываем этот процесс и начинаем процесс заполнения анкеты для отклика

    if 'information_form' not in context.user_data:
        context.user_data['information_form'] = {}
    user_inf = context.user_data['information_form']
    try:
        current_text = update.message.text
    except Exception:
        current_text = None
        context.user_data['Запрос анкетных данных'] = 'Запуск анкетирования'

    
    step = {
        'Запуск анкетирования': ('Утверждение найденной анкеты', None),
        'Подтверждение старта': ('ФИО', None),
        
        'ФИО': ('Резюме вопрос', 'Хотите прикрепить резюме?'),
        'Резюме вопрос': ('Проверка pdf файла', 'Пожалуйста, пришлите ваше резюме в формате .pdf'),
        'Проверка pdf файла': ('Номер телефона', 'Ваш контактный номер телефона:'),

        'Утверждение найденной анкеты': ('ФИО', 'Хотите прикрепить резюме?'),
        'Доп резюме вопрос': ('Доп pdf файл', None),
        'Доп pdf файл': ('Резюме', None),
        
        'Резюме': ('Номер телефона', 'Ваш контактный номер телефона:'),
        'Номер телефона': ('email', 'Ваш электронный адрес:'),
        'email': ('Должность', 'Желаемая должность:'),
        'Должность': ('Опыт работы', 'Ваш стаж:'),
        'Опыт работы': ('Образование', 'Ваш уровень образования:'),
        'Образование': ('Подтверждение', None),
        'Подтверждение': ('done', None),
        'done': (None, None)
    }
    save_steps = [
        'ФИО', 'Номер телефона', 'email', 'Должность', 'Опыт работы', 'Образование'
        ]

    current_step = context.user_data['Запрос анкетных данных']
    
    if current_text == 'Главное меню' or current_text == 'Назад':
        
        context.user_data['Запрос анкетных данных'] = 'Запуск анкетирования'
        context.user_data.pop('Запрос анкетных данных')
        
        admin_check = user_id in admins_id
        if admin_check:
            context.user_data['admin_status'] = True
            buttons_list = admin_main_menu_keyboard
        else:
            buttons_list = user_main_menu_keyboard

        keyboard = [
            ['Главное меню'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text('Возвращаем вас в главное меню', reply_markup=reply_markup)
        await set_inline_keyboard(update, context, buttons_list = buttons_list, message_text = welcome_text)
        return
    
    if current_step in save_steps:
        context.user_data['information_form'][current_step] = current_text
        await update_user_in_db(user_id, user_inf={current_step:current_text})

    print(context.user_data['Запрос анкетных данных'])
    print(current_step) 
    next_step, message_text = step[current_step]
    context.user_data['Запрос анкетных данных'] = next_step

    if current_step.__eq__('Запуск анкетирования'):

        if 'Образование' in user_inf_db:
                message_text = 'У нас уже есть ваши данные,\nможем использовать их в отклике\nили хотите заполнить анкету заново?'
                keyboard = [
                    ['Продолжить с моими данными'],
                    ['Заполнить заново']
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                await context.bot.send_message(chat_id=user_id, text=message_text, reply_markup=reply_markup)
        else:

            context.user_data['Запрос анкетных данных'] = 'Подтверждение старта'

            text_wait = (
            'Просто отвечайте на вопросы бота,\nа он бережно соберет Ваши данные в анкету 📠\nДля продолжения работы нажмите кнопку внизу экрана.'
        )

            keyboard = [
                ['Согласен с политикой обработки персональных данных ✅'],
                ['Назад']
            ]

            project_folder = await get_current_directory()
            pdf_path = project_folder + '/constants/soglasie-na-obrabotku-dannykh.docx'
            with open(pdf_path, 'rb') as pdf_file:
                await context.bot.send_document(chat_id=user_id, document=pdf_file, filename='Согласие на обработку персональных данных.docx')

            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id=user_id, text=text_wait, reply_markup=reply_markup)

    
    elif current_step.__eq__('Подтверждение старта'):
        text = 'Для начала укажите в сообщении ваши ФИО:'
        keyboard = [
            ['Назад']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        if current_text.__eq__('Согласен с политикой обработки персональных данных ✅'):
            await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)
        
        else:
            context.user_data['Запрос анкетных данных'] = 'Запуск анкетирования'
            context.user_data.pop('Запрос анкетных данных')
            
            admin_check = user_id in admins_id
            if admin_check:
                context.user_data['admin_status'] = True
                buttons_list = admin_main_menu_keyboard
            else:
                buttons_list = user_main_menu_keyboard

            keyboard = [
                ['Главное меню'],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id=user_id, text='Возвращаем вас в главное меню', reply_markup=reply_markup)
            await set_inline_keyboard(update, context, buttons_list = buttons_list, message_text = welcome_text)


    elif current_step.__eq__('ФИО'):
        print(context.user_data['Запрос анкетных данных'])
        context.user_data['Запрос анкетных данных'] = 'Резюме вопрос'
        text = 'Хотите прикрепить резюме?'
        keyboard = [
                ['Да'],
                ['Нет'],
            ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)
    

    elif current_step.__eq__('check'):
        text = 'Для начала укажите в сообщении ваши ФИО:'
        keyboard = [
            ['Назад']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        if current_text.__eq__('Согласен с политикой обработки персональных данных ✅'):
            await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)

        else:
            context.user_data['Запрос анкетных данных'] = 'Запуск анкетирования'
            context.user_data.pop('Запрос анкетных данных')
            
            admin_check = user_id in admins_id
            if admin_check:
                context.user_data['admin_status'] = True
                buttons_list = admin_main_menu_keyboard
            else:
                buttons_list = user_main_menu_keyboard

            keyboard = [
                ['Главное меню'],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id=user_id, text='Возвращаем вас в главное меню', reply_markup=reply_markup)
            await set_inline_keyboard(update, context, buttons_list = buttons_list, message_text = welcome_text)


    elif next_step.__eq__('Резюме вопрос'):
        text = 'Хотите прикрепить резюме?'
        keyboard = [
                ['Да'],
                ['Нет'],
            ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)

    elif current_step.__eq__('Резюме вопрос'):
        
        if current_text.__eq__('Да'):
            context.user_data['Запрос анкетных данных'] = 'Проверка pdf файла'
            text = 'Пожалуйста, пришлите ваше резюме в формате .pdf'
            keyboard = [
                ['Главное меню'],
            ]

            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)

        elif current_text.__eq__('Нет'):

            context.user_data['Запрос анкетных данных'] = 'Номер телефона'
            text = 'Ваш контактный номер телефона:'
            keyboard = [
                ['Главное меню'],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)

    elif current_step.__eq__('Проверка pdf файла'):
        document = update.message.document
        file_name = document.file_name
        if not file_name.lower().endswith('.pdf'):
            await context.bot.send_message(chat_id=user_id, text='Ошибка: файл должен быть в формате PDF.', reply_markup=reply_markup)
            
            context.user_data['Запрос анкетных данных'] = 'Проверка pdf файла'
            
        # Получаем файл
        new_file = await context.bot.get_file(document.file_id)
        project_pwd = await get_current_directory()
        file_path = f"downloads/{file_name}"
        context.user_data['pdf_path'] = f"{project_pwd}/{file_path}"

        await new_file.download_to_drive(file_path)
        
        context.user_data['Запрос анкетных данных'] = 'Номер телефона'
        text = 'Резюме успешно загруженно!\nВаш контактный номер телефона:'
        keyboard = [
            ['Главное меню'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)



    elif current_step.__eq__('Доп резюме вопрос'):
        
        if current_text.__eq__('Да'):
            context.user_data['Запрос анкетных данных'] = 'Доп pdf файл'
            text = 'Пожалуйста, пришлите ваше резюме в формате .pdf'
            keyboard = [
                ['Главное меню'],
            ]

            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)

        elif current_text.__eq__('Нет'):
            context.user_data['Запрос анкетных данных'] = 'Номер телефона'
            text = 'Ваш контактный номер телефона:'
            keyboard = [
                ['Главное меню'],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)
    

    elif current_step.__eq__('Доп pdf файл'):
        document = update.message.document
        file_name = document.file_name
        if not file_name.lower().endswith('.pdf'):
            await context.bot.send_message(chat_id=user_id, text='Ошибка: файл должен быть в формате PDF.')
            
            context.user_data['Запрос анкетных данных'] = 'Доп pdf файл'
            
        # Получаем файл
        new_file = await context.bot.get_file(document.file_id)
        project_pwd = await get_current_directory()
        file_path = f"downloads/{file_name}.pdf"
        context.user_data['pdf_path'] = project_pwd+file_path
        await new_file.download_to_drive(file_path)

        text = 'Резюме успешно загруженно.\nУкажите Ваш контактный номер телефона:'
        context.user_data['Запрос анкетных данных'] = 'Номер телефона'
        keyboard = [
            ['Главное меню'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)


    elif current_step.__eq__('Утверждение найденной анкеты'):

        keyboard = [
                ['Главное меню'],
            ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 

        if current_text.__eq__('Продолжить с моими данными'):
            context.user_data.pop('Запрос анкетных данных')
            
            final_text = (
                'Мы приняли Вашу анкету в работу. Спасибо за уделённое время.\n'
                'Мы изучим вашу анкету и предложим существующие вакансии.\n'
                'Если вы хотите уточнить информацию лично, просим\nобращаться по адресу электронной почты: career@gehia.ru'
            )
            user_inf = user['user_inf']
            user_name = user_inf['ФИО']
            vacancion_name = context.user_data['vacancy_name']

            phone = user_inf['Номер телефона']
            email = user_inf['email']
            work = user_inf['Должность']
            exp = user_inf['Опыт работы']
            educ = user_inf['Образование']

            place = user_inf['Регион поиска']

            user_bio = (
                f'Регион поиска: {place}\n\n'
                f'ФИО: {user_name}\n'
                f'Номер телефона: {phone}\n'
                f'Email: {email}\n'
                f'Должность: {work}\n'
                f'Опыт работы: {exp}\n'
                f'Образование: {educ}\n'
                )


            note_text = f'Пользователь: {user_name}\nОткликнулся на вакансию: {vacancion_name}\n\nПользовательские данные:\n{user_bio}'

                       

            await context.bot.send_message(chat_id=user_id, text='Возвращаемся в главное меню.', reply_markup=reply_markup)
            await extra_inline_button(update, context, final_text,)

            pdf_path = None
            if 'pdf_path' in context.user_data:
                pdf_path = context.user_data['pdf_path']
            await send_email(
                subject = 'Отклик на вакансию',
                body = note_text,
                to_email = 'rabota@ogk2.ru',
                pdf_file = pdf_path
            )
            await context.bot.send_message(chat_id=group_id, text=note_text)
            
            if 'pdf_path' in context.user_data:
                pdf_path = context.user_data['pdf_path']
                # Если есть pdf файл, то мы прикрепляем его к сообщению, а не отправляем отдельно
                await send_pdf(update, context, pdf_path=pdf_path, chat_id=group_id, user_name=user_name)
            
                context.user_data.pop('pdf_path')

        elif current_text.__eq__('Заполнить заново'):

            context.user_data['Запрос анкетных данных'] = 'Подтверждение старта'

            text_wait = (
            'Просто отвечайте на вопросы бота,\nа он бережно соберет Ваши данные в анкету 📠\nДля продолжения работы нажмите кнопку внизу экрана.'
        )

            keyboard = [
                ['Согласен с политикой обработки персональных данных ✅'],
                ['Назад']
            ]

            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            project_folder = await get_current_directory()
            pdf_path = project_folder + '/constants/soglasie-na-obrabotku-dannykh.docx' 
            with open(pdf_path, 'rb') as pdf_file:
                await context.bot.send_document(chat_id=user_id, document=pdf_file, filename='Согласие на обработку персональных данных.docx')  
            await context.bot.send_message(chat_id=user_id, text=text_wait, reply_markup=reply_markup)

    elif next_step.__eq__('email'):
        logging.info(f'ТЕКУЩИЙ ШАГ {current_step} а текст сообщения {current_text}')
        text = 'Ваш электронный адрес:'
        keyboard = [
        ['Главное меню'],
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)

    elif next_step.__eq__('Должность'):
        text = 'Желаемая должность:'
        keyboard = [
                ['Главное меню'],
            ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)

    elif next_step.__eq__('Опыт работы'):
        text = 'Ваш стаж:'
        keyboard = [
        ['менее 1 года'],
        ['1-2 года'],
        ['2-3 года'],
        ['3+ лет']
        
    ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)


    elif next_step.__eq__('Образование'):
        text = 'Ваш уровень образования:'
        keyboard = [
        ['Высшее образование'],
        ['Среднее профессиональное'],
        ['Школьное'],

    ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)
    
    elif next_step.__eq__('Подтверждение'):
        keyboard = [
        ['Всё верно!✅'],
        ['Редактировать'],
        ]
        user_inf = context.user_data['information_form']
        full_name = user_inf['ФИО']
        phone = user_inf['Номер телефона']
        email = user_inf['email']
        work = user_inf['Должность']
        exp = user_inf['Опыт работы']
        educ = user_inf['Образование']
        
        user_bio = (
            f'<b>ФИО:</b>\n{full_name}\n\n'
            f'<b>Номер телефона:</b>\n{phone}\n\n'
            f'<b>Email:</b>\n{email}\n\n'
            f'<b>Должность:</b>\n{work}\n\n'
            f'<b>Опыт работы:</b>\n{exp}\n\n'
            f'<b>Образование:</b>\n{educ}\n\n'
            )
        logging.info(user_bio)
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=user_id, text=user_bio, reply_markup=reply_markup, parse_mode='HTML')
    
    elif current_step.__eq__('Подтверждение'):
        if current_text.__eq__('Всё верно!✅'):
            context.user_data.pop('Запрос анкетных данных')
            
            user_inf = context.user_data['information_form']
            final_text = (
                'Спасибо, что откликнулись! ☺️ Наши специалисты свяжутся с вами в течение 7 дней.\n\n'
                'Если вам не терпится связаться с нами, то напишите нам на почту rabota@ogk2.ru\n\n'
                'Или позвоните по номеру 8-800-30-20-10-9'
            )

            keyboard = [
                ['Главное меню'],
            ]

            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id=user_id, text='Возвращаемся в главное меню.', reply_markup=reply_markup)

            await extra_inline_button(update, context, final_text, user_id=user_id, parse_mode='Markdown')

            user_inf = user['user_inf']
            user_name = user_inf['ФИО']
            vacancion_name = context.user_data['vacancy_name']


            phone = user_inf['Номер телефона']
            email = user_inf['email']
            work = user_inf['Должность']
            exp = user_inf['Опыт работы']
            educ = user_inf['Образование']
            
            place = user_inf['Регион поиска']

            user_bio = (
                f'Регион поиска: {place}\n\n'
                f'Номер телефона: {phone}\n'
                f'Email: {email}\n'
                f'Должность: {work}\n'
                f'Опыт работы: {exp}\n'
                f'Образование: {educ}\n'
                )


            note_text = f'Пользователь: {user_name}\nОткликнулся на вакансию: {vacancion_name}\n\nПользовательские данные:\n{user_bio}'


            pdf_path = None
            if 'pdf_path' in context.user_data:
                pdf_path = context.user_data['pdf_path']
            await send_email(
                subject = 'Отклик на вакансию',
                body = note_text,
                to_email = 'rabota@ogk2.ru',
                pdf_file = pdf_path
            )
            await context.bot.send_message(chat_id=group_id, text=note_text)
            if 'pdf_path' in context.user_data:
                pdf_path = context.user_data['pdf_path']
                # Та же тема с прикреплением документа и отправкой одного смс, а не двух, как делали в телеграмм чате
                await send_pdf(update, context, pdf_path=pdf_path, chat_id=group_id, user_name=user_name)
            
                context.user_data.pop('pdf_path')

        else:
            context.user_data['Запрос анкетных данных'] = 'ФИО'
            keyboard = [
                ['Главное меню'],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id=user_id, text='Тогда начнем сначала.\nУкажите ваши ФИО:', reply_markup=reply_markup)


async def send_pdf(update, context, pdf_path, chat_id, user_name):
    # Путь к вашему PDF-файлу
    pdf_file_path = pdf_path
    pdf_name = f'Резюме {user_name}.pdf'
    with open(pdf_file_path, 'rb') as pdf_file:
        await context.bot.send_document(chat_id=chat_id, document=pdf_file, filename=pdf_name)