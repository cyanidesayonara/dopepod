# Generated by Django 2.0 on 2017-12-30 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0010_auto_20171230_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='podcast',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]