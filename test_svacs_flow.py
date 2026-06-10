from svacs_adapter import prepare_signal
from validator import validate_signal
from sanskar_simple import analyze_svacs


# -------------------------------
# SAMPLE EVENT (SVACS INPUT)
# -------------------------------
event = {
    "event_id": "E1",
    "timestamp": "2026-04-20T10:00:00",
    "vessel": {
        "type": "cargo",
        "confidence_score": 0.8
    },
    "metadata": {}
}


# -------------------------------
# STEP 1: ADAPTER
# -------------------------------
adapter_output = prepare_signal(event)

if adapter_output.get("status") != "SUCCESS":
    print("❌ Adapter Failed:", adapter_output)
    exit()

signal = adapter_output.get("signal")
trace_id = signal.get("trace_id")

print("✅ Signal:", signal)


# -------------------------------
# STEP 2: VALIDATION (NICAI)
# -------------------------------
validation = validate_signal(signal)
print("✅ Validation:", validation)

if validation.get("status") == "ERROR":
    print("❌ Validation Failed — Not sending to Sanskar")
    exit()


# -------------------------------
# STEP 3: SANSKAR (INTELLIGENCE)
# -------------------------------
intelligence = analyze_svacs(signal, trace_id)
print("✅ Intelligence:", intelligence)


# -------------------------------
# STEP 4: STATE ENGINE (SIMULATION)
# -------------------------------
print("📡 Sent to State Engine:", intelligence)