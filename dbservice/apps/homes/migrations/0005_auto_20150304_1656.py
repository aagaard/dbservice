# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homes', '0004_auto_20150304_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meterport',
            name='unit',
            field=models.CharField(max_length=32, choices=[('milliwatt*hour', 'mWh'), ('milliwatt', 'mW'), ('millivolt', 'mV'), ('milliampere', 'mA'), ('millihertz', 'mHz'), ('millidegrees_celsius', 'm°C'), ('parts_per_thousand', '‰')]),
            preserve_default=True,
        ),
    ]
