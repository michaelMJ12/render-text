from django.utils import timezone
from datetime import timedelta
from AtendanceApp.models import AttendanceDevice


def get_offline_devices(minutes=10):
    threshold = timezone.now() - timedelta(minutes=minutes)
    return AttendanceDevice.objects.filter(last_seen__lt=threshold)
