# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-27 22:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0007_auto_20171128_0049'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='last_updated',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='pod',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='user',
        ),
    ]
