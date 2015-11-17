"""
Filters for the measurement data
"""
# pylint: disable=W0232,C0112,R0903,C1001,E1101,C0111

import django_filters
from django_filters.filterset import STRICTNESS

from .models import (Appliance, EnergyConsumptionPeriod,
                     EnergyProductionPeriod, MainMeter, Measurement, MeterPort,
                     ResidentialHome, SubMeter)


class MeasurementFilter(django_filters.FilterSet):
    strict = STRICTNESS.RAISE_VALIDATION_ERROR
    meter_port = django_filters.NumberFilter(
        name='meter_port')
    min_value = django_filters.NumberFilter(
        name='value', lookup_type='gte')
    max_value = django_filters.NumberFilter(
        name='value',
        lookup_type='lte')
    min_timestamp = django_filters.DateTimeFilter(
        name='timestamp',
        lookup_type='gte',
    )
    max_timestamp = django_filters.DateTimeFilter(
        name='timestamp',
        lookup_type='lte',
    )

    class Meta:
        model = Measurement
        order_by = ['timestamp', 'id']
        fields = [
            'meter_port',
            'min_value',
            'max_value',
            'min_timestamp',
            'max_timestamp',
        ]


class MeterPortFilter(django_filters.FilterSet):
    strict = STRICTNESS.RAISE_VALIDATION_ERROR
    mainmeter = django_filters.NumberFilter(name='mainmeter')
    submeter = django_filters.NumberFilter(name='submeter')
    unit = django_filters.CharFilter(name='unit')
    resource_type = django_filters.CharFilter(name='resource_type')

    class Meta:
        model = MeterPort
        order_by = ['created', 'id']
        fields = [
            'mainmeter',
            'submeter',
            'resource_type',
            'unit',
        ]


class SubMeterFilter(django_filters.FilterSet):
    strict = STRICTNESS.RAISE_VALIDATION_ERROR

    class Meta:
        model = SubMeter
        order_by = ['created', 'id']
        fields = [
            'residential_home',
        ]


class MainMeterFilter(django_filters.FilterSet):
    strict = STRICTNESS.RAISE_VALIDATION_ERROR

    class Meta:
        model = MainMeter
        order_by = ['created', 'id']
        fields = [
            'residential_home',
        ]


class EnergyConsumptionPeriodFilter(django_filters.FilterSet):
    strict = STRICTNESS.RAISE_VALIDATION_ERROR

    class Meta:
        model = EnergyConsumptionPeriod
        order_by = ['created', 'id']
        fields = [
            'appliance',
        ]


class EnergyProductionPeriodFilter(django_filters.FilterSet):
    strict = STRICTNESS.RAISE_VALIDATION_ERROR

    class Meta:
        model = EnergyProductionPeriod
        order_by = ['created', 'id']
        fields = [
            'appliance',
        ]


class ApplianceFilter(django_filters.FilterSet):
    strict = STRICTNESS.RAISE_VALIDATION_ERROR

    class Meta:
        model = Appliance
        order_by = ['created', 'id']
        fields = [
            'residential_home',
        ]


class ResidentialHomeFilter(django_filters.FilterSet):
    strict = STRICTNESS.RAISE_VALIDATION_ERROR

    class Meta:
        model = ResidentialHome
        order_by = ['created', 'id']
        fields = [
            'dno_customer_id'
        ]
