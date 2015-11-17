from django.conf.urls import patterns
from django.conf.urls import url
from django.conf.urls import include

from dbservice.apps.utils.routers import AppRouter
import dbservice.apps.homes.views


router = AppRouter('homes-v1')


router.register(r'residential_homes',
                dbservice.apps.homes.views.ResidentialHomeViewSet)
router.register(r'appliances',
                dbservice.apps.homes.views.ApplianceViewSet)
router.register(r'energy_production_period',
                dbservice.apps.homes.views.EnergyProductionPeriodViewSet)
router.register(r'energy_consumption_period',
                dbservice.apps.homes.views.EnergyConsumptionPeriodViewSet)
router.register(r'main_meters',
                dbservice.apps.homes.views.MainMeterViewSet)
router.register(r'sub_meters',
                dbservice.apps.homes.views.SubMeterViewSet)
router.register(r'meter_ports',
                dbservice.apps.homes.views.MeterPortViewSet)
router.register(r'fixed_value_meter_ports',
                dbservice.apps.homes.views.FixedValueMeterPortViewSet)
router.register(r'measurements',
                dbservice.apps.homes.views.MeasurementViewSet)
router.register(r'virtual_energy_ports',
                dbservice.apps.homes.views.VirtualEnergyPortViewSet)

urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)
