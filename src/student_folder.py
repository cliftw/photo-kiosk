# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/student_folder.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Legacy or helper code for student Google Drive folder handling.
# =============================================================================
#!/usr/bin/env python3

import re
import subprocess


REMOTE = "HilhiEngineeringDrive"
ROOT_FOLDER = "PhotoKioskStudents"


def safe_folder_name(text):
    text = text.strip()
    text = re.sub(r'[<>:"/\\|?*]', "_", text)
    text = re.sub(r"\s+", "_", text)
    return text


def username_from_email(email):
    email = email.strip()
    return email.split("@", 1)[0]


def student_folder_path(student):
    username = username_from_email(student["email"])
    username = safe_folder_name(username)
    return f"{ROOT_FOLDER}/{username}"


def ensure_student_folder(student):
    folder_path = student_folder_path(student)

    command = [
        "rclone",
        "mkdir",
        f"{REMOTE}:{folder_path}",
    ]

    result = subprocess.run(command, text=True)

    if result.returncode != 0:
        raise RuntimeError("Could not create student Drive folder")

    return folder_path
