from django.core.management.base import BaseCommand, CommandError
from podcasts.models import Podcast, Filterable

class Command(BaseCommand):
    args = ''
    help = 'set charts'

    def handle(self, *args, **options):
        Podcast.set_charts()
        Podcast.cache_charts()
        Filterable.count_n_podcasts()
