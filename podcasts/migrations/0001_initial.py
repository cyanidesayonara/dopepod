# Generated by Django 2.0 on 2018-01-27 20:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(max_length=16)),
                ('header', models.CharField(default='Top 50 podcasts', max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pubDate', models.DateTimeField()),
                ('title', models.CharField(max_length=1000)),
                ('summary', models.TextField(blank=True, null=True)),
                ('length', models.DurationField(blank=True, null=True)),
                ('url', models.CharField(max_length=1000)),
                ('kind', models.CharField(max_length=16)),
                ('size', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('name', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('n_podcasts', models.IntegerField(default=0)),
                ('genreid', models.IntegerField()),
                ('supergenre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='podcasts.Genre')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('name', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('n_podcasts', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('-n_podcasts',),
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField()),
                ('chart', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='podcasts.Chart')),
            ],
        ),
        migrations.CreateModel(
            name='Podcast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('podid', models.IntegerField()),
                ('feedUrl', models.CharField(max_length=1000)),
                ('title', models.CharField(max_length=1000)),
                ('artist', models.CharField(max_length=1000)),
                ('explicit', models.BooleanField()),
                ('copyrighttext', models.CharField(max_length=5000)),
                ('description', models.TextField(blank=True, max_length=5000)),
                ('n_subscribers', models.IntegerField(default=0)),
                ('reviewsUrl', models.CharField(max_length=1000)),
                ('artworkUrl', models.CharField(max_length=1000)),
                ('podcastUrl', models.CharField(max_length=1000)),
                ('discriminate', models.BooleanField(default=False)),
                ('views', models.IntegerField(default=0)),
                ('last_episode', models.DateTimeField(blank=True, null=True)),
                ('rank', models.IntegerField(default=0)),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='podcasts.Genre')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='podcasts.Language')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('new_episodes', models.IntegerField(default=0)),
                ('podcast', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='podcast', to='podcasts.Podcast')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('parent__title',),
            },
        ),
        migrations.AddField(
            model_name='order',
            name='podcast',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='podcasts.Podcast'),
        ),
        migrations.AddField(
            model_name='episode',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='podcasts.Podcast'),
        ),
        migrations.AddField(
            model_name='chart',
            name='genre',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='podcasts.Genre'),
        ),
        migrations.AddField(
            model_name='chart',
            name='podcasts',
            field=models.ManyToManyField(through='podcasts.Order', to='podcasts.Podcast'),
        ),
    ]
