from fake_useragent import UserAgent

import os
import re
import time
from io import BytesIO

import django
import requests
from bs4 import BeautifulSoup
from django.core.files import File
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_info.settings')
django.setup()

from cars.models import *

session = requests.Session()

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': UserAgent()['google_chrome']
}
url = 'https://www.auto-data.net'

'''
Modification.objects.all().delete()
Performance.objects.all().delete()
ICEngine.objects.all().delete()
ElectricEngine.objects.all().delete()
SpaceVolumeWeights.objects.all().delete()
Dimensions.objects.all().delete()
DrivetrainBrakesSuspension.objects.all().delete()
ElectricCarsHybrids.objects.all().delete()
InternalCombustionEngine.objects.all().delete()
Generation.objects.all().delete()
Model.objects.all().delete()
Brand.objects.all().delete()
EngineOil.objects.all().delete()
'''


def image_field(img_path, img_name, count=0):
    try:
        response = session.get(img_path, headers=headers, timeout=None)
        return {
            'name': slugify(img_name) + '.' + img_path.split('.')[-1],
            'content': File(BytesIO(response.content))
        }
    except:
        print('image_field error')
        time.sleep(5)
        if count == 4:
            return False
        return image_field(img_path, img_name, count=count + 1)


def parse(url, tag=None, attrs=None, first=False):
    try:
        response = session.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(response.content, features="html5lib")
        if not tag and not attrs:
            return soup
        if first:
            return soup.find(tag, attrs)
        return soup.find_all(tag, attrs)
    except:
        time.sleep(5)
        print('parse error')
        return parse(url, tag, attrs, first)


# Удаляет пробелы больше 2
def sc(text):
    text = text.replace('  ', ' ').replace('\n', ' ').replace('\t', ' ')
    if '  ' in text:
        return sc(text)
    return text


def get_val(rows, search, in_search=True):
    if type(search) == str:
        search = [search]
    for elem in search:
        for row in rows:
            if row.find('th'):
                name = row.find('th').text.strip()
                value = sc(row.find('td').text.strip()) if row.find('td') else None
                if elem.lower() == name.lower():
                    return value
    if not in_search:
        return None
    for elem in search:
        for row in rows:
            if row.find('th'):
                name = row.find('th').text.strip()
                value = sc(row.find('td').text.strip()) if row.find('td') else None
                if elem.lower() in name.lower():
                    return value

    return None


def get_field_data(rows):
    header = 'no header'
    fields = {}
    for row in rows:
        data = []
        if row.find('th'):
            name = row.find('th').text.strip()
            value = sc(row.find('td').text.strip()) if row.find('td') else None
            if not value:
                header = name
                continue
            data = fields.get(header) if fields.get(header) else data
            if name not in data:
                fields.update(
                    {
                        header: data + [{name: value}]
                    }
                )
    return fields


def sti(s):
    st = [int(i) for i in re.findall(r'\d+', str(s))]
    if st:
        return st[0]
    return ''


def mod_parse(generation_obj, mod_path):
    content = parse(url + mod_path, 'div', {'id': 'outer'}, True)
    if not content:
        return False
    table = content.find('table', {'class': 'cardetailsout'})
    if not table:
        return False
    rows = table.find_all('tr')
    fields_data = get_field_data(rows)
    # get Modification
    # if 'General information' in fields_data:
    mod_name = get_val(rows, 'Modification (Engine)')
    obj, created = Modification.objects.update_or_create(
        generation=generation_obj,
        modification=mod_name,
        start_prod=sti(get_val(rows, 'Start of production')),
        end_prod=sti(get_val(rows, 'End of production')),
        powertrain_architecture=get_val(rows, 'Powertrain Architecture'),
        body_type=get_val(rows, 'Body type'),
        seats=get_val(rows, 'Seats'),
        doors=get_val(rows, 'Doors'),
    )
    print('Modification', obj, created)
    mod_img = parse(url + mod_path).find("meta", property='og:image')

    if mod_img:
        img_name = '_'.join([generation_obj.model.brand.name, generation_obj.model.name, mod_name])
        obj.image.save(
            **image_field(mod_img.get('content'), img_name)
        )
    # else:
    #     return None
    # get Performance
    if 'Performance specs' in fields_data:
        obj.performance, _created = Performance.objects.update_or_create(
            fuel_consumption_economy_urban=get_val(rows, 'Fuel consumption (economy) - urban'),
            fuel_consumption_economy_extra_urban=get_val(rows, 'Fuel consumption (economy) - extra urban'),
            fuel_consumption_economy_combined=get_val(rows, 'Fuel consumption (economy) - combined'),
            co2_emissions=get_val(rows, 'CO2 emissions'),
            fuel_type=get_val(rows, 'Fuel Type'),
            acceleration_0_100_km_h=get_val(rows, 'Acceleration 0 - 100 km/h'),
            acceleration_0_62_mph=get_val(rows, 'Acceleration 0 - 62 mph'),
            maximum_speed=get_val(rows, 'Maximum speed'),
            weight_to_power_ratio=get_val(rows, 'Weight-to-power ratio'),
            weight_to_torque_ratio=get_val(rows, 'Weight-to-torque ratio'),
            emission_standard=get_val(rows, 'Emission standard'),
            fuel_consumption_at_low_speed_wltp=get_val(rows, 'Fuel consumption at Low speed (WLTP)'),
            fuel_consumption_at_medium_speed_wltp=get_val(rows, 'Fuel consumption at Medium speed (WLTP)'),
            fuel_consumption_at_high_speed_wltp=get_val(rows, 'Fuel consumption at high speed (WLTP)'),
            fuel_consumption_at_very_high_speed_wltp=get_val(rows, 'Fuel consumption at very high speed (WLTP)'),
            combined_fuel_consumption_wltp=get_val(rows, 'Combined fuel consumption (WLTP)'),
            co2_emissions_wltp=get_val(rows, 'CO2 emissions (WLTP)'),
            acceleration_0_60_mph=get_val(rows, 'Acceleration 0 - 60 mph'),
            s_100_km_h_0=get_val(rows, '100 km/h - 0'),
            fuel_consumption_economy_urban_nedc_wltp_equivalent=get_val(rows, 'Fuel consumption (economy) - urban (NEDC, WLTP equivalent)'),
            fuel_consumption_economy_extra_urban_nedc_wltp_equivalent=get_val(rows, 'Fuel consumption (economy) - extra urban (NEDC, WLTP equivalent)'),
            fuel_consumption_economy_combined_nedc_wltp_equivalent=get_val(rows, 'Fuel consumption (economy) - combined (NEDC, WLTP equivalent)'),
            co2_emissions_nedc_wltp_equivalent=get_val(rows, 'CO2 emissions (NEDC, WLTP equivalent)'),
            acceleration_0_300_km_h=get_val(rows, 'Acceleration 0 - 300 km/h'),
            fuel_consumption_economy_urban_nedc=get_val(rows, 'Fuel consumption (economy) - urban (NEDC)'),
            fuel_consumption_economy_extra_urban_nedc=get_val(rows, 'Fuel consumption (economy) - extra urban (NEDC)'),
            fuel_consumption_economy_combined_nedc=get_val(rows, 'Fuel consumption (economy) - combined (NEDC)'),
            co2_emissions_nedc=get_val(rows, 'CO2 emissions (NEDC)'),
            fuel_consumption_at_low_speed_wltp_cng=get_val(rows, 'Fuel consumption at Low speed (WLTP) (CNG)'),
            fuel_consumption_at_medium_speed_wltp_cng=get_val(rows, 'Fuel consumption at Medium speed (WLTP) (CNG)'),
            fuel_consumption_at_high_speed_wltp_cng=get_val(rows, 'Fuel consumption at high speed (WLTP) (CNG)'),
            fuel_consumption_at_very_high_speed_wltp_cng=get_val(rows, 'Fuel consumption at very high speed (WLTP) (CNG)'),
            combined_fuel_consumption_wltp_cng=get_val(rows, 'Combined fuel consumption (WLTP) (CNG)'),
            fuel_consumption_economy_urban_cng_nedc=get_val(rows, 'Fuel consumption (economy) - urban (CNG) (NEDC)'),
            fuel_consumption_economy_extra_urban_cng_nedc=get_val(rows, 'Fuel consumption (economy) - extra urban (CNG) (NEDC)'),
            fuel_consumption_economy_combin=get_val(rows, 'Fuel consumption (economy) - combined (CNG) (NEDC)'),
        )
    # get Space, Volume and weights
    if 'Space, Volume and weights' in fields_data:
        obj.space_volume_weights, _created = SpaceVolumeWeights.objects.update_or_create(
            kerb_weight=get_val(rows, 'Kerb Weight'),
            fuel_tank_capacity=get_val(rows, 'Fuel tank capacity'),
            trunk_boot_space_minimum=get_val(rows, 'Trunk (boot) space - minimum'),
            permitted_trailer_load_with_brakes_12=get_val(rows, 'Permitted trailer load with brakes (12%)'),
            max_weight=get_val(rows, 'Max. weight'),
            max_load=get_val(rows, 'Max load'),
            trunk_boot_space_maximum=get_val(rows, 'Trunk (boot) space - maximum'),
            max_roof_load=get_val(rows, 'Max. roof load'),
            adblue_tank=get_val(rows, 'AdBlue tank'),
            permitted_trailer_load_without_brakes=get_val(rows, 'Permitted trailer load without brakes'),
            permitted_towbar_download=get_val(rows, 'Permitted towbar download'),
            permitted_trailer_load_with_brakes_8=get_val(rows, 'Permitted trailer load with brakes (8%)'),
            cng_cylinder_capacity=get_val(rows, 'CNG cylinder capacity'),
        )
    # get Dimensions
    if 'Dimensions' in fields_data:
        obj.dimensions, _created = Dimensions.objects.update_or_create(
            length=get_val(rows, 'Length'),
            width=get_val(rows, 'Width'),
            height=get_val(rows, 'Height'),
            wheelbase=get_val(rows, 'Wheelbase'),
            front_track=get_val(rows, 'Front track'),
            rear_back_track=get_val(rows, 'Rear (Back) track'),
            minimum_turning_circle_turning_diameter=get_val(rows, 'Minimum turning circle (turning diameter)'),
            width_including_mirrors=get_val(rows, 'Width including mirrors'),
            front_overhang=get_val(rows, 'Front overhang'),
            rear_overhang=get_val(rows, 'Rear overhang'),
            ride_height_ground_clearance=get_val(rows, 'Ride height (ground clearance)'),
            width_with_mirrors_folded=get_val(rows, 'Width with mirrors folded'),
            approach_angle=get_val(rows, 'Approach angle'),
            departure_angle=get_val(rows, 'Departure angle'),
            drag_coefficient_cd=get_val(rows, 'Drag coefficient (Cd)'),
            ramp_angle=get_val(rows, 'Ramp angle'),
            wading_depth=get_val(rows, 'Wading depth'),
        )
    # get Drivetrain, brakes and suspension specs
    if 'Drivetrain, brakes and suspension specs' in fields_data:
        obj.drivetrain_brakes_suspension, _created = DrivetrainBrakesSuspension.objects.update_or_create(
            drivetrain_architecture=get_val(rows, 'Drivetrain Architecture'),
            drive_wheel=get_val(rows, 'Drive wheel'),
            number_of_gears_automatic_transmission=get_val(rows, 'Number of Gears (automatic transmission)'),
            front_suspension=get_val(rows, 'Front suspension'),
            rear_suspension=get_val(rows, 'Rear suspension'),
            front_brakes=get_val(rows, 'Front brakes'),
            rear_brakes=get_val(rows, 'Rear brakes'),
            assisting_systems=get_val(rows, 'Assisting systems'),
            steering_type=get_val(rows, 'Steering type'),
            power_steering=get_val(rows, 'Power steering'),
            tires_size=get_val(rows, 'Tires size'),
            wheel_rims_size=get_val(rows, 'Wheel rims size'),
            number_of_gears_manual_transmission=get_val(rows, 'Number of Gears (manual transmission)')
        )
    # get Electric cars and hybrids specs
    if 'Electric cars and hybrids specs' in fields_data:
        obj.electric_cars_hybrids, _created = ElectricCarsHybrids.objects.update_or_create(
            gross_battery_capacity=get_val(rows, 'Gross battery capacity'),
            all_electric_range_wltp=get_val(rows, 'All-electric range (WLTP)'),
            all_electric_range=get_val(rows, 'All-electric range'),
            average_energy_consumption_wltp=get_val(rows, 'Average Energy consumption (WLTP)'),
            average_energy_consumption=get_val(rows, 'Average Energy consumption'),
            system_power=get_val(rows, 'System power'),
            system_torque=get_val(rows, 'System torque'),
            average_energy_consumption_nedc=get_val(rows, 'Average Energy consumption (NEDC)'),
            max_speed_electric=get_val(rows, 'Max speed (electric)'),
            all_electric_range_nedc=get_val(rows, 'All-electric range (NEDC)'),
            net_usable_battery_capacity=get_val(rows, 'Net (usable) battery capacity'),
            battery_technology=get_val(rows, 'Battery technology'),
            recuperation_output=get_val(rows, 'Recuperation output'),
            all_electric_range_nedc_wltp_equivalent=get_val(rows, 'All-electric range (NEDC, WLTP equivalent)'),
            average_energy_consumption_nedc_wltp_equivalent=get_val(rows, 'Average Energy consumption (NEDC, WLTP equivalent)'),
            battery_voltage=get_val(rows, 'Battery voltage')
        )
    # get Electric Engines
    for header, fields in fields_data.items():
        if 'Electric motor' in header:
            for field in fields:
                electric_engine, created = ElectricEngine.objects.update_or_create(
                    power=field.get('Electric motor power'),
                    torque=field.get('Electric motor Torque'),
                    location=field.get('Engine location'),
                    system_power=field.get('System power'),
                    system_torque=field.get('System torque')
                )
                obj.electric_engine.add(electric_engine)
    # get Internal combustion engine specs
    if 'Internal combustion engine specs' in fields_data:
        obj.internal_combustion_engine, _created = InternalCombustionEngine.objects.update_or_create(
            power=get_val(rows, 'Power'),
            power_per_litre=get_val(rows, 'Power per litre'),
            torque=get_val(rows, 'Torque'),
            engine_location=get_val(rows, 'Engine location'),
            engine_displacement=get_val(rows, 'Engine displacement'),
            number_of_cylinders=get_val(rows, 'Number of cylinders'),
            position_of_cylinders=get_val(rows, 'Position of cylinders'),
            cylinder_bore=get_val(rows, 'Cylinder Bore'),
            piston_stroke=get_val(rows, 'Piston Stroke'),
            compression_ratio=get_val(rows, 'Compression ratio'),
            number_of_valves_per_cylinder=get_val(rows, 'Number of valves per cylinder'),
            fuel_system=get_val(rows, 'Fuel System'),
            engine_aspiration=get_val(rows, 'Engine aspiration'),
            valvetrain=get_val(rows, 'Valvetrain'),
            maximum_engine_speed=get_val(rows, 'Maximum engine speed'),
            engine_model_code=get_val(rows, 'Engine Model/Code'),
            engine_oil_capacity=get_val(rows, 'Engine oil capacity'),
            oil_viscosity=get_val(rows, 'Oil viscosity'),
            coolant=get_val(rows, 'Coolant'),
            engine_systems=get_val(rows, 'Engine systems')
        )
    # get Engine oil specification
    if 'Engine oil specification' in fields_data:
        obj.engine_oil, _created = EngineOil.objects.update_or_create(
            coolant=get_val(rows, 'Coolant'),
            engine_systems=get_val(rows, 'Engine systems')
        )
    obj.save()
    return obj


def mods_parse(generation_obj, mod_path):
    table = parse(url + mod_path, 'table', {}, True)
    if not table:
        print('not table', mod_path)
        return False

    mods_soup = table.find_all('tr')

    for mod_soup in mods_soup:
        if not mod_soup.get('class'):
            continue
        if 'i' in mod_soup.get('class'):
            mod_path = mod_soup.find('a').get('href')
            mod_parse(generation_obj, mod_path)


def generations_parse(model_obj, generations_path):
    table = parse(url + generations_path, 'table', {'id': 'generr'}, True)
    if not table:
        return False
    generations_soup = table.find_all('tr')
    for generation_soup in generations_soup:
        if not generation_soup.get('id'):
            print('Реклама generations_parse', generation_soup)
            continue
        generation_tag = generation_soup.find('a', {'class': 'position'})
        generation_path = generation_tag.get('href')
        generation_name = generation_tag.find('strong', {'class': 'tit'}).text.strip()
        generation_img = parse(url + generation_path).find("meta", property='og:image')

        generation_obj, created = Generation.objects.update_or_create(
            model=model_obj,
            name=generation_name,
        )

        if generation_img:
            generation_obj.image.save(
                **image_field(generation_img.get('content'), generation_name)
            )

        print('Generation:', generation_obj, created)
        mods_parse(generation_obj, generation_path)


def models_parse(brand_obj, models_path):
    content = parse(url + models_path, 'div', {'id': 'outer'}, True)
    if not content:
        return False
    models_soup = content.find_all('a', {'class': 'modeli'})

    for model_soup in models_soup:
        generations_path = model_soup.get('href')
        model_name = model_soup.text.strip()
        model_img = parse(url + generations_path).find("meta", property='og:image')

        model_obj, created = Model.objects.update_or_create(
            brand=brand_obj,
            name=model_name
        )

        if model_img:
            model_obj.image.save(
                **image_field(model_img.get('content'), model_name)
            )

        print('Model', model_obj, created)
        generations_parse(model_obj, generations_path)


def brands_parse():
    path = '/en/allbrands'
    content = parse(url + path, 'div', {'id': 'outer'}, True)
    if not content:
        return False
    brands_soup = content.find_all('a', {'class': 'marki_blok'})
    for brand_soup in brands_soup:
        brand_name = brand_soup.text.strip()
        models_path = brand_soup.get('href')
        brand_img = brand_soup.find('img')

        brand_obj, created = Brand.objects.update_or_create(
            name=brand_name
        )

        if brand_img:
            brand_obj.image.save(
                **image_field(url + brand_img.get('src'), brand_name)
            )

        print('Brand', brand_obj, created)
        models_parse(brand_obj, models_path)


brands_parse()
