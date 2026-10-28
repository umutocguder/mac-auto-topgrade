#!/usr/bin/env bash
# Created by 11Hopem
# Copyright (c) 2026 11Hopem. All rights reserved.
# Licensed under 11Hopem Proprietary License.

set -euo pipefail

LABEL="com.11hopem.mac-auto-topgrade"
PLIST_PATH="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_FILE="$HOME/Library/Logs/mac-auto-topgrade/runner.log"
PROJECT_DIR="/Users/umut/mycodespaces/mac-auto-topgrade"

echo "========================================================"
echo "          11HOPEM MAC AUTO-TOPGRADE STATUS              "
echo "========================================================"

if [ -f "$PLIST_PATH" ]; then
    echo "[✓] LaunchAgent Plist: Installed ($PLIST_PATH)"
else
    echo "[!] LaunchAgent Plist: NOT INSTALLED"
fi

if launchctl print "gui/$(id -u)/$LABEL" >/dev/null 2>&1 || launchctl list | grep -q "$LABEL"; then
    echo "[✓] Launchctl Daemon: REGISTERED AND ACTIVE"
    launchctl print "gui/$(id -u)/$LABEL" 2>/dev/null | grep -E "state =|active count =" || true
else
    echo "[!] Launchctl Daemon: NOT LOADED"
fi

echo ""
echo "--- Last Run Summary (data/runs.json) ---"
if [ -f "$PROJECT_DIR/data/runs.json" ]; then
    python3 -c "
import json
try:
    with open('$PROJECT_DIR/data/runs.json') as f:
        data = json.load(f)
        if data:
            latest = data[0]
            print(f'Timestamp:   {latest.get(\"timestamp\")}')
            print(f'Status:      {latest.get(\"status\")}')
            print(f'Exit Code:   {latest.get(\"exitCode\")}')
            print(f'Duration:    {latest.get(\"durationSeconds\")}s')
        else:
            print('No run history logged yet.')
except Exception as e:
    print(f'Error reading history: {e}')
"
else
    echo "No runs recorded yet."
fi

echo ""
echo "--- Recent Runner Logs ($LOG_FILE) ---"
if [ -f "$LOG_FILE" ]; then
    tail -n 12 "$LOG_FILE"
else
    echo "No log file found."
fi
echo "========================================================"
