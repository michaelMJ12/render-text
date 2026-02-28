from datetime import timedelta
from ..models import AttendanceEvent

def is_duplicate_scan(user, device, event_type, timestamp):
    return AttendanceEvent.objects.filter(
        user=user,
        device=device,
        event_type=event_type,
        timestamp__gte=timestamp - timedelta(seconds=30)
    ).exists()
