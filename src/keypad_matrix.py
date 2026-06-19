# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/keypad_matrix.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Scans the matrix keypad and returns debounced keypresses.
# =============================================================================
import time
from gpiozero import DigitalOutputDevice, DigitalInputDevice


class MatrixKeypad:
    def __init__(self):
        self.row_pins = [18, 23, 24, 25]  # R1, R2, R3, R4
        self.col_pins = [12, 16, 20]      # C1, C2, C3

        self.keys = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["*", "0", "#"],
        ]

        self.rows = [
            DigitalOutputDevice(pin, active_high=True, initial_value=False)
            for pin in self.row_pins
        ]

        self.cols = [
            DigitalInputDevice(pin, pull_up=False)
            for pin in self.col_pins
        ]

        self.last_key = None

    def scan(self):
        for r, row in enumerate(self.rows):
            row.on()
            time.sleep(0.001)

            for c, col in enumerate(self.cols):
                if col.value:
                    row.off()
                    return self.keys[r][c]

            row.off()

        return None

    def get_key(self):
        key = self.scan()

        if key is not None and self.last_key is None:
            self.last_key = key
            return key

        if key is None:
            self.last_key = None

        return None

    def close(self):
        for row in self.rows:
            row.close()
        for col in self.cols:
            col.close()
