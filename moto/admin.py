from django.contrib import admin

from moto.models import *

admin.site.register(Brand)
admin.site.register(Model)
admin.site.register(Modification)
admin.site.register(EngineTransmissionSpecifications)
admin.site.register(BrakesSuspensionFrameWheels)
admin.site.register(PhysicalMeasuresCapacities)
admin.site.register(OtherSpecs)
