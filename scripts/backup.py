# Created by 11Hopem
# Copyright (c) 2026 11Hopem. All rights reserved.
# Licensed under 11Hopem Proprietary License.

"""
Autonomous Backup Engine with SHA-256 Hash Verification.
Archives local audit logs and run histories to data/backups with a rotating ring buffer.
"""

import hashlib
import json
import logging
import os
import shutil
import time
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("mac-auto-topgrade.backup")

MAX_BACKUP_SLOTS = 10


def calculate_sha256(filepath: str) -> str:
    """Computes SHA-256 hexadecimal digest for a given file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def create_backup() -> dict:
    """Creates a timestamped snapshot of data files and maintains rotating index."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(base_dir, "data")
    backup_dir = os.path.join(data_dir, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    snapshot_filename = f"backup_{timestamp_str}.tar.gz"
    snapshot_path = os.path.join(backup_dir, snapshot_filename)

    # Files to backup
    target_files = ["runs.json", "telemetry_logs.jsonl"]
    archived_files = []

    temp_stage = os.path.join(backup_dir, f"stage_{timestamp_str}")
    os.makedirs(temp_stage, exist_ok=True)

    for tf in target_files:
        src = os.path.join(data_dir, tf)
        if os.path.isfile(src):
            dest = os.path.join(temp_stage, tf)
            shutil.copy2(src, dest)
            archived_files.append({"filename": tf, "sha256": calculate_sha256(src)})

    archive_base = os.path.join(backup_dir, f"backup_{timestamp_str}")
    shutil.make_archive(archive_base, "gztar", temp_stage)
    shutil.rmtree(temp_stage, ignore_errors=True)

    final_archive_path = f"{archive_base}.tar.gz"
    archive_hash = calculate_sha256(final_archive_path)

    manifest_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "archive": os.path.basename(final_archive_path),
        "sha256": archive_hash,
        "files": archived_files
    }

    manifest_path = os.path.join(backup_dir, "backup_manifest.json")
    manifest = []
    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as mf:
                manifest = json.load(mf)
        except Exception:
            manifest = []

    manifest.insert(0, manifest_entry)

    # Prune old backups exceeding MAX_BACKUP_SLOTS
    while len(manifest) > MAX_BACKUP_SLOTS:
        pruned = manifest.pop()
        pruned_file = os.path.join(backup_dir, pruned["archive"])
        if os.path.isfile(pruned_file):
            try:
                os.remove(pruned_file)
            except OSError as err:
                logger.warning(f"Could not remove old archive: {err}")

    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2, ensure_ascii=False)

    logger.info(f"Backup archive created: {final_archive_path} (SHA-256: {archive_hash[:12]}...)")
    return manifest_entry


if __name__ == "__main__":
    create_backup()
