
import os
import sys
import json

# Add project directories to Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


print("--- Testing database module ---")

from database import db_manager as db

# Initialize database
db.init_db()
assert db is not None, "Database module failed to initialize"

# Create user
uid = db.create_user(
    "Test User",
    age=25,
    gender="Male",
    weight_kg=70,
    height_cm=175
)

print(f"Created user: ID={uid}")
assert uid is not None, "User creation failed"

# Retrieve user
user = db.get_user(uid)

assert user is not None, "User retrieval failed"
assert user["name"] == "Test User", "User name does not match"

print("User fetched:", user["name"])


print()
print("--- Testing medication operations ---")

# Add medication
med_id = db.add_medication(
    uid,
    "Paracetamol",
    "500mg",
    "Twice daily",
    json.dumps(["08:00", "20:00"]),
    "2026-07-10",
    notes="After meals"
)

print("Added medication: ID =", med_id)
assert med_id is not None, "Medication creation failed"

# Retrieve medications
meds = db.get_medications(uid)

print("Fetched medications:", len(meds), "active")
assert len(meds) > 0, "Medication was not retrieved"

# Log medication
db.log_medication(
    med_id,
    uid,
    "2026-07-10 08:00",
    status="taken"
)

db.log_medication(
    med_id,
    uid,
    "2026-07-10 20:00",
    status="missed"
)

# Calculate adherence
adherence = db.get_adherence_rate(uid, days=7)

print("Adherence rate:", adherence, "%")
assert adherence is not None, "Adherence rate calculation failed"


print()
print("--- Testing health metrics ---")

# Add health metrics
db.log_health_metric(
    uid,
    "steps",
    8500,
    "steps"
)

db.log_health_metric(
    uid,
    "heart_rate",
    72,
    "bpm"
)

db.log_health_metric(
    uid,
    "sleep_hours",
    7.5,
    "hours"
)

db.log_health_metric(
    uid,
    "weight",
    70.0,
    "kg"
)

# Retrieve health metrics
metrics = db.get_health_metrics(uid, days=7)

print("Logged metrics count:", len(metrics))
assert len(metrics) >= 4, "Health metrics were not stored correctly"


print()
print("--- Testing data parser ---")

from utils.data_parser import generate_sample_json, parse_auto

# Generate sample data
sample = generate_sample_json()

assert sample is not None, "Sample JSON generation failed"

# Parse sample data
parsed = parse_auto(sample)

print("Parsed records from sample JSON:", len(parsed))

assert parsed is not None, "JSON parsing failed"
assert len(parsed) > 0, "No records were parsed"


print()
print("--- Testing MedlinePlus tool ---")

from tools.medical_info_tool import search_medlineplus

result = search_medlineplus(
    "diabetes",
    max_results=1
)

print("MedlinePlus result length:", len(result), "chars")

assert result is not None, "MedlinePlus search failed"


print()
print("--- Testing visualizations ---")

from utils.visualizations import (
    chart_health_metric,
    chart_steps_gauge
)

# Get steps data
metrics_data = db.get_health_metrics(
    uid,
    metric_type="steps"
)

# Generate health metric chart
fig = chart_health_metric(
    metrics_data,
    "steps"
)

print("Steps chart type:", type(fig).__name__)

assert fig is not None, "Health metric chart generation failed"

# Generate steps gauge
gauge = chart_steps_gauge(8500)

print("Gauge chart type:", type(gauge).__name__)

assert gauge is not None, "Steps gauge generation failed"


print()
print("=== ALL TESTS PASSED ===")
