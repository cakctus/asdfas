from django.contrib import admin

# Register your models here.
from scooters.models import Modification, Model, Brand, GearBox, Engine, ChassisBody, Dimensions, Performance

admin.site.register(Brand)
admin.site.register(Model)
admin.site.register(Modification)

admin.site.register(GearBox)
admin.site.register(Engine)
admin.site.register(ChassisBody)
admin.site.register(Dimensions)
admin.site.register(Performance)
