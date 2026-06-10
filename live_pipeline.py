from validator import validate_signal
from sanskar_simple import analyze_signal


def process_perception_event(event):

    print("\n-------------------------------")

    # STEP 1: ACCEPT RAW INPUT (NO CHANGE)
    print("📥 Perception Event:", event)

    # STEP 2: DIRECT MAP (STRICT ALIGNMENT)
    signal = {
        "trace_id": event.get("trace_id"),
        "signal_id": event.get("trace_id"),
        "timestamp": "LIVE",
        "value": event.get("confidence_score"),
        "asset_id": event.get("vessel_type"),
        "feature_type": "acoustic",
        "dataset_id": "svacs",
        "signal_type": "acoustic_detection",
        "source": "svacs",
        "metadata": {
            "dominant_freq_hz": event.get("dominant_freq_hz"),
            "anomaly_flag": event.get("anomaly_flag", False)
        },
        "state": "live",

        # REQUIRED FOR VALIDATOR
        "latitude": 0.0,
        "longitude": 0.0
    }

    print("✅ NICAI Signal:", signal)

    # STEP 3: VALIDATION (NO HARD BLOCK)
    validation = validate_signal(signal)
    print("✅ Validation:", validation)

    # DO NOT STOP PIPELINE
    if validation.get("status") not in ["ALLOW", "FLAG"]:
        print("⚠️ Logged invalid but continuing pipeline")

    # STEP 4: SANSKAR INTELLIGENCE
    intelligence = analyze_signal(signal)
    print("✅ Intelligence:", intelligence)

    # STEP 5: FINAL OUTPUT
    print("📡 Sent to State Engine:", intelligence)

    return intelligence


# -------------------------------
# TEST LIVE FLOW (FINAL - 5 CASES)
# -------------------------------
if __name__ == "__main__":

    events = [

        # CASE 1: HIGH CONFIDENCE → LOW RISK
        {
            "trace_id": "T1",
            "vessel_type": "cargo",
            "confidence_score": 0.8,
            "dominant_freq_hz": 120,
            "anomaly_flag": False
        },

        # CASE 2: LOW CONFIDENCE → HIGH RISK
        {
            "trace_id": "T2",
            "vessel_type": "cargo",
            "confidence_score": 0.4,
            "dominant_freq_hz": 90,
            "anomaly_flag": False
        },

        # CASE 3: ANOMALY → CRITICAL
        {
            "trace_id": "T3",
            "vessel_type": "unknown",
            "confidence_score": 0.9,
            "dominant_freq_hz": 200,
            "anomaly_flag": True
        },

        # CASE 4: MEDIUM CASE (SPEEDBOAT)
        {
            "trace_id": "T4",
            "vessel_type": "speedboat",
            "confidence_score": 0.6,
            "dominant_freq_hz": 150,
            "anomaly_flag": False
        },

        # CASE 5: VERY LOW CONFIDENCE → CRITICAL
        {
            "trace_id": "T5",
            "vessel_type": "submarine",
            "confidence_score": 0.2,
            "dominant_freq_hz": 220,
            "anomaly_flag": False
        }
    ]

    for e in events:
        process_perception_event(e)