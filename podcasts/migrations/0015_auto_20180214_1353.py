# Generated by Django 2.0.2 on 2018-02-14 11:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0014_auto_20180210_2226'),
    ]

    operations = [
        migrations.CreateModel(
            name='Last_Played',
            fields=[
                ('episode_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='podcasts.Episode')),
            ],
            bases=('podcasts.episode',),
        ),
        migrations.RemoveField(
            model_name='episode',
            name='played',
        ),
    ]