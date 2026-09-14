# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      tests/test_workflow.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Legacy terminal workflow test for the photo import and upload path.
# =============================================================================
#!/usr/bin/env python3

from src.device_detect import device_status
from src.student_lookup import lookup_student
from src.student_folder_store import get_folder_id, save_folder_id
from src.filesystem_import import import_from_filesystem
from src.gphoto2_import import import_from_gphoto2
from src.google_drive_api import (
    get_or_create_student_folder,
    share_folder_with_student,
    upload_file_to_folder,
    get_next_upload_number,
)


def get_or_setup_student_folder(student):
    folder_id = get_folder_id(student["id"])

    if folder_id:
        print(f"Using existing folder_id: {folder_id}")
        return folder_id

    print("No folder_id found.")
    print("Creating student folder...")

    folder_id = get_or_create_student_folder(student)

    print(f"Folder ID: {folder_id}")
    print("Sharing folder with student as viewer...")

    share_folder_with_student(folder_id, student["email"])

    save_folder_id(student["id"], folder_id)

    print("Folder shared and saved.")
    return folder_id


def main():
    status, devices = device_status()

    if status == "none":
        print("NO DEVICE")
        return

    if status == "too_many":
        print("TOO MANY DEVICES")
        print("Please connect only one camera or USB source.")
        return

    device = devices[0]

    print("Device detected:")
    print(f"Type: {device['type']}")
    print(f"Description: {device['description']}")

    if "mount_path" in device:
        print(f"Mount path: {device['mount_path']}")

    print()

    student_id = input("Student ID: ").strip()
    student = lookup_student(student_id)

    if student is None:
        print("ID ERROR")
        return

    print(f"Student: {student['name']}")
    print(f"Email:   {student['email']}")
    print()

    folder_id = get_or_setup_student_folder(student)

    print()
    print("Choose import mode:")
    print("  Press Enter = COPY ONLY")
    print("  Type DELETE = COPY, THEN DELETE SOURCE IMAGES")
    print()

    confirm = input("> ").strip()
    delete_after_import = confirm == "DELETE"

    if delete_after_import:
        print("Delete mode enabled.")
    else:
        print("Copy-only mode enabled.")

    print()

    if device["type"] == "gphoto":
        result = import_from_gphoto2(
            student_id=student["id"],
            delete_after_import=delete_after_import,
        )

    elif device["type"] == "usb_storage":
        result = import_from_filesystem(
            mount_path=device["mount_path"],
            student_id=student["id"],
            delete_after_import=delete_after_import,
        )

    else:
        print(f"Unsupported device type: {device['type']}")
        return

    imported_files = result["imported_files"]
    deleted_files = result["deleted_files"]

    print()
    print(f"Imported {len(imported_files)} file(s).")
    print(f"Deleted {len(deleted_files)} source file(s).")
    print(f"Archive folder: {result['destination_dir']}")
    print()

    if not imported_files:
        print("No images found. Nothing to upload.")
        return

    print("Uploading to student Drive folder...")
    print()

    upload_number = get_next_upload_number(folder_id)
    upload_prefix = f"U{upload_number:03d}_"

    for path in imported_files:
        drive_filename = f"{upload_prefix}{path.name}"
        print(f"Uploading {drive_filename}...")
        uploaded = upload_file_to_folder(
            path,
            folder_id,
            drive_filename=drive_filename,
        )
        print(f"{uploaded['action'].title()}: {uploaded['name']}")

    print()
    print("WORKFLOW COMPLETE")


if __name__ == "__main__":
    main()
