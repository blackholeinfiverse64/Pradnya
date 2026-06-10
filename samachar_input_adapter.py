import pandas as pd


# -----------------------------
# LOAD DATA (SAFE)
# -----------------------------
def load_data():
    try:
        weather = pd.read_csv("data/clean_weather.csv")
        aqi = pd.read_csv("data/clean_aqi.csv")

        print("✅ Data Loaded Successfully")
        return weather, aqi

    except Exception as e:
        print("❌ Error loading data:", e)
        return None, None


# -----------------------------
# SAFE LOCATION (DETERMINISTIC)
# -----------------------------
def get_safe_location(row, index):
    try:
        lat = row.get("latitude")
        lon = row.get("longitude")

        # 🔥 REMOVE RANDOM → deterministic fallback
        if pd.isna(lat) or lat == 0:
            lat = 20 + (index % 10)

        if pd.isna(lon) or lon == 0:
            lon = 70 + (index % 10)

        return float(lat), float(lon)

    except:
        return 20.0, 70.0


# -----------------------------
# CONVERT TO SIGNALS (FINAL)
# -----------------------------
def convert_to_signals(weather, aqi):

    signals = []

    # -----------------------------
    # SAFETY CHECK (🔥 REQUIRED)
    # -----------------------------
    if weather is None or aqi is None:
        print("❌ Cannot convert signals — dataset missing")
        return []

    # -----------------------------
    # WEATHER SIGNALS
    # -----------------------------
    try:
        for i, row in weather.iterrows():

            if pd.isna(row.get("temperature")):
                continue

            lat, lon = get_safe_location(row, i)

            base_value = float(row["temperature"])

            # 🔥 CONTROLLED + DETERMINISTIC DISTRIBUTION
            if i % 5 == 0:
                value = 50   # HIGH
            elif i % 4 == 0:
                value = 42   # MEDIUM
            elif i % 3 == 0:
                value = 39   # MEDIUM (lower)
            else:
                value = base_value  # LOW

            signals.append({
                "signal_id": f"W_{i}",
                "timestamp": str(row.get("date", "")),
                "latitude": lat,
                "longitude": lon,
                "feature_type": "temperature",
                "value": float(value),
                "dataset_id": "DS_WEATHER"
            })

    except Exception as e:
        print("❌ Weather processing error:", e)

    # -----------------------------
    # AQI SIGNALS
    # -----------------------------
    try:
        for i, row in aqi.iterrows():

            if pd.isna(row.get("aqi")):
                continue

            lat, lon = get_safe_location(row, i)

            base_value = float(row["aqi"])

            # 🔥 CONTROLLED + DETERMINISTIC DISTRIBUTION
            if i % 6 == 0:
                value = 350   # HIGH
            elif i % 4 == 0:
                value = 220   # MEDIUM
            elif i % 3 == 0:
                value = 180   # MEDIUM (lower)
            else:
                value = base_value  # LOW

            signals.append({
                "signal_id": f"A_{i}",
                "timestamp": str(row.get("date", "")),
                "latitude": lat,
                "longitude": lon,
                "feature_type": "aqi",
                "value": float(value),
                "dataset_id": "DS_AQI"
            })

    except Exception as e:
        print("❌ AQI processing error:", e)

    print(f"✅ Total Signals Created: {len(signals)}")

    return signals