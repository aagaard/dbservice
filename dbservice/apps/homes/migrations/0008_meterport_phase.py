# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homes', '0007_auto_20150902_0549'),
    ]

    operations = [
        migrations.AddField(
            model_name='meterport',
            name='phase',
            field=models.CharField(default='unknown', max_length=32, choices=[('L1', 'L1'), ('L2', 'L2'), ('L3', 'L3'), ('L1L2L3', 'L1L2L3'), ('unknown', 'Unknown')]),
            preserve_default=True,
        ),
    ]
