employers_list = {

    10696710: {
        "Санкт-Петербург": "rabotaNZL@reph.ru"
    },
    2763248: {
        "Екатеринбург": "personal@urtu.ru"
    },
    538640: {
        "Брянск": "e.matusevich@turboremont.gesturbo.ru",
        "Щекино": "t.novikova@zavod-rto.su",
        "Наро-Фоминск": "ok@turbonara.ru",
        "Камышин": "ok@rotorcom.ru",
    },


    5436353: "d.grigorova@gehlt.ru",
    # {
    #     "cities_list": "d.grigorova@gehlt.ru"
    # }, # ООО Газпром энергохолдинг индустриальные активы (много городов..)
    3147445: {
        "Тюмень": "kadry@tmotor.ru; k.haibabulina@tmotor.ru"
    }
}


def send_email(employer_id, vacancy_city, subject, body, pdf_file=None):
    """
    employer_id - ID работодателя (например: 10696710)

    vacancy_city - Город вакансии (например: Санкт-Петербург)

    subject - Тема сообщения (например: Отклик пользователя на вакансию)

    body - Текст сообщения (например: Данные об откликнувшемся пользователе)

    pdf_file - Путь к PDF файлу, который нужно отправить (по умолчанию None)

    """
    # Получаем email работодателя по его ID
    # Если ID работодателя не найден, то возвращаем None

    employer_data = employers_list.get(employer_id)
    employer_email = employer_data.get(vacancy_city) if isinstance(employer_data, dict) else employer_data
    if not employer_email:
        print(f"Работодатель с ID {employer_id} не найден.")
        return
    
    # Настройки почтового сервера Mail.ru
    smtp_server = 'smtp.mail.ru'
    smtp_port = 587
    from_email = 'gaz@mail.ru'  # Ваш адрес электронной почты Yandex
    password = os.getenv('GAZ_APP_PASSWORD')  # Ваш пароль приложения Mail.ru
    # Создание сообщения
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = employer_email
    msg['Subject'] = subject
    # Добавление текста в сообщение
    msg.attach(MIMEText(body, 'plain'))
    # Если PDF файл передан, добавляем его к сообщению
    if pdf_file:
        try:
            with open(pdf_file,
                        'rb') as f:
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
        server.quit()
        # Закрытие соединения
        # if __name__ == '__main__':
        # send_email(10696710, "Санкт-Петербург", "Тема сообщения", "Текст сообщения", "путь_к_pdf_файлу")
