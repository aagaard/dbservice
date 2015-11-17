import datetime
import itertools
import operator
from collections import OrderedDict, namedtuple

from .condensed import condense
from .models import Measurement, VirtualEnergyPort
from .serializers import AggregatedSerializer, PaginatedTemperatureSerializer, \
    VirtualEnergyMeasurementSerializer
from .utils import get_urlquery_timespan, get_urlquery_value, pairwise
from dateutil.relativedelta import relativedelta
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg
from django.views.decorators.http import require_GET
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from dbservice.apps.homes.serializers import PaginatedCondensedSerializer
from dbservice.apps.utils import MEASUREMENT_UNIT_CHOICES


condensed_options = OrderedDict([
    ('1min', datetime.timedelta(minutes=1)),
    ('5min', datetime.timedelta(minutes=5)),
    ('10min', datetime.timedelta(minutes=10)),
    ('15min', datetime.timedelta(minutes=15)),
    ('20min', datetime.timedelta(minutes=20)),
    ('30min', datetime.timedelta(minutes=30)),
    ('1h', datetime.timedelta(hours=1)),
    ('12h', datetime.timedelta(hours=12)),
    ('hourly', datetime.timedelta(hours=1)),
    ('daily', datetime.timedelta(days=1)),
    ('1d', datetime.timedelta(days=1)),
    ('weekly', datetime.timedelta(days=7)),
    ('1w', datetime.timedelta(days=7)),
    ('monthly', relativedelta(months=1)),
    ('1m', relativedelta(months=1)),
    ('yearly', relativedelta(years=1))
])

AveragePower = namedtuple(
    'AveragePower', ['value', 'from_timestamp', 'to_timestamp', 'unit'])


def _find_negative_accumulated_values(data):
    """Return negative differential in data if next is positiv."""
    idx0_values, idx1_values, idx2_values = itertools.tee(data, 3)
    next(idx1_values), next(idx2_values), next(idx2_values)
    return [
        idx0.value - idx1.value
        for idx0, idx1, idx2 in
        zip(idx0_values, idx1_values, idx2_values)
        if idx1.value < idx0.value and idx1.value <= idx2.value
    ]


def aggregate_mainmeter_consumption(home_id,
                                    from_timestamp, to_timestamp, tau):
    """Aggregate consumption from mainmeter."""
    energy_unit = MEASUREMENT_UNIT_CHOICES[0][0]
    filters = {
        'meter_port__mainmeter__residential_home__id': home_id,
        'meter_port__unit': energy_unit,
    }
    if from_timestamp and to_timestamp:
        filters['timestamp__gte'] = from_timestamp - tau
        filters['timestamp__lte'] = to_timestamp + tau
    data = Measurement.objects.filter(**filters).order_by('timestamp')
    if tau:
        return condense(data, from_timestamp, tau)
    else:
        value = 0
        if data:
            not_accumulated_values = _find_negative_accumulated_values(data)
            to_value, from_value = data.reverse()[0].value, data[0].value
            value = to_value - from_value + sum(not_accumulated_values)
        return [
            AveragePower(
                value=value,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
                unit=energy_unit,
            )
        ]


def aggregate_submeter_measured_production(home_id,
                                           from_timestamp, to_timestamp, tau):
    """Aggregate production from submeters based on home_id."""
    energy_unit = MEASUREMENT_UNIT_CHOICES[0][0]
    filters = {
        'meter_port__submeter__residential_home__id': home_id,
        ('meter_port__energy_production_period__'
         'appliance__residential_home__id'): home_id,
        'meter_port__unit': energy_unit,
    }
    if from_timestamp and to_timestamp:
        filters['timestamp__gte'] = from_timestamp - tau
        filters['timestamp__lte'] = to_timestamp + tau

    data = Measurement.objects.filter(**filters).order_by(
        'timestamp',
    ).values_list(
        'meter_port__submeter__id', 'timestamp', 'value',
    )
    if tau:
        result = []
        data = sorted(data, key=lambda x: x[0])  # Sort before groupby
        SubmeterMeasurement = namedtuple('Measurement', ['value', 'timestamp'])
        for key, group in itertools.groupby(data, key=lambda x: x[0]):
            raw_data = [SubmeterMeasurement(timestamp=timestamp, value=value)
                        for submeter, timestamp, value in group]
            result.append(condense(raw_data, from_timestamp, tau))

        def sum_values(condense_timeslot_set):
            ft, tt = zip(
                *map(
                    operator.attrgetter('from_timestamp', 'to_timestamp'),
                    condense_timeslot_set
                )
            )
            assert len(set(ft)) == 1
            assert len(set(tt)) == 1

            if condense_timeslot_set:
                return condense_timeslot_set[0]._replace(
                    value=sum([entry.value for entry in condense_timeslot_set])
                )
            return []
        return map(sum_values, zip(*result))
    else:
        prod_value = 0
        if data:
            for key, group in itertools.groupby(data, lambda x: x[0]):
                data_submeter = [item[2] for item in group]
                not_accumulated_values = _find_negative_accumulated_values(
                    data_submeter)
                prod_value += (data_submeter[-1] - data_submeter[0] +
                               sum(not_accumulated_values))
        return [
            AveragePower(
                value=prod_value,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
                unit=energy_unit,
            )
        ]


@require_GET
def aggregated(request, home_id, pflow):
    """Aggregate the measurements based on `home_id` and power flow `pflow`."""
    from_timestamp, to_timestamp = get_urlquery_timespan(request)
    tau = get_urlquery_value(request,
                             'tau',
                             parser_options=condensed_options,
                             default_return=datetime.timedelta(seconds=0))
    # Aggregate measurement based on flow
    if pflow is 'consumption':
        result = aggregate_mainmeter_consumption(
            home_id, from_timestamp, to_timestamp, tau)
    elif pflow is 'production':
        result = aggregate_submeter_measured_production(
            home_id, from_timestamp, to_timestamp, tau)
    if tau:
        paginator = Paginator(list(result), 20)
        page = request.QUERY_PARAMS.get('page')
        try:
            result_paginated = paginator.page(page)
        except PageNotAnInteger:
            result_paginated = paginator.page(1)
        except EmptyPage:
            result_paginated = paginator.page(paginator.num_pages)

        serializer_context = {'request': request}
        serializer = PaginatedCondensedSerializer(result_paginated,
                                                  context=serializer_context)
    else:
        serializer = AggregatedSerializer(result, many=True)
    return Response(serializer.data)


Temperature = namedtuple(
    'Temperature', [
        'temperature',
        'timestamp',
        'submeter_name',
    ]
)


@require_GET
def get_temperature_home(request, pk):
    from_timestamp, to_timestamp = get_urlquery_timespan(request,
                                                         required=False)
    kwargs = {
        'meter_port__submeter__residential_home__id': pk,
        'meter_port__resource_type': 'temperature',
    }
    if from_timestamp and to_timestamp:
        kwargs.update({
            'timestamp__gte': from_timestamp,
            'timestamp__lte': to_timestamp,
        })
    result = Measurement.objects.filter(**kwargs).order_by(
        'meter_port__submeter__residential_home__id',
        'meter_port__submeter__name',
        'timestamp',
    ).values_list(
        'value', 'timestamp', 'meter_port__submeter__name')
    result_queryset = list(map(lambda m: Temperature(*m), result))
    paginator = Paginator(result_queryset, 20)
    page = request.QUERY_PARAMS.get('page')
    try:
        result_paginated = paginator.page(page)
    except PageNotAnInteger:
        result_paginated = paginator.page(1)
    except EmptyPage:
        result_paginated = paginator.page(paginator.num_pages)

    serializer_context = {'request': request}
    serializer = PaginatedTemperatureSerializer(
        result_paginated,
        context=serializer_context
    )
    return Response(serializer.data)


# Class to feed the serializer
ConsumptionAligned = namedtuple(
    'ConsumptionAligned', [
        'consumption_acc_start',
        'consumption_acc_stop',
        'current',
        'voltage',
        'power_factor',
        'from_timestamp',
        'to_timestamp',
    ]
)


def virtual_energy_measurements_to_objs(
        consumption_acc_start,
        consumption_acc_stop,
        current,
        voltage,
        power_factor,
        from_timestamp,
        to_timestamp):
    return ConsumptionAligned(consumption_acc_start=consumption_acc_start,
                              consumption_acc_stop=consumption_acc_stop,
                              current=current,
                              voltage=voltage,
                              power_factor=power_factor,
                              from_timestamp=from_timestamp,
                              to_timestamp=to_timestamp)


def get_virtual_energy_measurements(virtual_port_id, from_timestamp,
                                    to_timestamp):
    """
    Get follower measurements (current, voltage, and power_factor) and leading
    measurements (the consumption)
    """
    leader_field = 'consumption'
    followers = ['current', 'voltage', 'power_factor']
    try:
        meter_port_ids = VirtualEnergyPort.objects.get(id=virtual_port_id)
    except MultipleObjectsReturned:
        err_msg = "Virtualport '{}' have multiple entries".format(
            virtual_port_id)
        raise ParseError()
    except ObjectDoesNotExist:
        err_msg = "Virtualport '{}' does not exist".format(virtual_port_id)
        raise ParseError(err_msg)
    except:
        raise ParseError("Unexpected error")

    leader_measurements = Measurement.objects.filter(
        meter_port_id=getattr(meter_port_ids, leader_field).id
    ).order_by('timestamp')

    if from_timestamp and to_timestamp:
        leader_measurements = leader_measurements.filter(
            timestamp__gt=from_timestamp,
            timestamp__lt=to_timestamp
        )

        follower_measurements = [
            Measurement.objects.filter(
                meter_port_id=getattr(meter_port_ids, m_type).id,
                timestamp__gt=from_timestamp,
                timestamp__lt=to_timestamp)
            for m_type in followers
        ]

    return follower_measurements, leader_measurements


def calc_timeslots(followers, leader):
    """
    Calculate `avg_timeslot` on timeslots defined by leader
    """
    def avg_timeslot(follower, from_timestamp, to_timestamp):
        values = [measurement.value for measurement in list(follower) if
                  from_timestamp <= measurement.timestamp <= to_timestamp]
        if len(values):
            return round(sum(values)/len(values))

    def measurement_timeslot(from_meas, to_meas, followers):
        return ([
            avg_timeslot(field, from_meas.timestamp, to_meas.timestamp)
            for field in itertools.takewhile(lambda x: bool(x), followers)
        ]),

    leader_overlap = pairwise(leader)
    entries = ((from_meas.value, to_meas.value) +
               measurement_timeslot(from_meas, to_meas, followers) +
               (from_meas.timestamp, to_meas.timestamp)
               for from_meas, to_meas in leader_overlap)
    return itertools.filterfalse(lambda x: not all(x), entries)


@require_GET
def response_virtual_energy_port_measurements(request, virtual_port_id):
    """
    Returns a response of virtual energy mesurement request for a
    virtual_port_id
    """
    from_timestamp, to_timestamp = get_urlquery_timespan(request,
                                                         required=False)

    followers, leader = get_virtual_energy_measurements(virtual_port_id,
                                                        from_timestamp,
                                                        to_timestamp)
    entries = calc_timeslots(followers, leader)
    result = itertools.starmap(virtual_energy_measurements_to_objs, entries)
    serializer = VirtualEnergyMeasurementSerializer(result, many=True)
    return Response(serializer.data)
