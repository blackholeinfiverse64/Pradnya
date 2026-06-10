import requests
import time

# ✅ Correct URL (Raj ka latest)
URL = "https://7765-157-119-200-153.ngrok-free.app/ingest/intelligence"

headers = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true"
}

# ✅ FINAL 5 EVENTS (NUPUR TRACE IDs - DO NOT CHANGE)
events = [

    # 1. Cargo
    {
        "trace_id": "25d3f7c3-ba2a-4bc9-af02-dc3446b03189",
        "vessel_type": "cargo",
        "confidence": 0.6396,
        "risk_level": "MEDIUM",
        "anomaly_flag": False,
        "explanation": "Moderate confidence acoustic detection — medium risk",
        "validation_status": "ALLOW"
    },

    # 2. Speedboat
    {
        "trace_id": "756f9f06-f904-4315-99f1-5506f98c8868",
        "vessel_type": "speedboat",
        "confidence": 0.3922,
        "risk_level": "HIGH",
        "anomaly_flag": False,
        "explanation": "Low confidence acoustic detection — high risk",
        "validation_status": "ALLOW"
    },

    # 3. Submarine
    {
        "trace_id": "2466c4aa-fefe-433b-b97b-d39dd99f0568",
        "vessel_type": "submarine",
        "confidence": 0.1734,
        "risk_level": "CRITICAL",
        "anomaly_flag": True,
        "explanation": "Anomalous acoustic pattern detected",
        "validation_status": "ALLOW"
    },

    # 4. Low Confidence
    {
        "trace_id": "fb381325-4292-4483-b66a-b55aa37a2fd2",
        "vessel_type": "unknown",
        "confidence": 0.20,
        "risk_level": "HIGH",
        "anomaly_flag": False,
        "explanation": "Low confidence detection",
        "validation_status": "ALLOW"
    },

    # 5. Anomaly
    {
        "trace_id": "193f1e6c-d403-4bff-bbe4-9d4a7183d2ac",
        "vessel_type": "unknown",
        "confidence": 0.02,
        "risk_level": "CRITICAL",
        "anomaly_flag": True,
        "explanation": "Anomalous acoustic pattern detected",
        "validation_status": "ALLOW"
    }
]

print("🚀 STARTING FINAL END-TO-END TEST...")

# 👉 Loop to send all events
for i, event in enumerate(events, start=1):
    print(f"\n🚀 Sending Event {i}: {event['trace_id']}")

    try:
        # ✅ FIXED: use URL (not url)
        response = requests.post(URL, json=event, headers=headers)

        print("Status Code:", response.status_code)

        try:
            print("Response:", response.json())
        except:
            print("Raw Response:", response.text)

    except Exception as e:
        print("❌ Error:", e)


    time.sleep(1)

print("\n✅ ALL EVENTS SENT SUCCESSFULLY")