# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      tests/test_device_detect.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Manual test for camera and USB device detection.
# =============================================================================
#!/usr/bin/env python3

from src.device_detect import device_status


def main():
    status, devices = device_status()

    print(f"Status: {status}")
    print(f"Device count: {len(devices)}")
    print()

    for number, device in enumerate(devices, start=1):
        print(f"Device {number}")
        print("--------")
        print(f"Type:        {device['type']}")
        print(f"Description: {device['description']}")

        if "mount_path" in device:
            print(f"Mount path:  {device['mount_path']}")

        print()


if __name__ == "__main__":
    main()
