# -*- coding: utf-8 -*-

"""
Constants for models
"""
# pylint: disable=C0111


COUNTRY_CHOICES = (
    ('denmark', 'Denmark'),
    ('belarus', 'Republic of Belarus')
)

RESOURCE_TYPE_CHOICES = (
    ('electricity', 'electricity'),
    ('temperature', 'temperature'),
)

APPLIANCES_CHOICES = (
    ('air_conditioner', 'Air conditioner'),
    ('dishwasher', 'Dishwasher'),
    ('electrical_vehicle', 'Electrical Vehicle'),
    ('freezer', 'Freezer'),
    ('heat_pump', 'Heat pump'),
    ('hifi', 'Hi-Fi'),
    ('kettle', 'Kettle'),
    ('microwave', 'Microwave'),
    ('other', 'Other'),
    ('oven', 'Oven'),
    ('photo_voltaic', 'Photo Voltaic'),
    ('tumble_dryer', 'Tumble dryer'),
    ('tv', 'TV'),
    ('washing_machine', 'Washing machine'),
    ('refrigerator', 'Refrigerator'),
    ('stove', 'Stove'),
    ('stove_oven', 'Stove & Oven'),
    ('ventilation', 'Ventilation'),
    ('service_line', 'Service Line'),
    ('genvex', 'Genvex'),
    ('lighting', 'Lighting')
)

INDEX_UNIT_CHOICES = (
    ('dkk/gigawatthour', u'DKK/gWh'),
    ('gram_co2/kilowatthour', u'gCO₂/kWh'),
    ('millidegreedays/day', u'millidegreedays/day'),
)

MEASUREMENT_UNIT_CHOICES = (
    # compatible with unit conversion library:
    ('milliwatt*hour', 'mWh'),    # energy
    ('milliwatt', 'mW'),          # power
    ('millivolt', 'mV'),          # voltage
    ('milliampere', 'mA'),        # current
    ('millihertz', 'mHz'),        # frequency
    # not compatible with unit conversion library:
    ('millidegrees_celsius', u'm°C'),       # temperature
    ('parts_per_thousand', u'‰'),           # power factor
    ('millivolt_ampere', 'mVA'),            # apparent, complex (volt-amps)
    ('millivolt_ampere_reactive', 'mVAR'),  # reactive (volt-amps reactive)
)

LOCATION_CHOICES = (
    ('living_room', 'Living room'),
    ('bathroom', 'Bathroom'),
    ('kitchen', 'Kitchen'),
    ('hallway', 'Hallway'),
    ('bedroom', 'Bedroom'),
    ('control_room', 'Control room'),
    ('outside', 'Outside'),
    ('unknown', 'Unknown'),
    ('other_location', 'Other location'),
)

PHASE_CHOICES = (
    ('unknown', 'Unknown'),
    ('L1', 'L1'),
    ('L2', 'L2'),
    ('L3', 'L3'),
    ('L1L2L3', 'L1L2L3'),
)
