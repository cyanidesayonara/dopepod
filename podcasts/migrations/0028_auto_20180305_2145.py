# Generated by Django 2.0.2 on 2018-03-05 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0027_episode_position'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='podcast',
            index=models.Index(fields=['title'], name='podcasts_po_title_b6422d_idx'),
        ),
        migrations.AddIndex(
            model_name='podcast',
            index=models.Index(fields=['artist'], name='podcasts_po_artist_010d17_idx'),
        ),
        migrations.AddIndex(
            model_name='podcast',
            index=models.Index(fields=['genre'], name='podcasts_po_genre_i_653dbd_idx'),
        ),
        migrations.AddIndex(
            model_name='podcast',
            index=models.Index(fields=['language'], name='podcasts_po_languag_73c689_idx'),
        ),
        migrations.AddIndex(
            model_name='podcast',
            index=models.Index(fields=['rank'], name='podcasts_po_rank_d437a5_idx'),
        ),
    ]