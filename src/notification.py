# Created by 11Hopem
# Copyright (c) 2026 11Hopem. All rights reserved.
# Licensed under 11Hopem Proprietary License.

"""
Notification helper for dispatching native macOS desktop banners.
"""

import subprocess
import logging

logger = logging.getLogger(__name__)


def send_notification(message: str, title: str = "Mac Auto Topgrade", subtitle: str = "") -> bool:
    """
    Displays a native macOS User Notification banner via AppleScript.

    :param message: Main body of the notification.
    :param title: Notification header title.
    :param subtitle: Optional secondary subtitle.
    :return: True if the notification was delivered, False otherwise.
    """
    safe_message = message.replace('"', '\\"')
    safe_title = title.replace('"', '\\"')
    safe_subtitle = subtitle.replace('"', '\\"')

    if safe_subtitle:
        script = f'display notification "{safe_message}" with title "{safe_title}" subtitle "{safe_subtitle}"'
    else:
        script = f'display notification "{safe_message}" with title "{safe_title}"'

    try:
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return True
    except Exception as exc:
        logger.warning(f"Failed to display native notification: {exc}")
        return False
