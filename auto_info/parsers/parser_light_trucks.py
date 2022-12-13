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

from light_trucks.models import *

session = requests.Session()
url = 'http://truck-data.com'

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}

'''
Modification.objects.all().delete()
Model.objects.all().delete()
Engine.objects.all().delete()
ChassisBody.objects.all().delete()
Transmission.objects.all().delete()
BrakeSystem.objects.all().delete()
Steering.objects.all().delete()
Performance.objects.all().delete()
Capacity.objects.all().delete()
DimensionsAndWidth.objects.all().delete()
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
    mod_obj.engine.get_or_create(
        engine_model=find_in_rows(rows, 'Engine model'),
        eco_standard=find_in_rows(rows, 'ECO standard'),
        capacity=find_in_rows(rows, 'Capacity'),
        power=find_in_rows(rows, 'Power'),
        max_power_rpm=find_in_rows(rows, 'Maximum power at rpm'),
        torque=find_in_rows(rows, 'Torque'),
        max_torque_rpm=find_in_rows(rows, 'Maximum torque at rpm'),
        engine_type=find_in_rows(rows, 'Engine type'),
        position_of_cylinders=find_in_rows(rows, 'Position of cylinders'),
        cylinders=find_in_rows(rows, 'Cylinders'),
        valves_per_cylinder=find_in_rows(rows, 'Valves per cylinder'),
        compression=find_in_rows(rows, 'Compression'),
        fuel_type=find_in_rows(rows, 'Fuel type')
    )
    mod_obj.chassis_body.get_or_create(
        body_type=find_in_rows(rows, 'Body type'),
        length=find_in_rows(rows, 'Length'),
        width=find_in_rows(rows, 'Width'),
        height=find_in_rows(rows, 'Height'),
        wheelbase=find_in_rows(rows, 'Wheelbase'),
        ride_height=find_in_rows(rows, 'Ride height')
    )
    mod_obj.transmission.get_or_create(
        wheel_drive=find_in_rows(rows, 'Wheel drive'),
        number_of_gears=find_in_rows(rows, 'Number of gears (manual gearbox)')
    )
    mod_obj.brake_system.get_or_create(
        front_brakes=find_in_rows(rows, 'Front brakes'),
        rear_brakes=find_in_rows(rows, 'Rear brakes')
    )
    mod_obj.steering.get_or_create(
        power_steering=find_in_rows(rows, 'Power steering'),
        turning_diameter=find_in_rows(rows, 'Turning diameter')
    )
    mod_obj.performance.get_or_create(
        top_speed=find_in_rows(rows, 'Top speed'),
        fuel_tank_capacity=find_in_rows(rows, 'Fuel tank capacity'),
        fuel_consumption=find_in_rows(rows, 'Fuel consumption'),
        acceleration_to_100=find_in_rows(rows, 'Acceleration to 100 km/h'),
    )
    mod_obj.capacity.get_or_create(
        number_of_seats=find_in_rows(rows, 'Number of seats'),
        capacity=find_in_rows(rows, 'Capacity'),
        length_of_the_cargo_compartment=find_in_rows(rows, 'Length of the cargo compartment'),
        width_of_the_cargo_compartment=find_in_rows(rows, 'Width of the cargo compartment'),
        height_of_the_cargo_compartment=find_in_rows(rows, 'Height of the cargo compartment')
    )
    mod_obj.dimensions_and_width.get_or_create(
        width=find_in_rows(rows, 'Weight'),
        max_width=find_in_rows(rows, 'Max. weight'),
        tires=find_in_rows(rows, 'Tires'),
    )
    mod_img_url = get_thumbnail(section)
    if mod_img_url:
        model_obj.image.save(
            slugify(mod_name) + '.' + mod_img_url.split('.')[-1],
            File(
                get_img(
                    link(mod_img_url, url)
                )
            )
        )
        model_obj.save()

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

        print('series:', series_name)
        mods_parse(series_link, brand_obj)


def brands_parse():
    path = '/en/light-truck/'
    section = parse(url + path, 'section', {'id': 'content'}, True)
    if not section:
        return False
    table_soup = section.find('table')

    brands_soup = table_soup.find_all('a')

    for brand_soup in brands_soup:
        brand_name = brand_soup.text.strip()
        if brand_name:
            brand_link = link(brand_soup.get('href'), url)
            brand_obj, created = Brand.objects.get_or_create(
                name=brand_name,
                link=brand_link
            )
            print('Brand:', brand_obj, created)
            serieses_parse(brand_link, brand_obj)


def run():
    brands_parse()


run()
