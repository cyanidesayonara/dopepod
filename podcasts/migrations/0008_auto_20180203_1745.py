# Generated by Django 2.0 on 2018-02-03 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0007_auto_20180201_0356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='size',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
