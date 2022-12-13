import json
import os
import time
import sys
import django
import requests

from io import BytesIO
from bs4 import BeautifulSoup
from django.core.files import File
from django.utils.text import slugify

sys.path.append("/")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_info.settings')
django.setup()
from lawn_tractors.models import *

session = requests.Session()

url = 'https://www.tractordata.com'

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}
resume = False


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


def get_val(rows, search_string, header_name=''):
    data = []
    header = ''
    search_string = search_string.replace(':', '')
    search_string = search_string.strip()
    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 1:
            if cols[0].get('style'):
                if 'background:rgb(51,51,51)' in cols[0].get('style'):
                    header = cols[0].text.strip()
        if len(cols) >= 2:
            if header_name in header:
                name = cols[0].text
                name = name.replace(':', '')
                name = name.strip()
                value = cols[1].text.strip()
                if data and name:
                    return ', '.join(data)
                if value:
                    if search_string.lower() == name.lower():
                        data.append(value)
                    if data and not name:
                        data.append(
                            value
                        )

    return ', '.join(data)


fields = {}


def mod_parse(mod_link, model_obj):
    general_article_group = parse(mod_link, 'div', {'class': 'tdArticleGroup'}, True)
    engine_article_group = parse(mod_link.replace('.html', '-engine.html'), 'div', {'class': 'tdArticleGroup'}, True)
    transmission_article_group = parse(mod_link.replace('.html', '-transmission.html'), 'div', {'class': 'tdArticleGroup'}, True)
    dimensions_article_group = parse(mod_link.replace('.html', '-dimensions.html'), 'div', {'class': 'tdArticleGroup'}, True)
    articles = parse(mod_link, 'div', {'class': 'tdArticleItem'})

    img = None
    for article in articles:
        image = article.find('img')
        print(image)
        if image:
            img = image.get('src')
            break

    rows = []
    for article_group in [general_article_group, engine_article_group, transmission_article_group, dimensions_article_group]:
        tables = article_group.find_all('table')
        for table in tables:
            rows += table.find_all('tr')

    manufacturer = get_val(rows, 'Manufacturer', 'Production')
    obj, created = Modification.objects.update_or_create(
        model=model_obj,
        manufacturer=manufacturer,
        type=get_val(rows, 'Type', 'Production'),
        factory=get_val(rows, 'Factory', 'Production'),
        original_price=get_val(rows, 'Original price', 'Production'),
        distributor=get_val(rows, 'Distributor', 'Production'),
        total_built=get_val(rows, 'Total built', 'Production'),
        factories=get_val(rows, 'Factories', 'Production'),
    )
    if img:
        obj.image.save(
            **image_field(img, manufacturer + model_obj.name)
        )

    obj.mechanical, created = Mechanical.objects.update_or_create(
        chassis=get_val(rows, 'Chassis', 'Mechanical'),
        steering=get_val(rows, 'Steering', 'Mechanical'),
        brakes=get_val(rows, 'Brakes', 'Mechanical'),
        cab=get_val(rows, 'Cab', 'Mechanical'),
        transmission=get_val(rows, 'Transmission', 'Mechanical'),
        final_drives=get_val(rows, 'Final drives', 'Mechanical'),
        differential_lock=get_val(rows, 'Differential lock', 'Mechanical'),
        transmissions=get_val(rows, 'Transmissions', 'Mechanical'),
        trailer_brakes=get_val(rows, 'Trailer brakes', 'Mechanical'),
        rops_differential_lock=get_val(rows, 'ROPS Differential lock', 'Mechanical'),
        cab_differential_lock=get_val(rows, 'Cab Differential lock', 'Mechanical'),
        rops_brakes=get_val(rows, 'ROPS Brakes', 'Mechanical'),
        cab_brakes=get_val(rows, 'Cab Brakes', 'Mechanical')
    )
    obj.electrical, created = Electrical.objects.update_or_create(
        ground=get_val(rows, 'Ground', 'Electrical'),
        charging_system=get_val(rows, 'Charging system', 'Electrical'),
        charging_amps=get_val(rows, 'Charging amps', 'Electrical'),
        batteries=get_val(rows, 'Batteries', 'Electrical'),
        battery_cca=get_val(rows, 'Battery CCA', 'Electrical'),
        battery_volts=get_val(rows, 'Battery volts', 'Electrical'),
        rops_charging_amps=get_val(rows, 'ROPS Charging amps', 'Electrical'),
        cab_charging_amps=get_val(rows, 'Cab Charging amps', 'Electrical'),
        battery_ah=get_val(rows, 'Battery AH', 'Electrical'),
        charging_volts=get_val(rows, 'Charging volts', 'Electrical'),
        gas_batteries=get_val(rows, 'Gas Batteries', 'Electrical'),
        diesel_batteries=get_val(rows, 'Diesel Batteries', 'Electrical'),
        battery_group=get_val(rows, 'Battery Group', 'Electrical'),
        rops_battery_cca=get_val(rows, 'ROPS Battery CCA', 'Electrical'),
        cab_battery_cca=get_val(rows, 'Cab Battery CCA', 'Electrical')
    )
    obj.engine, created = Engine.objects.update_or_create(
        displacement=get_val(rows, 'Displacement', 'Engine'),
        bore_stroke=get_val(rows, 'Bore/Stroke', 'Engine'),
        power=get_val(rows, 'Power', 'Engine'),
        air_cleaner=get_val(rows, 'Air cleaner', 'Engine'),
        compression=get_val(rows, 'Compression', 'Engine'),
        rated_rpm=get_val(rows, 'Rated RPM', 'Engine'),
        starter_volts=get_val(rows, 'Starter volts', 'Engine'),
        fuel_system=get_val(rows, 'Fuel system', 'Engine'),
        pre_heating=get_val(rows, 'Pre-heating', 'Engine'),
        torque=get_val(rows, 'Torque', 'Engine'),
        torque_rpm=get_val(rows, 'Torque RPM', 'Engine'),
        emissions=get_val(rows, 'Emissions', 'Engine'),
        starter=get_val(rows, 'Starter', 'Engine'),
        emission_control=get_val(rows, 'Emission control', 'Engine'),
        maximum_power=get_val(rows, 'Maximum Power', 'Engine'),
        power_gross=get_val(rows, 'Power (gross)', 'Engine'),
        cooling_system=get_val(rows, 'Cooling system', 'Engine'),
        idle_rpm=get_val(rows, 'Idle RPM', 'Engine'),
        starter_power=get_val(rows, 'Starter power', 'Engine'),
        oil_capacity=get_val(rows, 'Oil capacity', 'Engine'),
        starter_type=get_val(rows, 'Starter type', 'Engine'),
        coolant_capacity=get_val(rows, 'Coolant capacity', 'Engine'),
        firing_order=get_val(rows, 'Firing order', 'Engine'),
        intake_valve_clearance=get_val(rows, 'Intake valve clearance', 'Engine'),
        exhaust_valve_clearance=get_val(rows, 'Exhaust valve clearance', 'Engine'),
        sparkplug_gap=get_val(rows, 'Sparkplug gap', 'Engine'),
        point_gap=get_val(rows, 'Point gap', 'Engine'),
        fuel_use=get_val(rows, 'Fuel use', 'Engine'),
        coolant_change=get_val(rows, 'Coolant change', 'Engine'),
        sparkplug=get_val(rows, 'Sparkplug', 'Engine'),
        rated_power_ec_97_98=get_val(rows, 'Rated Power (EC 97/98)', 'Engine'),
        operating_rpm=get_val(rows, 'Operating RPM', 'Engine'),
        oil_change=get_val(rows, 'Oil change', 'Engine'),
        rated_power_ece_r24=get_val(rows, 'Rated Power (ECE R24)', 'Engine'),
        maximum_power_ece_r24=get_val(rows, 'Maximum Power (ECE R24)', 'Engine'),
        rated_power_2000_25_ce=get_val(rows, 'Rated Power (2000/25/CE)', 'Engine'),
        rated_power_ece_r120=get_val(rows, 'Rated Power (ECE R120)', 'Engine'),
        maximum_power_ece_r120=get_val(rows, 'Maximum Power (ECE R120)', 'Engine'),
        maximum_power_ec_97_68=get_val(rows, 'Maximum Power (EC 97/68)', 'Engine')
    )

    obj.transmission, created = Transmission.objects.update_or_create(
        transmission=get_val(rows, 'Transmission', 'Transmission'),
        gears=get_val(rows, 'Gears', 'Transmission'),
        type=get_val(rows, 'Type', 'Transmission'),
        clutch=get_val(rows, 'Clutch', 'Transmission'),
        oil_capacity=get_val(rows, 'Oil capacity', 'Transmission'),
        manufacturer=get_val(rows, 'Manufacturer', 'Transmission'),
        n_2wd_oil_capacity=get_val(rows, '2WD Oil capacity', 'Transmission'),
        n_4wd_oil_capacity=get_val(rows, '4WD Oil capacity', 'Transmission'),
    )
    obj.dimensions, created = Dimensions.objects.update_or_create(
        operating_weight=get_val(rows, 'Operating weight', 'Dimensions'),
        ballasted_weight=get_val(rows, 'Ballasted weight', 'Dimensions'),
        wheelbase=get_val(rows, 'Wheelbase', 'Dimensions'),
        length=get_val(rows, 'Length', 'Dimensions'),
        width=get_val(rows, 'Width', 'Dimensions'),
        height=get_val(rows, 'Height', 'Dimensions'),
        shiping_weight=get_val(rows, 'Shiping weight', 'Dimensions'),
        height_cab=get_val(rows, 'Height (cab)', 'Dimensions'),
        front_axle=get_val(rows, 'Front axle', 'Dimensions'),
        max_weight=get_val(rows, 'Max weight', 'Dimensions'),
        rear_axle=get_val(rows, 'Rear axle', 'Dimensions'),
        rear_tread=get_val(rows, 'Rear tread', 'Dimensions'),
        n_2wd_wheelbase=get_val(rows, '2WD Wheelbase', 'Dimensions'),
        n_4wd_wheelbase=get_val(rows, '4WD Wheelbase', 'Dimensions'),
        n_2wd_front_tread=get_val(rows, '2WD Front tread', 'Dimensions'),
        n_4wd_front_tread=get_val(rows, '4WD Front tread', 'Dimensions'),
        weight=get_val(rows, 'Weight', 'Dimensions'),
        height_rops=get_val(rows, 'Height (ROPS)', 'Dimensions'),
        front_tread=get_val(rows, 'Front tread', 'Dimensions'),
        n_2wd_rops_weight=get_val(rows, '2WD ROPS Weight', 'Dimensions'),
        n_4wd_cab_weight=get_val(rows, '4WD Cab Weight', 'Dimensions'),
        clearance_drawbar=get_val(rows, 'Clearance (drawbar)', 'Dimensions'),
        n_2wd_length=get_val(rows, '2WD Length', 'Dimensions'),
        n_4wd_length=get_val(rows, '4WD Length', 'Dimensions'),
        n_2wd_width=get_val(rows, '2WD Width', 'Dimensions'),
        n_4wd_width=get_val(rows, '4WD Width', 'Dimensions'),
        n_2wd_height_cab=get_val(rows, '2WD Height (cab)', 'Dimensions'),
        n_4wd_height_cab=get_val(rows, '4WD Height (cab)', 'Dimensions'),
        n_4wd_shiping_weight=get_val(rows, '4WD Shiping weight', 'Dimensions'),
        cvt_shiping_weight=get_val(rows, 'CVT Shiping weight', 'Dimensions'),
        n_4wd_cvt_length=get_val(rows, '4WD CVT Length', 'Dimensions'),
        n_2wd_shiping_weight=get_val(rows, '2WD Shiping weight', 'Dimensions'),
        ground_clearance=get_val(rows, 'Ground clearance', 'Dimensions'),
        height_exhaust=get_val(rows, 'Height (exhaust)', 'Dimensions'),
        n_2wd_ground_clearance=get_val(rows, '2WD Ground clearance', 'Dimensions'),
        n_4wd_ground_clearance=get_val(rows, '4WD Ground clearance', 'Dimensions'),
        n_2wd_clearance_front_axle=get_val(rows, '2WD Clearance (front axle)', 'Dimensions'),
        n_4wd_clearance_front_axle=get_val(rows, '4WD Clearance (front axle)', 'Dimensions'),
        clearance_front_axle=get_val(rows, 'Clearance (front axle)', 'Dimensions'),
        gas_weight=get_val(rows, 'Gas Weight', 'Dimensions'),
        diesel_weight=get_val(rows, 'Diesel Weight', 'Dimensions'),
        height_steering_wheel=get_val(rows, 'Height (steering wheel)', 'Dimensions'),
        n_2wd_weight=get_val(rows, '2WD Weight', 'Dimensions'),
        n_4wd_weight=get_val(rows, '4WD Weight', 'Dimensions'),
        height_hood=get_val(rows, 'Height (hood)', 'Dimensions'),
        clearance_rear_axle=get_val(rows, 'Clearance (rear axle)', 'Dimensions'),
        gas_wheelbase=get_val(rows, 'Gas Wheelbase', 'Dimensions'),
        diesel_wheelbase=get_val(rows, 'Diesel Wheelbase', 'Dimensions'),
        gas_length=get_val(rows, 'Gas Length', 'Dimensions'),
        diesel_length=get_val(rows, 'Diesel Length', 'Dimensions'),
        shipping_weight=get_val(rows, 'Shipping weight', 'Dimensions'),
        gauge=get_val(rows, 'Gauge', 'Dimensions'),
        wide_front_length=get_val(rows, 'Wide-front Length', 'Dimensions'),
        wide_front_width=get_val(rows, 'Wide-front Width', 'Dimensions'),
        wide_front_shiping_weight=get_val(rows, 'Wide-front Shiping weight', 'Dimensions'),
        wide_front_ground_clearance=get_val(rows, 'Wide-front Ground clearance', 'Dimensions'),
        gear_operating_weight=get_val(rows, 'Gear Operating weight', 'Dimensions'),
        hydro_operating_weight=get_val(rows, 'Hydro Operating weight', 'Dimensions'),
        shuttle_operating_weight=get_val(rows, 'Shuttle Operating weight', 'Dimensions'),
        gear_weight=get_val(rows, 'Gear Weight', 'Dimensions'),
        hydro_weight=get_val(rows, 'Hydro Weight', 'Dimensions'),
        standard_steer_wheelbase=get_val(rows, 'Standard Steer Wheelbase', 'Dimensions'),
        ultra_steer_wheelbase=get_val(rows, 'Ultra Steer Wheelbase', 'Dimensions'),
        standard_steer_length=get_val(rows, 'Standard Steer Length', 'Dimensions'),
        ultra_steer_length=get_val(rows, 'Ultra Steer Length', 'Dimensions'),
        rops_weight=get_val(rows, 'ROPS Weight', 'Dimensions'),
        cab_weight=get_val(rows, 'Cab Weight', 'Dimensions'),
        wide_front_wheelbase=get_val(rows, 'Wide front Wheelbase', 'Dimensions'),
        n_4wd_rops_operating_weight=get_val(rows, '4WD ROPS Operating weight', 'Dimensions'),
        n_2wd_height=get_val(rows, '2WD Height', 'Dimensions'),
        n_4wd_height=get_val(rows, '4WD Height', 'Dimensions'),
        n_2wd_rops_shiping_weight=get_val(rows, '2WD ROPS Shiping weight', 'Dimensions'),
        n_4wd_cab_shiping_weight=get_val(rows, '4WD cab Shiping weight', 'Dimensions'),
        n_4wd_rops_weight=get_val(rows, '4WD ROPS Weight', 'Dimensions'),
        minimum_width=get_val(rows, 'Minimum Width', 'Dimensions'),
        frame_ground_clearance=get_val(rows, 'Frame Ground clearance', 'Dimensions'),
        duals_width=get_val(rows, 'Duals Width', 'Dimensions'),
        n_2wd_shipping_weight=get_val(rows, '2WD Shipping weight', 'Dimensions'),
        n_4wd_shipping_weight=get_val(rows, '4WD Shipping weight', 'Dimensions'),
        rops_length=get_val(rows, 'ROPS Length', 'Dimensions'),
        cab_length=get_val(rows, 'Cab Length', 'Dimensions'),
        n_4wd_rops_wheelbase=get_val(rows, '4WD ROPS Wheelbase', 'Dimensions'),
        n_4wd_cab_wheelbase=get_val(rows, '4WD Cab Wheelbase', 'Dimensions'),
        n_2wd_operating_weight=get_val(rows, '2WD Operating weight', 'Dimensions'),
        n_4wd_operating_weight=get_val(rows, '4WD Operating weight', 'Dimensions'),
        n_2wd_rops_operating_weight=get_val(rows, '2WD ROPS Operating weight', 'Dimensions'),
        n_2wd_cab_operating_weight=get_val(rows, '2WD Cab Operating weight', 'Dimensions'),
        n_4wd_cab_operating_weight=get_val(rows, '4WD Cab Operating weight', 'Dimensions'),
        min_width=get_val(rows, 'Min Width', 'Dimensions'),
        max_width=get_val(rows, 'Max Width', 'Dimensions'),
        n_2wd_fixed_wheelbase=get_val(rows, '2WD fixed Wheelbase', 'Dimensions'),
        tricycle_length=get_val(rows, 'Tricycle Length', 'Dimensions'),
        tricycle_width=get_val(rows, 'Tricycle Width', 'Dimensions'),
        tricycle_shiping_weight=get_val(rows, 'Tricycle Shiping weight', 'Dimensions'),
        tricycle_ground_clearance=get_val(rows, 'Tricycle Ground clearance', 'Dimensions'),
        tricycle_wheelbase=get_val(rows, 'Tricycle Wheelbase', 'Dimensions'),

    )
    obj.hydraulics, created = Hydraulics.objects.update_or_create(
        type=get_val(rows, 'Type', 'Hydraulics'),
        pressure=get_val(rows, 'Pressure', 'Hydraulics'),
        valves=get_val(rows, 'Valves', 'Hydraulics'),
        pump_flow=get_val(rows, 'Pump flow', 'Hydraulics'),
        scv_flow=get_val(rows, 'SCV flow', 'Hydraulics'),
        total_flow=get_val(rows, 'Total flow', 'Hydraulics'),
        steering_flow=get_val(rows, 'Steering flow', 'Hydraulics'),
        capacity=get_val(rows, 'Capacity', 'Hydraulics'),
        steering_press=get_val(rows, 'Steering press.', 'Hydraulics'),
        steering_cap=get_val(rows, 'Steering cap.', 'Hydraulics'),
        mid_valves=get_val(rows, 'Mid valves', 'Hydraulics'),
        rear_valves=get_val(rows, 'Rear valves', 'Hydraulics'),
        n_2wd_capacity=get_val(rows, '2WD Capacity', 'Hydraulics'),
        n_4wd_capacity=get_val(rows, '4WD Capacity', 'Hydraulics'),
        powershift_total_flow=get_val(rows, 'Powershift Total flow', 'Hydraulics'),
        syncroshift_total_flow=get_val(rows, 'SyncroShift Total flow', 'Hydraulics'),
        gear_steering_flow=get_val(rows, 'Gear Steering flow', 'Hydraulics'),
        hydro_steering_flow=get_val(rows, 'Hydro Steering flow', 'Hydraulics'),
        n_2wd_pump_flow=get_val(rows, '2WD Pump flow', 'Hydraulics'),
        n_4wd_pump_flow=get_val(rows, '4WD Pump flow', 'Hydraulics'),
        n_2wd_total_flow=get_val(rows, '2WD Total flow', 'Hydraulics'),
        n_4wd_total_flow=get_val(rows, '4WD Total flow', 'Hydraulics'),
        gear_capacity=get_val(rows, 'Gear Capacity', 'Hydraulics'),
        hydro_capacity=get_val(rows, 'Hydro Capacity', 'Hydraulics'),
        rops_type=get_val(rows, 'ROPS Type', 'Hydraulics'),
        cab_type=get_val(rows, 'Cab Type', 'Hydraulics'),
        autopower_capacity=get_val(rows, 'AutoPower Capacity', 'Hydraulics'),
        cvt_capacity=get_val(rows, 'CVT Capacity', 'Hydraulics'),
        ap6_capacity=get_val(rows, 'AP6 Capacity', 'Hydraulics')
    )
    obj.tractor_hitch, created = TractorHitch.objects.update_or_create(
        rear_type=get_val(rows, 'Rear Type', 'TractorHitch'),
        rear_lift_at_24_610mm=get_val(rows, 'Rear lift (at 24"/610mm)', 'TractorHitch'),
        rear_lift_at_ends=get_val(rows, 'Rear lift (at ends)', 'TractorHitch'),
        front_hitch=get_val(rows, 'Front Hitch', 'TractorHitch'),
        front_lift_at_ends=get_val(rows, 'Front lift (at ends)', 'TractorHitch'),
        drawbar=get_val(rows, 'Drawbar', 'TractorHitch'),
        rear_arms=get_val(rows, 'Rear Arms', 'TractorHitch'),
        rear_lift=get_val(rows, 'Rear lift', 'TractorHitch'),
        control=get_val(rows, 'Control', 'TractorHitch'),
        cvt_rear_lift_at_24_610mm=get_val(rows, 'CVT Rear lift (at 24"/610mm)', 'TractorHitch'),
        front_lift=get_val(rows, 'Front lift', 'TractorHitch'),
        cvt_rear_lift=get_val(rows, 'CVT Rear lift', 'TractorHitch'),
        type=get_val(rows, 'Type', 'TractorHitch'),
        n_2134v_rear_lift_at_ends=get_val(rows, '2134V Rear lift (at ends)', 'TractorHitch'),
        n_2134e_rear_lift_at_ends=get_val(rows, '2134E Rear lift (at ends)', 'TractorHitch'),
        front_lift_at_24_610mm=get_val(rows, 'Front lift (at 24"/610mm)', 'TractorHitch'),
        optional_rear_type=get_val(rows, 'Optional Rear Type', 'TractorHitch'),
        ap_rear_lift_at_24_610mm=get_val(rows, 'AP Rear lift (at 24"/610mm)', 'TractorHitch')
    )
    obj.power_take_off, created = PowerTakeOff.objects.update_or_create(
        rear_pto=get_val(rows, 'Rear PTO', 'PowerTakeOff'),
        rear_rpm=get_val(rows, 'Rear RPM', 'PowerTakeOff'),
        clutch=get_val(rows, 'Clutch', 'PowerTakeOff'),
        engine_rpm=get_val(rows, 'Engine RPM', 'PowerTakeOff'),
        front_pto=get_val(rows, 'Front PTO', 'PowerTakeOff'),
        front_rpm=get_val(rows, 'Front RPM', 'PowerTakeOff'),
        mid_pto=get_val(rows, 'Mid PTO', 'PowerTakeOff'),
        mid_rpm=get_val(rows, 'Mid RPM', 'PowerTakeOff'),
        gear_rear_pto=get_val(rows, 'Gear Rear PTO', 'PowerTakeOff'),
        hydro_rear_pto=get_val(rows, 'Hydro Rear PTO', 'PowerTakeOff'),
        optional_rear_pto=get_val(rows, 'Optional Rear PTO', 'PowerTakeOff'),
        gear_clutch=get_val(rows, 'Gear Clutch', 'PowerTakeOff'),
        hydro_clutch=get_val(rows, 'Hydro Clutch', 'PowerTakeOff'),
        gear_mid_pto=get_val(rows, 'Gear Mid PTO', 'PowerTakeOff'),
        hydro_mid_pto=get_val(rows, 'Hydro Mid PTO', 'PowerTakeOff'),
    )
    obj.сapacity, created = Capacity.objects.update_or_create(
        fuel=get_val(rows, 'Fuel', 'Capacity'),
        hydraulic_system=get_val(rows, 'Hydraulic system', 'Capacity'),
        rear_diff=get_val(rows, 'Rear diff.', 'Capacity'),
        steering=get_val(rows, 'Steering', 'Capacity'),
        aux_fuel=get_val(rows, 'Aux. fuel', 'Capacity'),
        front_axle=get_val(rows, 'Front axle', 'Capacity'),
        front_hubs=get_val(rows, 'Front hubs', 'Capacity'),
        front_diff=get_val(rows, 'Front diff.', 'Capacity'),
        rear_hubs=get_val(rows, 'Rear hubs', 'Capacity'),
        rops_fuel=get_val(rows, 'ROPS Fuel', 'Capacity'),
        cab_fuel=get_val(rows, 'Cab Fuel', 'Capacity'),
        n_2wd_hydraulic_system=get_val(rows, '2WD Hydraulic system', 'Capacity'),
        n_4wd_hydraulic_system=get_val(rows, '4WD Hydraulic system', 'Capacity'),
        exhaust_fluid_def=get_val(rows, 'Exhaust fluid (DEF)', 'Capacity'),
        gear_hydraulic_system=get_val(rows, 'Gear Hydraulic system', 'Capacity'),
        hydro_hydraulic_system=get_val(rows, 'Hydro Hydraulic system', 'Capacity'),
        autopower_hydraulic_system=get_val(rows, 'AutoPower Hydraulic system', 'Capacity'),
        cvt_hydraulic_system=get_val(rows, 'CVT Hydraulic system', 'Capacity'),
        ap6_hydraulic_system=get_val(rows, 'AP6 Hydraulic system', 'Capacity'),
    )
    obj.belt_pulley, created = BeltPulley.objects.update_or_create(
        diameter=get_val(rows, 'Diameter', 'BeltPulley'),
        width=get_val(rows, 'Width', 'BeltPulley'),
        rpm=get_val(rows, 'RPM', 'BeltPulley'),
        speed=get_val(rows, 'Speed', 'BeltPulley'),
    )
    obj.engine_oil, created = EngineOil.objects.update_or_create(
        oil_capacity=get_val(rows, 'Oil capacity', 'EngineOil'),
        oil_change=get_val(rows, 'Oil change', 'EngineOil'),
    )
    obj.save()


def models_parse(models_link, brand_obj):
    table = parse(models_link, 'table', {'class': 'tdMenu1'}, True)
    articles = parse(models_link, 'div', {'class': 'tdArticleItem'})
    img = None
    for article in articles:
        image = article.find('img')
        if image:
            img = image.get('src')

    if not table:
        table = parse(models_link, 'table', {'class': 'tdmenu1'}, True)
        if not table:
            return False
    for row in table.find_all('tr'):
        cols = row.find_all('td')
        a_tag = cols[0].find('a')
        if len(cols) < 3 or not a_tag:
            continue

        model_name = str(cols[0].text).strip()
        mod_link = a_tag.get('href')

        global resume

        if model_name == 'LX178':
            resume = True

        if resume:
            obj, created = Model.objects.update_or_create(
                brand=brand_obj,
                name=model_name,
            )
            if img:
                obj.image.save(
                    **image_field(img, model_name)
                )

            print('- model', model_name)
            mod_parse(mod_link, obj)


def brands_parse():
    path = '/lawn-tractors/'
    table = parse(url + path, 'table', {'class': 'tdMenu1'}, True)
    for row in table.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) != 4:
            continue
        models_link = cols[0].find('a').get('href')
        brand_name = str(cols[0].text)
        brand_name = brand_name.replace('lawn tractors', '')
        brand_name = brand_name.strip()
        print('- brand', brand_name)

        obj, created = Brand.objects.update_or_create(
            name=brand_name
        )
        models_parse(models_link, obj)


def run():
    brands_parse()


run()
