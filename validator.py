from schemas import required_fields
from dataset_registry import get_dataset
from utils import validate_output_schema

# OPTIONAL SAFE IMPORTS
try:
    from bucket_emitter import emit_bucket_artifact
    from telemetry_emitter import emit_telemetry
except ImportError:
    def emit_bucket_artifact(x): pass
    def emit_telemetry(a, b): pass


# -------------------------------
# SAFE FLAG FORMAT (NO HARD REJECT)
# -------------------------------
def build_flag(reason, trace_id=None, signal=None):
    result = {
        "signal_id": signal.get("signal_id") if isinstance(signal, dict) else None,
        "status": "FLAG",  # ✅ ALWAYS FLAG (NO REJECT)
        "confidence_score": 0.5,
        "trace_id": trace_id or "TRACE_UNKNOWN",
        "reason": str(reason)
    }

    try:
        validate_output_schema(result)
        emit_bucket_artifact(result)
        emit_telemetry(signal, result)
    except:
        pass

    return result


# -------------------------------
# VALIDATE SINGLE SIGNAL
# -------------------------------
def validate_signal(signal):

    try:
        if not isinstance(signal, dict):
            return build_flag("Invalid signal format")

        # ✅ USE EXISTING TRACE ID (DO NOT GENERATE NEW)
        trace_id = signal.get("trace_id", "TRACE_UNKNOWN")

        # -------------------------------
        # REQUIRED FIELDS CHECK
        # -------------------------------
        for field in required_fields:
            if field not in signal or signal.get(field) in [None, ""]:
                return build_flag(f"Missing field: {field}", trace_id, signal)

        # -------------------------------
        # DATASET CHECK
        # -------------------------------
        dataset_id = signal.get("dataset_id")

        if not isinstance(dataset_id, (str, int)):
            return build_flag("Invalid dataset_id type", trace_id, signal)

        dataset = get_dataset(dataset_id)

        if not isinstance(dataset, dict):
            return build_flag("Dataset not registered", trace_id, signal)

        # -------------------------------
        # DATASET STATUS
        # -------------------------------
        if dataset.get("status") != "active":
            result = {
                "signal_id": signal.get("signal_id"),
                "status": "FLAG",
                "confidence_score": dataset.get("trust_score", 0.5),
                "trace_id": trace_id,
                "reason": "Dataset inactive"
            }

            validate_output_schema(result)
            emit_bucket_artifact(result)
            emit_telemetry(signal, result)

            return result

        # -------------------------------
        # FEATURE VALIDATION
        # -------------------------------
        value = signal.get("value")
        feature = str(signal.get("feature_type", "")).lower()

        if not isinstance(value, (int, float)):
            return build_flag("Invalid value type", trace_id, signal)

        # -------------------------------
        # RULE LOGIC
        # -------------------------------

        if feature == "temperature":
            if value >= 35:
                status = "FLAG"
                confidence = 0.7
                reason = "Temperature anomaly"
            else:
                status = "ALLOW"
                confidence = 0.9
                reason = "Normal temperature"

        elif feature == "aqi":
            if value >= 150:
                status = "FLAG"
                confidence = 0.7
                reason = "AQI anomaly"
            else:
                status = "ALLOW"
                confidence = 0.9
                reason = "Normal AQI"

        elif feature == "traffic":
            if value >= 70:
                status = "FLAG"
                confidence = 0.7
                reason = "Traffic anomaly"
            else:
                status = "ALLOW"
                confidence = 0.9
                reason = "Normal traffic"

        else:
            # ✅ SVACS ACOUSTIC CASE
            status = "ALLOW"
            confidence = float(value)   # dynamic confidence
            reason = "Valid signal"

        # -------------------------------
        # FINAL OUTPUT
        # -------------------------------
        result = {
            "signal_id": signal.get("signal_id"),
            "status": status,   # ONLY ALLOW / FLAG
            "confidence_score": confidence,
            "trace_id": trace_id,
            "reason": reason
        }

        validate_output_schema(result)
        emit_bucket_artifact(result)
        emit_telemetry(signal, result)

        return result

    except Exception as e:
        return build_flag(str(e), None, signal)


# -------------------------------
# VALIDATE BATCH
# -------------------------------
def validate_batch(signals):

    try:
        if not isinstance(signals, list):
            return {
                "status": "FLAG",
                "reason": "Input must be list",
                "trace_id": None
            }

        safe_signals = [s for s in signals if isinstance(s, dict)]
        safe_signals.sort(key=lambda x: str(x.get("signal_id", "")))

        results = [validate_signal(s) for s in safe_signals]

        return {
            "status": "SUCCESS",
            "results": results
        }

    except Exception as e:
        return {
            "status": "FLAG",
            "reason": str(e),
            "trace_id": None
        }


# -------------------------------
# FILTER VALID SIGNALS
# -------------------------------
def get_validated_signals(signals):

    try:
        batch = validate_batch(signals)

        if batch.get("status") == "FLAG":
            return batch

        return [
            r for r in batch.get("results", [])
            if isinstance(r, dict) and r.get("status") in ["ALLOW", "FLAG"]
        ]

    except Exception as e:
        return {
            "status": "FLAG",
            "reason": str(e),
            "trace_id": None
        }