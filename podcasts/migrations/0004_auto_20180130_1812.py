# Generated by Django 2.0 on 2018-01-30 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0003_auto_20180130_0000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podcast',
            name='last_episode',
        ),
        migrations.AddField(
            model_name='podcast',
            name='plays',
            field=models.IntegerField(default=0),
        ),
    ]