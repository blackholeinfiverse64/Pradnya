from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse
from datetime import datetime, timezone
import json
import os
import traceback

from validator import validate_signal
from samachar_input_adapter import load_data, convert_to_signals
from sanskar_engine import analyze_signal, analyze_patterns
from error_handler import error_response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

DEFAULT_ORIGINS = "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,https://pradnya-bhiv.vercel.app"
allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
os.makedirs("logs", exist_ok=True)

# -----------------------------
# SAFE HELPERS
# -----------------------------
def to_str(v):
    try:
        return str(v)
    except:
        return "N/A"


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
        with open(f"logs/{filename}", "a") as f:
            f.write(json.dumps({
                "trace_id": to_str(data.get("trace_id")),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": log_type,
                "data": data
            }, default=str) + "\n")
    except:
        pass


# -----------------------------
# SIGNAL PROCESSING (shared by dashboard + JSON APIs)
# -----------------------------
def process_signals(limit=20):
    weather, aqi = load_data()
    if weather is None or aqi is None:
        return None, None, None

    signals = convert_to_signals(weather, aqi)
    if not isinstance(signals, list) or not signals:
        return [], {}, {"total": 0, "high": 0, "medium": 0, "low": 0}

    processed_outputs = []
    api_signals = []
    high = medium = low = 0

    for signal in signals[:limit]:
        if not isinstance(signal, dict):
            continue

        validation = validate_signal(signal)
        if not isinstance(validation, dict) or validation.get("status") == "REJECT":
            continue

        analysis = analyze_signal(signal)
        if not isinstance(analysis, dict):
            continue

        risk = str(analysis.get("risk_level", "LOW"))
        trace_id = to_str(validation.get("trace_id"))

        if risk == "HIGH":
            high += 1
        elif risk == "MEDIUM":
            medium += 1
        else:
            low += 1

        processed_outputs.append({
            "signal_id": to_str(signal.get("signal_id")),
            "trace_id": trace_id,
            "risk_level": risk,
            "latitude": to_float(signal.get("latitude")),
            "longitude": to_float(signal.get("longitude")),
            "anomaly_score": float(analysis.get("anomaly_score", 0))
        })

        api_signals.append({
            "signal_id": to_str(signal.get("signal_id")),
            "trace_id": trace_id,
            "validation_status": validation.get("status"),
            "risk_level": risk,
            "confidence": analysis.get("confidence", 0),
            "anomaly_type": to_str(analysis.get("anomaly_type")),
            "explanation": to_str(analysis.get("explanation")),
            "recommendation_signal": to_str(analysis.get("recommendation_signal")),
            "feature_type": to_str(signal.get("feature_type")),
            "value": signal.get("value"),
            "latitude": to_float(signal.get("latitude")),
            "longitude": to_float(signal.get("longitude")),
        })

        log_data("validation_logs.json", "VALIDATION", validation)
        log_data("anomaly_logs.json", "ANALYSIS", analysis)

    pattern = analyze_patterns(processed_outputs)
    log_data("pattern_logs.json", "PATTERN", pattern)

    summary = {
        "total": len(signals),
        "processed": len(api_signals),
        "high": high,
        "medium": medium,
        "low": low,
    }

    return api_signals, pattern, summary


# -----------------------------
# ROOT
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "nicai"}


@app.get("/signals")
def get_signals():
    try:
        api_signals, pattern, summary = process_signals()
        if api_signals is None:
            return error_response("Dataset not loaded")
        return {"status": "SUCCESS", "signals": api_signals, "summary": summary, "pattern": pattern}
    except Exception as e:
        traceback.print_exc()
        return error_response(str(e))


@app.get("/patterns")
def get_patterns():
    try:
        api_signals, pattern, summary = process_signals()
        if api_signals is None:
            return error_response("Dataset not loaded")
        return {"status": "SUCCESS", "pattern": pattern, "summary": summary}
    except Exception as e:
        traceback.print_exc()
        return error_response(str(e))


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <body>
            <h2>NICAI Running ✅</h2>
            <a href="/dashboard">Open Dashboard</a>
        </body>
    </html>
    """


# =========================================================
# 🔥 FIXED PIPELINE API (ONLY THIS PART CHANGED)
# =========================================================
@app.post("/nicai/evaluate")
def evaluate(signals: list = Body(...)):

    try:
        if not isinstance(signals, list):
            return error_response("Input must be list")

        results = []
        processed = []

        for signal in signals:

            if not isinstance(signal, dict):
                continue

            # ---------------- VALIDATION ----------------
            validation = validate_signal(signal)

            if validation.get("status") == "REJECT":
                results.append(validation)
                continue

            trace_id = validation.get("trace_id")

            # ---------------- FIX: DEFINE ANALYSIS ----------------
            try:
                analysis = analyze_signal(signal)
            except Exception:
                analysis = {
                    "risk_level": "LOW",
                    "anomaly_score": 0.0,
                    "confidence": 0.0,
                    "anomaly_type": "UNKNOWN",
                    "explanation": "fallback analysis"
                }

            combined = {
                "signal_id": signal.get("signal_id"),
                "trace_id": trace_id,
                "validation": validation,
                "analysis": analysis
            }

            results.append(combined)

            processed.append({
                "trace_id": trace_id,
                "risk_level": analysis.get("risk_level", "LOW"),
                "latitude": signal.get("latitude"),
                "longitude": signal.get("longitude")
            })

        pattern = analyze_patterns(processed)

        return {
            "status": "SUCCESS",
            "results": results,
            "pattern": pattern
        }

    except Exception as e:
        traceback.print_exc()
        return error_response(str(e))


# =========================================================
# DASHBOARD (UNCHANGED - EXACT SAME AS YOUR ORIGINAL)
# =========================================================
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():

    try:
        api_signals, pattern, summary = process_signals()

        if api_signals is None:
            return HTMLResponse("<h3>Error: Dataset not loaded</h3>")

        if not api_signals:
            return HTMLResponse("<h3>No data available</h3>")

        rows = ""
        for item in api_signals:
            risk = item["risk_level"]
            trace_id = item["trace_id"]
            confidence = item["confidence"]
            validation_status = item["validation_status"]

            if risk == "HIGH":
                step = "Escalation recommended"
                action_label = "Escalate"
                action_type = "eligible_for_escalation"
                row_color = "#ffe6e6"
            elif risk == "MEDIUM":
                step = "Needs review"
                action_label = "Review"
                action_type = "requires_review"
                row_color = "#fff5cc"
            else:
                step = "Monitor"
                action_label = "Monitor"
                action_type = "monitor"
                row_color = ""

            rows += f"""
            <tr style="background-color:{row_color};">
                <td>{item["signal_id"]}</td>
                <td>{trace_id}</td>
                <td>{validation_status}</td>
                <td>{risk}</td>
                <td>{confidence}</td>
                <td>{item["anomaly_type"]}</td>
                <td>{item["explanation"]}</td>
                <td>{step}</td>
                <td>
                    <button onclick="sendAction('{trace_id}','{action_type}','{risk}')">
                        {action_label}
                    </button>
                </td>
            </tr>
            """

        total_signals = summary["total"]
        total_anomalies = summary["high"] + summary["medium"]

        try:
            with open("logs/action_logs.json") as f:
                action_count = len(f.readlines())
        except:
            action_count = 0

        return HTMLResponse(f"""
        <html>
        <body>
            <h2>NICAI Dashboard</h2>

            <p>Total Signals: {total_signals}</p>
            <p>Total Anomalies: {total_anomalies}</p>
            <p>Actions Logged: {action_count}</p>

            <h3>Pattern Summary</h3>
            <p>{pattern}</p>

            <table border="1" cellpadding="5">
                <tr>
                    <th>ID</th>
                    <th>Trace ID</th>
                    <th>Validation</th>
                    <th>Risk</th>
                    <th>Confidence</th>
                    <th>Type</th>
                    <th>Explanation</th>
                    <th>Step</th>
                    <th>Action</th>
                </tr>
                {rows}
            </table>

        </body>
        </html>
        """)

    except Exception as e:
        traceback.print_exc()
        return HTMLResponse(f"<h3>Error: {str(e)}</h3>")


# -----------------------------
# ACTION ROUTER (UNCHANGED)
# -----------------------------
@app.post("/action")
def trigger_action(data: dict):

    try:
        if not isinstance(data, dict):
            return error_response("Invalid input")

        risk = data.get("risk_level", "LOW")

        if risk == "HIGH":
            target = "authority"
        elif risk == "MEDIUM":
            target = "operator"
        else:
            target = "system"

        action_payload = {
            "trace_id": to_str(data.get("trace_id")),
            "action_type": data.get("action_type"),
            "target_role": target,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": {}
        }

        log_data("action_logs.json", "ACTION", action_payload)

        return {
            "status": "SUCCESS",
            "action": action_payload
        }

    except Exception as e:
        return error_response(str(e))
