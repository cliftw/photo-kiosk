# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/google_drive_api.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Creates Google Drive services, folders, permissions, and file
#            uploads.
# =============================================================================
#!/usr/bin/env python3

import re
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]

CONFIG_DIR = Path("config")
TOKEN_FILE = CONFIG_DIR / "token.json"

ROOT_FOLDER_NAME = "PhotoKioskStudents"


def get_drive_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json())

    return build("drive", "v3", credentials=creds)


def find_folder(service, name, parent_id=None):
    safe_name = name.replace("'", "\\'")
    query_parts = [
        "mimeType = 'application/vnd.google-apps.folder'",
        f"name = '{safe_name}'",
        "trashed = false",
    ]

    if parent_id:
        query_parts.append(f"'{parent_id}' in parents")

    query = " and ".join(query_parts)

    response = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)",
    ).execute()

    files = response.get("files", [])

    if files:
        return files[0]["id"]

    return None


def create_folder(service, name, parent_id=None):
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }

    if parent_id:
        metadata["parents"] = [parent_id]

    folder = service.files().create(
        body=metadata,
        fields="id, name",
    ).execute()

    return folder["id"]


def get_or_create_folder(service, name, parent_id=None):
    folder_id = find_folder(service, name, parent_id)

    if folder_id:
        return folder_id

    return create_folder(service, name, parent_id)


def username_from_email(email):
    return email.strip().split("@", 1)[0]


def get_or_create_student_folder(student):
    service = get_drive_service()

    root_id = get_or_create_folder(service, ROOT_FOLDER_NAME)
    username = username_from_email(student["email"])
    student_folder_id = get_or_create_folder(service, username, parent_id=root_id)

    return student_folder_id


def share_folder_with_student(folder_id, email):
    service = get_drive_service()

    permission = {
        "type": "user",
        "role": "reader",
        "emailAddress": email,
    }

    result = service.permissions().create(
        fileId=folder_id,
        body=permission,
        sendNotificationEmail=True,
        fields="id",
    ).execute()

    return result["id"]


def find_file_in_folder(service, filename, folder_id):
    safe_name = filename.replace("'", "\\'")

    query = (
        f"name = '{safe_name}' "
        f"and '{folder_id}' in parents "
        f"and trashed = false"
    )

    response = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)",
    ).execute()

    files = response.get("files", [])

    if files:
        return files[0]["id"]

    return None


def get_next_upload_number(folder_id):
    service = get_drive_service()

    response = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        spaces="drive",
        fields="files(name)",
    ).execute()

    highest = 0

    for file in response.get("files", []):
        match = re.match(r"^U(\d{3})_", file["name"])

        if match:
            highest = max(highest, int(match.group(1)))

    return highest + 1


def upload_file_to_folder(local_file, folder_id, drive_filename=None):
    from googleapiclient.http import MediaFileUpload

    local_file = Path(local_file)
    if drive_filename is None:
        drive_filename = local_file.name
    service = get_drive_service()

    existing_file_id = find_file_in_folder(
        service,
        drive_filename,
        folder_id,
    )

    media = MediaFileUpload(
        str(local_file),
        resumable=True,
    )

    if existing_file_id:
        updated = service.files().update(
            fileId=existing_file_id,
            media_body=media,
            fields="id, name",
        ).execute()

        return {
            "id": updated["id"],
            "name": updated["name"],
            "action": "updated",
        }

    metadata = {
        "name": drive_filename,
        "parents": [folder_id],
    }

    created = service.files().create(
        body=metadata,
        media_body=media,
        fields="id, name",
    ).execute()

    return {
        "id": created["id"],
        "name": created["name"],
        "action": "created",
    }
