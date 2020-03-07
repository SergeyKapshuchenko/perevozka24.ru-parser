from requests_html import HTMLSession

import random

import csv

from region_parser import cities

host = "https://perevozka24.ru"

url_spets = "https://perevozka24.ru/arenda-spetstehniki"
url_gruzoperevozki = "https://perevozka24.ru/gruzoperevozki"
url_perevozki = "https://perevozka24.ru/arenda-passazhirskogo-transporta"

write_file_perevozki = "Cities_perevozki.csv"
write_file_gruzoperevozki = "Cities_gruzoperevozki.csv"
write_file_spetstechnika = "Cities_spetstechnika.csv"


def regions(url):
    with HTMLSession() as session:
        response = ""
        while not response:
            try:
                response = session.get(url)
            except Exception:
                response = ""

    all_regions = []
    regions_name = response.html.xpath("//div[@class='region-wrapper mb15 collaspe collapse in hidden-xs']//a")
    regions_url = response.html.xpath("//div[@class='region-wrapper mb15 collaspe collapse in hidden-xs']//a/@href")

    for index in range(len(regions_name)):
        region_name = regions_name[index].text.split('(')[0][:-1]
        region_url = host + regions_url[index]
        region_cities = cities(region_url, region_name)

        if region_cities:
            all_regions.append({
                'region name': region_name,
                'region url': region_url,
                'cities': region_cities
            })

    # Файл в который сохраняем
    with open(write_file_spetstechnika, mode='w') as csv_file:
        fieldnames = ['region name', 'region url', 'city', 'city url']
        writer = csv.DictWriter(csv_file, delimiter=';', fieldnames=fieldnames)

        writer.writeheader()
        for single_region in all_regions:
            name = single_region['region name']
            url = single_region['region url']
            for city in single_region['cities']:
                writer.writerow({'region name': name, 'region url': url, 'city': city[0], 'city url': city[1]})

    print("Successfully Done")


regions(url_perevozki)
