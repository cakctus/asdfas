import datetime
from email.mime import image
from email.policy import default
from pyexpat import model
import re
from tkinter import N
from django.conf import settings

from django.db import models
from django.utils.translation import gettext as _


class Year:
    @staticmethod
    def choices():
        return [(r, r) for r in range(1984, datetime.date.today().year + 1)]

    @staticmethod
    def current():
        return datetime.date.today().year


class Brand(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=64)
    image = models.ImageField(verbose_name=_('image'), upload_to='brands_img/', blank=True, null=True)

    class Meta:
        ordering = ('name', '-image',)

    def __str__(self):
        return self.name


class Model(models.Model):
    brand = models.ForeignKey(Brand, verbose_name=_('brand'), on_delete=models.PROTECT, blank=True, null=True)  # Mercedes
    name = models.CharField(verbose_name=_('name'), max_length=64)
    image = models.ImageField(verbose_name=_('image'), upload_to='models/', blank=True, null=True)
    link = models.CharField(verbose_name=_('link'), max_length=128, blank=True, null=True)

    class Meta:
        ordering = ('name', '-image',)

    def __str__(self):
        return self.name

    def get_last_modification(self):
        for object in Modification.objects.filter(model=self):
            if object.image:
                return object
        return Modification.objects.filter(model=self).last()


class EngineTransmissionSpecifications(models.Model):
    clutch = models.CharField(verbose_name=_('clutch'), max_length=64, blank=True, null=True)
    transmission_type_final_drive = models.CharField(verbose_name=_('transmission type, final drive'), max_length=64, blank=True, null=True)
    gearbox = models.CharField(verbose_name=_('gearbox'), max_length=64, blank=True, null=True)
    cooling_system = models.CharField(verbose_name=_('cooling system'), max_length=64, blank=True, null=True)
    valves_per_cylinder = models.CharField(verbose_name=_('valves per cylinder'), max_length=64, blank=True, null=True)
    bore_x_stroke = models.CharField(verbose_name=_('bore x stroke'), max_length=64, blank=True, null=True)
    torque = models.CharField(verbose_name=_('torque'), max_length=64, blank=True, null=True)
    power = models.CharField(verbose_name=_('power'), max_length=64, blank=True, null=True)
    engine_type = models.CharField(verbose_name=_('engine type'), max_length=64, blank=True, null=True)
    capacity = models.CharField(verbose_name=_('capacity'), max_length=64, blank=True, null=True)
    engine_details = models.CharField(verbose_name=_('engine details'), max_length=64, blank=True, null=True)
    ignition = models.CharField(verbose_name=_('ignition'), max_length=64, blank=True, null=True)
    compression = models.CharField(verbose_name=_('compression'), max_length=64, blank=True, null=True)
    stroke = models.CharField(verbose_name=_('stroke'), max_length=64, blank=True, null=True)
    emission_details = models.CharField(verbose_name=_('emission details'), max_length=64, blank=True, null=True)
    exhaust_system = models.CharField(verbose_name=_('exhaust system'), max_length=64, blank=True, null=True)
    top_speed = models.CharField(verbose_name=_('top speed'), max_length=64, blank=True, null=True)
    driveline = models.CharField(verbose_name=_('driveline'), max_length=64, blank=True, null=True)
    _0_100_kmh = models.CharField(verbose_name=_('0-100 km/h'), max_length=64, blank=True, null=True)
    _60_140_kmh_highest_gear = models.CharField(verbose_name=_('60-140 km/h_highest gear'), max_length=64, blank=True, null=True)
    _14_mile = models.CharField(verbose_name=_('1/4 mile'), max_length=64, blank=True, null=True)


class BrakesSuspensionFrameWheels(models.Model):
    rear_brakes_diameter = models.CharField(verbose_name=_('rear brakes diameter'), max_length=64, blank=True, null=True)
    rear_brakes = models.CharField(verbose_name=_('rear brakes'), max_length=64, blank=True, null=True)
    front_brakes_diameter = models.CharField(verbose_name=_('front brakes diameter'), max_length=64, blank=True, null=True)
    front_brakes = models.CharField(verbose_name=_('front brakes'), max_length=64, blank=True, null=True)
    rear_tyre = models.CharField(verbose_name=_('rear tyre'), max_length=64, blank=True, null=True)
    front_tyre = models.CharField(verbose_name=_('front tyre'), max_length=64, blank=True, null=True)
    rear_wheel_travel = models.CharField(verbose_name=_('rear wheel travel'), max_length=64, blank=True, null=True)
    front_wheel_travel = models.CharField(verbose_name=_('front wheel travel'), max_length=64, blank=True, null=True)
    frame_type = models.CharField(verbose_name=_('frame type'), max_length=64, blank=True, null=True)
    wheels = models.CharField(verbose_name=_('wheels'), max_length=64, blank=True, null=True)
    rake = models.CharField(verbose_name=_('rake'), max_length=64, blank=True, null=True)
    rear_suspension_travel = models.CharField(verbose_name=_('rear suspension travel'), max_length=64, blank=True, null=True)
    front_suspension_travel = models.CharField(verbose_name=_('front suspension travel'), max_length=64, blank=True, null=True)
    rear_suspension = models.CharField(verbose_name=_('rear suspension'), max_length=64, blank=True, null=True)
    front_suspension = models.CharField(verbose_name=_('front suspension'), max_length=64, blank=True, null=True)
    rear_tyre_dimensions = models.CharField(verbose_name=_('rear tyre dimensions'), max_length=64, blank=True, null=True)
    front_tyre_dimensions = models.CharField(verbose_name=_('front tyre dimensions'), max_length=64, blank=True, null=True)
    seat = models.CharField(verbose_name=_('seat'), max_length=64, blank=True, null=True)
    trail = models.CharField(verbose_name=_('trail'), max_length=64, blank=True, null=True)


class PhysicalMeasuresCapacities(models.Model):
    fuel_capacity = models.CharField(verbose_name=_('fuel capacity'), max_length=64, blank=True, null=True)
    fuel_control = models.CharField(verbose_name=_('fuel control'), max_length=64, blank=True, null=True)
    fuel_system = models.CharField(verbose_name=_('fuel system'), max_length=64, blank=True, null=True)
    fuel_consumption_pr_10_km = models.CharField(verbose_name=_('fuel consumption pr. 10 km'), max_length=64, blank=True, null=True)
    fuel_consumption = models.CharField(verbose_name=_('fuel consumption'), max_length=64, blank=True, null=True)
    seat_height = models.CharField(verbose_name=_('seat height'), max_length=64, blank=True, null=True)
    alternate_seat_height = models.CharField(verbose_name=_('alternate seat height'), max_length=64, blank=True, null=True)
    weight_incl_oil_gas_etc = models.CharField(verbose_name=_('weight incl. oil, gas, etc'), max_length=64, blank=True, null=True)
    wheelbase = models.CharField(verbose_name=_('wheelbase'), max_length=64, blank=True, null=True)
    ground_clearance = models.CharField(verbose_name=_('ground clearance'), max_length=64, blank=True, null=True)
    power_weight_ratio = models.CharField(verbose_name=_('power/weight ratio'), max_length=64, blank=True, null=True)
    dry_weight = models.CharField(verbose_name=_('dry weight'), max_length=64, blank=True, null=True)
    overall_length = models.CharField(verbose_name=_('overall length'), max_length=64, blank=True, null=True)
    overall_width = models.CharField(verbose_name=_('overall width'), max_length=64, blank=True, null=True)
    overall_height = models.CharField(verbose_name=_('overall height'), max_length=64, blank=True, null=True)
    rear_percentage_of_weight = models.CharField(verbose_name=_('rear percentage of weight'), max_length=64, blank=True, null=True)
    front_percentage_of_weight = models.CharField(verbose_name=_('front percentage of weight'), max_length=64, blank=True, null=True)


class OtherSpecs(models.Model):
    comments = models.CharField(verbose_name=_('comments'), max_length=64, blank=True, null=True)
    starter = models.CharField(verbose_name=_('starter'), max_length=64, blank=True, null=True)
    color_options = models.CharField(verbose_name=_('color options'), max_length=64, blank=True, null=True)
    reserve_fuel_capacity = models.CharField(verbose_name=_('reserve fuel capacity'), max_length=64, blank=True, null=True)
    electrical = models.CharField(verbose_name=_('electrical'), max_length=64, blank=True, null=True)
    factory_warranty = models.CharField(verbose_name=_('factory warranty'), max_length=64, blank=True, null=True)
    instruments = models.CharField(verbose_name=_('instruments'), max_length=64, blank=True, null=True)
    light = models.CharField(verbose_name=_('light'), max_length=64, blank=True, null=True)
    carrying_capacity = models.CharField(verbose_name=_('carrying capacity'), max_length=64, blank=True, null=True)
    oil_capacity = models.CharField(verbose_name=_('oil capacity'), max_length=64, blank=True, null=True)
    lubrication_system = models.CharField(verbose_name=_('lubrication system'), max_length=64, blank=True, null=True)
    max_rpm = models.CharField(verbose_name=_('max rpm'), max_length=64, blank=True, null=True)
    modifications_compared_to_previous_model = models.CharField(verbose_name=_('modifications compared to previous model'), max_length=64, blank=True, null=True)
    greenhouse_gases = models.CharField(verbose_name=_('greenhouse gases'), max_length=64, blank=True, null=True)


class Modification(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=64)
    model = models.ForeignKey('Model', verbose_name=_('model'), on_delete=models.PROTECT)
    category = models.CharField(verbose_name=_('category'), max_length=64, blank=True, null=True)
    year = models.CharField(choices=Year.choices(), default=Year.current, verbose_name=_('year'), max_length=5, blank=True, null=True)
    image = models.ImageField(verbose_name=_('image'), default=settings.STATIC_URL + 'scooters/noimage.png', upload_to='moto_img/')
    engine_transmission_specifications = models.ForeignKey(EngineTransmissionSpecifications, verbose_name=_('engine transmission specifications'), blank=True, on_delete=models.PROTECT)
    brakes_suspension_frame_wheels = models.ForeignKey(BrakesSuspensionFrameWheels, verbose_name=_('brakes suspension frame wheels'), blank=True, on_delete=models.PROTECT)
    physical_measures_capacities = models.ForeignKey(PhysicalMeasuresCapacities, verbose_name=_('physical measures capacities'), blank=True, on_delete=models.PROTECT)
    other_specs = models.ForeignKey(OtherSpecs, verbose_name=_('other specs'), blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def get_image(self):
        image_url = self.image.url if self.image else settings.STATIC_URL + 'moto/noimage.png'
        return image_url

    # class Meta:
        # verbose_name = _('modification')
