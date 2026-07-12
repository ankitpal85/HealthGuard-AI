"""
Data parsing utilities for HealthGuard AI.
Handles JSON, CSV, and XML health data import/export.
"""

import json
import csv
import io
from xml.etree import ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any, Optional


SUPPORTED_METRICS = [
    "steps", "heart_rate", "blood_pressure_systolic", "blood_pressure_diastolic",
    "weight", "blood_glucose", "oxygen_saturation", "sleep_hours",
    "calories_burned", "water_intake", "bmi",
]

METRIC_UNITS = {
    "steps": "steps",
    "heart_rate": "bpm",
    "blood_pressure_systolic": "mmHg",
    "blood_pressure_diastolic": "mmHg",
    "weight": "kg",
    "blood_glucose": "mg/dL",
    "oxygen_saturation": "%",
    "sleep_hours": "hours",
    "calories_burned": "kcal",
    "water_intake": "liters",
    "bmi": "kg/m²",
}


def parse_json_health_data(json_str: str) -> List[Dict[str, Any]]:
    """
    Parse JSON health data into a standardized list of metric dicts.

    Expected format:
    [
        {"metric_type": "steps", "value": 8500, "recorded_at": "2024-01-15 08:00"},
        {"metric_type": "heart_rate", "value": 72, "recorded_at": "2024-01-15 09:00"}
    ]
    """
    data = json.loads(json_str)
    if isinstance(data, dict):
        data = [data]

    standardized = []
    for record in data:
        metric_type = record.get("metric_type", "").lower().replace(" ", "_")
        if metric_type not in SUPPORTED_METRICS:
            continue
        standardized.append({
            "metric_type": metric_type,
            "value": float(record.get("value", 0)),
            "value2": float(record["value2"]) if record.get("value2") else None,
            "unit": METRIC_UNITS.get(metric_type, "units"),
            "recorded_at": record.get("recorded_at", datetime.now().strftime("%Y-%m-%d %H:%M")),
            "notes": record.get("notes", ""),
        })
    return standardized


def parse_csv_health_data(csv_str: str) -> List[Dict[str, Any]]:
    """
    Parse CSV health data into standardized metric dicts.

    Expected columns: metric_type, value, recorded_at, notes (optional)
    """
    reader = csv.DictReader(io.StringIO(csv_str.strip()))
    standardized = []
    for row in reader:
        metric_type = row.get("metric_type", "").lower().replace(" ", "_")
        if metric_type not in SUPPORTED_METRICS:
            continue
        try:
            standardized.append({
                "metric_type": metric_type,
                "value": float(row.get("value", 0)),
                "value2": float(row["value2"]) if row.get("value2") else None,
                "unit": METRIC_UNITS.get(metric_type, "units"),
                "recorded_at": row.get("recorded_at", datetime.now().strftime("%Y-%m-%d %H:%M")),
                "notes": row.get("notes", ""),
            })
        except (ValueError, KeyError):
            continue
    return standardized


def parse_xml_health_data(xml_str: str) -> List[Dict[str, Any]]:
    """
    Parse XML health data.

    Expected format:
    <health_data>
        <metric>
            <type>steps</type>
            <value>8500</value>
            <recorded_at>2024-01-15 08:00</recorded_at>
        </metric>
    </health_data>
    """
    root = ET.fromstring(xml_str)
    standardized = []
    for metric_el in root.findall(".//metric"):
        metric_type = (metric_el.findtext("type") or "").lower().replace(" ", "_")
        if metric_type not in SUPPORTED_METRICS:
            continue
        try:
            value_text = metric_el.findtext("value") or "0"
            value2_text = metric_el.findtext("value2")
            standardized.append({
                "metric_type": metric_type,
                "value": float(value_text),
                "value2": float(value2_text) if value2_text else None,
                "unit": METRIC_UNITS.get(metric_type, "units"),
                "recorded_at": metric_el.findtext("recorded_at") or datetime.now().strftime("%Y-%m-%d %H:%M"),
                "notes": metric_el.findtext("notes") or "",
            })
        except (ValueError, TypeError):
            continue
    return standardized


def export_metrics_to_json(metrics: list) -> str:
    """Export health metrics list to a JSON string."""
    return json.dumps(metrics, indent=2, default=str)


def export_metrics_to_csv(metrics: list) -> str:
    """Export health metrics list to a CSV string."""
    if not metrics:
        return "No data to export."
    output = io.StringIO()
    fields = ["id", "metric_type", "value", "value2", "unit", "recorded_at", "notes"]
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(metrics)
    return output.getvalue()


def detect_format(data_str: str) -> str:
    """Auto-detect the format of health data string."""
    stripped = data_str.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        return "json"
    elif stripped.startswith("<"):
        return "xml"
    elif "," in stripped and "\n" in stripped:
        return "csv"
    return "unknown"


def parse_auto(data_str: str) -> List[Dict[str, Any]]:
    """Auto-detect and parse health data."""
    fmt = detect_format(data_str)
    if fmt == "json":
        return parse_json_health_data(data_str)
    elif fmt == "csv":
        return parse_csv_health_data(data_str)
    elif fmt == "xml":
        return parse_xml_health_data(data_str)
    return []


def generate_sample_json() -> str:
    """Generate a sample JSON for user reference."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sample = [
        {"metric_type": "steps", "value": 8500, "recorded_at": now},
        {"metric_type": "heart_rate", "value": 75, "recorded_at": now},
        {"metric_type": "blood_pressure_systolic", "value": 118, "recorded_at": now},
        {"metric_type": "blood_pressure_diastolic", "value": 78, "recorded_at": now},
        {"metric_type": "sleep_hours", "value": 7.5, "recorded_at": now},
        {"metric_type": "water_intake", "value": 2.2, "recorded_at": now},
    ]
    return json.dumps(sample, indent=2)
