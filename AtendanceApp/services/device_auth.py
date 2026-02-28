import hmac
import hashlib
from datetime import timedelta
from datetime import datetime

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




