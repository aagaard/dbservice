import datetime
import itertools
import random

from django.core.urlresolvers import reverse
from django.test import TestCase

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework.test import APIClient

from dbservice.apps.users.models import User
from dbservice.apps.utils import APPLIANCES_CHOICES
from dbservice.apps.utils import COUNTRY_CHOICES
from dbservice.apps.utils import LOCATION_CHOICES
from dbservice.apps.utils import RESOURCE_TYPE_CHOICES
from dbservice.apps.utils import MEASUREMENT_UNIT_CHOICES

from . import models
from . import views
from . import aggregated


class AccessControlFilteringTestCase(TestCase):

    """TestCase for access control.

    superusers has access to everything
    (normal) users only have access to themselves and their own data
    """

    def setUp(self):
        """Setup of TestCase."""
        self.superuser = User.objects.create_superuser(
            'super@test.com', 'qwe')
        self.user1 = User.objects.create_user(
            'normal1@test.com', 'qwe')

        self.user2 = models.User.objects.create_user(
            'normal2@test.com', 'qwe')

        self.user1_home = models.ResidentialHome.objects.create(
            dno_customer_id=self.user1,
            country=COUNTRY_CHOICES[0][0]
        )
        self.user2_home = models.ResidentialHome.objects.create(
            dno_customer_id=self.user2,
            country=COUNTRY_CHOICES[0][0]
        )

        self.user1_appliance = models.Appliance.objects.create(
            residential_home=self.user1_home,
            name=APPLIANCES_CHOICES[0][0],
            location=LOCATION_CHOICES[0][0]
        )
        self.user2_appliance = models.Appliance.objects.create(
            residential_home=self.user2_home,
            name=APPLIANCES_CHOICES[0][0],
            location=LOCATION_CHOICES[0][0]
        )

        now = datetime.datetime.now()
        soon = now + datetime.timedelta(minutes=1)
        self.user1_consumption = models.EnergyConsumptionPeriod.objects.create(
            appliance=self.user1_appliance,
            from_timestamp=now,
            to_timestamp=soon
        )
        self.user2_consumption = models.EnergyConsumptionPeriod.objects.create(
            appliance=self.user2_appliance,
            from_timestamp=now,
            to_timestamp=soon
        )

        self.user1_production = models.EnergyProductionPeriod.objects.create(
            appliance=self.user1_appliance,
            from_timestamp=now,
            to_timestamp=soon
        )
        self.user2_production = models.EnergyProductionPeriod.objects.create(
            appliance=self.user2_appliance,
            from_timestamp=now,
            to_timestamp=soon
        )

        self.user1_mainmeter = models.MainMeter.objects.create(
            residential_home=self.user1_home,
            name="user1 main meter"
        )
        self.user2_mainmeter = models.MainMeter.objects.create(
            residential_home=self.user2_home,
            name="user1 main meter"
        )

        self.user1_submeter = models.SubMeter.objects.create(
            residential_home=self.user1_home,
            name="user1 sub meter"
        )
        self.user2_submeter = models.SubMeter.objects.create(
            residential_home=self.user2_home,
            name="user1 sub meter"
        )

        self.user1_meterport = models.MeterPort.objects.create(
            mainmeter=self.user1_mainmeter,
            name='user1 meter port',
            resource_type=RESOURCE_TYPE_CHOICES[0][0],
            unit=MEASUREMENT_UNIT_CHOICES[0][0]
        )
        self.user2_meterport = models.MeterPort.objects.create(
            mainmeter=self.user2_mainmeter,
            name='user2 meter port',
            resource_type=RESOURCE_TYPE_CHOICES[0][0],
            unit=MEASUREMENT_UNIT_CHOICES[0][0]
        )

        self.user1_virtualport = models.VirtualEnergyPort.objects.create(
            submeter=self.user1_submeter,
            name='user1 virtual port',
            resource_type=RESOURCE_TYPE_CHOICES[0][0],
            unit=MEASUREMENT_UNIT_CHOICES[0][0]
        )
        self.user2_virtualport = models.VirtualEnergyPort.objects.create(
            submeter=self.user2_submeter,
            name='user2 meter port',
            resource_type=RESOURCE_TYPE_CHOICES[0][0],
            unit=MEASUREMENT_UNIT_CHOICES[0][0]
        )

        self.user1_measurement = models.Measurement.objects.create(
            meter_port=self.user1_virtualport,
            timestamp=now,
            value=42
        )
        self.user2_measurement = models.Measurement.objects.create(
            meter_port=self.user2_virtualport,
            timestamp=now,
            value=24
        )

        self.residential_home_list_view = \
            views.ResidentialHomeViewSet.as_view({'get': 'list'})
        self.appliance_list_view = \
            views.ApplianceViewSet.as_view({'get': 'list'})
        self.energy_consumption_period_list_view = \
            views.EnergyConsumptionPeriodViewSet.as_view({'get': 'list'})
        self.energy_production_period_list_view = \
            views.EnergyProductionPeriodViewSet.as_view({'get': 'list'})
        self.main_meter_list_view = \
            views.MainMeterViewSet.as_view({'get': 'list'})
        self.sub_meter_list_view = \
            views.SubMeterViewSet.as_view({'get': 'list'})
        self.meter_port_list_view = \
            views.MeterPortViewSet.as_view({'get': 'list'})
        self.virtual_energy_port_list_view = \
            views.VirtualEnergyPortViewSet.as_view({'get': 'list'})
        self.measurement_list_view = \
            views.MeasurementViewSet.as_view({'get': 'list'})

        factory = APIRequestFactory()
        self.requests = {
            name: factory.get('/v1/homes/' + name)
            for name in [
                    'residential_homes',
                    'appliances',
                    'energy_consumption_period',
                    'energy_production_period',
                    'main_meters',
                    'sub_meters',
                    'meter_ports',
                    'virtual_energy_ports',
                    'measurements',
            ]
        }

    def test_residential_home_superuser_filtering(self):
        request = self.requests['residential_homes']
        force_authenticate(request, user=self.superuser)
        response = self.residential_home_list_view(request)
        self.assertEqual(2, response.data['count'])

    def test_residential_home_user_filtering(self):
        request = self.requests['residential_homes']
        force_authenticate(request, user=self.user1)
        response = self.residential_home_list_view(request)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(
            request.build_absolute_uri(reverse(
                'users-v1-user-detail',
                kwargs={'pk': self.user1.id})),
            response.data['results'][0]['dno_customer_id'])

    def test_appliance_superuser_filtering(self):
        request = self.requests['appliances']
        force_authenticate(request, user=self.superuser)
        response = self.appliance_list_view(request)
        self.assertEqual(2, response.data['count'])

    def test_appliance_user_filtering(self):
        request = self.requests['appliances']
        force_authenticate(request, user=self.user1)
        response = self.appliance_list_view(request)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(
            request.build_absolute_uri(reverse(
                'homes-v1-residentialhome-detail',
                kwargs={'pk': self.user1_home.id},
            )),
            response.data['results'][0]['residential_home']
        )

    def test_energy_consumption_period_superuser_filtering(self):
        request = self.requests['energy_consumption_period']
        force_authenticate(request, user=self.superuser)
        response = self.energy_consumption_period_list_view(request)
        self.assertEqual(2, response.data['count'])

    def test_energy_consumption_period_user_filtering(self):
        request = self.requests['energy_consumption_period']
        force_authenticate(request, user=self.user1)
        response = self.energy_consumption_period_list_view(request)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(
            request.build_absolute_uri(reverse(
                'homes-v1-appliance-detail',
                kwargs={'pk': self.user1_appliance.id},
            )),
            response.data['results'][0]['appliance']
        )

    def test_energy_production_period_superuser_filtering(self):
        request = self.requests['energy_production_period']
        force_authenticate(request, user=self.superuser)
        response = self.energy_production_period_list_view(request)
        self.assertEqual(2, response.data['count'])

    def test_energy_production_period_user_filtering(self):
        request = self.requests['energy_production_period']
        force_authenticate(request, user=self.user1)
        response = self.energy_production_period_list_view(request)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(
            request.build_absolute_uri(reverse(
                'homes-v1-appliance-detail',
                kwargs={'pk': self.user1_appliance.id},
            )),
            response.data['results'][0]['appliance']
        )

    def test_main_meter_superuser_filtering(self):
        request = self.requests['main_meters']
        force_authenticate(request, user=self.superuser)
        response = self.main_meter_list_view(request)
        self.assertEqual(2, response.data['count'])

    def test_main_meter_user_filtering(self):
        request = self.requests['main_meters']
        force_authenticate(request, user=self.user1)
        response = self.main_meter_list_view(request)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(
            request.build_absolute_uri(reverse(
                'homes-v1-residentialhome-detail',
                kwargs={'pk': self.user1_home.id})),
            response.data['results'][0]['residential_home']
        )

    def test_sub_meter_superuser_filtering(self):
        request = self.requests['sub_meters']
        force_authenticate(request, user=self.superuser)
        response = self.sub_meter_list_view(request)
        self.assertEqual(2, response.data['count'])

    def test_sub_meter_user_filtering(self):
        request = self.requests['sub_meters']
        force_authenticate(request, user=self.user1)
        response = self.sub_meter_list_view(request)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(
            request.build_absolute_uri(reverse(
                'homes-v1-residentialhome-detail',
                kwargs={'pk': self.user1_home.id})),
            response.data['results'][0]['residential_home']
        )

    def test_meter_port_superuser_filtering(self):
        request = self.requests['meter_ports']
        force_authenticate(request, user=self.superuser)
        response = self.meter_port_list_view(request)
        # Note that we expect 4 here as virtual energy ports also are meter
        # ports.
        self.assertEqual(4, response.data['count'])

    def test_meter_port_user_filtering(self):
        request = self.requests['meter_ports']
        force_authenticate(request, user=self.user1)
        response = self.meter_port_list_view(request)
        # Note that we expect 2 here as virtual energy ports also are meter
        # ports.
        self.assertEqual(2, response.data['count'])
        self.assertEqual(
            'user1 meter port',
            response.data['results'][0]['name']
        )
        self.assertEqual(
            'user1 virtual port',
            response.data['results'][1]['name']
        )

    def test_virtual_energy_port_superuser_filtering(self):
        request = self.requests['virtual_energy_ports']
        force_authenticate(request, user=self.superuser)
        response = self.virtual_energy_port_list_view(request)
        self.assertEqual(2, response.data['count'])

    def test_virtual_energy_port_user_filtering(self):
        request = self.requests['virtual_energy_ports']
        force_authenticate(request, user=self.user1)
        response = self.virtual_energy_port_list_view(request)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(
            'user1 virtual port',
            response.data['results'][0]['name']
        )

    def test_measurement_superuser_filtering(self):
        request = self.requests['measurements']
        force_authenticate(request, user=self.superuser)
        response = self.measurement_list_view(request)
        self.assertEqual(2, response.data['count'])

    def test_measurement_user_filtering(self):
        request = self.requests['measurements']
        force_authenticate(request, user=self.user1)
        response = self.measurement_list_view(request)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(
            42,
            response.data['results'][0]['value']
        )


class FixedValueMeterPortTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'normal@test.com', 'qwe')
        self.port = models.FixedValueMeterPort.objects.create(
            user=self.user,
            value=42,
            resolution_in_seconds=60,
        )
        self.client = APIClient()


def create_consumption_pattern(sample_period,
                               start_datetime,
                               nsamples=100,
                               start=10000,
                               error_increasing_monotonical=False,
                               error_random_delay_sample_period=False,
                               ):
    """
    Generate list of `nsamples` consumption measurements from `start_datetime`
    (datetime) with sample_period (timedelta). Errors can be introduced:

    `error_increasing_monotonical`: introduces a reset of meter counter and
    start below the previous measurement

    `error_random_delay_sample_period`: introduces time randomness in
    sample_period, thus not creating a uneven period.
    """
    def monotonical_true(start, delta, i):
        return round(start + delta * i)

    def monotonical_error(start, delta, i):
        if i > round(nsamples / 2):
            return round(start + delta * (i - round(nsamples / 2)))
        else:
            return round(start + delta * i)

    def date_generator():
        from_date = start_datetime
        while True:
            yield from_date
            from_date = from_date + sample_period
            if error_random_delay_sample_period:
                from_date = from_date + datetime.timedelta(
                    seconds=random.randint(0, 10))

    stop = 100 * start
    delta = (stop - start) / (nsamples - 1)
    monotonical = monotonical_true
    if error_increasing_monotonical:
        monotonical = monotonical_error

    return ((time, monotonical(start, delta, i))
            for time, i in zip(itertools.islice(date_generator(), nsamples),
                               range(nsamples)))


def create_measurement(sample_period, start_datetime, end_datetime, dist_fct):
    """
    Generate a list of `nsamples` measurements from `start_datetime` (datetime)
    with a `sample_period` (timedelta). The distribution of the measurements is
    set by the generator `dist_fct`
    """
    def date_generator():
        from_date = start_datetime
        while True:
            yield from_date
            from_date = from_date + sample_period

    nsamples = (end_datetime - start_datetime).seconds // sample_period.seconds
    return [(time, dist_fct())
            for time, _ in zip(itertools.islice(date_generator(), nsamples),
                               range(nsamples))]


def insert_measurement(obj, pattern):
    for timestamp, value in pattern:
        models.Measurement.objects.create(
            meter_port=obj,
            timestamp=timestamp,
            value=value,
        )


class VirtualEnergyMeasurementsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'normal@test.com', 'qwe'
        )
        self.user_home = models.ResidentialHome.objects.create(
            dno_customer_id=self.user,
            country=COUNTRY_CHOICES[0][0]
        )
        self.user_appliance = models.Appliance.objects.create(
            residential_home=self.user_home,
            name=APPLIANCES_CHOICES[0][0],
            location=LOCATION_CHOICES[0][0]
        )
        self.user_mainmeter = models.MainMeter.objects.create(
            residential_home=self.user_home,
            name="user main meter"
        )
        self.user_submeter = models.SubMeter.objects.create(
            residential_home=self.user_home,
            name="user sub meter"
        )
        self.meter_port_cons = models.MeterPort.objects.create(
            mainmeter=self.user_mainmeter,
            name='user meter port mainmeter consumption',
            resource_type=RESOURCE_TYPE_CHOICES[0][0],
            unit=MEASUREMENT_UNIT_CHOICES[0][0]  # consumption
        )
        self.meter_port_vol = models.MeterPort.objects.create(
            mainmeter=self.user_mainmeter,
            name='user meter port mainmeter voltage',
            resource_type=RESOURCE_TYPE_CHOICES[0][0],
            unit=MEASUREMENT_UNIT_CHOICES[2][0]  # voltage
        )
        self.meter_port_pf = models.MeterPort.objects.create(
            mainmeter=self.user_mainmeter,
            name='user meter port main meter power factor',
            resource_type=RESOURCE_TYPE_CHOICES[0][0],
            unit=MEASUREMENT_UNIT_CHOICES[6][0]  # power factor
        )
        self.meter_port_cur = models.MeterPort.objects.create(
            submeter=self.user_submeter,
            name='user meter port subemeter current',
            resource_type=RESOURCE_TYPE_CHOICES[0][0],
            unit=MEASUREMENT_UNIT_CHOICES[3][0]  # current
        )
        self.virtualenergyport = models.VirtualEnergyPort.objects.create(
            consumption=self.meter_port_cons,
            current=self.meter_port_cur,
            voltage=self.meter_port_vol,
            power_factor=self.meter_port_pf,
        )

        self.start_datetime = datetime.datetime.now() - datetime.timedelta(
            weeks=1)
        self.sample_period = datetime.timedelta(seconds=30)
        self.sample_period_cur = datetime.timedelta(seconds=5)
        self.sample_period_vol = datetime.timedelta(seconds=8)
        self.sample_period_pf = datetime.timedelta(seconds=11)
        self.n_samples = 100
        self.end_datetime = self.start_datetime + self.n_samples\
            * self.sample_period

        self.consumption_pattern = create_consumption_pattern(
            self.sample_period,
            self.start_datetime,
            nsamples=self.n_samples,
            error_random_delay_sample_period=False,
            error_increasing_monotonical=False,
        )
        insert_measurement(self.meter_port_cons, self.consumption_pattern)

        self.powerfactor_pattern = create_measurement(
            self.sample_period_pf, self.start_datetime, self.end_datetime,
            lambda: int(round(1000*random.betavariate(20, 0.5)))
        )
        insert_measurement(self.meter_port_pf, self.powerfactor_pattern)

        self.current_pattern = create_measurement(
            self.sample_period_cur, self.start_datetime, self.end_datetime,
            lambda: int(round(random.gauss(100, 10)))
        )
        insert_measurement(self.meter_port_cur, self.current_pattern)

        self.voltage_pattern = create_measurement(
            self.sample_period_vol, self.start_datetime, self.end_datetime,
            lambda: int(round(random.gauss(230000, 10000)))
        )
        insert_measurement(self.meter_port_vol, self.voltage_pattern)

        self.url = (
            '/api/v1/homes/virtual_energy_ports/%s/get_measurements/'
        ) % (self.virtualenergyport.id,)
        self.client = APIClient()

    def test_get_virtual_measurements(self):
        datetime_now_str = self.start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")
        datetime_end_str = self.end_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {
            'from_timestamp': '{}'.format(datetime_now_str),
            'to_timestamp': '{}'.format(datetime_end_str),
        })
        self.assertEqual(self.n_samples-2, len(response.data))

    def test_virtual_energy_measurements_intervals(self):
        def minmax(pattern):
            trace = list(zip(*pattern))[1]
            return min(trace), max(trace)

        datetime_now_str = self.start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")
        datetime_end_str = self.end_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")
        pf_minmax = minmax(self.powerfactor_pattern)
        vol_minmax = minmax(self.voltage_pattern)
        cur_minmax = minmax(self.current_pattern)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {
            'from_timestamp': '{}'.format(datetime_now_str),
            'to_timestamp': '{}'.format(datetime_end_str),
        })

        for m in response.data:
            self.assertEqual(m['to_timestamp'] - m['from_timestamp'],
                             self.sample_period)
            self.assertGreaterEqual(pf_minmax[1], m['power_factor'])
            self.assertLessEqual(pf_minmax[0], m['power_factor'])
            self.assertGreaterEqual(vol_minmax[1], m['voltage'])
            self.assertLessEqual(vol_minmax[0], m['voltage'])
            self.assertGreaterEqual(cur_minmax[1], m['current'])
            self.assertLessEqual(cur_minmax[0], m['current'])


class TemperatureMeasurementsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'normal1@test.com', 'qwe')
        self.user_home = models.ResidentialHome.objects.create(
            dno_customer_id=self.user,
            country=COUNTRY_CHOICES[0][0]
        )
        self.user_submeter1 = models.SubMeter.objects.create(
            residential_home=self.user_home,
            name="user submeter1"
        )
        self.user_submeter2 = models.SubMeter.objects.create(
            residential_home=self.user_home,
            name="user submeter2"
        )
        self.meter_port1 = models.MeterPort.objects.create(
            submeter=self.user_submeter1,
            name='user meterport temperature sensor',
            resource_type=RESOURCE_TYPE_CHOICES[1][0],
            unit=MEASUREMENT_UNIT_CHOICES[5][0]
        )
        self.meter_port2 = models.MeterPort.objects.create(
            submeter=self.user_submeter2,
            name='user meterport temperature sensor',
            resource_type=RESOURCE_TYPE_CHOICES[1][0],
            unit=MEASUREMENT_UNIT_CHOICES[5][0]
        )
        self.url = (
            '/api/v1/homes/residential_homes/%s/get_temperature/'
        ) % (self.user_home.id,)
        self.client = APIClient()

    def test_temperature(self):
        self.client.force_authenticate(user=self.user)
        datetime1 = datetime.datetime.now()
        datetime2 = datetime.datetime.now() + datetime.timedelta(seconds=10)
        measurements1 = [
            (datetime1, "12000"),  # 12℃
            (datetime2, "10000"),  # 10℃
        ]
        measurements2 = [
            (datetime1, "8000"),  # 8℃
            (datetime2, "1000"),  # 1℃
        ]
        insert_measurement(self.meter_port2, measurements2)
        insert_measurement(self.meter_port1, measurements1)
        datetime1_str = datetime1.strftime("%Y-%m-%dT%H:%M:%S.%f")
        datetime2_str = datetime2.strftime("%Y-%m-%dT%H:%M:%S.%f")
        response = self.client.get(self.url, {
            'from_timestamp': '{}'.format(datetime1_str),
            'to_timestamp': '{}'.format(datetime2_str),
        })
        self.assertEqual(4, len(response.data))
        response = self.client.get(self.url)
        self.assertEqual(4, len(response.data))


class AggregationTestCase(TestCase):

    """
    TestCase of aggregation functionality for consumption and production.

    The test case tests the following: - The condense function used in
    get_consumption and production - The API interface for correct data
    retrieval from get_consumption with and without tau
    """

    def setUp(self):
        """Setup of testcase."""
        self.user = User.objects.create_user(
            'normal1@test.com', 'qwe')
        self.user_home = models.ResidentialHome.objects.create(
            dno_customer_id=self.user,
            country=COUNTRY_CHOICES[0][0]
        )
        self.user_appliance = models.Appliance.objects.create(
            residential_home=self.user_home,
            name=APPLIANCES_CHOICES[0][0],
            location=LOCATION_CHOICES[0][0]
        )
        self.user_energy_prod_p = models.EnergyProductionPeriod.objects.create(
            appliance=self.user_appliance,
            from_timestamp=datetime.datetime.now(),
            to_timestamp=None,
        )
        self.user_submeter = models.SubMeter.objects.create(
            residential_home=self.user_home,
            name="user sub meter"
        )
        self.user_mainmeter = models.MainMeter.objects.create(
            residential_home=self.user_home,
            name="user main meter"
        )
        self.meter_port_main = models.MeterPort.objects.create(
            mainmeter=self.user_mainmeter,
            name='user meter port mainmeter consumption',
            resource_type=RESOURCE_TYPE_CHOICES[0][0],
            unit=MEASUREMENT_UNIT_CHOICES[0][0]
        )
        self.meter_port_sub = models.MeterPort.objects.create(
            submeter=self.user_submeter,
            energy_production_period=self.user_energy_prod_p,
            unit=MEASUREMENT_UNIT_CHOICES[0][0],
            name='user meter port submeter production'
        )
        self.url_get_consumption = ('/api/v1/homes/residential_homes/'
                                    '{}/get_energy_consumption/').format(
                                        self.user_home.id)
        self.url_get_production = ('/api/v1/homes/residential_homes/'
                                   '{}/get_energy_production/').format(
                                       self.user_home.id)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_condense_function(self):
        """Test condense for # of elements, endvalue correctness, timedelta."""
        from collections import namedtuple
        Measurement = namedtuple('Measurement', ['timestamp', 'value'])

        mid_minutes, end_minutes = 5, 10
        datetime1 = datetime.datetime.now()
        datetime2 = datetime1 + datetime.timedelta(minutes=mid_minutes)
        datetime3 = datetime1 + datetime.timedelta(minutes=end_minutes)
        startvalue, midvalue, endvalue = 100, 200, 500
        increment_minutes = 2
        increment = datetime.timedelta(minutes=2)

        entry1 = Measurement(timestamp=datetime1, value=startvalue)
        entry2 = Measurement(timestamp=datetime2, value=midvalue)
        entry3 = Measurement(timestamp=datetime3, value=endvalue)

        data = list(
            aggregated.condense(
                [entry1, entry2, entry3],
                datetime1,
                increment
            )
        )

        # Number elements are correct?
        self.assertEqual(end_minutes / increment_minutes, len(data))

        # Endvalue of accumulated consumption is correct?
        cond_endvalue = startvalue + sum([item.value for item in data])
        self.assertEqual(cond_endvalue, endvalue)

        # Timedelta between condensed values are correct?
        time1, time2 = itertools.tee([item.from_timestamp for item in data])
        next(time2, None)
        timediff = [t2 - t1 for t1, t2 in zip(time1, time2)]
        for td in timediff:
            self.assertEqual(td, increment)

    def test_get_consumption_without_tau(self):
        """Test `get_consumption` without tau returns one correct element."""
        value_start = 500
        value_end = 800
        time_duration = datetime.timedelta(minutes=3)

        datetime_start = datetime.datetime.now()
        datetime_end = datetime_start + time_duration
        data = [
            (datetime_start, value_start),
            (datetime_end, value_end),
        ]

        insert_measurement(self.meter_port_main, data)
        datetime_start_str = datetime_start.strftime("%Y-%m-%dT%H:%M:%S.%f")
        datetime_end_str = datetime_end.strftime("%Y-%m-%dT%H:%M:%S.%f")
        response = self.client.get(self.url_get_consumption, {
            'from_timestamp': datetime_start_str,
            'to_timestamp': datetime_end_str,
        })
        self.assertEqual(1, len(response.data))
        self.assertEqual(value_end - value_start, response.data[0]['value'])

    def test_get_consumption_with_tau(self):
        """Test `get_consumption` with tau returns right number of elements."""
        value_start = 20
        value_end = 1000
        time_duration = datetime.timedelta(minutes=30)
        tau = '30min'

        datetime_start = datetime.datetime.now()
        datetime_end = datetime_start + time_duration
        data = [
            (datetime_start, value_start),
            (datetime_end, value_end),
        ]
        insert_measurement(self.meter_port_main, data)

        tau_timedelta = aggregated.condensed_options[tau]
        datetime_start_str = datetime_start.strftime("%Y-%m-%dT%H:%M:%S.%f")
        datetime_end_str = datetime_end.strftime("%Y-%m-%dT%H:%M:%S.%f")
        response = self.client.get(self.url_get_consumption, {
            'from_timestamp': datetime_start_str,
            'to_timestamp': datetime_end_str,
            'tau': tau,
        })
        self.assertEqual(int(time_duration / tau_timedelta),
                         len(response.data))

    def test_get_production_without_tau(self):
        """Test get_production without tau that returns one element."""
        value_start = 500
        value_end = 800
        time_duration = datetime.timedelta(minutes=30)

        datetime_start = datetime.datetime.now()
        datetime_end = datetime_start + time_duration
        data = [
            (datetime_start, value_start),
            (datetime_end, value_end),
        ]
        insert_measurement(self.meter_port_sub, data)
        datetime_start_str = datetime_start.strftime("%Y-%m-%dT%H:%M:%S.%f")
        datetime_end_str = datetime_end.strftime("%Y-%m-%dT%H:%M:%S.%f")
        response = self.client.get(self.url_get_production, {
            'from_timestamp': datetime_start_str,
            'to_timestamp': datetime_end_str,
        })
        self.assertEqual(1, len(response.data))
        self.assertEqual(value_end - value_start, response.data[0]['value'])

    def test_get_production_with_tau(self):
        """Test get_production with τ that returns the right # of elements."""
        self.user_energy_prod_p2 = (
            models.EnergyProductionPeriod.objects.create(
                appliance=self.user_appliance,
                from_timestamp=datetime.datetime.now(),
                to_timestamp=None,
            )
        )
        self.user_submeter2 = models.SubMeter.objects.create(
            residential_home=self.user_home,
            name="user sub meter2"
        )
        self.meter_port_sub2 = models.MeterPort.objects.create(
            submeter=self.user_submeter2,
            energy_production_period=self.user_energy_prod_p2,
            unit=MEASUREMENT_UNIT_CHOICES[0][0],
            name='user meter port submeter production2'
        )

        value_start = 20
        value_mid = 300
        value_end = 1000
        time_duration = datetime.timedelta(minutes=30)
        tau = '1min'

        datetime_start = datetime.datetime.now()
        datetime_mid = datetime_start + datetime.timedelta(minutes=15)
        datetime_end = datetime_start + time_duration
        data = [
            (datetime_start, value_start),
            (datetime_mid, value_mid),
            (datetime_end, value_end),
        ]
        insert_measurement(self.meter_port_sub, data)
        insert_measurement(self.meter_port_sub2, data)

        tau_timedelta = aggregated.condensed_options[tau]
        datetime_start_str = datetime_start.strftime("%Y-%m-%dT%H:%M:%S.%f")
        datetime_end_str = datetime_end.strftime("%Y-%m-%dT%H:%M:%S.%f")
        response = self.client.get(self.url_get_production, {
            'from_timestamp': datetime_start_str,
            'to_timestamp': datetime_end_str,
            'tau': tau,
        })
        self.assertEqual(int(time_duration / tau_timedelta),
                         len(response.data))
