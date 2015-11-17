# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('homes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='residentialhome',
            name='dno_customer_id',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='residential_homes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='meterport',
            name='energy_consumption_period',
            field=models.OneToOneField(blank=True, to='homes.EnergyConsumptionPeriod', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='meterport',
            name='energy_production_period',
            field=models.OneToOneField(blank=True, to='homes.EnergyProductionPeriod', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='meterport',
            name='mainmeter',
            field=models.ForeignKey(to='homes.MainMeter', blank=True, related_name='meter_ports', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='meterport',
            name='submeter',
            field=models.ForeignKey(to='homes.SubMeter', blank=True, related_name='meter_ports', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='measurement',
            name='meter_port',
            field=models.ForeignKey(to='homes.MeterPort', related_name='measurement'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mainmeter',
            name='residential_home',
            field=models.ForeignKey(to='homes.ResidentialHome', related_name='main_meter'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='energyproductionperiod',
            name='appliance',
            field=models.ForeignKey(to='homes.Appliance', related_name='energy_production_period', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='energyconsumptionperiod',
            name='appliance',
            field=models.ForeignKey(to='homes.Appliance', related_name='energy_consumption_period', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='appliance',
            name='residential_home',
            field=models.ForeignKey(to='homes.ResidentialHome', related_name='appliances'),
            preserve_default=True,
        ),
    ]
