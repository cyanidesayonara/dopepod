# Generated by Django 2.0 on 2017-12-15 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0020_episode'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='length',
            field=models.DurationField(blank=True, null=True),
        ),
    ]
