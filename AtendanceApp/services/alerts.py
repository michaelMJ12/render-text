from AtendanceApp.models import DeviceAlert


def trigger_device_alert(device, message):
    if not DeviceAlert.objects.filter(
        device=device,
        message=message,
        is_resolved=False
    ).exists():
        DeviceAlert.objects.create(
            device=device,
            message=message
        )
