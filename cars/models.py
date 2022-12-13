import datetime

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

from auto_info import settings


class Year:
    @staticmethod
    def choices():
        return [(r, r) for r in range(1984, datetime.date.today().year + 1)]

    @staticmethod
    def current():
        return datetime.date.today().year


class Brand(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=64)  # Mercedes
    image = models.ImageField(verbose_name=_('image'), upload_to='brands_img/', blank=True, null=True)

    def __str__(self):
        return self.name


class Model(models.Model):
    brand = models.ForeignKey(Brand, verbose_name=_('brand'), on_delete=models.PROTECT, blank=True, null=True)  # Mercedes
    name = models.CharField(verbose_name=_('name'), max_length=64)  # G Class
    image = models.ImageField(verbose_name=_('image'), upload_to='models_img/', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_last_generation(self):
        for object in Generation.objects.filter(model=self):
            if object.image:
                return object


class Generation(models.Model):
    model = models.ForeignKey(Model, verbose_name=_('model'), on_delete=models.PROTECT, blank=True, null=True)  # Модель
    name = models.CharField(verbose_name=_('name'), max_length=64)  # Название
    image = models.ImageField(verbose_name=_('image'), upload_to='generations_img/', blank=True, null=True)

    def __str__(self):
        return ' '.join([self.model.brand.name, self.model.name, self.name])


class EngineOil(models.Model):
    coolant = models.CharField(verbose_name=_('coolant'), blank=True, null=True, max_length=32)
    engine_systems = models.CharField(verbose_name=_('engine systems'), blank=True, null=True, max_length=32)


class InternalCombustionEngine(models.Model):
    power = models.CharField(verbose_name=_('power'), blank=True, null=True, max_length=32)
    power_per_litre = models.CharField(verbose_name=_('power per litre'), blank=True, null=True, max_length=32)
    torque = models.CharField(verbose_name=_('torque'), blank=True, null=True, max_length=32)
    engine_location = models.CharField(verbose_name=_('engine location'), blank=True, null=True, max_length=32)
    engine_displacement = models.CharField(verbose_name=_('engine displacement'), blank=True, null=True, max_length=32)
    number_of_cylinders = models.CharField(verbose_name=_('number of cylinders'), blank=True, null=True, max_length=32)
    position_of_cylinders = models.CharField(verbose_name=_('position of cylinders'), blank=True, null=True, max_length=32)
    cylinder_bore = models.CharField(verbose_name=_('cylinder bore'), blank=True, null=True, max_length=32)
    piston_stroke = models.CharField(verbose_name=_('piston stroke'), blank=True, null=True, max_length=32)
    compression_ratio = models.CharField(verbose_name=_('compression ratio'), blank=True, null=True, max_length=32)
    number_of_valves_per_cylinder = models.CharField(verbose_name=_('number of valves per cylinder'), blank=True, null=True, max_length=32)
    fuel_system = models.CharField(verbose_name=_('fuel system'), blank=True, null=True, max_length=32)
    engine_aspiration = models.CharField(verbose_name=_('engine aspiration'), blank=True, null=True, max_length=32)
    valvetrain = models.CharField(verbose_name=_('valvetrain'), blank=True, null=True, max_length=32)
    maximum_engine_speed = models.CharField(verbose_name=_('maximum engine speed'), blank=True, null=True, max_length=32)
    engine_model_code = models.CharField(verbose_name=_('engine model/code'), blank=True, null=True, max_length=32)
    engine_oil_capacity = models.CharField(verbose_name=_('engine oil capacity'), blank=True, null=True, max_length=32)
    oil_viscosity = models.CharField(verbose_name=_('oil viscosity'), blank=True, null=True, max_length=32)
    coolant = models.CharField(verbose_name=_('coolant'), blank=True, null=True, max_length=32)
    engine_systems = models.CharField(verbose_name=_('engine systems'), blank=True, null=True, max_length=32)


class ElectricCarsHybrids(models.Model):
    gross_battery_capacity = models.CharField(verbose_name=_('gross battery capacity'), blank=True, null=True, max_length=32)
    all_electric_range_wltp = models.CharField(verbose_name=_('all-electric range (wltp)'), blank=True, null=True, max_length=32)
    all_electric_range = models.CharField(verbose_name=_('all-electric range'), blank=True, null=True, max_length=32)
    average_energy_consumption_wltp = models.CharField(verbose_name=_('average energy consumption (wltp)'), blank=True, null=True, max_length=32)
    average_energy_consumption = models.CharField(verbose_name=_('average energy consumption'), blank=True, null=True, max_length=32)
    system_power = models.CharField(verbose_name=_('system power'), blank=True, null=True, max_length=32)
    system_torque = models.CharField(verbose_name=_('system torque'), blank=True, null=True, max_length=32)
    average_energy_consumption_nedc = models.CharField(verbose_name=_('average energy consumption (nedc)'), blank=True, null=True, max_length=32)
    max_speed_electric = models.CharField(verbose_name=_('max speed (electric)'), blank=True, null=True, max_length=32)
    all_electric_range_nedc = models.CharField(verbose_name=_('all-electric range (nedc)'), blank=True, null=True, max_length=32)
    net_usable_battery_capacity = models.CharField(verbose_name=_('net (usable) battery capacity'), blank=True, null=True, max_length=32)
    battery_technology = models.CharField(verbose_name=_('battery technology'), blank=True, null=True, max_length=32)
    recuperation_output = models.CharField(verbose_name=_('recuperation output'), blank=True, null=True, max_length=32)
    all_electric_range_nedc_wltp_equivalent = models.CharField(verbose_name=_('all-electric range (nedc, wltp equivalent)'), blank=True, null=True, max_length=32)
    average_energy_consumption_nedc_wltp_equivalent = models.CharField(verbose_name=_('average energy consumption (nedc, wltp equivalent)'), blank=True, null=True, max_length=32)
    battery_voltage = models.CharField(verbose_name=_('battery voltage'), blank=True, null=True, max_length=32)


class DrivetrainBrakesSuspension(models.Model):
    drivetrain_architecture = models.CharField(verbose_name=_('drivetrain architecture'), blank=True, null=True, max_length=32)
    drive_wheel = models.CharField(verbose_name=_('drive wheel'), blank=True, null=True, max_length=32)
    number_of_gears_automatic_transmission = models.CharField(verbose_name=_('number of gears (automatic transmission)'), blank=True, null=True, max_length=32)
    front_suspension = models.CharField(verbose_name=_('front suspension'), blank=True, null=True, max_length=32)
    rear_suspension = models.CharField(verbose_name=_('rear suspension'), blank=True, null=True, max_length=32)
    front_brakes = models.CharField(verbose_name=_('front brakes'), blank=True, null=True, max_length=32)
    rear_brakes = models.CharField(verbose_name=_('rear brakes'), blank=True, null=True, max_length=32)
    assisting_systems = models.CharField(verbose_name=_('assisting systems'), blank=True, null=True, max_length=32)
    steering_type = models.CharField(verbose_name=_('steering type'), blank=True, null=True, max_length=32)
    power_steering = models.CharField(verbose_name=_('power steering'), blank=True, null=True, max_length=32)
    tires_size = models.CharField(verbose_name=_('tires size'), blank=True, null=True, max_length=32)
    wheel_rims_size = models.CharField(verbose_name=_('wheel rims size'), blank=True, null=True, max_length=32)
    number_of_gears_manual_transmission = models.CharField(verbose_name=_('number of gears (manual transmission)'), blank=True, null=True, max_length=32)


class Dimensions(models.Model):
    length = models.CharField(verbose_name=_('length'), blank=True, null=True, max_length=32)
    width = models.CharField(verbose_name=_('width'), blank=True, null=True, max_length=32)
    height = models.CharField(verbose_name=_('height'), blank=True, null=True, max_length=32)
    wheelbase = models.CharField(verbose_name=_('wheelbase'), blank=True, null=True, max_length=32)
    front_track = models.CharField(verbose_name=_('front track'), blank=True, null=True, max_length=32)
    rear_back_track = models.CharField(verbose_name=_('rear (back) track'), blank=True, null=True, max_length=32)
    minimum_turning_circle_turning_diameter = models.CharField(verbose_name=_('minimum turning circle (turning diameter)'), blank=True, null=True, max_length=32)
    width_including_mirrors = models.CharField(verbose_name=_('width including mirrors'), blank=True, null=True, max_length=32)
    front_overhang = models.CharField(verbose_name=_('front overhang'), blank=True, null=True, max_length=32)
    rear_overhang = models.CharField(verbose_name=_('rear overhang'), blank=True, null=True, max_length=32)
    ride_height_ground_clearance = models.CharField(verbose_name=_('ride height (ground clearance)'), blank=True, null=True, max_length=32)
    width_with_mirrors_folded = models.CharField(verbose_name=_('width with mirrors folded'), blank=True, null=True, max_length=32)
    approach_angle = models.CharField(verbose_name=_('approach angle'), blank=True, null=True, max_length=32)
    departure_angle = models.CharField(verbose_name=_('departure angle'), blank=True, null=True, max_length=32)
    drag_coefficient_cd = models.CharField(verbose_name=_('drag coefficient (cd)'), blank=True, null=True, max_length=32)
    ramp_angle = models.CharField(verbose_name=_('ramp angle'), blank=True, null=True, max_length=32)
    wading_depth = models.CharField(verbose_name=_('wading depth'), blank=True, null=True, max_length=32)


class SpaceVolumeWeights(models.Model):
    kerb_weight = models.CharField(verbose_name=_('kerb weight'), blank=True, null=True, max_length=64)
    fuel_tank_capacity = models.CharField(verbose_name=_('fuel tank capacity'), blank=True, null=True, max_length=64)  # Мощность
    trunk_boot_space_minimum = models.CharField(verbose_name=_('trunk (boot) space - minimum'), blank=True, null=True, max_length=64)  # Мощность
    permitted_trailer_load_with_brakes_12 = models.CharField(verbose_name=_('permitted trailer load with brakes (12%)'), blank=True, null=True, max_length=64)  # Мощность
    max_weight = models.CharField(verbose_name=_('max. weight'), blank=True, null=True, max_length=64)  # Мощность
    max_load = models.CharField(verbose_name=_('max load'), blank=True, null=True, max_length=64)  # Мощность
    trunk_boot_space_maximum = models.CharField(verbose_name=_('trunk (boot) space - maximum'), blank=True, null=True, max_length=64)  # Мощность
    max_roof_load = models.CharField(verbose_name=_('max. roof load'), blank=True, null=True, max_length=64)  # Мощность
    adblue_tank = models.CharField(verbose_name=_('adblue tank'), blank=True, null=True, max_length=64)  # Мощность
    permitted_trailer_load_without_brakes = models.CharField(verbose_name=_('permitted trailer load without brakes'), blank=True, null=True, max_length=64)  # Мощность
    permitted_towbar_download = models.CharField(verbose_name=_('permitted towbar download'), blank=True, null=True, max_length=64)  # Мощность
    permitted_trailer_load_with_brakes_8 = models.CharField(verbose_name=_('permitted trailer load with brakes (8%)'), blank=True, null=True, max_length=64)  # Мощность
    cng_cylinder_capacity = models.CharField(verbose_name=_('cng cylinder capacity'), blank=True, null=True, max_length=64)  # Мощность


class ElectricEngine(models.Model):
    power = models.CharField(verbose_name=_('power'), blank=True, null=True, max_length=64)
    torque = models.CharField(verbose_name=_('torque'), blank=True, null=True, max_length=64)
    location = models.CharField(verbose_name=_('location'), blank=True, null=True, max_length=128)
    system_power = models.CharField(verbose_name=_('system power'), blank=True, null=True, max_length=128)
    system_torque = models.CharField(verbose_name=_('system torque'), blank=True, null=True, max_length=128)


class ICEngine(models.Model):
    power = models.CharField(verbose_name=_('power'), blank=True, null=True, max_length=32)
    power_per_litre = models.CharField(verbose_name=_('power per litre'), blank=True, null=True, max_length=32)
    torque = models.CharField(verbose_name=_('torque'), blank=True, null=True, max_length=32)
    engine_location = models.CharField(verbose_name=_('engine location'), blank=True, null=True, max_length=32)
    engine_displacement = models.CharField(verbose_name=_('engine displacement'), blank=True, null=True, max_length=32)
    number_of_cylinders = models.CharField(verbose_name=_('number of cylinders'), blank=True, null=True, max_length=32)
    position_of_cylinders = models.CharField(verbose_name=_('position of cylinders'), blank=True, null=True, max_length=32)
    cylinder_bore = models.CharField(verbose_name=_('cylinder bore'), blank=True, null=True, max_length=32)
    piston_stroke = models.CharField(verbose_name=_('piston stroke'), blank=True, null=True, max_length=32)
    compression_ratio = models.CharField(verbose_name=_('compression ratio'), blank=True, null=True, max_length=32)
    number_of_valves_per_cylinder = models.CharField(verbose_name=_('number of valves per cylinder'), blank=True, null=True, max_length=32)
    engine_aspiration = models.CharField(verbose_name=_('engine aspiration'), blank=True, null=True, max_length=32)
    engine_oil_capacity = models.CharField(verbose_name=_('engine oil capacity'), blank=True, null=True, max_length=32)
    oil_viscosity = models.CharField(verbose_name=_('oil viscosity'), blank=True, null=True, max_length=32)
    coolant = models.CharField(verbose_name=_('coolant'), blank=True, null=True, max_length=32)
    engine_model_code = models.CharField(verbose_name=_('engine model/code'), blank=True, null=True, max_length=32)
    fuel_system = models.CharField(verbose_name=_('fuel system'), blank=True, null=True, max_length=32)
    valvetrain = models.CharField(verbose_name=_('valvetrain'), blank=True, null=True, max_length=32)
    engine_systems = models.CharField(verbose_name=_('engine systems'), blank=True, null=True, max_length=32)
    maximum_engine_speed = models.CharField(verbose_name=_('maximum engine speed'), blank=True, null=True, max_length=32)

    def __str__(self):
        return self.power


class Performance(models.Model):
    fuel_consumption_economy_urban = models.CharField(verbose_name=_('fuel consumption (economy) - urban'), blank=True, null=True, max_length=32)
    fuel_consumption_economy_extra_urban = models.CharField(verbose_name=_('fuel consumption (economy) - extra urban'), blank=True, null=True, max_length=32)
    fuel_consumption_economy_combined = models.CharField(verbose_name=_('fuel consumption(economy) - combined'), blank=True, null=True, max_length=32)
    co2_emissions = models.CharField(verbose_name=_('cO2 emissions'), blank=True, null=True, max_length=32)
    fuel_type = models.CharField(verbose_name=_('fuel Type'), blank=True, null=True, max_length=32)
    acceleration_0_100_km_h = models.CharField(verbose_name=_('acceleration 0 - 100 km/h'), blank=True, null=True, max_length=32)
    acceleration_0_62_mph = models.CharField(verbose_name=_('acceleration 0 - 62 mph'), blank=True, null=True, max_length=32)
    maximum_speed = models.CharField(verbose_name=_('maximum speed'), blank=True, null=True, max_length=32)
    weight_to_power_ratio = models.CharField(verbose_name=_('weight-to-power ratio'), blank=True, null=True, max_length=32)
    weight_to_torque_ratio = models.CharField(verbose_name=_('weight-to-torque ratio'), blank=True, null=True, max_length=32)
    emission_standard = models.CharField(verbose_name=_('emission standard'), blank=True, null=True, max_length=32)
    fuel_consumption_at_low_speed_wltp = models.CharField(verbose_name=_('fuel consumption at Low speed (WLTP)'), blank=True, null=True, max_length=32)
    fuel_consumption_at_medium_speed_wltp = models.CharField(verbose_name=_('fuel consumption at Medium speed (WLTP)'), blank=True, null=True, max_length=32)
    fuel_consumption_at_high_speed_wltp = models.CharField(verbose_name=_('fuel consumption at high speed (WLTP)'), blank=True, null=True, max_length=32)
    fuel_consumption_at_very_high_speed_wltp = models.CharField(verbose_name=_('fuel consumption at very high speed (WLTP)'), blank=True, null=True, max_length=32)
    combined_fuel_consumption_wltp = models.CharField(verbose_name=_('combined fuel consumption (WLTP)'), blank=True, null=True, max_length=32)
    co2_emissions_wltp = models.CharField(verbose_name=_('cO2 emissions (WLTP)'), blank=True, null=True, max_length=32)
    acceleration_0_60_mph = models.CharField(verbose_name=_('acceleration 0 - 60 mph'), blank=True, null=True, max_length=32)
    s_100_km_h_0 = models.CharField(verbose_name=_('100 km/h - 0'), blank=True, null=True, max_length=32)
    fuel_consumption_economy_urban_nedc_wltp_equivalent = models.CharField(verbose_name=_('fuel consumption (economy) - urban (NEDC, WLTP equivalent)'), blank=True, null=True, max_length=32)
    fuel_consumption_economy_extra_urban_nedc_wltp_equivalent = models.CharField(verbose_name=_('fuel consumption (economy) - extra urban (NEDC, WLTP equivalent)'), blank=True, null=True, max_length=32)
    fuel_consumption_economy_combined_nedc_wltp_equivalent = models.CharField(verbose_name=_('fuel consumption (economy) - combined (NEDC, WLTP equivalent)'), blank=True, null=True, max_length=32)
    co2_emissions_nedc_wltp_equivalent = models.CharField(verbose_name=_('cO2 emissions (NEDC, WLTP equivalent)'), blank=True, null=True, max_length=32)
    acceleration_0_300_km_h = models.CharField(verbose_name=_('acceleration 0 - 300 km/h'), blank=True, null=True, max_length=32)
    fuel_consumption_economy_urban_nedc = models.CharField(verbose_name=_('fuel consumption (economy) - urban (NEDC)'), blank=True, null=True, max_length=32)
    fuel_consumption_economy_extra_urban_nedc = models.CharField(verbose_name=_('fuel consumption (economy) - extra urban (NEDC)'), blank=True, null=True, max_length=32)
    fuel_consumption_economy_combined_nedc = models.CharField(verbose_name=_('fuel consumption (economy) - combined (NEDC)'), blank=True, null=True, max_length=32)
    co2_emissions_nedc = models.CharField(verbose_name=_('cO2 emissions (NEDC)'), blank=True, null=True, max_length=32)
    fuel_consumption_at_low_speed_wltp_cng = models.CharField(verbose_name=_('fuel consumption at Low speed (WLTP) (CNG)'), blank=True, null=True, max_length=32)
    fuel_consumption_at_medium_speed_wltp_cng = models.CharField(verbose_name=_('fuel consumption at Medium speed (WLTP) (CNG)'), blank=True, null=True, max_length=32)
    fuel_consumption_at_high_speed_wltp_cng = models.CharField(verbose_name=_('fuel consumption at high speed (WLTP) (CNG)'), blank=True, null=True, max_length=32)
    fuel_consumption_at_very_high_speed_wltp_cng = models.CharField(verbose_name=_('fuel consumption at very high speed (WLTP) (CNG)'), blank=True, null=True, max_length=32)
    combined_fuel_consumption_wltp_cng = models.CharField(verbose_name=_('combined fuel consumption (WLTP) (CNG)'), blank=True, null=True, max_length=32)
    fuel_consumption_economy_urban_cng_nedc = models.CharField(verbose_name=_('fuel consumption (economy) - urban (CNG) (NEDC)'), blank=True, null=True, max_length=32)
    fuel_consumption_economy_extra_urban_cng_nedc = models.CharField(verbose_name=_('fuel consumption (economy) - extra urban (CNG) (NEDC)'), blank=True, null=True, max_length=32)
    fuel_consumption_economy_combin = models.CharField(verbose_name=_('fuel consumption (economy) - combined (CNG) (NEDC)'), blank=True, null=True, max_length=32)


class Modification(models.Model):
    generation = models.ForeignKey(Generation, verbose_name=_('generation'), on_delete=models.PROTECT)
    name = models.CharField(verbose_name=_('modification (engine)'), max_length=64, blank=True, null=True)
    image = models.ImageField(verbose_name=_('image'), upload_to='mods_img/', blank=True, null=True)
    start_prod = models.CharField(choices=Year.choices(), default=Year.current, verbose_name=_('year'), max_length=5, blank=True, null=True)
    end_prod = models.CharField(choices=Year.choices(), default=Year.current, verbose_name=_('year'), max_length=5, blank=True, null=True)
    powertrain_architecture = models.CharField(verbose_name=_('powertrain architecture'), max_length=64, blank=True, null=True)
    body_type = models.CharField(verbose_name=_('body type'), blank=True, null=True, max_length=64)
    seats = models.CharField(verbose_name=_('seats'), blank=True, null=True, max_length=64)
    doors = models.CharField(verbose_name=_('doors'), blank=True, null=True, max_length=64)
    engine_oil = models.ForeignKey(EngineOil, verbose_name=_('engine oil'), on_delete=models.PROTECT, blank=True, null=True)
    internal_combustion_engine = models.ForeignKey(InternalCombustionEngine, verbose_name=_('internal combustion engine specs'), on_delete=models.PROTECT, blank=True, null=True)
    electric_cars_hybrids = models.ForeignKey(ElectricCarsHybrids, verbose_name=_('electric cars and hybrids specs'), on_delete=models.PROTECT, blank=True, null=True)
    drivetrain_brakes_suspension = models.ForeignKey(DrivetrainBrakesSuspension, verbose_name=_('drivetrain, brakes and suspension specs'), on_delete=models.PROTECT, blank=True, null=True)
    dimensions = models.ForeignKey(Dimensions, verbose_name=_('dimensions'), on_delete=models.PROTECT, blank=True, null=True)
    space_volume_weights = models.ForeignKey(SpaceVolumeWeights, verbose_name=_('space, volume and weights'), on_delete=models.PROTECT, blank=True, null=True)
    electric_engine = models.ManyToManyField(ElectricEngine, verbose_name=_('electric engine'), blank=True)
    ic_engine = models.ForeignKey(ICEngine, verbose_name=_('ic engine specs'), on_delete=models.PROTECT, blank=True, null=True)
    performance = models.ForeignKey(Performance, verbose_name=_('performance specs'), on_delete=models.PROTECT, blank=True, null=True)

    def get_image(self):
        image_url = self.image.url if self.image else settings.STATIC_URL + 'moto/noimage.png'
        return image_url

    def get_absolute_url(self):
        return reverse('cars:modification_detail', args=[self.generation.model.brand.id, self.generation.model.id, self.generation.id, self.id])

    class Meta:
        ordering = ('-image',)
