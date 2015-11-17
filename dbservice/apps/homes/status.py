import datetime

import itertools
from collections import namedtuple, OrderedDict


from rest_framework.response import Response
from rest_framework.exceptions import ParseError

from django.views.decorators.http import require_GET

from .serializers import StatusSerializer
from .utils import (pairwise, get_urlquery_timespan,
                    meter_port_objs, extract_query, source_options)
from .models import Measurement, MeterPort

time_tolerance = OrderedDict([
    ('30min', datetime.timedelta(minutes=30)),
    ('1h', datetime.timedelta(hours=1)),
    ('12h', datetime.timedelta(hours=12)),
    ('1d', datetime.timedelta(days=1)),
    ('1w', datetime.timedelta(days=7)),
    ('1m', datetime.timedelta(days=30)),
])

StatusReport = namedtuple(
    'StatusReport', ['meter_type',
                     'meter_name',
                     'time_discrepancy_occurence',
                     'time_discrepancy_sec',
                     'resource_type',
                     'meterport_name'])


def tolerance_parser(tolerance):
    """
    Tolerance query parser
    """

    tolerance = time_tolerance.get(tolerance, None)

    if tolerance is None:
        msg = "".join([str(x) + ", " for x in time_tolerance.keys()])
        msg = msg[0:-2]
        raise ParseError('You must provide a tolerance value: {}'
                         .format(msg))
    return tolerance


def detect_time_discrepancy(dtseries, tolerance):
    """
    Check datetime series for time discrepancy between timestamps according to
    timedelta tolerance. If the time between two observations are above the
    tolerance level, it is included in the return value
    """
    # If dtseries is empty
    if not dtseries:
        return None

    # Find the timedelta between datetimes entries
    fromto_dt = pairwise(dtseries)
    td_dtseries = map(lambda fdt, tdt: tdt-fdt, fromto_dt)

    # Find time_discrepancy based on tolerance and index and violation
    time_discrepancy = ((idx, td) for idx, td in enumerate(td_dtseries)
                        if td > tolerance)

    return time_discrepancy


@require_GET
# pylint: disable-msg=R0914
def get_status(request, pk):
    """
    Get the status of reporting
    """
    # Get query and validate it
    from_timestamp, to_timestamp = get_urlquery_timespan(request)
    tolerance = extract_query(request, 'tolerance', tolerance_parser)

    status_report = []

    # First search in the mainmeter and then the submeters
    for meter_type in ['mainmeters', 'submeters']:

        # Get the meterport objects based on the residential_home_id
        mp_objs = meter_port_objs(pk, meter_type)

        # Get the measurments within the timespan
        mmeter = Measurement.objects.filter(
            meter_port_id__in=mp_objs[meter_type],
            timestamp__gt=from_timestamp,
            timestamp__lt=to_timestamp).order_by('timestamp')

        # Get only the timestamps from the measurements
        mmeter_time = mmeter.values_list('timestamp', flat=True)

        # Look for time discrepancy and return (index, size of timegap)
        mmeter_timedis = detect_time_discrepancy(mmeter_time, tolerance)

        if not mmeter_timedis:
            break

        # Get the possible time discrepancy
        result_timedis = zip(*list(mmeter_timedis))

        # If there are no entries, then we go out of loop
        if result_timedis:

            # Deconvolute the sequence
            mmeter_idx, time_discrepancy_sec = result_timedis

            # Get the ids and the time_discrepancy timestamp
            mp_timedis_ids, time_discrepancy_occur = zip(
                *[(mmeter[idx].meter_port_id, mmeter[idx].timestamp)
                  for idx in mmeter_idx])

            # For each meter port id, get the meter port object
            for mp_timedis_id in mp_timedis_ids:
                mport_timedis_obj = MeterPort.objects.get(id=mp_timedis_id)

                # Determine the meter name
                meter_name = None
                if meter_type is 'mainmeters':
                    meter_name = source_options[meter_type].objects.get(
                        id=mport_timedis_obj.mainmeter_id).name
                elif meter_type is 'submeters':
                    meter_name = source_options[meter_type].objects.get(
                        id=mport_timedis_obj.submeter_id).name

                # Generate an entry in the status_report object
                status_report.append(
                    (meter_type,
                     meter_name,
                     time_discrepancy_occur,
                     time_discrepancy_sec,
                     mport_timedis_obj.resource_type,
                     mport_timedis_obj.name))

    # Map the statusreport to the StatusReport class
    result = itertools.starmap(StatusReport, status_report)

    # Send the result through the serializer
    serializer = StatusSerializer(result, many=True)
    return Response(serializer.data)
