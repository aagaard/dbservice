# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=120)),
                ('postal_code', models.CharField(blank=True, max_length=30)),
                ('city', models.CharField(blank=True, max_length=120)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
