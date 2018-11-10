from django.core.management.base import BaseCommand, CommandError
from podcasts.models import Podcast, Filterable
from django.core.cache import cache
from django.core.management import call_command

class Command(BaseCommand):
    args = ''
    help = 'set charts'

    def handle(self, *args, **options):
        Podcast.set_charts()
        Filterable.count_n_podcasts()
        call_command('rebuild_index', verbosity=3)
        cache.clear()
