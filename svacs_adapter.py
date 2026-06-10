# svacs_adapter.py

import uuid


# -----------------------------------
# TRACE ID GENERATOR (NO utils needed)
# -----------------------------------
def generate_trace_id():
    return "TRACE_" + uuid.uuid4().hex[:12]


# -----------------------------------
# BASIC INPUT VALIDATION
# -----------------------------------
def validate_perception_event(event: dict):
    if not isinstance(event, dict):
        return False, "Invalid event format"

    if not event.get("event_id"):
        return False, "Missing event_id"

    if not event.get("timestamp"):
        return False, "Missing timestamp"

    vessel = event.get("vessel", {})

    if not isinstance(vessel, dict):
        return False, "Invalid vessel data"

    if vessel.get("confidence_score") is None:
        return False, "Missing confidence_score"

    return True, "Valid"


# -----------------------------------
# CONVERT SVACS → NICAI SIGNAL
# -----------------------------------
def convert_perception_to_signal(event: dict):

    vessel = event.get("vessel", {})
    metadata = event.get("metadata", {})

    signal = {
        # CORE FIELDS
        "signal_id": event.get("event_id"),
        "timestamp": event.get("timestamp"),
        "value": vessel.get("confidence_score"),

        # NICAI FORMAT
        "asset_id": vessel.get("type", "unknown"),
        "signal_type": "acoustic_detection",
        "feature_type": "acoustic",   # ✅ REQUIRED FIX
        "dataset_id": "svacs",
        "source": "svacs",

        # CONTEXT
        "metadata": metadata,
        "state": event.get("state", "unknown"),

        # GEO DEFAULTS
        "latitude": metadata.get("latitude", 0.0),
        "longitude": metadata.get("longitude", 0.0)
    }

    return signal


# -----------------------------------
# PREPARE SIGNAL + TRACE ID
# -----------------------------------
def prepare_signal(event: dict):

    is_valid, reason = validate_perception_event(event)

    if not is_valid:
        return {
            "status": "ERROR",
            "reason": reason,
            "trace_id": None,
            "signal": None
        }

    signal = convert_perception_to_signal(event)

    # Generate trace_id
    trace_id = generate_trace_id()

    signal["trace_id"] = trace_id

    return {
        "status": "SUCCESS",
        "signal": signal,
        "trace_id": trace_id
    }