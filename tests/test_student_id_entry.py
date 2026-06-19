# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      tests/test_student_id_entry.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Manual test for reusable six-digit student ID entry.
# =============================================================================
from src.lcd_grove import GroveRgbLcd
from src.keypad_matrix import MatrixKeypad
from src.student_id_entry import get_student_id


lcd = GroveRgbLcd()
keypad = MatrixKeypad()

try:

    while True:

        student_id = get_student_id(lcd, keypad)

        print(f"ID returned: {student_id}")

        lcd.message("Returned ID:", student_id)

except KeyboardInterrupt:

    lcd.clear()
    lcd.set_rgb(0, 0, 0)

    keypad.close()
    lcd.close()
