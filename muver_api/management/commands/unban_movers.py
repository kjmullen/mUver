import datetime
from django.utils import timezone
from django.core.management import BaseCommand
from muver_api.models import Strike, UserProfile


class Command(BaseCommand):
    def handle(self, *args, **options):
        two_days = timezone.now() - datetime.timedelta(days=2)
        ten_days = timezone.now() - datetime.timedelta(days=10)
        for profile in UserProfile.objects.all().filter(strikes__gt=0).filter(strikes__lt=3):
            if len(profile.strikes) == 1:
                for strike in profile.strikes:
                    if strike.created_at > two_days:
                        profile.unban_user()
            elif len(profile.strikes) == 2:
                for strike in profile.strikes:
                    if strike.created_at > ten_days:
                        profile.unban_user()