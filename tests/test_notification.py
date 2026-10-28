# Created by 11Hopem
# Copyright (c) 2026 11Hopem. All rights reserved.
# Licensed under 11Hopem Proprietary License.

"""
Unit tests for notification engine.
"""

import subprocess
import unittest
from unittest.mock import patch, MagicMock

from src.notification import send_notification


class TestNotificationModule(unittest.TestCase):
    @patch("subprocess.run")
    def test_send_notification_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        result = send_notification("System updated", title="Topgrade", subtitle="Complete")
        self.assertTrue(result)
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args[0], "osascript")
        self.assertEqual(call_args[1], "-e")
        self.assertIn("System updated", call_args[2])
        self.assertIn("Topgrade", call_args[2])

    @patch("subprocess.run")
    def test_send_notification_failure_gracefully_handled(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, ["osascript"])
        result = send_notification("Test failure")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
