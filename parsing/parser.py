import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests import HTTPError
from pathlib import Path

url = "https://ratcatcher.ru/media/summer_prac/parcing/1/index.html"


def get_html(link):
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    response = requests.get(link, headers=user_agent)
    try:#проверяем ответ, если ошибка, то возвращаем ее, иначе суп
        response.raise_for_status()
    except HTTPError:
        return HTTPError
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def parse_links(html):
    a = html.find_all('a')#ищем все "а", так как в них ссылки
    href = [] #пустой список для ссылок
    for i in a: #перебор списка
        source = i['href']
        href.append(source) #с заполнением его ссылками
    return href


def get_table_headers(header_link):
    html = get_html(header_link)#получем html у ссылки, в которой хотим найти заголовки
    if html != HTTPError:#если пришел корректный html, то работаем с ним
        table_part = html.select_one('table').select('tr')#ищем строку, которая содержит индексы
        table_headers = [th.text for th in table_part[0].select('th')]#записываем их в список
        return table_headers
    else:
        print(f"Не удалось получить заголовки из {header_link}")


def write_error_links(error_link):
    with open('log.txt', 'a') as file:#открываем файл для дозаписи ссылок, с которыми какие-то проблемы, если файла нет, он создастся автоматически
        file.write(f"{error_link}\n")#записываем ссылку, после ставим символ новой строки
    print(f"ошибка обработки {error_link}")


def collect_table_from_list(list_of_links):
    raw_table = []#создаем пустую таблицу, которую будем заполнять данными со ссылок

    for i in list_of_links:#проходим по списку ссылок
        try:
            html = get_html(i)#для каждой из них получаем html
            table_part = html.select_one('table').select('tr')#ищем таблицу
            rows = [#ищем строки
                [td.text for td in tr.select('td')]
                for tr in table_part[1:]
            ]
            for j in rows:
                raw_table.append(j) #добавляем их в таблицу
            print(f"Ссылка №{list_of_links.index(i)+1}")#вывод для отслеживания прогресса
        except AttributeError:
            write_error_links(i)#при ошибке записываем ссылку в логи

    table = pd.DataFrame(raw_table)
    return table



if __name__ == '__main__':
    user_input = "0"#значение по умолчанию
    logs = Path("log.txt")
    if logs.exists():#если есть файл с логами (раньше какие-то ссылки не работали) то спрашиваем
        user_input = input("Введите:\n0, если нужно пройти по всем ссылкам\n1, если нужно пройти только по ссылкам из файла log.txt\n")

    start_page = get_html(url)

    if start_page != HTTPError:
        if user_input == "0":#если файла логов нет или пользователь ввел 0, то проходим по всем ссылкам
            link_list = parse_links(start_page)
        else:
            with open('log.txt', 'r', encoding='utf-8') as file:#иначе только по ссылкам из логов
                link_list = file.read().splitlines()

        headers = None
        for item in link_list:#проходим по всем ссылкам
            headers = get_table_headers(item)#в поисках заголовка
            if headers is not None:#пока не найдем
                break

        collect_table_from_list(link_list).to_csv("Dataset.csv", index=False, header=headers)#когда прошли по всем ссылкам - сохраняем в CSV

    elif start_page == HTTPError:
        print("начальная ссылка возвращает ошибку")