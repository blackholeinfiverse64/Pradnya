from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

from validator import validate_signal
from sanskar_engine import analyze_signal

app = FastAPI()


# -----------------------------
# Input Schema
# -----------------------------
class PerceptionEvent(BaseModel):
    trace_id: str
    vessel_type: str
    confidence_score: float
    dominant_freq_hz: float
    anomaly_flag: bool


# -----------------------------
# NICAI Signal Builder
# -----------------------------
def build_signal(event: PerceptionEvent) -> Dict[str, Any]:
    return {
        "trace_id": event.trace_id,
        "signal_id": event.trace_id,
        "timestamp": "LIVE",
        "value": event.confidence_score,
        "asset_id": event.vessel_type,
        "feature_type": "acoustic",
        "dataset_id": "svacs",
        "signal_type": "acoustic_detection",
        "source": "svacs",
        "metadata": {
            "dominant_freq_hz": event.dominant_freq_hz,
            "anomaly_flag": event.anomaly_flag
        },
        "state": "live",
        "latitude": 0.0,
        "longitude": 0.0
    }


# -----------------------------
# MAIN ENDPOINT
# -----------------------------
@app.post("/nicai/classify")
def classify(event: PerceptionEvent):

    # Step 1: Build signal
    signal = build_signal(event)

    # Step 2: Validate
    validation_result = validate_signal(signal)

    # Step 3: Intelligence
    intelligence = analyze_signal(signal)

    # 🔥 CRITICAL FIX 1: force trace_id
    intelligence["trace_id"] = signal["trace_id"]

    # 🔥 CRITICAL FIX 2: validation propagation
    intelligence["validation_status"] = validation_result["status"]

    # 🔥 SAFETY CHECK (optional but strong)
    if intelligence["trace_id"] is None:
        raise ValueError("trace_id missing in intelligence_event")

    return {
        "trace_id": signal["trace_id"],   # use signal not event
        "perception_event": event.dict(),
        "nicai_signal": signal,
        "validation": validation_result,
        "intelligence_event": intelligence
    }


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/")
def home():
    return {"message": "NICAI API is running 🚀"}