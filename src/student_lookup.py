# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/student_lookup.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Looks up student roster records from the local CSV file.
# =============================================================================
#!/usr/bin/env python3

import csv
from pathlib import Path

ROSTER_FILE = Path(__file__).resolve().parent.parent / "config" / "roster.csv"


def clean_row(row):
    cleaned = {}

    for key, value in row.items():
        clean_key = key.strip() if key is not None else ""

        if value is None:
            cleaned[clean_key] = ""
        else:
            cleaned[clean_key] = value.strip()

    return cleaned


def lookup_student(student_id):
    student_id = student_id.strip()

    with open(ROSTER_FILE, newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            row = clean_row(row)

            if row["id"] == student_id:
                if row["active"].lower() != "yes":
                    return None
                return row

    return None
