# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homes', '0010_auto_20150915_1247'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='measurement',
            options={'get_latest_by': 'timestamp'},
        ),
    ]
