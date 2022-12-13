import datetime

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

    def __str__(self):
        return self.name


class Engine(models.Model):
    starter = models.CharField(verbose_name=_('starter'), max_length=16, blank=True, null=True)
    capacity = models.CharField(verbose_name=_('capacity'), max_length=16, blank=True, null=True)
    power = models.CharField(verbose_name=_('power'), max_length=16, blank=True, null=True)
    max_power_rpm = models.CharField(verbose_name=_('maximum power at rpm'), max_length=16, blank=True, null=True)
    torque = models.CharField(verbose_name=_('torque'), max_length=16, blank=True, null=True)
    max_torque_rpm = models.CharField(verbose_name=_('maximum torque at rpm'), max_length=16, blank=True, null=True)
    fuel_supply_system = models.CharField(verbose_name=_('fuel supply system'), max_length=16, blank=True, null=True)
    motor_type = models.CharField(verbose_name=_('motor type'), max_length=32, blank=True, null=True)
    cooling = models.CharField(verbose_name=_('cooling'), max_length=32, blank=True, null=True)
    cylinder_dimensions = models.CharField(verbose_name=_('cylinder dimensions'), max_length=32, blank=True, null=True)
    compression_ratio = models.CharField(verbose_name=_('compression ratio'), max_length=32, blank=True, null=True)
    compression = models.CharField(verbose_name=_('compression'), max_length=32, blank=True, null=True)


class GearBox(models.Model):
    number_of_gears = models.CharField(verbose_name=_('number of gears'), max_length=16, blank=True, null=True)
    transmission_type = models.CharField(verbose_name=_('transmission type'), max_length=16, blank=True, null=True)


class ChassisBody(models.Model):
    front_brakes = models.CharField(verbose_name=_('front brakes'), max_length=32, blank=True, null=True)
    rear_brakes = models.CharField(verbose_name=_('rear brakes'), max_length=32, blank=True, null=True)
    front_brake_diameter = models.CharField(verbose_name=_('front brake diameter'), max_length=32, blank=True, null=True)
    rear_brake_diameter = models.CharField(verbose_name=_('rear brake diameter'), max_length=32, blank=True, null=True)
    front_suspension = models.CharField(verbose_name=_('front suspension'), max_length=32, blank=True, null=True)
    rear_suspension = models.CharField(verbose_name=_('rear suspension'), max_length=32, blank=True, null=True)
    body = models.CharField(verbose_name=_('body'), max_length=32, blank=True, null=True)


class Dimensions(models.Model):
    total_weight = models.CharField(verbose_name=_('total weight'), max_length=32, blank=True, null=True)
    length = models.CharField(verbose_name=_('length'), max_length=32, blank=True, null=True)
    width = models.CharField(verbose_name=_('width'), max_length=32, blank=True, null=True)
    height = models.CharField(verbose_name=_('height'), max_length=32, blank=True, null=True)
    seat_height = models.CharField(verbose_name=_('seat height'), max_length=32, blank=True, null=True)
    front_wheel_size = models.CharField(verbose_name=_('front wheel size'), max_length=32, blank=True, null=True)
    rear_wheel_size = models.CharField(verbose_name=_('rear wheel size'), max_length=32, blank=True, null=True)
    fuel_tank_capacity = models.CharField(verbose_name=_('fuel tank capacity'), max_length=32, blank=True, null=True)
    fuel_tank_reserve = models.CharField(verbose_name=_('fuel tank reserve'), max_length=32, blank=True, null=True)


class Performance(models.Model):
    top_speed = models.CharField(verbose_name=_('top speed'), max_length=32, blank=True, null=True)
    estimated_fuel_consumption = models.CharField(verbose_name=_('estimated fuel consumption'), max_length=32, blank=True, null=True)


class Modification(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=64)
    model = models.ForeignKey(Model, verbose_name=_('model'), on_delete=models.PROTECT)
    image = models.ImageField(verbose_name=_('image'), upload_to='scooters_img/', blank=True, null=True)
    performance = models.ManyToManyField(Performance, verbose_name=_('performance'), blank=True)
    dimensions = models.ManyToManyField(Dimensions, verbose_name=_('dimensions'), blank=True)
    chassis_body = models.ManyToManyField(ChassisBody, verbose_name=_('chassis and body'), blank=True)
    gear_box = models.ManyToManyField(GearBox, verbose_name=_('gear_box'), blank=True)
    engine = models.ManyToManyField(Engine, verbose_name=_('engine'), blank=True)

    def __str__(self):
        return self.name
