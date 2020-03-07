from requests_html import HTMLSession

host = "https://perevozka24.ru"


def cities(url, region):
    with HTMLSession() as session:
        response = ""
        while not response:
            try:
                response = session.get(url)
            except Exception:
                response = ""

    cities_name = response.html.xpath("//div[@class='city-list']//a")
    if cities_name:
        cities_urls = response.html.xpath("//div[@class='city-list']//a//@href")
        cities_urls = [host + i for i in cities_urls]
        cities_name = [i.text for i in cities_name]
        print("Region: ", region)
        return list(zip(cities_name, cities_urls))
    else:
        name = response.html.xpath("//div[@class='main']/span")[0].text
        print("City:", name)
        return None
