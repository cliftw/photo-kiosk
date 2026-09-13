# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/device_detect.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Detects attached cameras and USB storage devices for kiosk import.
# =============================================================================
#!/usr/bin/env python3

import subprocess
from pathlib import Path


MEDIA_ROOT = Path("/media/cliftw")


def detect_gphoto_devices():
    devices = []

    result = subprocess.run(
        ["gphoto2", "--auto-detect"],
        capture_output=True,
        text=True,
    )

    lines = result.stdout.strip().splitlines()

    if len(lines) <= 2:
        return devices

    for line in lines[2:]:
        line = line.strip()
        if line:
            devices.append({
                "type": "gphoto",
                "description": line,
            })

    return devices


def detect_usb_storage_devices():
    devices = []

    if not MEDIA_ROOT.exists():
        return devices

    for mount in MEDIA_ROOT.iterdir():
        if mount.is_mount():
            devices.append({
                "type": "usb_storage",
                "description": mount.name,
                "mount_path": str(mount),
            })

    return devices


def detect_devices():
    gphoto_devices = detect_gphoto_devices()
    usb_devices = detect_usb_storage_devices()

    usb_mount_paths = {
        device["mount_path"]
        for device in usb_devices
    }

    devices = []

    for device in gphoto_devices:
        description = device["description"]
        parts = description.rsplit(None, 1)

        if len(parts) == 2:
            port = parts[1]

            if port.startswith("disk:"):
                disk_path = port[len("disk:"):]

                if disk_path in usb_mount_paths:
                    continue

        devices.append(device)

    devices.extend(usb_devices)
    return devices


def device_status():
    devices = detect_devices()

    if len(devices) == 0:
        return "none", devices

    if len(devices) == 1:
        return "ready", devices

    return "too_many", devices
