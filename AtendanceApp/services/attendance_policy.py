from datetime import datetime, timedelta
from django.utils.timezone import make_aware


def evaluate_attendance(record, shift, policy):
    """
    Apply business rules after CHECK-OUT
    """

    if not record.check_in or not record.check_out:
        return record

    work_duration = record.check_out - record.check_in
    worked_hours = work_duration.total_seconds() / 3600

    shift_start = make_aware(
        datetime.combine(record.date, shift.start_time)
    )

    late_threshold = shift_start + timedelta(minutes=policy.late_grace_minutes)

    # LATE
    if record.check_in > late_threshold:
        record.status = "LATE"

    # HALF DAY
    if worked_hours < policy.half_day_hours:
        record.status = "HALF_DAY"

    # PRESENT
    if worked_hours >= policy.half_day_hours:
        record.status = "PRESENT"

    record.save()
    return record
