import datetime

from dateutil.relativedelta import relativedelta
from rest_framework import status, viewsets
from rest_framework.decorators import link, list_route
from rest_framework.exceptions import ParseError
from rest_framework.fields import ValidationError
from rest_framework.response import Response

from dbservice.apps.homes.models import Measurement
from dbservice.apps.users.models import User
from dbservice.apps.utils.viewsets import (BulkCreateModelMixin,
                                           JSONSchemaViewSet)

from . import filters, models, serializers
from .aggregated import (aggregated, get_temperature_home,
                         response_virtual_energy_port_measurements)
from .condensed import condensed
from .status import get_status
from .utils import response_fixed_value_measurements, response_measurements


class ApplianceViewSet(viewsets.ModelViewSet):
    """
    `/schemas/homes/appliances/list/`
    `/schemas/homes/appliances/detail/` and
    `/schemas/homes/appliances/update/`

    Appliance  may be filtered on `residential_home`.
    """
    model = models.Appliance
    serializer_class = serializers.ApplianceSerializer
    filter_class = filters.ApplianceFilter
    filter_fields = ('residential_home')

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValidationError as e:
            raise ParseError(e)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        else:
            return qs.filter(residential_home__dno_customer_id=user)

    # def create(self, request):
    #      ec_period = request.POST.get('energy_consumption_period', None)
    #      ep_period = request.POST.get('energy_production_period', None)
    #      import ipdb; ipdb.set_trace()
    #      oneflow_defined = bool(ec_period) != bool(ep_period)

    #      if not oneflow_defined:
    #          raise ParseError(
    #              "A single consumption/production period must be defined")

    #      serializer = ApplianceSerializer(data=request.DATA)
    #      if serializer.is_valid():
    #          serializer.save()

    #          return Response(serializer.data, status=status.HTTP_201_CREATED)
    #      return Response(serializer.errors,
    #          status=status.HTTP_400_BAD_REQUEST)


class ApplianceSchema(JSONSchemaViewSet):
    schema_for = serializers.ApplianceSerializer
    app_name = 'homes-v1'


class EnergyConsumptionPeriodViewSet(viewsets.ModelViewSet):
    """
    Data format described in
    `/schemas/homes/energy_consumption_period/list/`
    `/schemas/homes/energy_consumption_period/detail/` and
    `/schemas/homes/energy_consumption_period/update/`

    Energy consumption period may be filtered on `appliance`.
    """
    model = models.EnergyConsumptionPeriod
    serializer_class = serializers.EnergyConsumptionPeriodSerializer
    filter_class = filters.EnergyConsumptionPeriodFilter
    filter_fields = ('appliance')

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValidationError as e:
            raise ParseError(e)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        else:
            return qs.filter(appliance__residential_home__dno_customer_id=user)


class EnergyConsumptionPeriodSchema(JSONSchemaViewSet):
    schema_for = serializers.EnergyConsumptionPeriodSerializer
    app_name = 'homes-v1'


class EnergyProductionPeriodViewSet(viewsets.ModelViewSet):
    """
    Data format described in
    `/schemas/homes/energy_production_period/list/`
    `/schemas/homes/energy_production_period/detail/` and
    `/schemas/homes/energy_production_period/update/`

    Energy production period may be filtered on `appliance`.
    """
    model = models.EnergyProductionPeriod
    serializer_class = serializers.EnergyProductionPeriodSerializer
    filter_class = filters.EnergyProductionPeriodFilter
    filter_fields = ('appliance')

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValidationError as e:
            raise ParseError(e)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        else:
            return qs.filter(appliance__residential_home__dno_customer_id=user)


class EnergyProductionPeriodSchema(JSONSchemaViewSet):
    schema_for = serializers.EnergyProductionPeriodSerializer
    app_name = 'homes-v1'


class MainMeterViewSet(viewsets.ModelViewSet):
    """
    Data format described in
    `/schemas/homes/main_meters/list`
    `/schemas/homes/main_meters/detail/` and
    `/schemas/homes/main_meters/update`

    Main meters may be filtered on `residential_home`.
    """
    model = models.MainMeter
    serializer_class = serializers.MainMeterSerializer
    filter_class = filters.MainMeterFilter
    filter_fields = ('residential_home')

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValidationError as e:
            raise ParseError(e)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        else:
            return qs.filter(residential_home__dno_customer_id=user)


class MainMeterSchema(JSONSchemaViewSet):
    schema_for = serializers.MainMeterSerializer
    app_name = 'homes-v1'


class SubMeterViewSet(viewsets.ModelViewSet, BulkCreateModelMixin):
    """
    Data format described in
    `/schemas/homes/sub_meters/list/`
    `/schemas/homes/sub_meters/detail/` and
    `/schemas/homes/sub_meters/update/`.

    Submeters may be filtered on `residential_home`.

    Bulk creation possible at `/homes/sub_meters/bulk/`
    (post JSON array of objects to create).
    """
    model = models.SubMeter
    serializer_class = serializers.SubMeterSerializer
    filter_class = filters.SubMeterFilter
    filter_fields = ('residential_home')

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValidationError as e:
            raise ParseError(e)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        else:
            return qs.filter(residential_home__dno_customer_id=user)


class SubMeterSchema(JSONSchemaViewSet):
    schema_for = serializers.SubMeterSerializer
    app_name = 'homes-v1'


class MeterPortViewSet(viewsets.ModelViewSet, BulkCreateModelMixin):
    """
    Data format described in
    `/schemas/homes/meter_ports/list/`
    `/schemas/homes/meter_ports/detail/` and
    `/schemas/homes/meter_ports/update/`

    Meter ports may be filtered on `mainmeter`, `submeter`,
    `resource_type`, `unit`.

    Configuration of a meter port can be obtained at
    `/homes/meter_ports/{id}/`,

    Bulk creation possible at `/homes/meter_ports/bulk/`
    (post JSON array of objects to create).
    """
    model = models.MeterPort
    serializer_class = serializers.MeterPortSerializer
    filter_class = filters.MeterPortFilter

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValidationError as e:
            raise ParseError(e)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        null_defs = ['None', 'none', 'Null', 'null', 'NULL']
        meters = ['submeter', 'mainmeter']
        myfilter = {"{}__isnull".format(key): True
                    for key, val in self.request.GET.items()
                    if key in meters and val in null_defs}
        if len(myfilter) > 0:
            return models.MeterPort.objects.filter(**myfilter)

        if user.is_superuser:
            return qs
        else:
            return (
                qs.filter(mainmeter__residential_home__dno_customer_id=user) |
                qs.filter(submeter__residential_home__dno_customer_id=user)
            )

    def create(self, request):
        """
        Ensure that only one flow is associated to one submeter or main meter
        is the only meter
        """
        submeter_def = bool(request.POST.get('submeter', None))
        mainmeter_def = bool(request.POST.get('mainmeter', None))
        ec_def = bool(request.POST.get('energy_consumption_period', None))
        ep_def = bool(request.POST.get('energy_production_period', None))

        # We cannot associate a meterport to a submeter and a main meter
        if submeter_def and mainmeter_def:
            raise ParseError(
                "Meter port cannot be associated to a submeter and main meter")

        # If main meter is defined then the submeter cannot not be defined
        if mainmeter_def:
            if ec_def or ep_def:
                raise ParseError(
                    'Meter port cannot be associated ' +
                    'to an energy consumption and production period ' +
                    'for a main meter'
                )
        # If submeter defined then ensure only one or none period is defined
        if submeter_def:
            if ec_def and ep_def:
                raise ParseError(
                    "Only a single consumption/production period " +
                    "can be defined for submeters"
                )

        # Serialize the data and check if it is valid
        serializer = serializers.MeterPortSerializer(
            data=request.DATA, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @link()
    def get_measurements(self, request, pk=None):
        return response_measurements(request, meter_port_pk=pk)


class MeterPortSchema(JSONSchemaViewSet):
    schema_for = serializers.MeterPortSerializer
    app_name = 'homes-v1'


class FixedValueMeterPortViewSet(viewsets.ModelViewSet, BulkCreateModelMixin):
    """
    Data format described in
    `/schemas/homes/fixed_value_meter_ports/list/`
    `/schemas/homes/fixed_value_meter_ports/detail/` and
    `/schemas/homes/fixed_value_meter_ports/update/`.

    Configuration of a meter port can be obtained at
    `/homes/fixed_value_meter_ports/{id}/`.

    Virtual measurements are obtained at
    `/homes/fixed_value_meter_ports/{id}/get_measurements/?from_timestamp={tf}&to_timestamp={tt}`.

    Bulk creation possible at `/homes/fixed_value_meter_ports/bulk/`
    (post JSON array of objects to create).
    """
    user = User
    model = models.FixedValueMeterPort
    serializer_class = serializers.FixedValueMeterPortSerializer

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValidationError as e:
            raise ParseError(e)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        else:
            return qs.filter(user=user)

    @link()
    def get_measurements(self, request, pk=None):
        return response_fixed_value_measurements(request, pk)


class FixedValueMeterPortSchema(JSONSchemaViewSet):
    schema_for = serializers.MeterPortSerializer
    app_name = 'homes-v1'


class VirtualEnergyPortViewSet(viewsets.ModelViewSet):
    """
    Data format described in
    `/schemas/homes/virtual_energy_ports/list/`
    `/schemas/homes/virtual_energy_ports/detail/` and
    `/schemas/homes/virtual_energy_ports/update/`

    A virtual energy port consists of four meterports that implicit represents
    a energy consumption port; a main meter consumption meter port, a current
    meterport, a voltage meterport and a power_factor meter port.

    An aligned energy measurement set consists of a tuple of an accumulated
    consumption start value, an accumulated stop value, an average current
    value, an average voltage, and an average power factor within the time
    period. The from_timestamp and to_timestamp indicate the time interval of
    energy measurement. It can be obtained from
    `/homes/virtual_energy_ports/{meter_port_id}/get_measurements/?from_timestamp={tf}&to_timestamp={tt}`
    """

    model = models.VirtualEnergyPort
    serializer_class = serializers.VirtualEnergyPortSerializer

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValidationError as e:
            raise ParseError(e)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        else:
            return (
                qs.filter(mainmeter__residential_home__dno_customer_id=user) |
                qs.filter(submeter__residential_home__dno_customer_id=user)
            )

    @link()
    def get_measurements(self, request, pk=None):
        return response_virtual_energy_port_measurements(request, pk)


class VirtualEnergyPortSchema(JSONSchemaViewSet):
    schema_for = serializers.VirtualEnergyPortSerializer
    app_name = 'homes-v1'


class MeasurementViewSet(viewsets.ModelViewSet, BulkCreateModelMixin):
    """
    Data format described in `/schemas/homes/measurements/list/`,
    `/schemas/homes/measurements/detail/` and
    `/schemas/homes/measurements/update/`.

    Measurements may be filtered on `meter_port`,
    `min_value`,`max_value`,`min_timestamp` and `max_timestamp`.

    Condensed stored data for each input can be obtained at
    `/homes/measurements/{meter_port_id}/hourly_condensed/`,
    `/homes/measurements/{meter_port_id}/daily_condensed/`,
    `/homes/measurements/{meter_port_id}/monthly_condensed/` and
    `/homes/measurements/{meter_port_id}/yearly_condensed/`. For condensed
    data, query parameters `from_timestamp` and `to_timestamp` must be
    provided.  The data format for condensed data is described in
    `/static/condensed-list.json`.

    Latest measurements can be viewed with `/homes/measurements/latest/`.

    Bulk creation possible at `/homes/measurements/bulk/`
    (post JSON array of objects to create).
    """
    throttle_scope = 'measurements'
    model = models.Measurement
    serializer_class = serializers.MeasurementSerializer
    filter_class = filters.MeasurementFilter
    filter_fields = ('meter_port', 'timestamp', 'value')

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValidationError as e:
            raise ParseError(e)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        else:
            return (
                qs.filter(meter_port__mainmeter__residential_home__dno_customer_id=user) |  # noqa
                qs.filter(meter_port__submeter__residential_home__dno_customer_id=user)  # noqa
            )

    @list_route()
    def latest(self, request):
        all_measurements = Measurement.objects.all().order_by('-timestamp')
        page = self.paginate_queryset(all_measurements)
        serializer = self.get_pagination_serializer(page)
        return Response(serializer.data)

    @link()
    def hourly_condensed(self, request, pk=None):
        return condensed(request, pk, datetime.timedelta(hours=1))

    @link()
    def daily_condensed(self, request, pk=None):
        return condensed(request, pk, datetime.timedelta(days=1))

    @link()
    def monthly_condensed(self, request, pk=None):
        return condensed(request, pk, relativedelta(months=1))

    @link()
    def yearly_condensed(self, request, pk=None):
        return condensed(request, pk, relativedelta(years=1))


class MeasurementSchema(JSONSchemaViewSet):
    schema_for = serializers.MeasurementSerializer
    app_name = 'homes-v1'


class ResidentialHomeViewSet(viewsets.ModelViewSet):
    """
    Data format described in `/schemas/homes/residential_homes/list`
    `/schemas/homes/residential_homes/detail/` and
    `/schemas/homes/residential_homes/update`.

    Electrical energy consumption and production for the residential home can
    be obtained at
    `/homes/residential_homes/{home_id}/get_energy_{consumption,production}/
    ?from_timestamp={tf}&to_timestamp={tt}[&tau={tau}]`, where `{home_id}` is
    the id of the residential home, `{tf}` and `{tt}` represent the
    timeslot. `{tau}` is optional and can have following values 1min, 5min,
    10min, 15min, 20min, 30min, hourly, daily, weekly, monthly, yearly.

    Consumption data is based on main meter data and production data is based
    on submeters.

    Get status of the residential can be obtained at
    `/homes/residential_homes/{home_id}/get_status/
    ?from_timestamp={tf}&to_timestamp={tt}&tolerance={tol}`, where `tf` is the
    start timestamp for checking to `tt` and `tol` is the tolerance `30min`,
    `1h`, `12h`, `1d`, `1w` and `1m`for which time interval between
    measurements that it must be within.

    Temperature measurements can be obtained from
    `/homes/residential_homes/{home_id}/get_temperature/[?from_timestamp={tf}&to_timestamp={tt}]`.

    Residential homes can be filtered on `dno_customer_id`.
    """
    model = models.ResidentialHome
    serializer_class = serializers.ResidentialHomeSerializer
    filter_class = filters.ResidentialHomeFilter
    filter_fields = ('dno_customer_id')

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValidationError as e:
            raise ParseError(e)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        else:
            return qs.filter(dno_customer_id=user)

    @link()
    def get_energy_consumption(self, request, pk=None):
        return aggregated(request, pk, 'consumption')

    @link()
    def get_energy_production(self, request, pk=None):
        return aggregated(request, pk, 'production')

    @link()
    def get_temperature(self, request, pk=None):
        return get_temperature_home(request, pk)

    @link()
    def get_status(self, request, pk=None):
        return get_status(request, pk)


class ResidentialHomeSchema(JSONSchemaViewSet):
    schema_for = serializers.ResidentialHomeSerializer
    app_name = 'homes-v1'
