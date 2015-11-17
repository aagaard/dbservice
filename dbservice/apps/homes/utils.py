import datetime
import itertools

from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from django import forms
from django.views.decorators.http import require_GET
from django.conf import settings
from django.shortcuts import get_object_or_404

from . import models
from .serializers import MeasurementSerializer

source_options = {
    'mainmeters': models.MainMeter,
    'appliances': models.Appliance,
    'submeters': models.SubMeter
}


class PeriodForm(forms.Form):
    from_timestamp = forms.DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS)
    to_timestamp = forms.DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS)


# pairwise from http://docs.python.org/2/library/itertools.html#recipes
def pairwise(iterable, tee=itertools.tee, izip=zip):
    """
    s -> (s0,s1), (s1,s2), (s2, s3), ...
    """
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


# tabulate from http://docs.python.org/2/library/itertools.html#recipes
def tabulate(function, start=0, imap=map, count=itertools.count):
    """
    Return function(0), function(1), ...
    """
    return imap(function, count(start))


def get_urlquery_timespan(request, required=True):
    """
    Parses a period object returned from the PeriodForm and return
    from_timestamp and to_timestamp. If not required test if from_timestamp or
    to_timestamp are present, if they are throw an error otherwise parse
    silently
    """
    period = PeriodForm(request.GET)
    if period.is_valid():
        from_timestamp = period.cleaned_data['from_timestamp']
        to_timestamp = period.cleaned_data['to_timestamp']
        return (from_timestamp, to_timestamp)
    else:
        if required:
            raise ParseError(period.errors)
        else:
            if 'from_timestamp' in period.cleaned_data \
               or 'to_timestamp' in period.cleaned_data:
                raise ParseError(period.errors)
            else:
                return (None, None)


def get_urlquery_value(request, query_field,
                       parser_options=None, default_return=None):
    """
    Get query value based on request and field
    """
    chosen_opt = request.GET.get(query_field, default_return)

    if parser_options and chosen_opt:
        converted_opt = parser_options.get(chosen_opt, default_return)
        if converted_opt is None:
            opt = "".join([str(x) + ", " for x in parser_options.keys()])
            opt = opt[0:-2]
            raise ParseError(
                'You must provide following values for {0}: {1}'.format(
                    query_field, opt)
            )
        return converted_opt
    return chosen_opt


def qobjects(cls_target, oid, foreign_name):
    """
    Get queryset objects based on `cls_target` given the object/id `oid` and
    the `foreign_name` is equal.
    """
    if isinstance(oid, int):
        fetcher = 'id'
    else:
        fetcher = 'in'

    kwargs = {'{0}__{1}'.format(foreign_name, fetcher): oid}
    return cls_target.objects.filter(**kwargs)


def meter_port_objs(home_id, sources=None):
    """
    Return a dict of meter port objects based specified `sources` and `home_id`
    """
    mp_objs = dict()

    if not isinstance(sources, list):
        sources = [sources]

    for source in sources:
        if source is 'appliances':
            appl = dict()
            appls = qobjects(models.Appliance, home_id, 'residential_home')

            epps = qobjects(models.EnergyProductionPeriod, appls, 'appliance')
            pmps = qobjects(models.MeterPort, epps, 'energy_production_period')

            appl.update([('energy_production_period', pmps)])

            ecps = qobjects(models.EnergyConsumptionPeriod, appls, 'appliance')
            cmps = qobjects(models.MeterPort, ecps, 'energy_production_period')

            appl.update([('energy_consumption_period', cmps)])
            mp_objs.update([('appliances', appl)])

        elif source is 'mainmeters':
            mmeter = qobjects(models.MainMeter, home_id, 'residential_home')
            mmps = qobjects(models.MeterPort, mmeter, 'mainmeter')
            mp_objs.update([('mainmeters', mmps)])

        elif source is 'submeters':

            smeter = qobjects(models.SubMeter, home_id, 'residential_home')
            mmps = qobjects(models.MeterPort, smeter, 'submeter')
            mp_objs.update([('submeters', mmps)])

    if len(sources) == 1:
        return mp_objs[sources[0]]

    return mp_objs


def extract_query(request, field, fparse):
    """
    Extract parameters based on the field string from the request and parse
    them with the fparse function and returns the value. If return value is
    None it was not included in the request
    """
    if type(field) is not set:
        if type(field) is not list:
            field = [field]
        field = set(field)

    if set(request.GET.viewkeys()).issuperset(field):
        fld = None
        if len(field) == 1:
            fld = request.GET[field.pop()]
        elif len(field) == 2:   # HACK TODO
            fld = PeriodForm(request.GET)
        return fparse(fld)
    else:
        fparse(None)


def get_meter_ports_id(virtual_port_pk):
    """
    Return all the set of meter_ports associated to a virtual port
    """
    res = models.VirtualEnergyPort.objects.filter(id=virtual_port_pk)
    if len(res) == 1:
        return {
            'consumption': res[0].consumption.id,
            'current': res[0].current.id,
            'voltage': res[0].voltage.id,
            'power_factor': res[0].power_factor.id,
        }
    else:
        return None


def get_measurements(request, meter_port_ids):
    """
    Return measurements based on pk within a timespan
    """
    from_timestamp, to_timestamp = get_urlquery_timespan(request)
    kwargs = {
        'meter_port_id__in': meter_port_ids,
        'timestamp__gt': from_timestamp,
        'timestamp__lt': to_timestamp,
    }
    return models.Measurement.objects.filter(**kwargs).order_by('timestamp')


@require_GET
def response_measurements(request, meter_port_pk=None, virtual_port_pk=None):
    """
    Response measurements based on a virtual_port or meter_port and timespan
    """
    assert bool(meter_port_pk) ^ bool(virtual_port_pk)
    result = []
    if virtual_port_pk:
        meter_port_ids = get_meter_ports_id(virtual_port_pk)
        if meter_port_ids:
            result = get_measurements(request, meter_port_ids.values())
    elif meter_port_pk:
        result = get_measurements(request, meter_port_pk)

    serializer = MeasurementSerializer(result, many=True)
    return Response(serializer.data)


def response_fixed_value_measurements(request, pk):
    port = get_object_or_404(models.FixedValueMeterPort, pk=pk)
    from_timestamp, to_timestamp = get_urlquery_timespan(request)
    delta_seconds = (to_timestamp - from_timestamp).total_seconds()
    measurements_needed = int(delta_seconds / port.resolution_in_seconds)
    from_clock_hour = from_timestamp.replace(
        minute=0, second=0, microsecond=0)
    return Response([
        {
            'timestamp': from_clock_hour + datetime.timedelta(
                seconds=(count * port.resolution_in_seconds),
            ),
            'value': port.value,
        }
        for count in range(measurements_needed)
    ])
