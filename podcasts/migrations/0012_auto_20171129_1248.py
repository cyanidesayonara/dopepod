# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-29 12:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0011_auto_20171129_1321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chart',
            name='pods',
        ),
        migrations.AddField(
            model_name='podcast',
            name='chart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='podcasts.Chart'),
        ),
    ]