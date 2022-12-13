import os
import time
from io import BytesIO
from termcolor import colored as __

import django
import requests
from bs4 import BeautifulSoup
from django.core.files import File
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_info.settings')
django.setup()

from trucks.models import *

session = requests.Session()
url = 'http://truck-data.com'

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}

'''
Modification.objects.all().delete()
DimensionAndWidth.objects.all().delete()
Performances.objects.all().delete()
Suspension.objects.all().delete()
Transmission.objects.all().delete()
Engine.objects.all().delete()
Body.objects.all().delete()
Model.objects.all().delete()
Brand.objects.all().delete()

'''


def parse(url, tag, attrs, first=False):
    try:
        response = session.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(response.content, features="html5lib")
        if first:
            return soup.find(tag, attrs)
        return soup.find_all(tag, attrs)
    except:
        time.sleep(5)
        print(__('parse error', 'red'), url)
        return parse(url, tag, attrs, first)


def find_in_rows(rows_soup, search_string):
    for row_soup in rows_soup:
        cols_soup = row_soup.find_all('td')
        if search_string == cols_soup[0].text.strip():
            result = cols_soup[1].text.strip()
            if result == '-':
                return None
            return result


def get_thumbnail(section):
    page_a_tags = section.find_all('a')
    for a_tag in page_a_tags:
        if a_tag.get('rel'):
            if 'thumbnail' in a_tag.get('rel'):
                img = a_tag.find('img')
                return img.get('src')
    return None


def mod_parse(mod_link, brand_obj, mod_name):
    section = parse(mod_link, 'section', {'id': 'content'}, True)
    if not section:
        return False
    rows = section.find_all('tr')
    model_name = find_in_rows(rows, 'Model')

    print('mod', mod_link)

    if not model_name:
        print(__(' - MODEL NOT FOUND', 'green'))
        return
    model_obj, created = Model.objects.get_or_create(
        name=model_name,
        brand=brand_obj,
    )

    mod_obj, created = Modification.objects.get_or_create(
        name=mod_name,
        model=model_obj,
    )
    mod_obj.body.get_or_create(
        cabin_type=find_in_rows(rows, 'Cabin type'),
        length=find_in_rows(rows, 'Length'),
        width=find_in_rows(rows, 'Width'),
        height=find_in_rows(rows, 'Height'),
        wheelbase=find_in_rows(rows, 'Wheelbase'),
        drive_height=find_in_rows(rows, 'Drive height'),
        front_track=find_in_rows(rows, 'Front track')
    )
    mod_obj.engine.get_or_create(
        engine_model=find_in_rows(rows, 'Engine model'),
        eco_standard=find_in_rows(rows, 'ECO standard'),
        capacity=find_in_rows(rows, 'Engine capacity'),
        power=find_in_rows(rows, 'Engine power'),
        torque=find_in_rows(rows, 'Torque'),
        max_torque_rpm=find_in_rows(rows, 'at RPM'),
        engine_type=find_in_rows(rows, 'Engine type'),
        boost=find_in_rows(rows, 'Boost'),
        position_of_cylinders=find_in_rows(rows, 'Cylinder layout'),
        cylinders=find_in_rows(rows, 'Number of cylinders'),
        fuel_type=find_in_rows(rows, 'Fuel type')
    )

    mod_obj.transmission.get_or_create(
        wheel_drive=find_in_rows(rows, 'Wheel drive'),
        number_of_gears=find_in_rows(rows, 'Number of gears'),
        gearbox_model=find_in_rows(rows, 'Gearbox model'),
        gearbox_type=find_in_rows(rows, 'Gearbox type'),
        axels=find_in_rows(rows, 'Axels')
    )
    mod_obj.suspension.get_or_create(
        front_suspension=find_in_rows(rows, 'Front suspension'),
        rear_suspension=find_in_rows(rows, 'Rear suspension')
    )
    mod_obj.performances.get_or_create(
        fuel_tank_capacity=find_in_rows(rows, 'Fuel tank capacity'),
        top_speed=find_in_rows(rows, 'Top speed'),
    )
    mod_obj.dimensions_and_width.get_or_create(
        gross_vehicle_weight=find_in_rows(rows, 'Gross vehicle weight'),
        gross_combination_weight=find_in_rows(rows, 'Gross combination weight'),
        front_axle_load=find_in_rows(rows, 'Front axle load'),
        rear_axle_load=find_in_rows(rows, 'Rear axle load'),
        wheel_dimensions=find_in_rows(rows, 'Wheel dimensions'),
        rear_truck_load=find_in_rows(rows, 'Rear axle (truck) load'),
        tires=find_in_rows(rows, 'Tires dimensions')
    )

    mod_img_url = get_thumbnail(section)
    if mod_img_url:
        # img for model
        model_obj.image.save(
            slugify(mod_name) + '.' + mod_img_url.split('.')[-1],
            File(
                get_img(
                    link(mod_img_url, url)
                )
            )
        )
        model_obj.save()

        # img for modification
        mod_obj.image.save(
            slugify(mod_name) + '.' + mod_img_url.split('.')[-1],
            File(
                get_img(
                    link(mod_img_url, url)
                )
            )
        )
        mod_obj.save()

    print('Modification', mod_obj, created)


def link(tag_link, base_url=None):
    if base_url:
        url = base_url
    return url + tag_link if tag_link else ''


def get_img(img_path):
    try:
        response = session.get(img_path, headers=headers, timeout=None)
        return BytesIO(response.content)
    except:
        time.sleep(5)
        print(__('get_img error', 'red'), img_path)
        return get_img(img_path)


def mods_parse(mods_link, brand_obj):
    section = parse(mods_link, 'section', {'id': 'content'}, True)
    if not section:
        return False
    tables_soup = section.find_all('table')

    for table_soup in tables_soup:
        if table_soup:
            mod_soup = table_soup.find_all('a')
            for mod in mod_soup:
                mod_name = mod.text.strip()
                mod_link = link(mod.get('href'), url)
                mod_parse(mod_link, brand_obj, mod_name)


def serieses_parse(serieses_link, brand_obj):
    section = parse(serieses_link, 'section', {'id': 'content'}, True)
    if not section:
        return False
    table_soup = section.find('table')
    serieses_soup = table_soup.find_all('a')

    for series_soup in serieses_soup:
        series_name = series_soup.text.strip()
        series_link = link(series_soup.get('href'), url)

        mods_parse(series_link, brand_obj)
        print('series:', series_name)


def brands_parse():
    path = '/en/truck/'
    section = parse(url + path, 'section', {'id': 'content'}, True)
    if not section:
        return False
    table_soup = section.find('table')

    brands_soup = table_soup.find_all('a')

    # c = False

    for brand_soup in brands_soup:
        brand_name = brand_soup.text.strip()

        # continue
        # if brand_name == 'ZIL':
        #     c = True
        # if not c:
        #     continue

        if brand_name:
            brand_link = link(brand_soup.get('href'), url)
            brand_obj, created = Brand.objects.get_or_create(
                name=brand_name,
                link=brand_link
            )
            print(__('Brand:', 'green'), brand_obj, brand_link)
            serieses_parse(brand_link, brand_obj)


brands_parse()
