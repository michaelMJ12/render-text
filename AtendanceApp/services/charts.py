from django.db.models import Count
from django.utils.timezone import localdate
from datetime import timedelta

from AtendanceApp.models import AttendanceEvent


def daily_attendance_trend(days=7):
    today = localdate()
    start_date = today - timedelta(days=days - 1)

    data = (
        AttendanceEvent.objects
        .filter(timestamp__date__range=[start_date, today])
        .values("timestamp__date", "event_type")
        .annotate(total=Count("id"))
        .order_by("timestamp__date")
    )

    result = {}
    for item in data:
        date = str(item["timestamp__date"])
        if date not in result:
            result[date] = {"IN": 0, "OUT": 0}
        result[date][item["event_type"]] = item["total"]

    return result
