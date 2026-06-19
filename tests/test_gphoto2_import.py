# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      tests/test_gphoto2_import.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Manual test for importing photos through gphoto2.
# =============================================================================
#!/usr/bin/env python3

from src.device_detect import device_status
from src.student_lookup import lookup_student
from src.gphoto2_import import import_from_gphoto2


def main():
    status, devices = device_status()

    if status == "none":
        print("NO DEVICE")
        return

    if status == "too_many":
        print("TOO MANY DEVICES")
        return

    device = devices[0]

    if device["type"] != "gphoto":
        print(f"DEVICE IS NOT GPHOTO2 CAMERA: {device['type']}")
        return

    student_id = input("Student ID: ").strip()
    student = lookup_student(student_id)

    if student is None:
        print("ID ERROR")
        return

    print(f"Student: {student['name']}")
    print()

    print("WARNING: This test can delete image files from the camera.")
    print("Only continue if the camera photos are expendable.")
    print()

    confirm = input("Type DELETE to import and delete source images: ").strip()
    delete_after_import = confirm == "DELETE"

    result = import_from_gphoto2(
        student_id=student["id"],
        delete_after_import=delete_after_import,
    )

    print()
    print(f"Destination: {result['destination_dir']}")
    print(f"Imported {len(result['imported_files'])} file(s).")
    print(f"Deleted {len(result['deleted_files'])} source file(s).")


if __name__ == "__main__":
    main()
