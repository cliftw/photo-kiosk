# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/student_id_entry.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Collects and validates six-digit keypad student ID entry.
# =============================================================================
import time


ID_LENGTH = 6


def get_student_id(lcd, keypad):
    entry = ""

    def display_entry():
        shown = entry + ("_" * (ID_LENGTH - len(entry)))
        lcd.write_line(0, "Enter 6-digit ID")
        lcd.write_line(1, shown)

    lcd.set_rgb(0, 128, 255)
    display_entry()

    while True:
        key = keypad.get_key()

        if key:

            if key.isdigit():
                if len(entry) < ID_LENGTH:
                    entry += key
                    display_entry()

            elif key == "*":
                if entry:
                    entry = entry[:-1]
                    display_entry()

            elif key == "#":

                if len(entry) == ID_LENGTH:
                    lcd.set_rgb(0, 128, 255)
                    lcd.message("Checking ID", entry)
                    time.sleep(1.0)
                    return entry

                lcd.set_rgb(255, 128, 0)
                lcd.message("Need 6 digits",
                            entry + ("_" * (ID_LENGTH - len(entry))))
                time.sleep(1.0)

                lcd.set_rgb(0, 128, 255)
                display_entry()

        time.sleep(0.02)
