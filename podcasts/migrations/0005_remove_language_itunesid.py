# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-25 22:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0004_auto_20171125_2359'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='language',
            name='itunesid',
        ),
    ]