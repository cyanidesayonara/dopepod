# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-29 14:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0013_auto_20171129_1256'),
    ]

    operations = [
        migrations.AddField(
            model_name='chart',
            name='name',
            field=models.CharField(default=0, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='chart',
            name='genre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='podcasts.Genre'),
        ),
    ]