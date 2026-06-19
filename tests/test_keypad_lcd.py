# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      tests/test_keypad_lcd.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Manual integrated test for keypad entry displayed on the LCD.
# =============================================================================
import time

from src.lcd_grove import GroveRgbLcd
from src.keypad_matrix import MatrixKeypad


ID_LENGTH = 6

lcd = GroveRgbLcd(cols=16, rows=2)
keypad = MatrixKeypad()

entry = ""


def display_entry():
    shown = entry + ("_" * (ID_LENGTH - len(entry)))
    lcd.write_line(0, "Enter 6-digit ID")
    lcd.write_line(1, shown)


lcd.set_rgb(0, 128, 255)
display_entry()

try:
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
                    print(f"Student ID entered: {entry}", flush=True)

                    lcd.set_rgb(0, 255, 0)
                    lcd.message("ID received:", entry)

                    time.sleep(1.5)

                    entry = ""
                    lcd.set_rgb(0, 128, 255)
                    display_entry()

                else:
                    lcd.set_rgb(255, 128, 0)
                    lcd.message("Need 6 digits", entry + ("_" * (ID_LENGTH - len(entry))))
                    time.sleep(1.0)
                    lcd.set_rgb(0, 128, 255)
                    display_entry()

        time.sleep(0.02)

except KeyboardInterrupt:
    lcd.clear()
    lcd.set_rgb(0, 0, 0)
    keypad.close()
    lcd.close()
