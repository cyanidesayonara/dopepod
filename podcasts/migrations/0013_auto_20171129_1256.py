# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-29 12:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0012_auto_20171129_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podcast',
            name='chart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pods', to='podcasts.Chart'),
        ),
    ]
