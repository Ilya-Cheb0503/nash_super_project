import asyncio
import json
import os

from playwright.async_api import async_playwright

from pwd_generator import get_current_directory


async def parse_data(url, output_file):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Headless-режим для браузера
        page = await browser.new_page()
        await page.goto(url)

        # Ждем, пока загрузится контейнер с элементами
        await page.wait_for_selector('div.spoiler-block')
        spoiler_blocks = await page.query_selector_all('div.spoiler-block')

        # results = {
        #     'Ставропольский край': [],
        #     'Ленинградская область': [],
        #     'Челябинская область': [],
        #     'Ростовская область': [],
        #     'Псковская область': [],
        #     'Краснодарский край': [],
        #     'Чеченская Республика': [],
        #     'Амурская область': [],
        #     'Вологодская область': [],
        #     'Ханты-Мансийский автономный округ - Югра': [],
        #     'Рязанская область': [],
        #     'Свердловская область': [],
        #     'unknown': []
        # }  # Список для хранения собранных данных
        
        results = []

        for block in spoiler_blocks:
            card_data = {}  # Словарь для хранения данных одной карточки

            # Извлекаем название должности
            title_element = await block.query_selector("a.dd-click")
            if title_element:
                title_text = await title_element.inner_text()
                card_data["Должность"] = title_text.strip()  # Удаляем лишние пробелы

            dd_inner = await block.query_selector('div.dd-inner')
            if dd_inner:
                # Извлекаем "Обязанности", "Требования" и "Условия"
                sections = ["Обязанности", "Требования", "Условия"]
                for section in sections:
                    try:
                        # Ищем заголовок <p><strong>...</strong> и следующий <ul>
                        title_element = await dd_inner.query_selector(f"p:has(strong:has-text('{section}'))")
                        if title_element:
                            list_element = await title_element.evaluate_handle(
                                """(el) => el.nextElementSibling && el.nextElementSibling.tagName === 'UL' ? el.nextElementSibling : null"""
                            )
                            if list_element:
                                list_items = await list_element.query_selector_all('li')
                                list_text = "\n- ".join([await li.inner_text() for li in list_items if li])
                                card_data[section] = list_text
                    except Exception as e:
                        print(f"Ошибка при обработке раздела '{section}': {e}")

                # Извлекаем данные о "Контактном лице"
                try:
                    
                    contact_title = await dd_inner.query_selector("p:has-text('Контактное лицо')")
                    if contact_title:
                        region_name = None
                        contact_data = []

                        # Извлекаем все следующие <p> после заголовка "Контактное лицо"
                        contact_paragraphs = await contact_title.query_selector_all("~ p")
                        for i, paragraph in enumerate(contact_paragraphs):
                            if i == 0:  # Если это первый <p>, ищем <strong> для ФИО
                                strong_element = await paragraph.query_selector("strong")
                                if strong_element:
                                    fio_text = await strong_element.inner_text()
                                    contact_data.append(f"ФИО: {fio_text.strip()}")  # Удаляем лишние пробелы
                            else:
                                # Все остальные <p> содержат должность, телефон и email
                                text = await paragraph.inner_text()
                                contact_data.append(text.strip())  # Удаляем лишние пробелы
                                region_name = await region_determ(contact_data)
                                
                        card_data["Контактное лицо"] = "\n".join(contact_data)
                        card_data["Регион"] = region_name
                except Exception as e:
                    print(f"Ошибка при обработке данных о контактном лице: {e}")
                if region_name:
                    # results[region_name].append(card_data)
                    results.append(card_data)

        await browser.close()
        return results
        # Сохраняем результаты в файл
        # with open(output_file, "w", encoding="utf-8") as f:
        #     for i, card in enumerate(results, 1):
        #         f.write(f"=== Карточка {i} ===\n")
        #         for title, content in card.items():
        #             f.write(f"{title}:\n{content}\n\n")
        #         f.write("\n")

        # await save_vacancies_info(results)


vacancies_info_file = '/data_holder/vacancies_info.json'

async def load_vacancies_keys():
    
    project_folder = await get_current_directory()
    vacancies_info_path = project_folder + vacancies_info_file
    
    if os.path.exists(vacancies_info_path):
        with open(vacancies_info_path, 'r', encoding="utf-8") as file:
            vacancies_info = json.load(file)
            return vacancies_info
    
    return {}


async def save_vacancies_info(vacancies_info):
    # logging.info("Сохранение уведомлений в файл.")
    
    project_folder = await get_current_directory()
    vacancies_info_path = project_folder + vacancies_info_file
    
    with open(vacancies_info_path, 'w', encoding="utf-8") as file:
        json.dump(vacancies_info, file, ensure_ascii=True, indent=4)
    



async def region_determ(contact_info):
    region_name = None
    for fio in fio_reg.keys():
        if fio in contact_info[0]:
            region_name = fio_reg[fio]
            return region_name

fio_reg = {
    'Беховых': 'Ростовская область',
    'Родионов': 'Ставропольский край',
    'Гаврилюк': 'Краснодарский край',
    'Кирильчева': 'Ленинградская область',
    'Петрова': 'Псковская область',
    'Лихачева': 'Свердловская область',
    'Зубакова': 'Челябинская область',
    'Романенко': 'Амурская область',
    'Музаева': 'Чеченская Республика',
    'Леонтьева': 'Ханты-Мансийский автономный округ - Югра',
    'Миловкина': 'Вологодская область',
    'Сурнина': 'Рязанская область',
    'Other': 'Остальное'
    }


# URL страницы с вакансиями
url = "https://www.ogk2.ru/karera/"  # Замените на ваш URL
output_file = "parsed_data_new.txt"  # Файл для сохранения результатов
async def main():
    await parse_data(url, output_file)
    print(f"Данные успешно сохранены в файл: {output_file}")
if __name__ == "__main__":
    # Запускаем асинхронный парсер

    asyncio.run(main())