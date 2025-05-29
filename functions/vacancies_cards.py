import re

from settings import logging


async def message_creater(vacancy):
    for key, value in vacancy.items():
        if type(value) == list:
            value = ', '.join(value)
            vacancy[key] = value

        if str(value) == '' or str(value) == 'None':
            vacancy[key] = 'Нет данных.\n'

    if 'None' in vacancy['Оплата ОТ']:
        vacancy['Оплата ОТ'] = ''
    if 'None' in vacancy['Оплата ДО']:
        vacancy['Оплата ДО'] = ''


    vacancy_name = vacancy['Вакансия']

    # valute = vacancy['Валюта']
    min_salary = vacancy['Оплата ОТ']
    max_salary = vacancy['Оплата ДО']
    min_max_salary_str = f'{min_salary}{max_salary}'
    if min_max_salary_str == '':
        min_max_salary_str = 'Нет данных\n'
    
    req_text = vacancy['Требования']
    if req_text != 'Нет данных.\n':
        logging.info(f'ПРОВЕРКА:\nreq_text = !!{req_text}!!\ntype ={type(req_text)}\n')
        requirement = vacancy['Требования'].split('. ')
        req_text = '\n'
        for req in requirement:
            
            if len(req) > 3:
                if req[0] == '-':
                    req = req[1::]
                req_text += f'- {req}.\n'
    
    resp_text = vacancy['Обязанности']
    if resp_text != 'Нет данных.\n':
        responsibilities = vacancy['Обязанности'].split('. ')
        resp_text = '\n'
        for resp in responsibilities:
            if resp != '': 
                resp_text += f'- {resp}.\n'

    schedule = vacancy['Рабочий график']

    experience = vacancy['Наличие опыта']
    if 'Нет опыта' in experience:
        experience = 'рассматриваются кандидаты без опыта работы'
    
    employment = vacancy['Занятость']

    vacancy_url = vacancy['Ссылка на вакансию']
    
    employer_name = vacancy['Компания']

    vacancy_text = (
    f'<b>Компания: {employer_name}</b>\n\n'

    f'<b>Вакансия: {vacancy_name}</b>\n\n'

    f'💰 <u><b>Оплата</b></u>:\n'
    f'{min_max_salary_str}\n'

    f'📋 <u><b>Требования</b></u>: {req_text}\n'

    f'⚙️ <u><b>Обязанности</b></u>: {resp_text}\n'

    f'🕒 <u><b>Рабочий график</b></u>: {schedule}.\n\n'

    f'👥 <u><b>Наличие опыта</b></u>: {experience}.\n\n'

    f'📅 <u><b>Занятость</b></u>: {employment}.\n\n'

    f'🔗 <a href="{vacancy_url}">Ссылка на вакансию</a>\n\n'

    'Присоединяйтесь к нашей команде! 💡✨'
    )

    return vacancy_text


async def inf_taker(full_information):
    tight_information = []
    for vac in full_information:
        new_vac = {}
        new_vac['id Вакансии'] = vac['id']

        new_vac['Компания'] = vac['employer']['name']

        new_vac['Регион'] = vac['area']['name']
        
        new_vac['Название Компании'] = vac['employer']['name']
        new_vac['Вакансия'] = vac['name']
        
        # new_vac['Валюта'] = vac['salary']['currency']
        try:
            valute = vac['salary']['currency']
            if valute.__eq__('RUR'):
                valute = 'руб'
            value_m = vac['salary']['from']
            new_vac['Оплата ОТ'] = f'От {value_m} {valute}\n'
            
            value_max = vac['salary']['to'] 
            new_vac['Оплата ДО'] = f'До {value_max} {valute}\n'
        except Exception:
            new_vac['Оплата ОТ'] = f'От: Нет данных\n'
            new_vac['Оплата ДО'] = f'До: Нет данных\n'
        
        # new_vac['изображение'] = vac['employer']['logo_urls']['original']
        work_req = vac['snippet']['requirement']
        if work_req:
            new_vac['Требования'] = re.sub(r'<[^>]+>', '', work_req)
        else:
            new_vac['Требования'] = None
        work_resp = vac['snippet']['responsibility']
        if work_resp:
            new_vac['Обязанности'] = re.sub(r'<[^>]+>', '', work_resp)
        else:
            new_vac['Обязанности'] = None

        new_vac['Рабочий график'] = vac['schedule']['name']

        new_vac['Наличие опыта'] = vac['experience']['name'] 

        new_vac['Занятость'] = vac['employment']['name']

        
        # new_vac['город'] = vac['address']['city']
        try:
            m_s = vac['address']['metro_stations']
            new_vac['Станции метро'] = []
            for metro_stations in m_s:
                # new_vac['станции метро'].append(metro_stations['station_name'], metro_stations['line_name'])
                new_vac['Станции метро'].append(metro_stations['station_name'])

        except Exception:
            pass
        
        
        new_vac['Ссылка на вакансию'] = vac['alternate_url']
        new_vac['Ссылка на работодателя'] = vac['employer']['alternate_url']
        tight_information.append(new_vac)
        
    return tight_information
