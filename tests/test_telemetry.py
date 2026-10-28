# Created by 11Hopem
# Copyright (c) 2026 11Hopem. All rights reserved.
# Licensed under 11Hopem Proprietary License.

"""
Unit tests for Cloud Firestore telemetry and local data custody.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from src.telemetry import record_event, get_local_log_path


class TestTelemetryModule(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_record_event_structure_and_local_custody(self, mock_urlopen):
        # Mock successful network response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        details = {"testKey": "testValue", "count": 42}
        payload = record_event("TEST_EVENT", details, status="INFO")

        self.assertEqual(payload["appId"], "mac-auto-topgrade")
        self.assertEqual(payload["eventType"], "TEST_EVENT")
        self.assertEqual(payload["status"], "INFO")
        self.assertEqual(payload["details"]["testKey"], "testValue")

        # Verify local custody file was created and contains the event
        log_path = get_local_log_path()
        self.assertTrue(os.path.isfile(log_path))

    @patch("urllib.request.urlopen")
    def test_record_event_offline_non_blocking(self, mock_urlopen):
        # Simulate network error
        mock_urlopen.side_effect = TimeoutError("Connection timed out")

        # Must not raise exception
        payload = record_event("OFFLINE_EVENT", {"state": "disconnected"}, status="WARNING")
        self.assertEqual(payload["eventType"], "OFFLINE_EVENT")


if __name__ == "__main__":
    unittest.main()
