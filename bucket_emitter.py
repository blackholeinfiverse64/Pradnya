import json
from datetime import datetime

BUCKET_FILE = "bucket_artifacts.jsonl"


def emit_bucket_artifact(data):
    """
    Standardized bucket logger

    Required format:
    {
        trace_id,
        input,
        output,
        timestamp,
        layer
    }
    """

    try:
        # -----------------------------------
        # EXTRACT DATA SAFELY
        # -----------------------------------
        trace_id = data.get("trace_id")

        input_data = data.get("input", {})
        output_data = data.get("output", {})

        # fallback (if someone passes flat structure)
        if not input_data and not output_data:
            output_data = data

        # -----------------------------------
        # FINAL ARTIFACT (TASK COMPLIANT)
        # -----------------------------------
        artifact = {
            "trace_id": trace_id,
            "input": input_data,
            "output": output_data,
            "timestamp": datetime.utcnow().isoformat(),
            "layer": data.get("layer", "NICAI_PIPELINE")
        }

        # -----------------------------------
        # WRITE TO FILE
        # -----------------------------------
        with open(BUCKET_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(artifact) + "\n")

    except Exception as e:
        print("❌ Bucket emission failed:", e)