from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def broadcast_attendance(user, event_type, timestamp):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "attendance_live",
        {
            "type": "attendance_event",
            "data": {
                "user": user.id,
                "event": event_type,
                "time": timestamp.isoformat(),
            }
        }
    )
