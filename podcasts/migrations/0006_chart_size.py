# Generated by Django 2.0 on 2018-01-31 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0005_auto_20180131_2324'),
    ]

    operations = [
        migrations.AddField(
            model_name='chart',
            name='size',
            field=models.IntegerField(default=0),
        ),
    ]
