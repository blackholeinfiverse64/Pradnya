from datetime import datetime
import hashlib


def generate_error_trace_id(message):
    return hashlib.sha256(message.encode()).hexdigest()


def error_response(reason, trace_id=None):
    return {
        "status": "ERROR",
        "reason": reason,
        "trace_id": trace_id or generate_error_trace_id(reason),
        "timestamp": str(datetime.utcnow())
    }


# ✅ Input validation gate (Phase 2)
def validate_basic_input(data):

    if data is None:
        return error_response("Input is None")

    if not isinstance(data, (list, dict)):
        return error_response("Input must be list or dict")

    if isinstance(data, list) and len(data) == 0:
        return error_response("Empty input list")

    return None