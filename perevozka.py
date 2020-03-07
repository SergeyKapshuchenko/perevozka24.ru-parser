from requests_html import HTMLSession
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor

import csv

locker = Lock()

host = "https://perevozka24.ru"

# Переменные, которые нужно заменить в файле ( при открытии csv файла)

read_file_perevozki = "Cities_perevozki.csv"
read_file_gruzoperevozki = "Cities_gruzoperevozki.csv"
read_file_spetstechnika = "Cities_spetstechnika.csv"

write_file_perevozki = "Data3.csv"
write_file_gruzoperevozki = "Data2.csv"
write_file_spetstechnika = "Data1.csv"


def crawler():
    links1 = []
    links2 = []
    links3 = []

    # Вставить файл, с которого читаем ссылки

    with open(read_file_perevozki, mode='r') as read_file:
        reader = csv.reader(read_file, delimiter=';')
        reader.__next__()

        for row in reader:
            links1.append(row[3])
            links2.append(row[0])
            links3.append(row[2])

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(city, links1, links2, links3)


def city(url, region_name, city_name):
    print("City name: ", city_name)
    with HTMLSession() as session:
        response = ""
        while not response:
            try:
                response = session.get(url)
            except Exception as e:
                print("Error in city: ", type(e))
                response = ""

    types_name = response.html.xpath("//div[@class='show_group']//a")

    for i in range(len(types_name)):
        type_name = types_name[i].text.split(' в ')[0]
        type_url = host + types_name[i].attrs['href']
        Thread(target=single_type, args=(type_url, type_name, region_name, city_name,)).start()


def single_type(url1, type_name, region_name, city_name):
    with HTMLSession() as session:
        response = ""
        while not response:
            try:
                response = session.get(url1)
            except Exception as e:
                print("Error in single_type: ", type(e))
                response = ""

    names = response.html.xpath("//div[@class='content']/div[@class='last']/div[@class='block' or 'block pseudo']//a")
    prices = response.html.xpath(
        "//div[@class='content']/div[@class='last']/div[@class='block' or 'block pseudo']//div[@class='price']")

    profiles_info = response.html.xpath(
        "//span[@class='' or 'verified']//i[@class='javalnk' or @class='h4 inline-block m0']")

    profiles = []
    for i in profiles_info:
        try:
            profile = i.attrs['rel'][0]
            profiles.append(check_profile(host + "/" + profile))
        except KeyError:
            profiles.append("Частное Лицо")

    for i in range(len(names)):
        result = {
            'Область': region_name,
            'Город': city_name,
            'Тип оборудования': type_name,
            'Название обьявления': names[i].text,
            'Стоимость': prices[i].text,
            'Ссылка': host + names[i].attrs['href'],
            'Признак': profiles[i],
        }

        with locker:
            # Файл в который сохраняем данные
            with open(write_file_perevozki, mode='a') as write_file:
                fieldnames = ['Область', 'Город', 'Тип оборудования', 'Название обьявления', 'Признак', 'Стоимость',
                              'Ссылка']
                writer = csv.DictWriter(write_file, delimiter=';', fieldnames=fieldnames)
                writer.writerow(result)


def check_profile(profile):
    with HTMLSession() as session1:
        response = ""
        while not response:
            try:
                response = session1.get(profile)
            except Exception as e:
                print("Error in profile: ", type(e))
                response = ""

    title = response.html.xpath("//h1[@id='detail_name']")[0].text

    if "Компания" in title:
        return "Компания"
    elif len(title.split()) > 3:
        try:
            req = response.html.xpath("//div[@id='company-details']//p")[0].text
        except IndexError:
            return "Частное лицо"
        if "ИНН" in req:
            return "ИП"
    return "Частное лицо"


crawler()
