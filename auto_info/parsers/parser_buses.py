import os
import time
from io import BytesIO

import django
import requests
from bs4 import BeautifulSoup
from django.utils.text import slugify
from url_normalize import url_normalize
from django.core.files import File
from werkzeug.urls import url_fix

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_info.settings')
django.setup()

from buses.models import Modification, Brand, Model, Generation

session = requests.Session()
url = 'https://en.wikipedia.org'


def parse(url, tag, attrs, first=False):
    response = session.get(url)
    soup = BeautifulSoup(response.content, features="html5lib")
    if first:
        return soup.find(tag, attrs)
    return soup.find_all(tag, attrs)


def getImageByUrl(image_url):
    image_url = url_normalize(image_url)
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
        'cache-control': 'no-cache',
        'cookie': 'WMF-Last-Access=23-Dec-2021',
        'pragma': 'no-cache',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    }
    img = session.get(url_fix(image_url), headers=headers)
    if img.status_code != 200:
        print(img.status_code, image_url)
        exit()
    return BytesIO(img.content)


# Remove empty Brands
# for brand in Brand.objects.all():
#     if not Model.objects.filter(brand=brand):
#         brand.delete()

def setBrand(soup):
    exist = Brand.objects.filter(name=soup.text.strip()).first()

    if exist:
        print('-- Brand:', exist, 'exist')
        return exist

    name = soup.text.strip()
    detail_path = soup.find('a').get('href') if soup.find('a') else None

    image_url = None
    image_name = None
    if detail_path:
        full_path = url + detail_path if not 'wikipedia.org' in detail_path else detail_path

        detail_soup = parse(full_path, 'td', {'class': {'infobox-image', 'logo'}}, True)
        if detail_soup:
            image_soup = detail_soup.find('img')
            if image_soup:
                image_url = url_fix(image_soup.get('src'))
                image_name = str(slugify(name) + '.' + image_url.split('.')[-1])

    obj = Brand()
    obj.name = name
    if image_url:
        obj.image.save(
            image_name,
            File(
                getImageByUrl(image_url)
            )
        )
    obj.save()
    print('-- Brand:', obj, 'crated')
    return obj


def setModel(soup, brand, image_url):
    exist = Model.objects.filter(name=soup.text.strip()).first()
    if exist:
        if image_url:
            image = parse(image_url, 'div', {'class': 'fullImageLink'}, True)
            image_tag = image.find('a') if image else image
            image_path = image_tag.get('href') if image else image
            if image_path:
                image_name = slugify(brand.name + '-' + soup.text.strip()) + '.jpg'
                print('image_path', image_name)

                exist.image.save(
                    image_name,
                    File(
                        getImageByUrl(image_path)
                    )
                )
        print('-- Model:', exist, 'exist')
        return exist

    obj = Model()
    obj.brand = brand
    obj.name = soup.text.strip()

    if image_url:
        image = parse(image_url, 'div', {'class': 'fullImageLink'}, True)
        print('IMAGE', image)
        image_name = slugify(brand.name + '-' + soup.text.strip() + str(image_url.split('.')[-1]))
        obj.image.save(
            image_name,
            File(
                getImageByUrl(image_url)
            )
        )

    obj.save()
    print('-- Model:', obj, 'created')
    return obj


def setGeneration(model):
    exist = Generation.objects.filter(model=model, name='1').first()
    if exist:
        print('-- Generation:', exist, 'exist')
        return exist
    obj = Generation()
    obj.model = model
    obj.name = '1'
    obj.save()
    print('-- Generation:', obj, 'created')
    return obj


def setModification(generation, class_, assembly, years):
    year_inits = ''.join(filter(str.isdigit, years))
    start_prod = year_inits[0:4] if year_inits[0:4] else None
    end_prod = year_inits[4:8] if year_inits[4:8] else None
    exist = Modification.objects.filter(generation=generation, assembly=assembly, gen_class=class_).first()
    if exist:
        print('-- Modification:', exist, 'exist')
        return exist

    obj = Modification()
    obj.generation = generation
    obj.assembly = assembly
    obj.start_prod = start_prod
    obj.end_prod = end_prod
    obj.gen_class = class_
    obj.save()
    print('-- Modification:', obj, 'created')
    return obj


def trucks(url, path, len_=8):
    tablesSoup = parse(url + path, 'table', {'class': 'wikitable'})
    for tableSoup in tablesSoup:
        for rowSoup in tableSoup.find_all('tr'):
            colsSoup = rowSoup.find_all('td')
            if len(colsSoup) == len_:
                brand_soup = colsSoup[0]
                model_soup = colsSoup[1]
                class_ = colsSoup[3].text.strip()
                image_tag = colsSoup[1].find('a', {'class': 'image'})
                href = image_tag.get('href') if image_tag else None
                image_url = url + url_fix(href) if href else None
                print(image_url)
                # assembly = colsSoup[6].text.strip()
                assembly = ''
                brand_obj = setBrand(brand_soup)
                model_obj = setModel(model_soup, brand_obj, image_url)
                generation_obj = setGeneration(model_obj)
                vehicle_obj = setModification(generation_obj, class_, assembly, years=None)


def buses(url, path, len_=8):
    tablesSoup = parse(url + path, 'table', {'class': 'wikitable'})
    for tableSoup in tablesSoup:
        for rowSoup in tableSoup.find_all('tr'):
            colsSoup = rowSoup.find_all('td')
            if len(colsSoup) == len_:
                years = colsSoup[4].text.strip()
                model_soup = colsSoup[0]
                image_tag = colsSoup[1].find('a', {'class': 'image'})
                href = image_tag.get('href') if image_tag else None
                image_url = url + url_fix(href) if href else None
                class_ = colsSoup[2].text.strip()
                brand_soup = colsSoup[3]
                assembly = colsSoup[6].text.strip()
                brand_obj = setBrand(brand_soup)
                model_obj = setModel(model_soup, brand_obj, image_url)
                generation_obj = setGeneration(model_obj)
                vehicle_obj = setModification(generation_obj, class_, assembly, years)


def trucksParse():
    path = '/wiki/List_of_trucks'
    trucks(url, path)


def militaryTrucksParse():
    path = '/wiki/List_of_military_trucks'
    trucks(url, path, 7)


def busesParse():
    path = '/wiki/List_of_buses'
    buses(url, path, 7)


busesParse()
