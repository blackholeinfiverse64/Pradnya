import requests
from validator import validate_signal
from sanskar_simple import analyze_signal


# -----------------------------------
# FETCH REAL EVENTS FROM NUPUR SERVER
# -----------------------------------
def fetch_events():
    url = "http://localhost:8000/perception_log"
    response = requests.get(url)
    data = response.json()
    return data.get("events", [])


# -----------------------------------
# PROCESS EACH EVENT THROUGH PIPELINE
# -----------------------------------
def process_event(event):

    print("\n-------------------------------")
    print("📥 Perception Event:", event)

    # STEP 1: Convert to NICAI signal
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
            "anomaly_flag": event.get("anomaly_flag")
        },
        "state": "live",
        "latitude": 0.0,
        "longitude": 0.0
    }

    print("✅ NICAI Signal:", signal)

    # STEP 2: Validation
    validation = validate_signal(signal)
    print("✅ Validation:", validation)

    # STEP 3: Intelligence
    intelligence = analyze_signal(signal)

    # ✅ FIX 1: Force trace_id propagation (MOST IMPORTANT)
    intelligence["trace_id"] = signal["trace_id"]

    # ✅ FIX 2: Add validation status (already correct)
    intelligence["validation_status"] = validation.get("status")

    print("✅ Intelligence:", intelligence)

    return {
        "event": event,
        "validation": validation,
        "intelligence": intelligence
    }


# -----------------------------------
# MAIN EXECUTION
# -----------------------------------
if __name__ == "__main__":

    events = fetch_events()

    results = []

    for event in events:
        result = process_event(event)
        results.append(result)

    print("\n🔥 TOTAL EVENTS PROCESSED:", len(results))