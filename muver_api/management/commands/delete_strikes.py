import datetime
from django.utils import timezone
from django.core.management import BaseCommand
from muver_api.models import Strike


class Command(BaseCommand):
    def handle(self, *args, **options):
        two_months = timezone.now() - datetime.timedelta(
            days=60)
        for strike in Strike.objects.all().filter(created_at__lt=two_months):
            strike.delete()
            print("Deleted strike for mover: {}".format(strike.profile))