# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      tests/test_keypad.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Manual test for keypad scanning and debounce behavior.
# =============================================================================
import time
from src.keypad_matrix import MatrixKeypad

keypad = MatrixKeypad()

print("Press keys. Ctrl-C to quit.")
print("* = backspace later, # = enter later")

try:
    while True:
        key = keypad.get_key()
        if key:
            print(key, flush=True)
        time.sleep(0.02)

except KeyboardInterrupt:
    keypad.close()
    print("\nDone.")
