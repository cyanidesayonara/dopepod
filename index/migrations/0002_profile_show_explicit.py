# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-30 05:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='show_explicit',
            field=models.BooleanField(default=True),
        ),
    ]