import asyncio
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from dotenv import load_dotenv

load_dotenv()
OGK_APP_PASSWORD = os.getenv('OGK_APP_PASSWORD')

async def send_email(subject, body, to_email='rabota@ogk2.ru', pdf_file=None):
    '''
    subject - Тема сообщения (например: Отклик пользователя на вакансию)

    body - Текст сообщения (например: Данные об откликнувшемся пользователе)

    to_email - email адрес, на который будет направлено уведомление в виде сообщения (например об отклике или заполненных анкетных данных)

    pdf_file - Путь к PDF файлу, который нужно отправить (по умолчанию None)
    '''
    # Настройки почтового сервера Mail.ru
    smtp_server = 'smtp.mail.ru'
    smtp_port = 587
    from_email = 'botogk2@mail.ru'  # Ваш адрес электронной почты Yandex
    password = OGK_APP_PASSWORD  # Ваш пароль приложения Mail.ru

    # Создание сообщения
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Добавление текста в сообщение
    msg.attach(MIMEText(body, 'plain'))

    # Если PDF файл передан, добавляем его к сообщению
    if pdf_file:
        try:
            with open(pdf_file, 'rb') as f:
                part = MIMEApplication(f.read(), Name='Резюме.pdf')
            part['Content-Disposition'] = f'attachment; filename="Резюме"'
            msg.attach(part)
        except Exception as e:
            print(f"Ошибка при добавлении PDF файла: {e}")

    try:
        # Подключение к почтовому серверу
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Защита соединения
        server.login(from_email, password)  # Вход в почтовый аккаунт
        server.send_message(msg)  # Отправка сообщения
        print("Письмо успешно отправлено!")
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")
    finally:
        server.quit()  # Закрытие соединения

# if __name__ == '__main__':
    # await send_email("TEST thema", "TEST message", "rabota@ogk2.ru")