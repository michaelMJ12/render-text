from datetime import timedelta
from django.utils.timezone import now
from AtendanceApp.utils import time_ago
from AtendanceApp.models import AttendanceDevice, DeviceAlert


OFFLINE_THRESHOLD_MINUTES = 10


def get_device_status(device):
    if not device.is_active:
        return "INACTIVE"

    if not device.last_seen:
        return "OFFLINE"

    if (now() - device.last_seen) > timedelta(minutes=OFFLINE_THRESHOLD_MINUTES):
        return "OFFLINE"

    return "ONLINE"


def get_device_health():
    devices = AttendanceDevice.objects.all()
    result = []

    for device in devices:
        status = get_device_status(device)

        alerts_count = DeviceAlert.objects.filter(
            device=device,
            is_resolved=False
        ).count()

        result.append({
            "device_id": device.device_id,
            "device_name": device.device_name,
            "status": status,
            "last_seen": device.last_seen,
            "last_seen_human": time_ago(device.last_seen),
            "alerts": alerts_count
        })

    return result


def get_offline_devices():
    return [d for d in get_device_health() if d["status"] == "OFFLINE"]
