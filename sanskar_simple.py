# OPTIONAL SAFE IMPORT
try:
    from bucket_emitter import emit_bucket_artifact
except ImportError:
    def emit_bucket_artifact(x):
        pass


# -----------------------------------
# RISK LEVEL ENGINE
# -----------------------------------
def get_risk_level(confidence):

    if confidence >= 0.75:
        return "LOW"
    elif confidence >= 0.5:
        return "MEDIUM"
    elif confidence >= 0.3:
        return "HIGH"
    else:
        return "CRITICAL"


# -----------------------------------
# ANOMALY DETECTOR
# -----------------------------------
def detect_anomaly(signal):

    vessel_type = signal.get("asset_id", "unknown")
    metadata = signal.get("metadata", {})

    incoming_flag = metadata.get("anomaly_flag", False)

    if incoming_flag is True:
        return True

    if vessel_type == "unknown":
        return True

    return False


# -----------------------------------
# EXPLANATION ENGINE
# -----------------------------------
def generate_explanation(confidence, vessel_type, risk, anomaly):

    if anomaly:
        return "Anomalous acoustic pattern detected — classified as critical risk"

    if vessel_type == "unknown":
        return "Unknown vessel detected — classified as critical risk"

    if risk == "CRITICAL":
        return "Very low confidence acoustic detection — critical risk"

    if risk == "HIGH":
        return "Low confidence acoustic detection — high risk"

    if risk == "MEDIUM":
        return "Moderate confidence acoustic detection — medium risk"

    return f"High confidence acoustic classification of {vessel_type} vessel — low risk"


# -----------------------------------
# BUCKET LOGGER
# -----------------------------------
def log_intelligence(signal, intelligence):

    emit_bucket_artifact({
        "trace_id": intelligence.get("trace_id"),
        "type": "intelligence_event",
        "layer": "SANSKAR_INTELLIGENCE",
        "input": signal,
        "output": intelligence,
        "timestamp": signal.get("timestamp")
    })


# -----------------------------------
# MAIN INTELLIGENCE ENGINE
# -----------------------------------
def analyze_signal(signal):

    try:
        # ✅ MUST EXIST
        trace_id = signal.get("trace_id")

        if not trace_id:
            raise ValueError("Missing trace_id in input signal")

        confidence = float(signal.get("value", 0.0))
        vessel_type = signal.get("asset_id", "unknown")

        anomaly = detect_anomaly(signal)

        risk = get_risk_level(confidence)

        if anomaly:
            risk = "CRITICAL"

        explanation = generate_explanation(
            confidence,
            vessel_type,
            risk,
            anomaly
        )

        intelligence = {
            "trace_id": trace_id,   # 🔥 IMPORTANT
            "vessel_type": vessel_type,
            "confidence": confidence,
            "risk_level": risk,
            "anomaly_flag": anomaly,
            "explanation": explanation
        }

        log_intelligence(signal, intelligence)

        return intelligence

    except Exception as e:
        return {
            "trace_id": signal.get("trace_id", "TRACE_UNKNOWN"),
            "status": "ERROR",
            "reason": str(e)
        }


# -----------------------------------
# WRAPPER
# -----------------------------------
def analyze_svacs(signal, trace_id=None):
    return analyze_signal(signal)