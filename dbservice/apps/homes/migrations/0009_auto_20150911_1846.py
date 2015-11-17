# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homes', '0008_meterport_phase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measurement',
            name='timestamp',
            field=models.DateTimeField(db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='meterport',
            name='phase',
            field=models.CharField(default=('unknown', 'Unknown'), choices=[('unknown', 'Unknown'), ('L1', 'L1'), ('L2', 'L2'), ('L3', 'L3'), ('L1L2L3', 'L1L2L3')], max_length=32),
            preserve_default=True,
        ),
    ]
