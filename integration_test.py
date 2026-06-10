from validator import get_validated_signals

signals = [

{
 "signal_id": "SIG910",
 "timestamp": "2026-03-10T10:00:00Z",
 "latitude": 19.07,
 "longitude": 72.87,
 "feature_type": "weather",
 "value": 34,
 "dataset_id": "DS01"
},

{
 "signal_id": "SIG911",
 "timestamp": "2026-03-10T10:05:00Z",
 "latitude": 18.52,
 "longitude": 73.85,
 "feature_type": "vessel",
 "value": 120,
 "dataset_id": "DS02"
},

{
 "signal_id": "SIG912"
}

]

result = get_validated_signals(signals)

print("Signals Sent To Sanskar:")
print(result)

from validator import validate_signal

print("\nINVALID INPUT TEST")

malformed_signal = {
    "timestamp": "2026-03-10T10:00:00Z"
}

print(validate_signal(malformed_signal))