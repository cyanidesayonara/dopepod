# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-30 05:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0017_auto_20171130_0350'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='new_episodes',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='genre',
            name='n_podcasts',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='language',
            name='n_podcasts',
            field=models.IntegerField(default=0),
        ),
    ]
