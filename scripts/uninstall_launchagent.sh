#!/usr/bin/env bash
# Created by 11Hopem
# Copyright (c) 2026 11Hopem. All rights reserved.
# Licensed under 11Hopem Proprietary License.

set -euo pipefail

PLIST_NAME="com.11hopem.mac-auto-topgrade.plist"
TARGET_PLIST="$HOME/Library/LaunchAgents/$PLIST_NAME"

if [ -f "$TARGET_PLIST" ]; then
    echo "Unloading LaunchAgent from launchctl..."
    launchctl unload "$TARGET_PLIST" 2>/dev/null || true
    echo "Removing $TARGET_PLIST..."
    rm -f "$TARGET_PLIST"
    echo "LaunchAgent successfully uninstalled."
else
    echo "LaunchAgent plist not found at $TARGET_PLIST. Nothing to remove."
fi
