# Generated by Django 2.0.2 on 2018-02-25 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0022_auto_20180225_0349'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podcast',
            name='bump',
        ),
        migrations.AddField(
            model_name='podcast',
            name='genre_rank',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='podcast',
            name='itunes_genre_rank',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='podcast',
            name='itunes_rank',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='podcast',
            name='language_rank',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='rank',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
