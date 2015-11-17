from django.contrib import admin

from dbservice.apps.utils import MEASUREMENT_UNIT_CHOICES
from . import models


admin.site.register(models.FixedValueMeterPort)


@admin.register(models.VirtualEnergyPort)
class VirtualPortEnergyAdmin(admin.ModelAdmin):
    fields = ('name', 'consumption', 'current', 'voltage', 'power_factor')
    view_on_site = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "consumption":
            kwargs["queryset"] = models.MeterPort.objects.filter(
                unit=MEASUREMENT_UNIT_CHOICES[0][0]
                )
        if db_field.name == "current":
            kwargs["queryset"] = models.MeterPort.objects.filter(
                unit=MEASUREMENT_UNIT_CHOICES[3][0]
                )
        if db_field.name == "voltage":
            kwargs["queryset"] = models.MeterPort.objects.filter(
                unit=MEASUREMENT_UNIT_CHOICES[2][0]
                )
        if db_field.name == "power_factor":
            kwargs["queryset"] = models.MeterPort.objects.filter(
                unit=MEASUREMENT_UNIT_CHOICES[6][0]
            )

        return super(VirtualPortEnergyAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)
