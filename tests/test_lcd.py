# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      tests/test_lcd.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Manual test for LCD messages and RGB backlight colors.
# =============================================================================
import random
import time

from src.lcd_grove import GroveRgbLcd


lcd = GroveRgbLcd(cols=16, rows=2)

messages = [
    ("Photo Kiosk", "Ready"),
    ("Insert camera", "Waiting..."),
    ("Enter ID", "______"),
    ("Uploading", "Please wait"),
    ("Done", "Remove camera"),
]

colors = [
    (0, 128, 255),
    (0, 255, 0),
    (255, 128, 0),
    (255, 0, 0),
    (128, 0, 255),
]

try:
    while True:
        line1, line2 = random.choice(messages)
        r, g, b = random.choice(colors)

        lcd.set_rgb(r, g, b)
        lcd.message(line1, line2)

        time.sleep(2)

except KeyboardInterrupt:
    lcd.clear()
    lcd.set_rgb(0, 0, 0)
    lcd.close()
