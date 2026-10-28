# Created by 11Hopem
# Copyright (c) 2026 11Hopem. All rights reserved.
# Licensed under 11Hopem Proprietary License.

"""
Core Topgrade Execution and System Maintenance Engine.
Executes non-interactive package maintenance safely on macOS system startup.
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

from .notification import send_notification
from .telemetry import record_event

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mac-auto-topgrade.updater")


def resolve_topgrade_binary() -> str:
    """
    Locates the topgrade executable across standard Homebrew and system PATH locations.
    """
    candidates = [
        "/opt/homebrew/bin/topgrade",
        "/usr/local/bin/topgrade",
        shutil.which("topgrade")
    ]
    for binary in candidates:
        if binary and os.path.isfile(binary) and os.access(binary, os.X_OK):
            return binary
    raise FileNotFoundError("topgrade binary not found in standard paths or PATH environment.")


def build_topgrade_arguments(dry_run: bool = False) -> list[str]:
    """
    Constructs safe non-interactive arguments for unattended startup maintenance.
    """
    args = [
        "--yes",
        "--no-ask-retry",
        "--cleanup",
        "--disable", "system"
    ]
    if dry_run:
        args.append("--dry-run")
    return args


def record_run_history(run_info: dict) -> None:
    """
    Maintains a rolling historical ledger of runs in data/runs.json.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    history_file = os.path.join(data_dir, "runs.json")

    history = []
    if os.path.isfile(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception as read_err:
            logger.warning(f"Failed to read existing history: {read_err}")

    history.insert(0, run_info)
    # Keep last 50 runs
    history = history[:50]

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def is_recent_successful_run(cooldown_seconds: int = 7200) -> bool:
    """
    Checks if a successful maintenance routine completed within the specified cooldown window.
    Prevents redundant consecutive executions when system reboots close to daily scheduled time.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    history_file = os.path.join(base_dir, "data", "runs.json")
    if not os.path.isfile(history_file):
        return False
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
            if not history or not isinstance(history, list):
                return False
            for entry in history:
                if entry.get("status") == "SUCCESS" and not entry.get("dryRun", False):
                    ts_str = entry.get("timestamp")
                    if ts_str:
                        run_time = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        now = datetime.now(timezone.utc)
                        delta = (now - run_time).total_seconds()
                        if 0 <= delta < cooldown_seconds:
                            return True
                    break
    except Exception as err:
        logger.warning(f"Could not evaluate recent run history: {err}")
    return False


def run_system_maintenance(dry_run: bool = False, notify: bool = True, force: bool = False) -> int:
    """
    Executes topgrade maintenance workflow with telemetry and user notifications.
    """
    if not force and not dry_run and is_recent_successful_run(cooldown_seconds=7200):
        logger.info("Maintenance already completed successfully within the last 2 hours. Skipping redundant execution.")
        return 0

    start_time = time.time()
    iso_start = datetime.now(timezone.utc).isoformat()
    logger.info("Initializing automated system maintenance routine...")

    if notify:
        send_notification(
            message="Starting automated developer toolchain maintenance...",
            title="11Hopem System Updater",
            subtitle="Startup Maintenance"
        )

    try:
        binary_path = resolve_topgrade_binary()
    except FileNotFoundError as err:
        logger.error(str(err))
        record_event("TOPGRADE_BINARY_NOT_FOUND", {"error": str(err)}, status="ERROR")
        if notify:
            send_notification(
                message="Maintenance aborted: topgrade binary could not be found.",
                title="11Hopem System Updater",
                subtitle="Error"
            )
        return 1

    topgrade_args = build_topgrade_arguments(dry_run=dry_run)
    command = [binary_path] + topgrade_args
    logger.info(f"Executing command: {' '.join(command)}")

    record_event(
        "TOPGRADE_STARTED",
        {
            "binary": binary_path,
            "args": topgrade_args,
            "dryRun": dry_run,
            "startedAt": iso_start
        },
        status="INFO"
    )

    exit_code = 0
    stdout_output = ""
    stderr_output = ""

    try:
        # Extend PATH to ensure Homebrew toolchain binaries are visible
        custom_env = os.environ.copy()
        custom_env["PATH"] = f"/opt/homebrew/bin:/usr/local/bin:{custom_env.get('PATH', '')}"

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=custom_env
        )
        collected_lines: list[str] = []
        try:
            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    sys.stdout.write(line)
                    sys.stdout.flush()
                    collected_lines.append(line)
                process.stdout.close()
            process.wait(timeout=5400)  # 90 minutes upper bound
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            exit_code = 124
            stderr_output = "Execution timed out after 90 minutes."
            logger.error("Topgrade execution timed out.")

        stdout_output = "".join(collected_lines)
    except Exception as exec_err:
        exit_code = 1
        stderr_output = str(exec_err)
        logger.error(f"Unexpected execution error: {exec_err}")

    duration = round(time.time() - start_time, 2)
    status_str = "SUCCESS" if exit_code == 0 else "ERROR"

    run_summary = {
        "timestamp": iso_start,
        "durationSeconds": duration,
        "exitCode": exit_code,
        "status": status_str,
        "dryRun": dry_run,
        "stdoutTail": stdout_output[-1000:] if stdout_output else "",
        "stderrTail": stderr_output[-1000:] if stderr_output else ""
    }
    record_run_history(run_summary)

    record_event(
        f"TOPGRADE_{status_str}",
        {
            "durationSeconds": duration,
            "exitCode": exit_code,
            "dryRun": dry_run
        },
        status=status_str
    )

    if notify:
        if exit_code == 0:
            send_notification(
                message=f"System packages successfully updated in {duration}s.",
                title="11Hopem System Updater",
                subtitle="Maintenance Complete"
            )
        else:
            send_notification(
                message=f"Maintenance finished with exit code {exit_code} ({duration}s).",
                title="11Hopem System Updater",
                subtitle="Notice"
            )

    logger.info(f"System maintenance routine finalized with exit code {exit_code} ({duration}s).")
    return exit_code


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated Topgrade runner for macOS.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate execution without modifying packages.")
    parser.add_argument("--silent", action="store_true", help="Suppress native desktop notifications.")
    parser.add_argument("--force", action="store_true", help="Force execution even if a recent run completed successfully.")
    args = parser.parse_args()

    code = run_system_maintenance(dry_run=args.dry_run, notify=not args.silent, force=args.force)
    sys.exit(code)


if __name__ == "__main__":
    main()
