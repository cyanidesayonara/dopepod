import pytz
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

class LocalDateMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            try:
                tz = pytz.timezone(tzname)
                timezone.activate(tz)
                return
            except pytz.exceptions.UnknownTimeZoneError:
                pass
        timezone.deactivate()
