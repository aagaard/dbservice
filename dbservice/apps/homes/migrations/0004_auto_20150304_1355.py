# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homes', '0003_fixedvaluemeterport'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualenergyport',
            name='consumption',
            field=models.ForeignKey(to='homes.MeterPort', null=True, related_name='meter_ports_consumption'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='meterport',
            name='resource_type',
            field=models.CharField(choices=[('electricity', 'electricity'), ('temperature', 'temperature')], max_length=32),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='meterport',
            name='unit',
            field=models.CharField(choices=[('milliwatt*hour', 'mWh'), ('milliwatt', 'mW'), ('millivolt', 'mV'), ('milliampere', 'mA'), ('millihertz', 'mHz'), ('millidegrees_celsius', 'm°C'), ('parts_per_thousand', '‰'), ('millipower_factor', 'pf')], max_length=32),
            preserve_default=True,
        ),
    ]
