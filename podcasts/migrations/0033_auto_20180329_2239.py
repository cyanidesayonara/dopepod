# Generated by Django 2.0.3 on 2018-03-29 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0032_auto_20180323_0311'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='podcast',
            name='podcasts_po_title_b6422d_idx',
        ),
        migrations.RemoveIndex(
            model_name='podcast',
            name='podcasts_po_artist_010d17_idx',
        ),
        migrations.RemoveIndex(
            model_name='podcast',
            name='podcasts_po_genre_i_653dbd_idx',
        ),
        migrations.RemoveIndex(
            model_name='podcast',
            name='podcasts_po_languag_73c689_idx',
        ),
        migrations.RemoveIndex(
            model_name='podcast',
            name='podcasts_po_rank_d437a5_idx',
        ),
    ]
