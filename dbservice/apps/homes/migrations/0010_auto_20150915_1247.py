# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homes', '0009_auto_20150911_1846'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appliance',
            options={},
        ),
        migrations.AlterModelOptions(
            name='energyconsumptionperiod',
            options={},
        ),
        migrations.AlterModelOptions(
            name='energyproductionperiod',
            options={},
        ),
        migrations.AlterModelOptions(
            name='fixedvaluemeterport',
            options={},
        ),
        migrations.AlterModelOptions(
            name='mainmeter',
            options={},
        ),
        migrations.AlterModelOptions(
            name='measurement',
            options={},
        ),
        migrations.AlterModelOptions(
            name='meterport',
            options={},
        ),
        migrations.AlterModelOptions(
            name='residentialhome',
            options={},
        ),
        migrations.AlterModelOptions(
            name='virtualenergyport',
            options={},
        ),
        migrations.AlterField(
            model_name='appliance',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='energyconsumptionperiod',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='energyproductionperiod',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fixedvaluemeterport',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mainmeter',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measurement',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='meterport',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='residentialhome',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='submeter',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
    ]
