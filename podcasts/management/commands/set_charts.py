from django.core.management.base import BaseCommand, CommandError
from podcasts.models import Chart

class Command(BaseCommand):
    args = ''
    help = 'set charts'

    def handle(self, *args, **options):
        Chart.set_charts()
