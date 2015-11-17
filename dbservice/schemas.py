from django.conf.urls import patterns
from django.conf.urls import url
from django.conf.urls import include

from django.db import models
from rest_framework.serializers import ModelSerializer
from rest_framework.fields import IntegerField

from dbservice.apps.utils.routers import JSONSchemaRouter
import dbservice.apps.users.views
import dbservice.apps.homes.views


# HACK
ModelSerializer.field_mapping[models.BigIntegerField] = IntegerField

router = JSONSchemaRouter()


router.register(
    'users/users',
    dbservice.apps.users.views.UserSchema,
    base_name='users-v1-user',
)

router.register(
    'homes/residential_homes',
    dbservice.apps.homes.views.ResidentialHomeSchema,
    base_name='homes-v1-residentialhome',
)

router.register(
    'homes/main_meters',
    dbservice.apps.homes.views.MainMeterSchema,
    base_name='homes-v1-mainmeter',
)

router.register(
    'homes/appliances',
    dbservice.apps.homes.views.ApplianceSchema,
    base_name='homes-v1-appliance',
)

router.register(
    'homes/sub_meters',
    dbservice.apps.homes.views.SubMeterSchema,
    base_name='homes-v1-submeter',
)

router.register(
    'homes/energy_consumption_periods',
    dbservice.apps.homes.views.EnergyConsumptionPeriodSchema,
    base_name='homes-v1-energyconsumptionperiod',
)

router.register(
    'homes/energy_production_periods',
    dbservice.apps.homes.views.EnergyProductionPeriodSchema,
    base_name='homes-v1-energyproductionperiod',
)

router.register(
    'homes/meter_ports',
    dbservice.apps.homes.views.MeterPortSchema,
    base_name='homes-v1-meterport',
)

router.register(
    'homes/virtual_energy_ports',
    dbservice.apps.homes.views.VirtualEnergyPortSchema,
    base_name='homes-v1-virtualenergyport',
)

router.register(
    'homes/measurements',
    dbservice.apps.homes.views.MeasurementSchema,
    base_name='homes-v1-measurement',
)

urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)
