import os
import time
from io import BytesIO

import django
import requests
from bs4 import BeautifulSoup
from django.core.files import File
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_info.settings')
django.setup()

from scooters.models import Brand, Model, Engine, Performance, Dimensions, ChassisBody, GearBox, Modification

session = requests.Session()
url = 'http://moto-data.com'

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}


# Modification.objects.all().delete()
# GearBox.objects.all().delete()
# ChassisBody.objects.all().delete()
# Dimensions.objects.all().delete()
# Performance.objects.all().delete()
# Engine.objects.all().delete()
# Model.objects.all().delete()
# Brand.objects.all().delete()


def parse(url, tag, attrs, first=False):
    try:
        response = session.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(response.content, features="html5lib")
        if first:
            return soup.find(tag, attrs)
        return soup.find_all(tag, attrs)
    except:
        time.sleep(5)
        print('parse error')
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


def mod_parse(mod_link, model_obj, mod_name):
    section = parse(mod_link, 'section', {'id': 'content'}, True)
    if not section:
        return False
    rows = section.find_all('tr')

    performance_obj, created = Performance.objects.get_or_create(
        top_speed=find_in_rows(rows, 'Top speed'),
        estimated_fuel_consumption=find_in_rows(rows, 'Estimated fuel consumption'),
    )
    dimensions_obj, created = Dimensions.objects.get_or_create(
        total_weight=find_in_rows(rows, 'Total weight'),
        length=find_in_rows(rows, 'Length'),
        width=find_in_rows(rows, 'Width'),
        height=find_in_rows(rows, 'Height'),
        seat_height=find_in_rows(rows, 'Seat height'),
        front_wheel_size=find_in_rows(rows, 'Front wheel size'),
        rear_wheel_size=find_in_rows(rows, 'Rear wheel size'),
        fuel_tank_capacity=find_in_rows(rows, 'Fuel tank capacity'),
        fuel_tank_reserve=find_in_rows(rows, 'Fuel tank reserve'),
    )
    chassis_body_obj, created = ChassisBody.objects.get_or_create(
        front_brakes=find_in_rows(rows, 'Front brakes'),
        rear_brakes=find_in_rows(rows, 'Rear brakes'),
        front_brake_diameter=find_in_rows(rows, 'Front brake diameter'),
        rear_brake_diameter=find_in_rows(rows, 'Rear brake diameter'),
        front_suspension=find_in_rows(rows, 'Front suspension'),
        rear_suspension=find_in_rows(rows, 'Rear suspension'),
        body=find_in_rows(rows, 'Body'),
    )
    gear_box_obj, created = GearBox.objects.get_or_create(
        number_of_gears=find_in_rows(rows, 'Number of gears'),
        transmission_type=find_in_rows(rows, 'Transmission type')
    )
    engine_obj, created = Engine.objects.get_or_create(
        starter=find_in_rows(rows, 'Starter'),
        capacity=find_in_rows(rows, 'Capacity'),
        power=find_in_rows(rows, 'Power'),
        max_power_rpm=find_in_rows(rows, 'Maximum power at rpm'),
        torque=find_in_rows(rows, 'Torque'),
        max_torque_rpm=find_in_rows(rows, 'Maximum torque at rpm'),
        fuel_supply_system=find_in_rows(rows, 'Fuel supply system'),
        motor_type=find_in_rows(rows, 'Motor type'),
        cooling=find_in_rows(rows, 'Cooling'),
        cylinder_dimensions=find_in_rows(rows, 'Cylinder dimensions'),
        compression_ratio=find_in_rows(rows, 'Compression ratio'),
        compression=find_in_rows(rows, 'Compression'),
    )
    mod_obj, created = Modification.objects.get_or_create(
        name=mod_name,
        model=model_obj,
    )
    mod_img_url = get_thumbnail(section)
    if mod_img_url:
        mod_obj.image.save(
            slugify(mod_name) + '.' + mod_img_url.split('.')[-1],
            File(
                get_img(
                    link(mod_img_url, url)
                )
            )
        )
        mod_obj.save()

    mod_obj.performance.add(performance_obj)
    mod_obj.dimensions.add(dimensions_obj)
    mod_obj.chassis_body.add(chassis_body_obj)
    mod_obj.gear_box.add(gear_box_obj)
    mod_obj.engine.add(engine_obj)
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
        print('get_img error')
        return get_img(img_path)


def mods_parse(mods_link, model_obj):
    section = parse(mods_link, 'section', {'id': 'content'}, True)
    if not section:
        return False
    table_soup = section.find('table')

    img = section.find('img')
    if img:
        model_obj.image.save(
            slugify(model_obj.name) + '.' + img.get('src').split('.')[-1],
            File(
                get_img(
                    link(img.get('src'), url)
                )
            )
        )
        model_obj.save()

    if table_soup:
        mod_soup = table_soup.find_all('a')

        for mod in mod_soup:
            mod_name = mod.text.strip()
            mod_link = link(mod.get('href'), url)
            mod_parse(mod_link, model_obj, mod_name)


def models_parse(models_link, brand_obj):
    section = parse(models_link, 'section', {'id': 'content'}, True)
    if not section:
        return False
    table_soup = section.find('table')

    models_soup = table_soup.find_all('a')

    for model_soup in models_soup:
        model_name = model_soup.text.strip()
        model_link = link(model_soup.get('href'), url)

        model_obj, created = Model.objects.get_or_create(
            brand=brand_obj,
            name=model_name,
            link=model_link
        )
        mods_parse(model_link, model_obj)
        print('Model:', model_obj, created)


def brands_parse():
    path = '/en/scooter/'
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
            models_parse(brand_link, brand_obj)


def run():
    brands_parse()


run()
