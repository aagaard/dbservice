# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appliance',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(choices=[('air_conditioner', 'Air conditioner'), ('dishwasher', 'Dishwasher'), ('electrical_vehicle', 'Electrical Vehicle'), ('freezer', 'Freezer'), ('heat_pump', 'Heat pump'), ('hifi', 'Hi-Fi'), ('kettle', 'Kettle'), ('microwave', 'Microwave'), ('other', 'Other'), ('oven', 'Oven'), ('photo_voltaic', 'Photo Voltaic'), ('tumble_dryer', 'Tumble dryer'), ('tv', 'TV'), ('washing_machine', 'Washing machine'), ('refrigerator', 'Refrigerator'), ('stove', 'Stove'), ('stove_oven', 'Stove & Oven'), ('ventilation', 'Ventilation'), ('service_line', 'Service Line'), ('genvex', 'Genvex')], max_length=64)),
                ('location', models.CharField(choices=[('living_room', 'Living room'), ('bathroom', 'Bathroom'), ('kitchen', 'Kitchen'), ('hallway', 'Hallway'), ('bedroom', 'Bedroom'), ('control_room', 'Control room'), ('outside', 'Outside'), ('unknown', 'Unknown'), ('other_location', 'Other location')], max_length=32)),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnergyConsumptionPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('from_timestamp', models.DateTimeField()),
                ('to_timestamp', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnergyProductionPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('from_timestamp', models.DateTimeField()),
                ('to_timestamp', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MainMeter',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('value', models.BigIntegerField()),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MeterPort',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('resource_type', models.CharField(choices=[('electricity', 'electricity'), ('gas', 'gas'), ('heat', 'heat'), ('water', 'water'), ('compressed_air', 'compressed air'), ('temperature', 'temperature'), ('relative_humidity', 'relative humidity')], max_length=32)),
                ('unit', models.CharField(choices=[('milliwatt*hour', 'mWh'), ('milliwatt', 'mW'), ('millivolt', 'mV'), ('milliampere', 'mA'), ('millihertz', 'mHz'), ('milliliter', 'mL'), ('milliliter/hour', 'mL/h'), ('millibar', 'mbar'), ('millidegrees_celsius', 'm°C'), ('parts_per_thousand', '‰'), ('millipower_factor', 'pf')], max_length=32)),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResidentialHome',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('country', models.CharField(choices=[('denmark', 'Denmark'), ('belarus', 'Republic of Belarus')], max_length=64)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubMeter',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('residential_home', models.ForeignKey(to='homes.ResidentialHome', related_name='sub_meter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VirtualEnergyPort',
            fields=[
                ('meterport_ptr', models.OneToOneField(to='homes.MeterPort', primary_key=True, auto_created=True, serialize=False, parent_link=True)),
                ('current', models.ForeignKey(to='homes.MeterPort', related_name='meter_ports_current', null=True)),
                ('power_factor', models.ForeignKey(to='homes.MeterPort', related_name='meter_ports_pf', null=True)),
                ('voltage', models.ForeignKey(to='homes.MeterPort', related_name='meter_ports_voltage', null=True)),
            ],
            options={
                'ordering': ['id'],
            },
            bases=('homes.meterport',),
        ),
    ]
