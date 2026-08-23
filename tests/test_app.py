import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


print('--- Testing database module ---')

from database import db_manager as db
db.init_db()
uid = db.create_user('Test User', age=25, gender='Male', weight_kg=70, height_cm=175)
print(f'Created user: ID={uid}')
user = db.get_user(uid)
print('User fetched:', user['name'])

print()
print('--- Testing medication operations ---')
import json
med_id = db.add_medication(uid, 'Paracetamol', '500mg', 'Twice daily',
    json.dumps(['08:00','20:00']), '2026-07-10', notes='After meals')
print('Added medication: ID =', med_id)
meds = db.get_medications(uid)
print('Fetched medications:', len(meds), 'active')

db.log_medication(med_id, uid, '2026-07-10 08:00', status='taken')
db.log_medication(med_id, uid, '2026-07-10 20:00', status='missed')
adherence = db.get_adherence_rate(uid, days=7)
print('Adherence rate:', adherence, '%')

print()
print('--- Testing health metrics ---')
db.log_health_metric(uid, 'steps', 8500, 'steps')
db.log_health_metric(uid, 'heart_rate', 72, 'bpm')
db.log_health_metric(uid, 'sleep_hours', 7.5, 'hours')
db.log_health_metric(uid, 'weight', 70.0, 'kg')
metrics = db.get_health_metrics(uid, days=7)
print('Logged metrics count:', len(metrics))

print()
print('--- Testing data parser ---')
from utils.data_parser import generate_sample_json, parse_auto
sample = generate_sample_json()
parsed = parse_auto(sample)
print('Parsed records from sample JSON:', len(parsed))

print()
print('--- Testing MedlinePlus tool ---')
from tools.medical_info_tool import search_medlineplus
result = search_medlineplus('diabetes', max_results=1)
print('MedlinePlus result length:', len(result), 'chars')

print()
print('--- Testing visualizations ---')
from utils.visualizations import chart_health_metric, chart_steps_gauge
metrics_data = db.get_health_metrics(uid, metric_type='steps')
fig = chart_health_metric(metrics_data, 'steps')
print('Steps chart type:', type(fig).__name__)
gauge = chart_steps_gauge(8500)
print('Gauge chart type:', type(gauge).__name__)

print()
print('=== ALL TESTS PASSED ===')
