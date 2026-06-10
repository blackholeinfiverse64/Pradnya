# OPTIONAL SAFE IMPORT

try:
    from bucket_emitter import emit_bucket_artifact
except ImportError:
    def emit_bucket_artifact(x):
        pass


# -----------------------------------
# RISK LEVEL ENGINE
# -----------------------------------

def get_risk_level(value):

    try:
        value = float(value)
    except:
        value = 0.0

    # Weather / AQI dataset thresholds
    if value >= 45:
        return "HIGH"

    elif value >= 35:
        return "MEDIUM"

    else:
        return "LOW"


# -----------------------------------
# ANOMALY DETECTOR
# -----------------------------------

def detect_anomaly(signal):

    metadata = signal.get("metadata", {})

    if metadata.get("anomaly_flag") is True:
        return True

    return False


# -----------------------------------
# EXPLANATION ENGINE
# -----------------------------------

def generate_explanation(value, feature_type, risk, anomaly):

    if anomaly:
        return f"Anomalous {feature_type} signal detected"

    if risk == "HIGH":
        return f"High {feature_type} reading detected"

    if risk == "MEDIUM":
        return f"Moderate {feature_type} reading detected"

    return f"Normal {feature_type} reading detected"


# -----------------------------------
# MAIN ANALYSIS ENGINE
# -----------------------------------

def analyze_signal(signal):

    try:

        trace_id = signal.get(
            "trace_id",
            f"TRACE_{signal.get('signal_id', 'UNKNOWN')}"
        )

        value = float(signal.get("value", 0))

        feature_type = signal.get(
            "feature_type",
            "unknown_feature"
        )

        anomaly = detect_anomaly(signal)

        risk = get_risk_level(value)

        if anomaly:
            risk = "HIGH"

        explanation = generate_explanation(
            value,
            feature_type,
            risk,
            anomaly
        )

        intelligence = {
            "trace_id": trace_id,
            "feature_type": feature_type,
            "confidence": value,
            "risk_level": risk,
            "anomaly_flag": anomaly,
            "anomaly_score": value,
            "anomaly_type": feature_type,
            "recommendation_signal": risk,
            "explanation": explanation
        }

        emit_bucket_artifact({
            "trace_id": trace_id,
            "input": signal,
            "output": intelligence,
            "layer": "SANSKAR_ENGINE"
        })

        return intelligence

    except Exception as e:

        return {
            "trace_id": signal.get(
                "trace_id",
                "TRACE_UNKNOWN"
            ),
            "status": "ERROR",
            "reason": str(e)
        }


# -----------------------------------
# PATTERN DETECTION
# -----------------------------------

def analyze_patterns(events):

    try:

        if not events:
            return {
                "pattern_id": "PATTERN_000",
                "anomaly_count": 0,
                "affected_zones": [],
                "pattern_type": "NONE",
                "severity_trend": "STABLE",
                "pattern_summary": "No events received"
            }

        anomaly_count = len([
            e for e in events
            if e.get("risk_level") in ["HIGH", "MEDIUM"]
        ])

        return {
            "pattern_id": "PATTERN_001",
            "anomaly_count": anomaly_count,
            "affected_zones": [],
            "pattern_type": "ENVIRONMENTAL_CLUSTER",
            "severity_trend": "STABLE",
            "pattern_summary": f"{anomaly_count} elevated-risk events detected"
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "reason": str(e)
        }
