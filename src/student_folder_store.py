# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/student_folder_store.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Stores and retrieves cached student Google Drive folder IDs.
# =============================================================================
#!/usr/bin/env python3

import csv
from pathlib import Path


STORE_FILE = Path("data/student_folders.csv")
FIELDNAMES = ["id", "folder_id"]


def clean(value):
    if value is None:
        return ""
    return value.strip()


def load_folder_map():
    folder_map = {}

    if not STORE_FILE.exists():
        return folder_map

    with open(STORE_FILE, newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            student_id = clean(row.get("id"))
            folder_id = clean(row.get("folder_id"))

            if student_id and folder_id:
                folder_map[student_id] = folder_id

    return folder_map


def get_folder_id(student_id):
    student_id = clean(student_id)
    folder_map = load_folder_map()
    return folder_map.get(student_id)


def save_folder_id(student_id, folder_id):
    student_id = clean(student_id)
    folder_id = clean(folder_id)

    STORE_FILE.parent.mkdir(parents=True, exist_ok=True)

    folder_map = load_folder_map()
    folder_map[student_id] = folder_id

    with open(STORE_FILE, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()

        for saved_student_id in sorted(folder_map.keys()):
            writer.writerow({
                "id": saved_student_id,
                "folder_id": folder_map[saved_student_id],
            })
