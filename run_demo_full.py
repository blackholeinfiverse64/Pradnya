"""
NICAI FULL SYSTEM DEMO (FINAL - DEMO SAFE + STABLE)
"""

import json
import os
import traceback   #
from datetime import datetime, timezone

from samachar_input_adapter import load_data, convert_to_signals
from sanskar_engine import analyze_signal
from error_handler import error_response, validate_basic_input


# -----------------------------
# FOLDERS
# -----------------------------
os.makedirs("logs", exist_ok=True)


# -----------------------------
# SAFE FLOAT
# -----------------------------
def to_float(v):
    try:
        return float(v)
    except:
        return 0.0


# -----------------------------
# LOGGING
# -----------------------------
def log_data(filename, log_type, data):
    try:
        log_entry = {
            "trace_id": str(data.get("trace_id", "N/A")),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": log_type,
            "data": data
        }

        with open(f"logs/{filename}", "a") as f:
            f.write(json.dumps(log_entry, default=str) + "\n")

    except:
        pass


# -----------------------------
# DEMO RUNNER
# -----------------------------
def run_demo():

    print("\n==============================")
    print(" NICAI FULL SYSTEM DEMO START ")
    print("==============================\n")

    try:
        # -----------------------------
        # STEP 1 — LOAD DATA
        # -----------------------------
        print("STEP 1 — Loading datasets...\n")

        weather, aqi = load_data()
        print("✅ Datasets loaded successfully\n")

        # -----------------------------
        # STEP 2 — CONVERT SIGNALS
        # -----------------------------
        print("STEP 2 — Converting to signals...\n")

        signals = convert_to_signals(weather, aqi)

        error = validate_basic_input(signals)
        if error:
            print(json.dumps(error, indent=2))
            return

        print(f"✅ Total signals: {len(signals)}\n")

        # -----------------------------
        # STEP 3 — PROCESSING
        # -----------------------------
        print("------------------------------------")
        print("STEP 3 — Running Intelligence")
        print("------------------------------------\n")

        processed_outputs = []

        low = medium = high = 0

        for signal in signals[:20]:

            if not isinstance(signal, dict):
                continue

            trace_id = f"TRACE_{signal.get('signal_id')}"

            validation = {
                "status": "VALID",
                "trace_id": trace_id,
                "confidence_score": 0.9
            }

            log_data("validation_logs.json", "VALIDATION", validation)

            # -----------------------------
            # ANALYSIS
            # -----------------------------
            analysis = analyze_signal(signal)

            print("\nDEBUG SIGNAL:")
            print(signal)

            print("\nDEBUG ANALYSIS:")
            print(analysis)

            if not isinstance(analysis, dict):
                continue

            risk = str(analysis.get("risk_level", "LOW"))

            lat = to_float(signal.get("latitude"))
            lon = to_float(signal.get("longitude"))

            output = {
                "signal_id": str(signal.get("signal_id")),
                "trace_id": str(trace_id),
                "risk_level": risk,
                "anomaly_score": float(analysis.get("anomaly_score", 0)),
                "anomaly_type": str(analysis.get("anomaly_type")),
                "recommendation_signal": str(analysis.get("recommendation_signal")),
                "latitude": lat,
                "longitude": lon
            }

            processed_outputs.append(output)

            if risk == "LOW":
                low += 1
            elif risk == "MEDIUM":
                medium += 1
            elif risk == "HIGH":
                high += 1

            log_data("anomaly_logs.json", "ANALYSIS", output)

        print("✅ Processing complete\n")

        # -----------------------------
        # SUMMARY
        # -----------------------------
        print("📊 SUMMARY:")
        print(f"LOW: {low}")
        print(f"MEDIUM: {medium}")
        print(f"HIGH: {high}\n")

        # -----------------------------
        # STEP 4 — PATTERN
        # -----------------------------
        print("------------------------------------")
        print("STEP 4 — Pattern Detection")
        print("------------------------------------\n")

        try:
            pattern_output = analyze_patterns(processed_outputs)
        except Exception as e:
            pattern_output = error_response(str(e))

        print("PATTERN:", pattern_output)

        log_data("pattern_logs.json", "PATTERN", pattern_output)

        # -----------------------------
        # STEP 5 — DASHBOARD
        # -----------------------------
        print("\n------------------------------------")
        print("STEP 5 — Starting Dashboard")
        print("------------------------------------\n")

        print("🚀 Launching API server...")

        os.system("uvicorn main:app --reload")

    # ✅ FIX: correct placement of except
    except Exception as e:
        traceback.print_exc()
        print(json.dumps(error_response(str(e)), indent=2))


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    run_demo()
