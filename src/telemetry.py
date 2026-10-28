# Created by 11Hopem
# Copyright (c) 2026 11Hopem. All rights reserved.
# Licensed under 11Hopem Proprietary License.

"""
Cloud Firestore REST Telemetry and Local Audit Logger.
Maintains 100% local custody while safely streaming events to Firebase.
"""

import json
import logging
import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

FIREBASE_PROJECT_ID = "hopem-software-cloud"
COLLECTION_NAME = "telemetry_logs"
APP_ID = "mac-auto-topgrade"


def get_base_dir() -> str:
    """Returns the project root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_local_log_path() -> str:
    """Returns path to the local audit JSON Lines file."""
    data_dir = os.path.join(get_base_dir(), "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "telemetry_logs.jsonl")


def record_event(event_type: str, details: dict, status: str = "INFO") -> dict:
    """
    Records an operational audit event locally and attempts non-blocking Firestore sync.

    :param event_type: Event identifier (e.g., START_UPGRADE, UPGRADE_COMPLETE).
    :param details: Dictionary containing metadata, duration, exit codes, etc.
    :param status: Severity indicator (INFO, SUCCESS, WARNING, ERROR).
    :return: The generated event payload.
    """
    now = datetime.now(timezone.utc)
    event_payload = {
        "appId": APP_ID,
        "eventType": event_type,
        "status": status,
        "timestamp": now.isoformat(),
        "unixTimestamp": int(now.timestamp()),
        "details": details
    }

    # 1. Local Data Custody (Always written first)
    try:
        log_path = get_local_log_path()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_payload) + "\n")
    except Exception as local_err:
        logger.error(f"Failed to persist event locally: {local_err}")

    # 2. Cloud Firestore REST Ingestion (Non-blocking)
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/{COLLECTION_NAME}"
        
        # Format payload into Firestore Document structure
        firestore_fields = {
            "appId": {"stringValue": APP_ID},
            "eventType": {"stringValue": event_type},
            "status": {"stringValue": status},
            "timestamp": {"timestampValue": now.strftime("%Y-%m-%dT%H:%M:%SZ")},
            "unixTimestamp": {"integerValue": str(int(now.timestamp()))},
            "detailsJson": {"stringValue": json.dumps(details)}
        }
        
        req_data = json.dumps({"fields": firestore_fields}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status not in (200, 201):
                logger.warning(f"Firestore returned non-200 code: {response.status}")
    except (urllib.error.URLError, TimeoutError, Exception) as cloud_err:
        # Never crash the application on telemetry network failures
        logger.debug(f"Telemetry cloud stream bypassed: {cloud_err}")

    return event_payload
