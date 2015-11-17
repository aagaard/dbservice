# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('homes', '0006_auto_20150315_1012'),
    ]

    operations = [
        migrations.AddField(
            model_name='appliance',
            name='created',
            field=models.DateTimeField(
                default=datetime.datetime(1, 1, 1, 0, 0),
                auto_now_add=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appliance',
            name='last_modified',
            field=models.DateTimeField(
                auto_now=True,
                default=datetime.datetime(1, 1, 1, 0, 0)
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='energyconsumptionperiod',
            name='created',
            field=models.DateTimeField(
                default=datetime.datetime(1, 1, 1, 0, 0),
                auto_now_add=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='energyconsumptionperiod',
            name='last_modified',
            field=models.DateTimeField(
                auto_now=True,
                default=datetime.datetime(1, 1, 1, 0, 0)
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='energyproductionperiod',
            name='created',
            field=models.DateTimeField(
                default=datetime.datetime(1, 1, 1, 0, 0),
                auto_now_add=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='energyproductionperiod',
            name='last_modified',
            field=models.DateTimeField(
                auto_now=True,
                default=datetime.datetime(1, 1, 1, 0, 0)
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fixedvaluemeterport',
            name='created',
            field=models.DateTimeField(
                default=datetime.datetime(1, 1, 1, 0, 0),
                auto_now_add=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fixedvaluemeterport',
            name='last_modified',
            field=models.DateTimeField(
                auto_now=True,
                default=datetime.datetime(1, 1, 1, 0, 0)
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mainmeter',
            name='created',
            field=models.DateTimeField(
                default=datetime.datetime(1, 1, 1, 0, 0),
                auto_now_add=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mainmeter',
            name='last_modified',
            field=models.DateTimeField(
                auto_now=True,
                default=datetime.datetime(1, 1, 1, 0, 0)
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='measurement',
            name='created',
            field=models.DateTimeField(
                default=datetime.datetime(1, 1, 1, 0, 0),
                auto_now_add=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='measurement',
            name='last_modified',
            field=models.DateTimeField(
                auto_now=True,
                default=datetime.datetime(1, 1, 1, 0, 0)
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meterport',
            name='created',
            field=models.DateTimeField(
                default=datetime.datetime(1, 1, 1, 0, 0),
                auto_now_add=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meterport',
            name='last_modified',
            field=models.DateTimeField(
                auto_now=True,
                default=datetime.datetime(1, 1, 1, 0, 0)
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='residentialhome',
            name='last_modified',
            field=models.DateTimeField(
                auto_now=True,
                default=datetime.datetime(1, 1, 1, 0, 0)
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submeter',
            name='created',
            field=models.DateTimeField(
                default=datetime.datetime(1, 1, 1, 0, 0),
                auto_now_add=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submeter',
            name='last_modified',
            field=models.DateTimeField(
                auto_now=True,
                default=datetime.datetime(1, 1, 1, 0, 0)
            ),
            preserve_default=False,
        ),
    ]
