# NICAI – TESTING PACKET (FINAL)

Project: NICAI – Networked Intelligence & Context Analysis Interface  
Developer: Ankita Prajapati  
Testing Authority: Vinayak Tiwari  
Testing Protocol: BHIV Universal Testing Protocol  

---

## 1. SYSTEM OVERVIEW

NICAI is a **deterministic intelligence system** that processes real-world datasets and produces structured anomaly intelligence outputs.

NICAI does NOT execute decisions.  
It only generates:

- interpretable intelligence  
- anomaly insights  
- structured action signals  

Pipeline:

```
Data → Signal Conversion → Validation → Intelligence → Pattern Detection → Dashboard → Action Logging
```

---

## 2. REAL DATA INGESTION

NICAI uses real-world datasets:

```
data/clean_weather.csv  
data/clean_aqi.csv
```

### Weather Dataset
Fields:
```
timestamp, temperature, latitude, longitude
```

### AQI Dataset
Fields:
```
timestamp, aqi, pm25, location
```

These datasets simulate environmental anomaly scenarios.

---

## 3. SIGNAL GENERATION

Data is converted into standardized NICAI signals using:

```
samachar_input_adapter.py
```

Example signal:

```json
{
  "signal_id": "W_2",
  "timestamp": "2026-04-14T04:21:32",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "value": 48.7,
  "dataset_id": "weather"
}
```

---

## 4. TRACEABILITY

Each signal receives a deterministic `trace_id`.

Generation:
```
trace_id = SHA256(signal_id + timestamp)
```

Trace flow:
```
Validation → Analysis → Pattern → Dashboard → Action Logs
```

This ensures **end-to-end traceability**.

---

## 5. VALIDATION LAYER TESTING

File:
```
validator.py
```

### Test Cases

| Case | Input | Expected Output |
|------|------|----------------|
| Missing field | No timestamp | ERROR response |
| Invalid dataset | Unknown dataset_id | ERROR response |
| Wrong type | value = string | ERROR response |
| Valid signal | Proper data | VALID / FLAG |

### Expected Error Format

```json
{
  "status": "ERROR",
  "reason": "Missing field: timestamp",
  "trace_id": "..."
}
```

---

## 6. INTELLIGENCE ENGINE TESTING

File:
```
sanskar_engine.py
```

### Test Cases

| Condition | Expected Result |
|----------|----------------|
| Normal value | LOW risk |
| Elevated value | MEDIUM risk |
| Extreme value | HIGH risk |

Example output:

```json
{
  "risk_level": "HIGH",
  "anomaly_score": 0.9,
  "anomaly_type": "TEMPERATURE_SPIKE",
  "explanation": "Extreme temperature detected",
  "recommendation_signal": "eligible_for_escalation"
}
```

---

## 7. MULTI-SIGNAL PATTERN TESTING

Function:
```
analyze_patterns()
```

### Test Cases

| Scenario | Expected |
|--------|----------|
| No anomalies | NO_PATTERN |
| Few anomalies | STABLE pattern |
| Cluster anomalies | REPEATED_ANOMALY |

Example:

```json
{
  "pattern_id": "PATTERN_xxx",
  "anomaly_count": 3,
  "affected_zones": ["North"],
  "pattern_type": "REPEATED_ANOMALY",
  "severity_trend": "STABLE"
}
```

---

## 8. DASHBOARD TESTING

Start server:

```
uvicorn main:app --reload
```

Open:

```
http://127.0.0.1:8000/dashboard
```

### Validate:

- No crashes  
- Data visible  
- Buttons working  
- Safe fallback on failure  

### Failure Case:

If API fails:
```
No data / invalid input
```

---

## 9. ACTION ROUTING TEST

Endpoint:

```
POST /action
```

### Request:

```json
{
  "trace_id": "...",
  "action_type": "eligible_for_escalation"
}
```

### Expected Response:

```json
{
  "status": "SUCCESS",
  "action": {...}
}
```

### Verify:

```
logs/action_logs.json
```

---

## 10. LOGGING VALIDATION

Log files:

```
logs/validation_logs.json  
logs/anomaly_logs.json  
logs/pattern_logs.json  
logs/action_logs.json
```

Each log entry MUST contain:

```json
{
  "trace_id": "...",
  "timestamp": "...",
  "type": "...",
  "data": {...}
}
```

---

## 11. FAILURE HANDLING TEST

### Test Scenarios

| Case | Expected |
|------|---------|
| Empty input | ERROR |
| Invalid JSON | ERROR |
| Missing fields | ERROR |
| Wrong type | ERROR |

System MUST:

- NEVER crash  
- ALWAYS return structured error  

---

## 12. INPUT GATE TEST

Before validation:

| Case | Expected |
|------|---------|
| Non-dict input | ERROR |
| Empty input | ERROR |
| Missing keys | ERROR |

---

## 13. DEMO FLOW VALIDATION

Run:

```
python run_demo_full.py
```

### Expected Flow:

1. Dataset load  
2. Signal conversion  
3. Validation  
4. Intelligence output  
5. Pattern detection  
6. Dashboard launch  
7. Action trigger  
8. Log verification  

---

## 14. SUCCESS CRITERIA

System passes testing if:

- No crashes  
- All errors structured  
- Dashboard stable  
- Actions logged  
- Patterns detected  
- Trace IDs consistent  
- Logs properly formatted  

---

## 15. FINAL STATUS

NICAI is:

- Deterministic  
- Traceable  
- Failure-safe  
- Demo-ready  
- TANTRA-aligned  

---

## CONCLUSION

The NICAI system has been validated under:

**BHIV Universal Testing Protocol**

It is now a:

→ Stable  
→ Controlled  
→ Demo-safe intelligence system  

Ready for final demonstration and evaluation.