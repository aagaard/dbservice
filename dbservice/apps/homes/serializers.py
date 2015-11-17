from . import models
from rest_framework import pagination, serializers

from dbservice.apps.utils import MEASUREMENT_UNIT_CHOICES


class DefaultSerializer(serializers.HyperlinkedModelSerializer):
    _default_view_name = 'homes-v1-%(model_name)s-detail'

    class Meta:
        abstract = True


class ResidentialHomeSerializer(DefaultSerializer):
    dno_customer_id = serializers.HyperlinkedRelatedField(
        view_name='users-v1-user-detail')

    class Meta:
        model = models.ResidentialHome
        fields = ('url', 'dno_customer_id', 'country')


class EnergyConsumptionPeriodSerializer(DefaultSerializer):
    class Meta:
        model = models.EnergyConsumptionPeriod
        fields = ('url', 'appliance', 'from_timestamp', 'to_timestamp')


class EnergyProductionPeriodSerializer(DefaultSerializer):
    class Meta:
        model = models.EnergyProductionPeriod
        fields = ('url', 'appliance', 'from_timestamp', 'to_timestamp')


class ApplianceSerializer(DefaultSerializer):
    energy_consumption_period = serializers.HyperlinkedRelatedField(
        many=True,
        required=False,
        view_name='homes-v1-energyconsumptionperiod-detail')

    energy_production_period = serializers.HyperlinkedRelatedField(
        many=True,
        required=False,
        view_name='homes-v1-energyproductionperiod-detail')

    class Meta:
        model = models.Appliance
        fields = ('url', 'residential_home', 'name', 'location',
                  'energy_consumption_period', 'energy_production_period')


class MainMeterSerializer(DefaultSerializer):
    class Meta:
        model = models.MainMeter
        fields = ('url', 'residential_home', 'name')


class SubMeterSerializer(DefaultSerializer):
    class Meta:
        model = models.SubMeter
        fields = ('url', 'residential_home', 'name')


class MeterPortSerializer(DefaultSerializer):
    class Meta:
        model = models.MeterPort
        fields = (
            'url',
            'mainmeter',
            'submeter',
            'energy_consumption_period',
            'energy_production_period',
            'name',
            'phase',
            'resource_type',
            'unit',
        )


class FixedValueMeterPortSerializer(DefaultSerializer):
    user = serializers.HyperlinkedRelatedField(
        view_name='users-v1-user-detail')

    class Meta:
        model = models.FixedValueMeterPort
        fields = ('url', 'user', 'value', 'resolution_in_seconds')


class MeasurementSerializer(DefaultSerializer):
    class Meta:
        model = models.Measurement
        fields = ('url', 'meter_port', 'timestamp', 'value')


class VirtualEnergyPortSerializer(DefaultSerializer):
    consumption = serializers.PrimaryKeyRelatedField(
        queryset=models.MeterPort.objects.filter(
            unit=MEASUREMENT_UNIT_CHOICES[0][0]
        )
    )
    current = serializers.PrimaryKeyRelatedField(
        queryset=models.MeterPort.objects.filter(
            unit=MEASUREMENT_UNIT_CHOICES[3][0]
        )
    )
    voltage = serializers.PrimaryKeyRelatedField(
        queryset=models.MeterPort.objects.filter(
            unit=MEASUREMENT_UNIT_CHOICES[2][0]
        )
    )
    power_factor = serializers.PrimaryKeyRelatedField(
        queryset=models.MeterPort.objects.filter(
            unit=MEASUREMENT_UNIT_CHOICES[6][0]
        )
    )

    class Meta:
        model = models.VirtualEnergyPort
        fields = (
            'url',
            'name',
            'consumption',
            'current',
            'voltage',
            'power_factor',
        )


class CondensedSerializer(serializers.Serializer):
    from_timestamp = serializers.DateTimeField()
    to_timestamp = serializers.DateTimeField()
    value = serializers.IntegerField()


class PaginatedCondensedSerializer(pagination.PaginationSerializer):
    """
    Serializes page objects of condense data querysets.
    """
    class Meta:
        object_serializer_class = CondensedSerializer


class AggregatedSerializer(serializers.Serializer):
    value = serializers.IntegerField()
    from_timestamp = serializers.DateTimeField()
    to_timestamp = serializers.DateTimeField()
    unit = serializers.CharField()


class StatusSerializer(serializers.Serializer):
    meter_type = serializers.CharField()
    meter_name = serializers.CharField()
    resource_type = serializers.CharField()
    meterport_name = serializers.CharField()
    time_discrepancy_occurence = serializers.DateTimeField()
    time_discrepancy_sec = serializers.DateTimeField()


class VirtualEnergyMeasurementSerializer(serializers.Serializer):
    consumption_acc_start = serializers.IntegerField()
    consumption_acc_stop = serializers.IntegerField()
    current = serializers.IntegerField()
    voltage = serializers.IntegerField()
    power_factor = serializers.IntegerField()
    from_timestamp = serializers.DateTimeField()
    to_timestamp = serializers.DateTimeField()


class TemperatureSerializer(serializers.Serializer):
    temperature = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    submeter_name = serializers.CharField()


class PaginatedTemperatureSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class = TemperatureSerializer
