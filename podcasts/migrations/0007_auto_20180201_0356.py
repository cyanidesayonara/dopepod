# Generated by Django 2.0 on 2018-02-01 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0006_chart_size'),
    ]

    operations = [
        migrations.RenameField(
            model_name='episode',
            old_name='parent',
            new_name='podcast',
        ),
        migrations.AlterField(
            model_name='episode',
            name='played',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
