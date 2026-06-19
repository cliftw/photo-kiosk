# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/roster_refresh.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Builds the local roster CSV from active tabs in a Google Sheet.
# =============================================================================
#!/usr/bin/env python3

import csv
from pathlib import Path

from googleapiclient.discovery import build

from src.google_drive_api import get_drive_service
from src.kiosk_logger import logger


SPREADSHEET_ID = "1wLe-DQnq7cPhGo3itsPMmr-O7zZS6UTsusMB0y3yb9M"

ROSTER_FILE = Path("config/roster.csv")

FIELDNAMES = ["id", "name", "email", "folder_id", "active"]

DISABLED_TAB_PREFIXES = (
    "OFF",
    "DISABLE",
    "DISABLED",
    "ARCHIVE",
    "TEMPLATE",
)


def get_sheets_service():
    drive_service = get_drive_service()
    creds = drive_service._http.credentials
    return build("sheets", "v4", credentials=creds)


def is_active_tab(tab_name):
    normalized = tab_name.strip().upper()

    for prefix in DISABLED_TAB_PREFIXES:
        if normalized.startswith(prefix):
            return False

    return True


def normalize_row(record):
    return {
        "id": record.get("id", "").strip(),
        "name": record.get("name", "").strip(),
        "email": record.get("email", "").strip(),
        "folder_id": record.get("folder_id", "").strip(),
        "active": record.get("active", "").strip(),
    }


def records_conflict(existing, incoming):
    for field in ["name", "email", "active"]:
        if existing.get(field, "") != incoming.get(field, ""):
            return True

    return False


def get_tab_names(service):
    metadata = (
        service.spreadsheets()
        .get(spreadsheetId=SPREADSHEET_ID)
        .execute()
    )

    tab_names = []

    for sheet in metadata.get("sheets", []):
        title = sheet["properties"]["title"]
        tab_names.append(title)

    return tab_names


def read_tab_records(service, tab_name):
    range_name = f"'{tab_name}'!A:E"

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
        )
        .execute()
    )

    rows = result.get("values", [])

    if not rows:
        return []

    header = [h.strip() for h in rows[0]]
    records = []

    for row_number, row in enumerate(rows[1:], start=2):
        padded = row + [""] * (len(header) - len(row))
        raw_record = dict(zip(header, padded))
        record = normalize_row(raw_record)

        if not record["id"]:
            continue

        record["_source_tab"] = tab_name
        record["_source_row"] = row_number

        records.append(record)

    return records


def refresh_roster():
    service = get_sheets_service()

    tab_names = get_tab_names(service)

    roster_by_id = {}
    tabs_used = []
    tabs_skipped = []
    tab_counts = {}
    duplicate_count = 0
    conflict_count = 0

    for tab_name in tab_names:

        if not is_active_tab(tab_name):
            tabs_skipped.append(tab_name)
            continue

        tabs_used.append(tab_name)

        records = read_tab_records(service, tab_name)
        tab_counts[tab_name] = len(records)

        for record in records:
            student_id = record["id"]

            clean_record = {
                "id": record["id"],
                "name": record["name"],
                "email": record["email"],
                "folder_id": record["folder_id"],
                "active": record["active"],
            }

            if student_id not in roster_by_id:
                roster_by_id[student_id] = clean_record
                continue

            existing = roster_by_id[student_id]

            if existing == clean_record:
                duplicate_count += 1
                continue

            if records_conflict(existing, clean_record):
                conflict_count += 1
                logger.warning(
                    f"ROSTER_CONFLICT,"
                    f"id={student_id},"
                    f"tab={record['_source_tab']},"
                    f"row={record['_source_row']},"
                    f"existing_name={existing['name']},"
                    f"incoming_name={clean_record['name']},"
                    f"existing_email={existing['email']},"
                    f"incoming_email={clean_record['email']},"
                    f"existing_active={existing['active']},"
                    f"incoming_active={clean_record['active']}"
                )

            duplicate_count += 1

    ROSTER_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(ROSTER_FILE, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()

        for student_id in sorted(roster_by_id.keys()):
            writer.writerow(roster_by_id[student_id])

    logger.info(
        f"ROSTER_REFRESH,"
        f"records={len(roster_by_id)},"
        f"tabs_used={len(tabs_used)},"
        f"tabs_skipped={len(tabs_skipped)},"
        f"duplicates={duplicate_count},"
        f"conflicts={conflict_count}"
    )

    return {
        "record_count": len(roster_by_id),
        "tabs_used": tabs_used,
        "tabs_skipped": tabs_skipped,
        "tab_counts": tab_counts,
        "duplicates": duplicate_count,
        "conflicts": conflict_count,
    }


if __name__ == "__main__":
    result = refresh_roster()

    print(f"Roster refreshed: {result['record_count']} unique records")
    print()

    print("Tabs used:")
    for tab_name in result["tabs_used"]:
        print(f"  {tab_name}: {result['tab_counts'].get(tab_name, 0)} rows")

    if result["tabs_skipped"]:
        print()
        print("Tabs skipped:")
        for tab_name in result["tabs_skipped"]:
            print(f"  {tab_name}")

    print()
    print(f"Unique records written: {result['record_count']}")
    print(f"Duplicates ignored: {result['duplicates']}")
    print(f"Conflicts logged: {result['conflicts']}")
