import json
import os

DATASET_FILE = "datasets.json"


# -------------------------------
# LOAD DATASETS (SAFE + CACHED)
# -------------------------------
_DATASET_CACHE = None

def load_datasets():
    global _DATASET_CACHE

    if _DATASET_CACHE is not None:
        return _DATASET_CACHE

    try:
        if not os.path.exists(DATASET_FILE):
            print("❌ datasets.json not found")
            _DATASET_CACHE = []
            return _DATASET_CACHE

        with open(DATASET_FILE, "r") as f:
            data = json.load(f)

            if not isinstance(data, list):
                print("❌ datasets.json must be a list")
                _DATASET_CACHE = []
                return _DATASET_CACHE

            # filter only valid dicts
            _DATASET_CACHE = [
                d for d in data if isinstance(d, dict)
            ]

            return _DATASET_CACHE

    except json.JSONDecodeError:
        print("❌ Invalid JSON in datasets.json")
        _DATASET_CACHE = []
        return _DATASET_CACHE

    except Exception as e:
        print(f"❌ Error loading datasets: {e}")
        _DATASET_CACHE = []
        return _DATASET_CACHE


# -------------------------------
# GET DATASET BY ID
# -------------------------------
def get_dataset(dataset_id):

    try:
        if not dataset_id:
            return None

        datasets = load_datasets()

        for dataset in datasets:
            if dataset.get("dataset_id") == dataset_id:
                return dataset

        return None

    except Exception:
        return None


# -------------------------------
# OPTIONAL: GET TRUST SCORE
# -------------------------------
def get_trust_score(dataset_id):
    dataset = get_dataset(dataset_id)

    if dataset:
        return dataset.get("trust_score", 0.5)

    return 0.0


# -------------------------------
# OPTIONAL: CHECK ACTIVE
# -------------------------------
def is_dataset_active(dataset_id):
    dataset = get_dataset(dataset_id)

    if dataset:
        return dataset.get("status") == "active"

    return False