from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime, timezone
import json
import html
import os
import traceback

from validator import validate_signal
from samachar_input_adapter import load_data, convert_to_signals
from sanskar_engine import analyze_signal, analyze_patterns
from error_handler import error_response

app = FastAPI()
os.makedirs("logs", exist_ok=True)


# -------------------------------
# SAFE STRING
# -------------------------------
def safe(v):
    try:
        return html.escape(str(v))
    except:
        return "N/A"


# -------------------------------
# SAFE FLOAT
# -------------------------------
def to_float(v):
    try:
        return float(v)
    except:
        return 0.0


# -------------------------------
# LOGGING
# -------------------------------
def log_data(filename, log_type, data):
    try:
        with open(f"logs/{filename}", "a") as f:
            f.write(json.dumps({
                "trace_id": str(data.get("trace_id", "N/A")),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": log_type,
                "data": data
            }, default=str) + "\n")
    except:
        pass


# -------------------------------
# ZONE DETECTION
# -------------------------------
def detect_zone(lat):
    try:
        lat = float(lat)
        if lat > 23:
            return "North"
        elif lat > 20:
            return "Central"
        else:
            return "South"
    except:
        return "Unknown"


# -------------------------------
# ACTION ROUTER (TANTRA SAFE)
# -------------------------------
@app.post("/action")
def action_router(data: dict):
    try:
        if not isinstance(data, dict):
            return error_response("Invalid input")

        risk = str(data.get("risk_level", "LOW"))

        if risk == "HIGH":
            target_role = "authority"
        elif risk == "MEDIUM":
            target_role = "operator"
        else:
            target_role = "system"

        action_payload = {
            "trace_id": str(data.get("trace_id")),
            "action_type": str(data.get("action_type")),  # already compliant
            "target_role": target_role,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": {}
        }

        log_data("action_logs.json", "ACTION", action_payload)

        return {"status": "SUCCESS", "action": action_payload}

    except Exception as e:
        return error_response(str(e))


# -------------------------------
# DASHBOARD
# -------------------------------
@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():

    print("🔥 FINAL DASHBOARD RUNNING")

    try:
        weather, aqi = load_data()
        signals = convert_to_signals(weather, aqi)

        if not isinstance(signals, list) or not signals:
            return HTMLResponse("<h3>No data</h3>")

        rows = ""
        processed_outputs = []

        for signal in signals[:20]:

            if not isinstance(signal, dict):
                continue

            # ✅ VALIDATION (FIXED)
            validation = validate_signal(signal)
            if validation.get("status") == "REJECT":
                continue

            # ANALYSIS
            analysis = analyze_signal(signal)
            if not isinstance(analysis, dict):
                continue

            lat = to_float(signal.get("latitude"))
            zone = detect_zone(lat)
            risk = str(analysis.get("risk_level", "LOW"))

            # ✅ TANTRA-COMPLIANT ACTIONS
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

            trace_id = str(validation.get("trace_id"))

            processed_outputs.append({
                "signal_id": str(signal.get("signal_id")),
                "trace_id": trace_id,
                "risk_level": risk,
                "latitude": lat,
                "longitude": to_float(signal.get("longitude")),
                "anomaly_score": float(analysis.get("anomaly_score", 0))
            })

            log_data("validation_logs.json", "VALIDATION", validation)
            log_data("anomaly_logs.json", "ANALYSIS", analysis)

            rows += f"""
            <tr style="background-color:{row_color};">
                <td>{safe(signal.get("signal_id"))}</td>
                <td>{safe(zone)}</td>
                <td>{safe(validation.get("status"))}</td>
                <td>{safe(risk)}</td>
                <td>{safe(analysis.get("anomaly_type"))}</td>
                <td>{safe(analysis.get("explanation"))}</td>
                <td>{safe(step)}</td>
                <td>
                    <button onclick="sendAction('{trace_id}','{action_type}','{risk}')">
                        {action_label}
                    </button>
                </td>
            </tr>
            """

        # PATTERN
        try:
            pattern = analyze_patterns(processed_outputs)
        except Exception as e:
            pattern = {"error": str(e)}

        log_data("pattern_logs.json", "PATTERN", pattern)

        total_signals = len(signals)
        total_anomalies = len([o for o in processed_outputs if o["risk_level"] != "LOW"])

        try:
            with open("logs/action_logs.json") as f:
                action_count = len(f.readlines())
        except:
            action_count = 0

        html_content = f"""
        <html>
        <head>
            <title>NICAI Dashboard</title>

            <script>
            async function sendAction(trace_id, action_type, risk) {{
                await fetch("/action", {{
                    method: "POST",
                    headers: {{"Content-Type": "application/json"}},
                    body: JSON.stringify({{
                        trace_id: trace_id,
                        action_type: action_type,
                        risk_level: risk
                    }})
                }});
                alert("Action logged");
                location.reload();
            }}
            </script>

        </head>

        <body>

        <h2>NICAI Dashboard</h2>

        <p>Total Signals: {total_signals}</p>
        <p>Total Anomalies: {total_anomalies}</p>
        <p>Actions Logged: {action_count}</p>

        <table border="1" cellpadding="5">
        <tr>
            <th>ID</th>
            <th>Zone</th>
            <th>Status</th>
            <th>Risk</th>
            <th>Type</th>
            <th>Explanation</th>
            <th>Recommended Step</th>
            <th>Action</th>
        </tr>

        {rows}

        </table>

        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except Exception as e:
        print(traceback.format_exc())
        return HTMLResponse(f"<h3>Error: {str(e)}</h3>")