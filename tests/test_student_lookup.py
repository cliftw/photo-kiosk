# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      tests/test_student_lookup.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Manual test for local roster lookup behavior.
# =============================================================================
#!/usr/bin/env python3

from src.student_lookup import lookup_student


def main():
    student_id = input("Student ID: ").strip()
    student = lookup_student(student_id)

    if student is None:
        print("ID ERROR")
        return

    print()
    print("Student Found")
    print("-------------")
    print(f"ID:     {student['id']}")
    print(f"Name:   {student['name']}")
    print(f"Email:  {student['email']}")
    print(f"Folder: {student['folder_id']}")


if __name__ == "__main__":
    main()
