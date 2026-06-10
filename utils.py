import hashlib
import json


# -------------------------------
# SAFE STRING CONVERTER
# -------------------------------
def to_safe_string(value):
    try:
        if isinstance(value, (dict, list)):
            return json.dumps(value, sort_keys=True)
        if value is None:
            return "null"
        return str(value)
    except:
        return "unknown"


# -------------------------------
# TRACE ID GENERATOR (IMPROVED)
# -------------------------------
def generate_trace_id(signal):

    try:
        if not isinstance(signal, dict):
            return "TRACE_INVALID"

        signal_id = to_safe_string(signal.get("signal_id", "unknown"))
        timestamp = to_safe_string(signal.get("timestamp", "unknown"))
        dataset_id = to_safe_string(signal.get("dataset_id", "unknown"))
        source = to_safe_string(signal.get("source", "unknown"))

        # 🔥 More unique + stable
        base_string = f"{signal_id}|{timestamp}|{dataset_id}|{source}"

        return "TRACE_" + hashlib.sha256(base_string.encode()).hexdigest()[:12]

    except:
        return "TRACE_ERROR"


# -------------------------------
# OUTPUT SCHEMA VALIDATION (SAFE + BASIC)
# -------------------------------
def validate_output_schema(output):

    try:
        if not isinstance(output, dict):
            return False

        required_fields = ["trace_id", "risk_level"]

        for field in required_fields:
            if field not in output:
                return False

        return True

    except:
        return False