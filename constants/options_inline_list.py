from constants.company_info import *
from constants.keyboards import *
from constants.messages_text import contacts_info, welcome_text, social_media, FQA_info

get_vacancies_options = {
    'risk': 'show_all',
}

but_opt = {
'region': [
    'Выберите регион поиска.',
    
    [
        ['г. Санкт-Петербург', 'Санкт-Петербург'],
        ['г. Москва', 'Москва'],
        ['Московская Область', 'Московская Область'],
        ['г. Тюмень', 'Тюмень'], 
        ['г. Брянск', 'Брянск'],
        ['г. Щекино, Тульская обл.', 'Щекино'], # , Тульская обл.
        ['г. Камышин, Волгоградская обл.', 'Камышин'], # , Волгоградская обл.
        ['г. Екатеринбург', 'Екатеринбург'],
        ['г. Узловая', 'Узловая']
]
],


'vacancies': [
    'Какую работу Вы ищете?\nВыберите нужный пункт.',
    
    [
        ['Все вакансии', 'show_all'],
        ['Вакансии по направлениям деятельности', 'categories'],
        ['Без опыта работы', 'no_exp'],
        # ['Перезвоните мне', 'user_data'],
        ['Главное меню', 'main_menu'],
    ]
],

'show_all': [
    'develop', # добавить вызов функции и определять количество вакансий или добавить в расписанин способ его обновления и тогда просто подставляем готовое значение в текст
    [
        ['Да, я готов 🔍', 'risk'],
        ['Назад', 'vacancies'],
    ]
],
'risk': [
    'will be soon',
    None
],



'categories': [
    'Выберите область профессиональной деятельности.',
    [

        ['Руководители', 'leadership'],
        ['ИТР', 'ITR'],
        ['Рабочие', 'workers'],
        ['Другие категории', 'other_categories'],
        ['Назад', 'vacancies']

    ]
],
'power_vacancies': [
    'Выберите нужную подкатегорию',
    [
        ['Теплоэнергетика', 'power'],
        ['Электроэнергетика', 'energy'],
        [
            ['АСУ ТП', 'ACY'],
            ['РЗА', 'PZA']
        ],
        [
            ['Ремонт', 'repair'],
            ['Химия', 'chemichal']
        ],
        # [
        #     ['HR', 'powe_HR'],
        #     ['ИТ', 'pow_IT']
        # ],
        # [
        #     ['Экономика', 'pow_economy'],
        #     ['Сбыт', 'sales']
        # ],
        # ['Промышленная безопасность и охрана труда', 'pow_safe'],
        ['Другое', 'other'],
        ['Назад', 'categories'],
    ]
],

'power': [
    '0',
    None
],
'energy': [
    '1',
    None
],
'ACY': [
    '2',
    None
],
'PZA': [
    '3',
    None
],
'repair': [
    '4',
    None
],
'chemichal': [
    '5',
    None
],
'powe_HR': [
    '6',
    None
],
'pow_IT': [
    '7',
    None
],

'pow_economy': [
    '8',
    None
],
'sales': [
    '9',
    None
],
'pow_safe': [
    '10',
    None
],
'other': [
    '11',
    None
],


'ofice_vacancies': [
    'Выберите нужную подкатегорию',
    [
        [
            ['Закупки', 'customs'],
            ['Экономика', 'ofi_economy']
        ],
        [
            ['HR', 'powe_HR'],
            ['ИТ', 'pow_IT']
        ],
        [
            ['Экономика', 'pow_economy'],
            ['Сбыт', 'sales']
        ],
        ['Промышленная безопасность и охрана труда', 'pow_safe'],
        [
            ['Юриспруденция', 'laws'],
            ['Производственное управление', 'prod_control']
        ],
        ['Промышленная безопасность и охрана труда', 'ofi_safe'],
        ['Назад', 'categories']
    ]
],


'customs': [
    '0',
    None
],
'ofi_economy': [
    '1',
    None
],
'ofi_HR': [
    '2',
    None
],
'ofi_sales': [
    '3',
    None
],
'ofi_IT': [
    '4',
    None
],
'laws': [
    '5',
    None
],
'prod_control': [
    '6',
    None
],
'ofi_safe': [
    '7',
    None
],

'duty_vacancies': [
    'Какая-то ошибка',
    None
],

'no_exp': [
    'Какая-то ошибка',
    None
],

'student': [
    'Выберите интересующий пункт',
    [
        ['Практика', 'student_pactice'],
        ['Целевое обучение', 'student_study'],
        ['Сотрудничество с вузами', 'student_cooperation'],
        ['Временное трудоустройство', 'student_time_work'],
        ['Постоянная работа', 'region'],
        ['Главное меню', 'main_menu'],
    ]
],

'student_pactice': [
    student_pactice_text,
    None
],

'student_study': [
    student_study_text,
    None
],

'student_cooperation': [
    student_cooperation_text,
    None
],

'student_time_work': [
    student_time_work_text,
    None
],

'about_company': [
    company_text,
    [
        ['Преимущества работы', 'benefits'],
        # ['Предприятия ГЭХИА', 'filiales'],
        # ['Основные направления деятельности', 'main_actions'],
        # ['Мотивационные и социальные программы', 'soc_programms'],
        ['Главное меню', 'main_menu'],
    ]
],
'benefits': [
    company_benefit,
    None
],
'filiales': [
    company_filiales,
    None
],

'main_actions': [
    main_actions,
    None
],

'soc_programms': [
    '👥 Что нас объединяет',
    [
        ['Кадровый резерв и преемственность', 'persons_reserve'],
        ['Обучение и развитие', 'prof_prep'],
        ['Конкурсы профессионального мастерства ', 'prof_masters'],
        ['Спорт', 'sport'],
        ['Культурно-массовые мероприятия', 'mass_events'],
        ['Совет молодых специалистов', 'juns_senate'],
        ['Назад', 'about_company'],
    ]
],
'persons_reserve': [
    motivations_programms[0],
    None
],
'prof_prep': [
    motivations_programms[1],
    None
],
'prof_masters': [
    motivations_programms[2],
    None
],
'sport': [
    motivations_programms[3],
    None
],
'mass_events': [
    motivations_programms[4],
    None
],
'juns_senate': [
    motivations_programms[5],
    None
],


'FQA': [
    FQA_info,
    None
],
'work_plan': [
    FAQ[0],
    None
],
'pay_lvl': [
    FAQ[1],
    None
],
'out_cities': [
    FAQ[2],
    None
],
'social_garants': [
    FAQ[3],
    None
],
'adresses': [
    FAQ[4],
    None
],
'whiches_no_exp': [
    FAQ[5],
    None
],


'user_data': [
    '0',
    None
],

'contacts': [
    contacts_info,
    None
],

'social_media' : [
    social_media,
    None
],

"admin_soft": [
        "Выберите опцию",
        [["Рассылка", "postman"], ["Метрика", "analiz"], ["Редактировать текст", "edit_text"], ["Главное меню", "main_menu"]],
    ],

"edit_text": [
    "Выберите раздел, текст которого необходимо отредактировать",
    [["Приветственное сообщение", "edit_welcome_text"], 
     ["Контакты", "edit_contacts_text"], 
     ["Соц. cети", "edit_social_media_text"],
     ["Информация о компании", "edit_company_info_text"],
     ["Назад", "admin_soft"]]
],

"edit_welcome_text":[
    f"Так выглядит приветственное сообщение на данный момент:\n\n{welcome_text}", #получать не из переменной, а из json файла
    None
],

"edit_contacts_text":[
    f"Так выглядит сообщение с контактной информацией на данный момент:\n\n{contacts_info}", #получать не из переменной, а из json файла
    None
],

"edit_social_media_text":[
    f"Так выглядит сообщение с указанием соц.сетей на данный момент:\n\n{social_media}", #получать не из переменной, а из json файла
    None
],

"edit_company_info_text":[
    f"Так выглядит сообщение с информацией о компании на данный момент:\n\n{company_text}", #получать не из переменной, а из json файла
    None
],

'postman': [
    'postman',
    None
],

'main_menu': [
    welcome_text,
    [
    user_main_menu_keyboard,
    admin_main_menu_keyboard
    ]
]
}