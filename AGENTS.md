# Created by 11Hopem
# Copyright (c) 2026 11Hopem. All rights reserved.
# Licensed under 11Hopem Proprietary License.

# Mac Auto Topgrade — Autonomous System & Tooling Maintenance Daemon

## Overview
`mac-auto-topgrade` is an autonomous macOS maintenance and package upgrade daemon powered by Topgrade and native `launchd`. It runs automatically every time the computer boots or the user logs in, updating developer toolchains (Homebrew, npm, pipx, cargo, VS Code extensions) non-interactively without blocking on sudo password requests, while streaming health telemetry to Cloud Firestore.

## Architecture
- **Language / Runtime:** Python 3 (zero external dependencies) and POSIX-compliant Bash.
- **Daemon Orchestrator:** Native macOS LaunchAgent (`com.11hopem.mac-auto-topgrade.plist`) with `RunAtLoad=true`.
- **Package Manager Wrapper:** `/opt/homebrew/bin/topgrade` executed with safety flags (`--yes --no-ask-retry --cleanup --disable system`).
- **Telemetry & Custody:** Non-blocking Cloud Firestore REST telemetry (`hopem-software-cloud`) and 100% local JSON logging.
- **Notification Engine:** Native macOS UserNotifications / AppleScript (`osascript`) notification banners.
- **Backup Engine:** Autonomous SHA-256 rolling ledger and backup system (Rule 17).

## Execution Commands
- **Run Updater (Manual Run):** `python3 src/updater.py` or `bash scripts/run_updater.sh`
- **Install Daemon:** `bash scripts/install_launchagent.sh`
- **Uninstall Daemon:** `bash scripts/uninstall_launchagent.sh`
- **Check Service Status:** `bash scripts/status.sh`
- **Run Automated Tests:** `python3 -m unittest discover -s tests -p "test_*.py"`
- **Execute Data Backup:** `python3 scripts/backup.py`

## Development Standards
- 100% English code, variable names, functions, docstrings, logs, and commit messages. Zero Turkish in code.
- Strict isolation from corporate workspaces (`/Users/umut/intetra/*`).
- Attribution: Created by 11Hopem (https://11hopem.com).
