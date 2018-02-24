from django.core.management.base import BaseCommand, CommandError
from podcasts.models import Chart, Filterable

class Command(BaseCommand):
    args = ''
    help = 'set charts'

    def handle(self, *args, **options):
        Chart.set_charts()
        Chart.cache_charts()
        Filterable.count_n_podcasts()
