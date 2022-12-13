from django.contrib import admin

from cars.models import *

admin.site.register(Brand)
admin.site.register(Model)
admin.site.register(Generation)
admin.site.register(EngineOil)
admin.site.register(InternalCombustionEngine)
admin.site.register(ElectricCarsHybrids)
admin.site.register(DrivetrainBrakesSuspension)
admin.site.register(Dimensions)
admin.site.register(SpaceVolumeWeights)
admin.site.register(ElectricEngine)
admin.site.register(Performance)


@admin.register(Modification)
class ModificationAdmin(admin.ModelAdmin):
    search_fields = [
        'modification'
    ]
