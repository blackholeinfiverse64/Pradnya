import json
from datetime import datetime


def emit_telemetry(signal, result):
    """
    Emit telemetry data for InsightFlow observability
    """

    telemetry_record = {
        "trace_id": result["trace_id"],
        "dataset_id": signal.get("dataset_id"),
        "status": result["status"],
        "confidence_score": result["confidence_score"],
        "timestamp": datetime.utcnow().isoformat()
    }

    # Append telemetry log
    with open("telemetry_metrics.json", "a") as f:
        json.dump(telemetry_record, f)
        f.write("\n")