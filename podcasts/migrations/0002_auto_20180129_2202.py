# Generated by Django 2.0 on 2018-01-29 20:02

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('podcast__title',)},
        ),
        migrations.AlterField(
            model_name='subscription',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 29, 20, 2, 45, 337712, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='podcast',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to='podcasts.Podcast'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to=settings.AUTH_USER_MODEL),
        ),
    ]