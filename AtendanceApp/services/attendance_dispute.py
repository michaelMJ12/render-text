from django.utils.timezone import now
from AtendanceApp.models import AttendanceDispute, AttendanceCorrection


def submit_dispute(user, attendance_log, reason, check_in=None, check_out=None):
    return AttendanceDispute.objects.create(
        attendance_log=attendance_log,
        requested_by=user,
        reason=reason,
        proposed_check_in=check_in,
        proposed_check_out=check_out
    )


def review_dispute(dispute, admin_user, approve, comment=None):
    dispute.reviewed_by = admin_user
    dispute.reviewed_at = now()
    dispute.admin_comment = comment

    if approve:
        dispute.status = "APPROVED"
        AttendanceCorrection.objects.create(
            attendance_log=dispute.attendance_log,
            corrected_timestamp=dispute.proposed_timestamp,
            corrected_event_type=dispute.proposed_event_type,
            approved_by=admin_user
        )
    else:
        dispute.status = "REJECTED"

    dispute.save()
