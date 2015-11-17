# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homes', '0011_auto_20150917_1309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meterport',
            name='unit',
            field=models.CharField(choices=[('milliwatt*hour', 'mWh'), ('milliwatt', 'mW'), ('millivolt', 'mV'), ('milliampere', 'mA'), ('millihertz', 'mHz'), ('millidegrees_celsius', 'm°C'), ('parts_per_thousand', '‰'), ('millivolt_ampere', 'mVA'), ('millivolt_ampere_reactive', 'mVAR')], max_length=32),
            preserve_default=True,
        ),
    ]
