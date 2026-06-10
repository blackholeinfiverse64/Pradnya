from validator import validate_signal

def validate_svacs_signal(signal: dict):
    try:
        if not isinstance(signal, dict) or not signal:
            return {"status": "ERROR", "reason": "Invalid signal"}

        # extra check (confidence 0–1)
        value = signal.get("value")
        if value is None or not (0 <= value <= 1):
            return {"status": "ERROR", "reason": "Invalid confidence score"}

        return validate_signal(signal)

    except Exception as e:
        return {"status": "ERROR", "reason": str(e)}