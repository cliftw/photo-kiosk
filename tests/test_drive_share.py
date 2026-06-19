# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      tests/test_drive_share.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Manual test for Google Drive folder sharing behavior.
# =============================================================================
#!/usr/bin/env python3

from src.student_lookup import lookup_student
from src.student_folder_store import get_folder_id, save_folder_id
from src.google_drive_api import (
    get_or_create_student_folder,
    share_folder_with_student,
)


def main():
    student_id = input("Student ID: ").strip()
    student = lookup_student(student_id)

    if student is None:
        print("ID ERROR")
        return

    print(f"Student: {student['name']}")
    print(f"Email:   {student['email']}")
    print()

    folder_id = get_folder_id(student["id"])

    if folder_id:
        print(f"Existing folder_id: {folder_id}")
        print("No folder created.")
    else:
        folder_id = get_or_create_student_folder(student)
        save_folder_id(student["id"], folder_id)

        print(f"Created/found folder_id: {folder_id}")
        print("Saved folder_id to data/student_folders.csv")

    print()

    confirm = input("Type SHARE to share this folder with the student: ").strip()

    if confirm != "SHARE":
        print("Cancelled.")
        return

    permission_id = share_folder_with_student(folder_id, student["email"])

    print()
    print("Share complete.")
    print(f"Permission ID: {permission_id}")


if __name__ == "__main__":
    main()
