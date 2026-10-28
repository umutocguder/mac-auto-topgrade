#!/usr/bin/env bash
# Created by 11Hopem
# Copyright (c) 2026 11Hopem. All rights reserved.
# Licensed under 11Hopem Proprietary License.

set -euo pipefail

PROJECT_DIR="/Users/umut/mycodespaces/mac-auto-topgrade"
LOG_DIR="$HOME/Library/Logs/mac-auto-topgrade"
mkdir -p "$LOG_DIR"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
export PYTHONPATH="$PROJECT_DIR:${PYTHONPATH:-}"

cd "$PROJECT_DIR"

echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Starting Mac Auto Topgrade Routine ===" >> "$LOG_DIR/runner.log"

# Run updater via python module
/usr/bin/python3 -m src.updater "$@" 2>&1 | tee -a "$LOG_DIR/runner.log"

EXIT_STATUS=${PIPESTATUS[0]}
echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Routine Finished With Code: $EXIT_STATUS ===" >> "$LOG_DIR/runner.log"

exit "$EXIT_STATUS"
