# -*- encoding: utf-8 -*-

"""
Data model of appliances and meters inside the residential home
"""
import sys

from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.db import connections
from model_utils.managers import PassThroughManager

from dbservice.apps.users.models import User
from dbservice.apps.utils import LOCATION_CHOICES
from dbservice.apps.utils import RESOURCE_TYPE_CHOICES
from dbservice.apps.utils import MEASUREMENT_UNIT_CHOICES
from dbservice.apps.utils import COUNTRY_CHOICES
from dbservice.apps.utils import APPLIANCES_CHOICES
from dbservice.apps.utils import PHASE_CHOICES


class ResidentialHome(models.Model):
    """
    Represents the residential home
    """
    dno_customer_id = models.OneToOneField(
        User,
        related_name='residential_homes',
    )
    country = models.CharField(
        max_length=64,
        choices=COUNTRY_CHOICES,
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Customer ID: {} from {}".format(self.dno_customer_id,
                                                str.upper(self.country))


class Appliance(models.Model):
    """
    Represents the appliances the meters are attached to
    """
    residential_home = models.ForeignKey(
        ResidentialHome,
        related_name='appliances',
    )
    name = models.CharField(max_length=64, choices=APPLIANCES_CHOICES)
    location = models.CharField(max_length=32, choices=LOCATION_CHOICES)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} from {} located in {}".format(self.name,
                                                 self.residential_home,
                                                 self.location)


class EnergyConsumptionPeriod(models.Model):
    """
    Period of the energy consumption for a single appliance
    """
    appliance = models.ForeignKey(
        Appliance,
        related_name='energy_consumption_period',
        null=True,
    )
    from_timestamp = models.DateTimeField()
    to_timestamp = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: from {} to {}".format(str(self.appliance),
                                          str(self.from_timestamp),
                                          str(self.to_timestamp))


class EnergyProductionPeriod(models.Model):
    """
    Period of the energy production for a single appliance
    """
    appliance = models.ForeignKey(
        Appliance,
        related_name='energy_production_period',
        null=True,
    )
    from_timestamp = models.DateTimeField()
    to_timestamp = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: from {} to {}".format(str(self.appliance),
                                          str(self.from_timestamp),
                                          str(self.to_timestamp))


class MainMeter(models.Model):
    """
    Represents the main meter in the residential home
    """
    residential_home = models.ForeignKey(
        ResidentialHome,
        related_name='main_meter',
        db_index=True,
    )
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} from {}".format(self.name, self.residential_home)


class SubMeter(models.Model):
    """
    Represents all the auxiliary meters in the residential home
    """
    residential_home = models.ForeignKey(
        ResidentialHome,
        related_name='sub_meter',
        db_index=True,
    )
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} from {}".format(self.name, self.residential_home)


class MeterPort(models.Model):
    """
    Represents a port on a meter
    """
    mainmeter = models.ForeignKey(
        MainMeter,
        related_name="meter_ports",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )
    submeter = models.ForeignKey(
        SubMeter,
        related_name="meter_ports",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )
    energy_consumption_period = models.OneToOneField(
        EnergyConsumptionPeriod,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )
    energy_production_period = models.OneToOneField(
        EnergyProductionPeriod,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )
    name = models.CharField(max_length=255)
    resource_type = models.CharField(
        max_length=32,
        choices=RESOURCE_TYPE_CHOICES,
    )
    phase = models.CharField(
        max_length=32,
        choices=PHASE_CHOICES,
        default=PHASE_CHOICES[0],
    )
    unit = models.CharField(
        max_length=32,
        choices=MEASUREMENT_UNIT_CHOICES,
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{name}".format(name=self.name)


class FixedValueMeterPort(models.Model):
    """
    A virtual meter port that is not associated with a meter and always gives a
    fixed value.
    """

    user = models.ForeignKey('users.User')
    value = models.BigIntegerField()
    resolution_in_seconds = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)


class VirtualEnergyPort(MeterPort):
    """
    Represents a virtual energy port where energy measurements can be
    calculated based on voltage, power factor and current.
    """
    consumption = models.ForeignKey(
        MeterPort,
        related_name="meter_ports_consumption",
        blank=False,
        null=True,
        db_index=True,
    )
    current = models.ForeignKey(
        MeterPort,
        related_name="meter_ports_current",
        blank=False,
        null=True,
        db_index=True,
    )
    voltage = models.ForeignKey(
        MeterPort,
        related_name="meter_ports_voltage",
        blank=False,
        null=True,
        db_index=True,
    )
    power_factor = models.ForeignKey(
        MeterPort,
        related_name="meter_ports_pf",
        blank=False,
        null=True,
        db_index=True,
    )


class MyFuzzyCountManager(QuerySet):
    def count(self):
        if 'test' in sys.argv:
            return super().count()
        else:
            postgres_engines = ("postgis", "postgresql", "django_postgrespool")
            engine = settings.DATABASES[self.db]["ENGINE"].split(".")[-1]
            is_postgres = engine.startswith(postgres_engines)
            is_filtered = self.query.where or self.query.having

            # if not is_postgres or is_filtered (hack for filtered as well):
            if not is_postgres:
                return super().count()

            cursor = connections[self.db].cursor()
            sqlquery = (
                "SELECT reltuples FROM pg_class ",
                "WHERE relname = '{}';".format(self.model._meta.db_table)
            )
            cursor.execute(''.join(sqlquery))
            count_estimate = int(cursor.fetchone()[0])

            if int(count_estimate) < 50000:
                return super().count()
            else:
                return count_estimate

MyCountManager = PassThroughManager.for_queryset_class(MyFuzzyCountManager)


class Measurement(models.Model):
    """
    A measurement on a meter port
    """
    meter_port = models.ForeignKey(
        MeterPort,
        related_name="measurement",
        db_index=True,
    )
    timestamp = models.DateTimeField(db_index=True)
    value = models.BigIntegerField()
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = MyCountManager()

    class Meta:
        get_latest_by = 'timestamp'
