# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      tests/test_drive_upload.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Manual test for uploading files to Google Drive.
# =============================================================================
#!/usr/bin/env python3

from src.drive_upload import upload_file


def main():
    local_file = input("Local file to upload: ").strip()
    remote_folder = input("Remote Drive folder: ").strip()

    print()
    print("Uploading...")
    upload_file(local_file, remote_folder)
    print("Upload complete.")


if __name__ == "__main__":
    main()
