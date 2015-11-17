import datetime
import itertools
from collections import namedtuple
from fractions import Fraction

from .models import Measurement, MeterPort
from .serializers import PaginatedCondensedSerializer
from .utils import get_urlquery_timespan, pairwise, tabulate
from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_GET
from rest_framework.exceptions import ParseError
from rest_framework.generics import Paginator
from rest_framework.response import Response

from dbservice.apps.utils import MEASUREMENT_UNIT_CHOICES


class CondensedPeriodForm(forms.Form):
    from_timestamp = forms.DateTimeField()
    to_timestamp = forms.DateTimeField()


def _interpolate_sample(target, sample_before, sample_after):
    # interpolate data at target timestamp, given data at time before and
    # after...
    assert isinstance(target, datetime.datetime)
    assert sample_before.timestamp < sample_after.timestamp
    assert sample_before.timestamp <= target <= sample_after.timestamp
    if sample_before.timestamp == target:
        return (target, sample_before.value)
    elif sample_after.timestamp == target:
        return (target, sample_after.value)
    else:
        timespan_total = (sample_after.timestamp -
                          sample_before.timestamp).total_seconds()
        timespan_before = (target -
                           sample_before.timestamp).total_seconds()
        delta_value = sample_after.value - sample_before.value
        rate = delta_value / Fraction(timespan_total)
        val = sample_before.value + rate * Fraction(timespan_before)
        return (target, int(val))


def _resolution_aligned_data(raw_data, next_timestamp, sample_resolution):
    def timestamp_n(n):
        return next_timestamp + (n * sample_resolution)

    timestamps = tabulate(timestamp_n)
    timestamp = next(timestamps)
    # iterate over raw samples in pairs...
    for sample_a, sample_b in pairwise(raw_data):
        while sample_a.timestamp > timestamp:
            timestamp = next(timestamps)
        # implicitly skip ahead in sample list until we reach something on both
        # sides of the target timestamp --- or we run out...
        while sample_a.timestamp <= timestamp <= sample_b.timestamp:
            # yield interpolated samples until we are past the interval between
            # the current pair of samples
            yield _interpolate_sample(timestamp, sample_a, sample_b)
            timestamp = next(timestamps)


CondensedValue = namedtuple(
    'CondensedValue', ['from_timestamp', 'to_timestamp', 'value'])


def condense_pair(from_to_pairs):
    from_pair, to_pair = from_to_pairs
    from_timestamp, from_value = from_pair
    to_timestamp, to_value = to_pair
    return CondensedValue(from_timestamp, to_timestamp, to_value - from_value)


def condense(raw_data, from_timestamp, increment):
    """
    The queryset `raw_data` is interpolated from `from_timestamp` to
    `to_timestamp` with the sample period `increment`
    """
    aligned = _resolution_aligned_data(raw_data, from_timestamp, increment)
    result = map(condense_pair, pairwise(aligned))
    return result


@require_GET
def condensed(request, pk, increment):
    # Validate the time span
    from_timestamp, to_timestamp = get_urlquery_timespan(request)

    if from_timestamp == to_timestamp:
        raise ParseError('Error: Cannot interpolate over equal timestamps')
    # extend from/to range but query on lt/gt rather than lte/gte --- when
    # available data doesn't exactly hit the from/to timestamps, we include
    # some extra to allow interpolation to hit from/to timestamps --- but not
    # quite enaugh to include an extra increment-size period in the output...
    raw_data = Measurement.objects.filter(
        meter_port_id=pk,
        timestamp__gt=(from_timestamp - increment),
        timestamp__lt=(to_timestamp + increment)).order_by(
            'timestamp')

    if not raw_data:
        if not Measurement.objects.filter(meter_port_id=pk).exists():
            raise ParseError('The meter port does not exists')
        else:
            raise ParseError('No measurements within the time interval')

    meter_port_unit = MeterPort.objects.filter(id=pk)[0].unit
    if meter_port_unit != MEASUREMENT_UNIT_CHOICES[0][0]:
        raise ParseError(
            'Condensed function cannot generate valid output, '
            'when meter port is not measuring energy. '
            'Meter port {} is measuring {}'.format(pk, meter_port_unit)
        )

    result = list(condense(raw_data, from_timestamp, increment))
    if not result:
        dummy_values = [
            Measurement(
                value=0,
                timestamp=(raw_data.earliest().timestamp - 2*increment)
            ),
            Measurement(
                value=0,
                timestamp=(raw_data.earliest().timestamp - increment)
            ),
            Measurement(
                value=0,
                timestamp=(raw_data.latest().timestamp + increment)
            ),
            Measurement(
                value=0,
                timestamp=(raw_data.earliest().timestamp + 2*increment)
            ),
        ]
        raw_data = itertools.chain(raw_data, dummy_values)
        result = list(condense(raw_data, from_timestamp, increment))
        if not result:
            raise ParseError('Condensed function has no valid output '
                             '(only one measurement was available maybe?)')

    paginator = Paginator(result, 20)
    page = request.QUERY_PARAMS.get('page')
    try:
        values = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        values = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999),
        # deliver last page of results.
        values = paginator.page(paginator.num_pages)

    serializer = PaginatedCondensedSerializer(values,
                                              context={'request': request})
    return Response(serializer.data)
