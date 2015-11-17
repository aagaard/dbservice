# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homes', '0005_auto_20150304_1656'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appliance',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='energyconsumptionperiod',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='energyproductionperiod',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='fixedvaluemeterport',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='mainmeter',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='measurement',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='meterport',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='residentialhome',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='virtualenergyport',
            options={'ordering': ['-id']},
        ),
        migrations.AlterField(
            model_name='appliance',
            name='name',
            field=models.CharField(max_length=64, choices=[('air_conditioner', 'Air conditioner'), ('dishwasher', 'Dishwasher'), ('electrical_vehicle', 'Electrical Vehicle'), ('freezer', 'Freezer'), ('heat_pump', 'Heat pump'), ('hifi', 'Hi-Fi'), ('kettle', 'Kettle'), ('microwave', 'Microwave'), ('other', 'Other'), ('oven', 'Oven'), ('photo_voltaic', 'Photo Voltaic'), ('tumble_dryer', 'Tumble dryer'), ('tv', 'TV'), ('washing_machine', 'Washing machine'), ('refrigerator', 'Refrigerator'), ('stove', 'Stove'), ('stove_oven', 'Stove & Oven'), ('ventilation', 'Ventilation'), ('service_line', 'Service Line'), ('genvex', 'Genvex'), ('lighting', 'Lighting')]),
            preserve_default=True,
        ),
    ]
