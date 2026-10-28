# Created by 11Hopem
# Copyright (c) 2026 11Hopem. All rights reserved.
# Licensed under 11Hopem Proprietary License.

"""
Unit tests for Topgrade resolver and argument builder.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from src.updater import (
    resolve_topgrade_binary,
    build_topgrade_arguments,
    record_run_history,
    is_recent_successful_run
)


class TestUpdaterModule(unittest.TestCase):
    def test_build_topgrade_arguments_standard(self):
        args = build_topgrade_arguments(dry_run=False)
        self.assertIn("--yes", args)
        self.assertIn("--no-ask-retry", args)
        self.assertIn("--cleanup", args)
        self.assertIn("--disable", args)
        self.assertIn("system", args)
        self.assertNotIn("--dry-run", args)

    def test_build_topgrade_arguments_dry_run(self):
        args = build_topgrade_arguments(dry_run=True)
        self.assertIn("--dry-run", args)
        self.assertIn("--yes", args)

    def test_resolve_topgrade_binary_finds_path(self):
        # We know topgrade exists on this system or can be found in PATH
        binary = resolve_topgrade_binary()
        self.assertTrue(os.path.isfile(binary))
        self.assertTrue(os.access(binary, os.X_OK))

    def test_record_run_history(self):
        sample_run = {
            "timestamp": "2026-10-28T20:00:00Z",
            "durationSeconds": 12.5,
            "exitCode": 0,
            "status": "SUCCESS",
            "dryRun": True
        }
        # Should not raise exception
        record_run_history(sample_run)

    def test_is_recent_successful_run(self):
        # Should execute safely and return a boolean
        result = is_recent_successful_run(cooldown_seconds=10)
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    unittest.main()
