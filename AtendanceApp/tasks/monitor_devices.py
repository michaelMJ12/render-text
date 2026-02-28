from datetime import timedelta
from django.utils.timezone import now
from AtendanceApp.models import AttendanceDevice
from AtendanceApp.services.alerts import trigger_device_alert
from celery import shared_task

OFFLINE_THRESHOLD_MINUTES = 10

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def monitor_devices():

    threshold = now() - timedelta(minutes=OFFLINE_THRESHOLD_MINUTES)

    devices = AttendanceDevice.objects.filter(is_active=True)

    for device in devices:
        if not device.last_seen or device.last_seen < threshold:
            trigger_device_alert(
                device,
                f"Device {device.device_name} is OFFLINE"
            )
