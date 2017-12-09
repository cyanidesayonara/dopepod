# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-30 07:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0018_auto_20171130_0526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podcast',
            name='artist',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='artworkUrl',
            field=models.URLField(max_length=500),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='copyrighttext',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='n_subscribers',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='podcastUrl',
            field=models.URLField(max_length=500),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='reviewsUrl',
            field=models.URLField(max_length=500),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='title',
            field=models.CharField(max_length=500),
        ),
    ]