# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/drive_upload.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Legacy or helper code for uploading files into Google Drive.
# =============================================================================
#!/usr/bin/env python3

import subprocess
from pathlib import Path

RCLONE_REMOTE = "HilhiEngineeringDrive"


def upload_file(local_file, remote_folder):
    local_file = Path(local_file)

    if not local_file.exists():
        raise FileNotFoundError(f"File not found: {local_file}")

    destination = f"{RCLONE_REMOTE}:{remote_folder}"

    command = [
        "rclone",
        "copy",
        str(local_file),
        destination,
        "-P",
    ]

    result = subprocess.run(command, text=True)

    if result.returncode != 0:
        raise RuntimeError("rclone upload failed")

    return True
