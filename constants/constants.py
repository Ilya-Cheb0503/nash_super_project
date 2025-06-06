import os

from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

group_id = '-1002434691003'
dev_id = 2091023767
admins_id = [787264207, 155771631]


stat_bank = {
        "keys_word": {},
        "categories": {},
        "replies": {},
        "year": {
            "Январь": 0,
            "Февраль": 0,
            "Март": 0,
            "Апрель": 0,
            "Май": 0,
            "Июнь": 0,
            "Июль": 0,
            "Август": 0,
            "Сентябрь": 0,
            "Октябрь": 0,
            "Ноябрь": 0,
            "Декабрь": 0,
        },
    }

aditable_text = {
    "welcome": "",
    "contacts": "",
    "social_media": "",
    "company_info": ""
    }
