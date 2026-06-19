# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      tests/test_folder_store.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Manual test for student folder ID cache storage.
# =============================================================================
#!/usr/bin/env python3

from src.student_folder_store import get_folder_id, save_folder_id


def main():
    student_id = input("Student ID: ").strip()
    current = get_folder_id(student_id)

    if current:
        print(f"Existing folder_id: {current}")
    else:
        print("No folder_id stored.")

    new_value = input("New folder_id to save, or Enter to skip: ").strip()

    if new_value:
        save_folder_id(student_id, new_value)
        print("Saved.")

    print()
    print(f"Current folder_id: {get_folder_id(student_id)}")


if __name__ == "__main__":
    main()
