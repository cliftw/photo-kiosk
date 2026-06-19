# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/cleanup_gdrive.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Deletes uploaded photo files from cached student Google Drive
#            folders.
# =============================================================================
#!/usr/bin/env python3

from src.google_drive_api import get_drive_service
from src.student_folder_store import load_folder_map
from src.kiosk_logger import logger


def list_files_in_folder(service, folder_id):
    files = []
    page_token = None

    while True:
        response = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents and trashed = false",
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
            )
            .execute()
        )

        files.extend(response.get("files", []))
        page_token = response.get("nextPageToken")

        if not page_token:
            break

    return files


def cleanup_drive_uploads(dry_run=True):
    service = get_drive_service()
    folder_map = load_folder_map()

    matched = 0
    deleted = 0

    for student_id, folder_id in folder_map.items():
        files = list_files_in_folder(service, folder_id)

        for file in files:
            matched += 1

            if dry_run:
                logger.info(
                    f"DRIVE_CLEANUP_DRY_RUN,"
                    f"student={student_id},"
                    f"file_id={file['id']},"
                    f"name={file['name']}"
                )
            else:
                service.files().delete(fileId=file["id"]).execute()
                deleted += 1

                logger.info(
                    f"DRIVE_CLEANUP_DELETED,"
                    f"student={student_id},"
                    f"file_id={file['id']},"
                    f"name={file['name']}"
                )

    logger.info(
        f"DRIVE_CLEANUP_COMPLETE,"
        f"dry_run={dry_run},"
        f"folders={len(folder_map)},"
        f"matched={matched},"
        f"deleted={deleted}"
    )

    return {
        "folders": len(folder_map),
        "matched": matched,
        "deleted": deleted,
    }


if __name__ == "__main__":
    result = cleanup_drive_uploads(dry_run=False)

    print("Google Drive Cleanup")
    print(f"Student folders checked: {result['folders']}")
    print(f"Files matched: {result['matched']}")
    print(f"Files deleted: {result['deleted']}")
