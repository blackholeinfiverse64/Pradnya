from validator import validate_signal, validate_batch

# 1️⃣ Valid Signal Test (should return ALLOW)

valid_signal = {
    "signal_id": "SIG100",
    "timestamp": "2026-03-10T10:00:00Z",
    "latitude": 19.07,
    "longitude": 72.87,
    "feature_type": "weather",
    "value": 34,
    "dataset_id": "DS01"
}

print("VALID SIGNAL TEST")
print(validate_signal(valid_signal))


# 2️⃣ FLAG Signal Test (inactive dataset)

flag_signal = {
    "signal_id": "SIG101",
    "timestamp": "2026-03-10T10:05:00Z",
    "latitude": 18.52,
    "longitude": 73.85,
    "feature_type": "vessel",
    "value": 120,
    "dataset_id": "DS02"
}

print("\nFLAG SIGNAL TEST")
print(validate_signal(flag_signal))


# 3️⃣ REJECT Signal Test (missing field)

reject_signal = {
    "signal_id": "SIG102",
    "timestamp": "2026-03-10T10:10:00Z",
    "latitude": 19.07,
    "feature_type": "weather",
    "value": 40,
    "dataset_id": "DS01"
}

print("\nREJECT SIGNAL TEST")
print(validate_signal(reject_signal))


# 4️⃣ Batch Test

batch_signals = [
    valid_signal,
    flag_signal,
    reject_signal
]

print("\nBATCH TEST")
print(validate_batch(batch_signals))


# 5️⃣ Malformed Input Test

malformed_signal = {}

print("\nMALFORMED INPUT TEST")
print(validate_signal(malformed_signal))