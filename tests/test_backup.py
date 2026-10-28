# Created by 11Hopem
# Copyright (c) 2026 11Hopem. All rights reserved.
# Licensed under 11Hopem Proprietary License.

"""
Unit tests for rotating backup engine with SHA-256 verification.
"""

import os
import tempfile
import unittest

from scripts.backup import calculate_sha256, create_backup


class TestBackupModule(unittest.TestCase):
    def test_calculate_sha256(self):
        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as temp_file:
            temp_file.write("11Hopem Backup Integrity Test Content")
            temp_path = temp_file.name

        try:
            digest = calculate_sha256(temp_path)
            self.assertIsInstance(digest, str)
            self.assertEqual(len(digest), 64)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_create_backup_generates_manifest(self):
        result = create_backup()
        self.assertIn("timestamp", result)
        self.assertIn("archive", result)
        self.assertIn("sha256", result)
        self.assertEqual(len(result["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
