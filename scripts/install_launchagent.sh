#!/usr/bin/env bash
# Created by 11Hopem
# Copyright (c) 2026 11Hopem. All rights reserved.
# Licensed under 11Hopem Proprietary License.

set -euo pipefail

PLIST_NAME="com.11hopem.mac-auto-topgrade.plist"
PROJECT_DIR="/Users/umut/mycodespaces/mac-auto-topgrade"
SOURCE_PLIST="$PROJECT_DIR/$PLIST_NAME"
TARGET_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$TARGET_DIR/$PLIST_NAME"

mkdir -p "$TARGET_DIR"
mkdir -p "$HOME/Library/Logs/mac-auto-topgrade"

chmod +x "$PROJECT_DIR/scripts/run_updater.sh"
chmod +x "$PROJECT_DIR/scripts/status.sh"

# Unload previous instance if present
if launchctl list | grep -q "com.11hopem.mac-auto-topgrade"; then
    echo "Unloading existing launchagent..."
    launchctl unload "$TARGET_PLIST" 2>/dev/null || true
fi

echo "Copying plist to $TARGET_PLIST..."
cp "$SOURCE_PLIST" "$TARGET_PLIST"

echo "Loading LaunchAgent into launchctl..."
launchctl load -w "$TARGET_PLIST"

echo "LaunchAgent successfully registered. Mac Auto Topgrade is now active on boot!"
