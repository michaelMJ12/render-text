from django.utils.timezone import localdate, now
from django.db.models import Count
from datetime import timedelta
from AtendanceApp.models import AttendanceDevice, AttendanceEvent




def get_admin_attendance_dashboard():
    today = localdate()

    return {
        "today": {
            "check_ins": AttendanceEvent.objects.filter(
                event_type="IN",
                timestamp__date=today
            ).count(),

            "check_outs": AttendanceEvent.objects.filter(
                event_type="OUT",
                timestamp__date=today
            ).count(),
        },

        "events_today": AttendanceEvent.objects.filter(
            timestamp__date=today
        ).count(),

        "total_events": AttendanceEvent.objects.count(),

        "devices": {
            "active": AttendanceDevice.objects.filter(is_active=True).count(),
            "inactive": AttendanceDevice.objects.filter(is_active=False).count(),
            "offline": AttendanceDevice.objects.filter(
                last_seen__lt=now() - timedelta(minutes=10)
            ).count() if hasattr(AttendanceDevice, "last_seen") else 0,
        },

        "top_devices": list(
            AttendanceEvent.objects.values(
                "device__device_id"
            ).annotate(
                total=Count("id")
            ).order_by("-total")[:5]
        ),
    }
