from validator import validate_signal
from sanskar_simple import analyze_signal   # ✅ correct import

# -------------------------------
# STEP 0 — REAL PERCEPTION EVENT
# -------------------------------
event = {
    "trace_id": "9d6dc7d6-d915-4738-a3bf-f20c78f6780b",
    "vessel_type": "cargo",
    "confidence_score": 0.6396,
    "dominant_freq_hz": 98.0,
    "anomaly_flag": False
}

print("\n📥 Perception Event:", event)

# -------------------------------
# STEP 1 — CONVERT TO NICAI SIGNAL
# -------------------------------
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

    # ✅ REQUIRED for validation
    "latitude": 0.0,
    "longitude": 0.0
}

print("✅ NICAI Signal:", signal)

# -------------------------------
# STEP 2 — VALIDATION
# -------------------------------
validation = validate_signal(signal)
print("✅ Validation:", validation)

# ❌ STOP if REJECT (TASK RULE)
if validation["status"] == "REJECT":
    print("❌ Signal rejected. Stopping pipeline.")
    exit()

# -------------------------------
# STEP 3 — INTELLIGENCE
# -------------------------------
intelligence = analyze_signal(signal)

# ✅ ADD validation_status (NEW TASK REQUIREMENT)
intelligence["validation_status"] = validation["status"]

print("✅ Intelligence:", intelligence)

# -------------------------------
# FINAL OUTPUT
# -------------------------------
print("📡 Sent to State Engine:", intelligence)