from validator import validate_signal
from analytics_engine import analyze_signal
from samachar_input_adapter import load_data, convert_to_signals
from multi_signal_analyzer import analyze_patterns


# STEP 1: Load data
weather, aqi = load_data()
print("✅ Data Loaded Successfully")

# STEP 2: Convert into signals
signals = convert_to_signals(weather, aqi)
print("✅ Total Signals Created:", len(signals))


# STEP 3: Process all signals
final_outputs = []

for signal in signals[:10]:   # demo ke liye first 10 signals

    print("\nPROCESSING SIGNAL:", signal["signal_id"])

    # VALIDATION
    validation = validate_signal(signal)
    print("VALIDATION:", validation)

    if validation["status"] != "REJECT":

        # ANALYSIS
        analysis = analyze_signal(signal)
        print("ANALYSIS:", analysis)

        # FINAL OUTPUT (NO DECISION LOGIC)
        output = {
            "signal_id": signal["signal_id"],
            "status": validation["status"],
            "confidence_score": validation.get("confidence_score", 0.9),
            "trace_id": validation.get("trace_id"),
            "anomaly_score": analysis.get("anomaly_score"),
            "risk_level": analysis.get("risk_level"),
            "anomaly_type": analysis.get("anomaly_type"),
            "explanation": analysis.get("explanation"),
            "recommendation_signal": analysis.get("recommendation_signal")
        }

        print("FINAL OUTPUT:", output)
        final_outputs.append(output)

    else:
        print("❌ SIGNAL REJECTED")


# STEP 4: MULTI-SIGNAL INTELLIGENCE (Phase 3)
print("\n🔍 MULTI-SIGNAL ANALYSIS")

pattern_result = analyze_patterns(final_outputs)

print("PATTERN OUTPUT:", pattern_result)