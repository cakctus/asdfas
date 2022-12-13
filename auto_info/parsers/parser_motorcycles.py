import json
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
from moto.models import *

session = requests.Session()

url = 'https://www.motorcycledb.com'

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}


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


def link(tag_link, url=None):
    return url + tag_link if tag_link else ''


def get_img(img_path):
    try:
        response = session.get(img_path, headers=headers, timeout=None)
        return BytesIO(response.content)
    except:
        time.sleep(5)
        print('get_img error')
        return get_img(img_path)


def find_in_rows(rows_soup, search):
    if type(search) == str:
        search = [search]
    for elem in search:
        for row_soup in rows_soup:
            cols_soup = row_soup.find_all('td')
            if elem.lower() == cols_soup[0].text.strip().lower():
                return cols_soup[1].text.strip()
    return None


def mod_parse(mod_link, model_obj):
    table = parse(url + mod_link, 'table', {}, True)
    if not table:
        print(url + mod_link)
        return None

    slides = parse(url + mod_link, 'div', {'class': 'mySlides'}, True)
    img_url = slides.find('img').get('src') if slides else None
    rows = table.find_all('tr')

    engine_transmission_specifications, created = EngineTransmissionSpecifications.objects.get_or_create(
        clutch=find_in_rows(rows, 'Clutch:'),
        transmission_type_final_drive=find_in_rows(rows, ['Transmission typefinal drive:', 'Transmission type,final drive:']),
        gearbox=find_in_rows(rows, 'Gearbox:'),
        cooling_system=find_in_rows(rows, 'Cooling system:'),
        valves_per_cylinder=find_in_rows(rows, 'Valves per cylinder:'),
        bore_x_stroke=find_in_rows(rows, ['Bore x stroke:', 'Bore x Stroke:']),
        torque=find_in_rows(rows, 'Torque:'),
        power=find_in_rows(rows, 'Power:'),
        engine_type=find_in_rows(rows, 'Engine type:'),
        capacity=find_in_rows(rows, 'Capacity:'),
        engine_details=find_in_rows(rows, 'Engine details:'),
        ignition=find_in_rows(rows, 'Ignition:'),
        compression=find_in_rows(rows, 'Compression:'),
        stroke=find_in_rows(rows, 'Stroke:'),
        emission_details=find_in_rows(rows, 'Emission details:'),
        exhaust_system=find_in_rows(rows, 'Exhaust system:'),
        top_speed=find_in_rows(rows, 'Top speed:'),
        driveline=find_in_rows(rows, 'Driveline:'),
        _0_100_kmh=find_in_rows(rows, '0-100 km/h (0-62 mph):'),
        _60_140_kmh_highest_gear=find_in_rows(rows, '60-140 km/h (37-87 mph), highest gear:'),
        _14_mile=find_in_rows(rows, '1/4 mile (0.4 km):')
    )
    brakes_suspension_frame_wheels, created = BrakesSuspensionFrameWheels.objects.get_or_create(
        rear_brakes_diameter=find_in_rows(rows, 'Rear brakes diameter:'),
        rear_brakes=find_in_rows(rows, 'Rear brakes:'),
        front_brakes_diameter=find_in_rows(rows, 'Front brakes diameter:'),
        front_brakes=find_in_rows(rows, 'Front brakes:'),
        rear_tyre=find_in_rows(rows, 'Rear tyre:'),
        front_tyre=find_in_rows(rows, 'Front tyre:'),
        rear_wheel_travel=find_in_rows(rows, 'Rear wheel travel:'),
        front_wheel_travel=find_in_rows(rows, 'Front wheel travel:'),
        frame_type=find_in_rows(rows, 'Frame type:'),
        wheels=find_in_rows(rows, 'Wheels:'),
        rake=find_in_rows(rows, 'Rake (fork angle):'),
        rear_suspension_travel=find_in_rows(rows, ['Rear Suspension suspension travel:', 'Rear suspension travel:']),
        front_suspension_travel=find_in_rows(rows, ['Front Suspension suspension travel:', 'Front suspension travel:']),
        rear_suspension=find_in_rows(rows, ['Rear Suspension:', 'Rear suspension:']),
        front_suspension=find_in_rows(rows, ['Front suspension:', 'Front Suspension:']),
        rear_tyre_dimensions=find_in_rows(rows, 'Rear tyre dimensions:'),
        front_tyre_dimensions=find_in_rows(rows, 'Front tyre dimensions:'),
        seat=find_in_rows(rows, 'Seat:'),
        trail=find_in_rows(rows, 'Trail:')
    )
    physical_measures_capacities, created = PhysicalMeasuresCapacities.objects.get_or_create(
        fuel_capacity=find_in_rows(rows, 'Fuel capacity:'),
        fuel_control=find_in_rows(rows, 'Fuel control:'),
        fuel_system=find_in_rows(rows, 'Fuel system:'),
        fuel_consumption_pr_10_km=find_in_rows(rows, 'Fuel consumption pr. 10 km (6.2 miles):'),
        fuel_consumption=find_in_rows(rows, 'Fuel consumption:'),
        seat_height=find_in_rows(rows, 'Seat height:'),
        alternate_seat_height=find_in_rows(rows, 'Alternate seat height:'),
        weight_incl_oil_gas_etc=find_in_rows(rows, 'Weight incl. oil, gas, etc:'),
        wheelbase=find_in_rows(rows, 'Wheelbase:'),
        ground_clearance=find_in_rows(rows, 'Ground clearance:'),
        power_weight_ratio=find_in_rows(rows, 'Power/weight ratio:'),
        dry_weight=find_in_rows(rows, 'Dry weight:'),
        overall_length=find_in_rows(rows, 'Overall length:'),
        overall_width=find_in_rows(rows, 'Overall width:'),
        overall_height=find_in_rows(rows, 'Overall height:'),
        rear_percentage_of_weight=find_in_rows(rows, 'Rear percentage of weight:'),
        front_percentage_of_weight=find_in_rows(rows, 'Front percentage of weight:'),
    )
    other_specs, created = OtherSpecs.objects.get_or_create(
        comments=find_in_rows(rows, 'Comments:'),
        starter=find_in_rows(rows, 'Starter:'),
        color_options=find_in_rows(rows, 'Color options:'),
        reserve_fuel_capacity=find_in_rows(rows, 'Reserve fuel capacity:'),
        electrical=find_in_rows(rows, 'Electrical:'),
        factory_warranty=find_in_rows(rows, 'Factory warranty:'),
        instruments=find_in_rows(rows, 'Instruments:'),
        light=find_in_rows(rows, 'Light:'),
        carrying_capacity=find_in_rows(rows, 'Carrying capacity:'),
        oil_capacity=find_in_rows(rows, 'Oil capacity:'),
        lubrication_system=find_in_rows(rows, 'Lubrication system:'),
        max_rpm=find_in_rows(rows, ['Max RPM RPM:', 'Max RPM:']),
        modifications_compared_to_previous_model=find_in_rows(rows, 'Modifications compared to previous model:'),
        greenhouse_gases=find_in_rows(rows, 'Greenhouse gases:'),
    )
    year = find_in_rows(rows, 'Year:')
    if not year:
        year = parse(url + mod_link, 'span', {'class': 'acyears'}, True).text
        print(year)
    mod_obj, created = Modification.objects.get_or_create(
        name=str(model_obj.name) + ' ' + year,
        year=year,
        category=find_in_rows(rows, 'Category:'),
        model=model_obj,
        engine_transmission_specifications=engine_transmission_specifications,
        brakes_suspension_frame_wheels=brakes_suspension_frame_wheels,
        physical_measures_capacities=physical_measures_capacities,
        other_specs=other_specs
    )

    if img_url:
        mod_obj.image.save(
            slugify(mod_obj.name) + '.' + img_url.split('.')[-1],
            File(
                get_img(img_url)
            )
        )

    print('--- mod', mod_obj, created)


cont_model = True


def models_parse(models_link, brand_obj):
    rows = parse(url + models_link, 'div', {'class': 'news_item_title'}, True)
    for row in rows.find_all('div', {'class': 'row'}):
        for item in row.find_all('a'):
            model_name = item.text.strip()
            global cont_model
            # contuner
            if model_name == 'Triumph Tiger 1200 XRX':
                cont_model = False
            if cont_model:
                continue

            model_link = item.get('href')
            model_obj, created = Model.objects.get_or_create(
                name=model_name,
                brand=brand_obj
            )
            print('-- model', model_obj, created)
            mod_parse(model_link, model_obj)


def brands_parse():
    path = '/manufacturers.php'
    items = parse(url + path, 'div', {'class': 'news_item_title'}, True)
    cont = True
    for item in items.find_all('div', {'class': 'makes'}):
        brand_name = item.text.strip()
        print(brand_name)
        # contuner
        if brand_name == 'Triumph':
            cont = False
        if cont:
            continue

        brand_img_src = item.find('img').get('src') if item.find('img') else None
        models_link = item.find('a').get('href')

        brand_obj, created = Brand.objects.get_or_create(
            name=brand_name
        )
        if brand_img_src:
            brand_obj.image.save(
                slugify(brand_obj.name) + '.' + brand_img_src.split('.')[-1],
                File(
                    get_img(
                        link(brand_img_src, url)
                    )
                )
            )

        print('- brand', brand_obj, created)
        models_parse(models_link, brand_obj)


def run():
    brands_parse()

# run()
