from django.core.management.base import BaseCommand, CommandError
from podcasts.models import Chart
from django.core.mail import send_mail

class Command(BaseCommand):
    args = ''
    help = 'set charts'

    def handle(self, *args, **options):
        Chart.set_charts()
        send_mail('set_charts finished', 'it\'s working!', 'noreply@dopepod.me', ['cyanidesayonara@gmail.com'])
