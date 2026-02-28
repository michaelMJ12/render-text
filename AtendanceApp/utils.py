import hmac
import hashlib
from datetime import timedelta
from datetime import datetime
from django.core.mail import send_mail
from django.utils import timezone
from AtendanceApp.services.device_queries import get_offline_devices

def verify_device_signature(device, payload, signature):
    message = (
        payload["biometric_uid"]
        + payload["device_id"]
        + payload["timestamp"].isoformat()
        + payload["event_type"]
    ).encode()

    expected = hmac.new(
        device.api_key.encode(),
        message,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)




def alert_offline_devices():
    offline = get_offline_devices()
    if offline:
        send_mail(
            subject="Offline Attendance Devices",
            message=f"The following devices are offline: {', '.join(d['device_name'] for d in offline)}",
            from_email="noreply@yourcompany.com",
            recipient_list=["admin@company.com"]
        )



def time_ago(dt):
    if not dt:
        return "Never"

    diff = timezone.now() - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return "Just now"
    if seconds < 3600:
        return f"{int(seconds // 60)} mins ago"
    if seconds < 86400:
        return f"{int(seconds // 3600)} hrs ago"
    return f"{int(seconds // 86400)} days ago"





# def evaluate_attendance(record, shift, policy):
#     if not record.check_in:
#         record.status = "ABSENT"
#         return

#     late_limit = (
#         datetime.combine(record.date, shift.start_time)
#         + timedelta(minutes=policy.late_grace_minutes)
#     )

#     if record.check_in > late_limit:
#         record.status = "LATE"
#     else:
#         record.status = "PRESENT"

#     if record.check_out:
#         worked_hours = (
#             record.check_out - record.check_in
#         ).total_seconds() / 3600

#         if worked_hours < policy.half_day_hours:
#             record.status = "HALF_DAY"