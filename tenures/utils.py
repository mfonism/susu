from django.utils import timezone


def seven_days_from_now():
    return timezone.now() + timezone.timedelta(7)

def two_weeks_from_now():
    return timezone.now() + timezone.timedelta(14)
