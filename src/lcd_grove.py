# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/lcd_grove.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Drives the Grove RGB I2C character LCD display.
# =============================================================================
import time
from smbus2 import SMBus


class GroveRgbLcd:
    LCD_ADDR = 0x3E
    RGB_ADDR = 0x62

    def __init__(self, bus_num=1, cols=16, rows=2):
        self.bus = SMBus(bus_num)
        self.cols = cols
        self.rows = rows
        self._init_lcd()
        self.set_rgb(0, 128, 255)
        self.clear()

    def _cmd(self, value):
        self.bus.write_byte_data(self.LCD_ADDR, 0x80, value)

    def _data(self, value):
        self.bus.write_byte_data(self.LCD_ADDR, 0x40, value)

    def _init_lcd(self):
        time.sleep(0.05)
        self._cmd(0x38)
        self._cmd(0x39)
        self._cmd(0x14)
        self._cmd(0x70)
        self._cmd(0x56)
        self._cmd(0x6C)
        time.sleep(0.2)
        self._cmd(0x38)
        self._cmd(0x0C)
        self.clear()

    def clear(self):
        self._cmd(0x01)
        time.sleep(0.002)

    def set_rgb(self, r, g, b):
        self.bus.write_byte_data(self.RGB_ADDR, 0x00, 0x00)
        self.bus.write_byte_data(self.RGB_ADDR, 0x01, 0x00)
        self.bus.write_byte_data(self.RGB_ADDR, 0x08, 0xAA)
        self.bus.write_byte_data(self.RGB_ADDR, 0x04, r)
        self.bus.write_byte_data(self.RGB_ADDR, 0x03, g)
        self.bus.write_byte_data(self.RGB_ADDR, 0x02, b)

    def set_cursor(self, col, row):
        offsets = [0x00, 0x40]
        self._cmd(0x80 | (col + offsets[row]))

    def write_line(self, row, text):
        text = str(text)[:self.cols].ljust(self.cols)
        self.set_cursor(0, row)
        for ch in text:
            self._data(ord(ch))

    def message(self, line1="", line2=""):
        self.write_line(0, line1)
        self.write_line(1, line2)

    def close(self):
        self.bus.close()

    def display_off(self):
        self._cmd(0x08)

    def display_on(self):
        self._cmd(0x0C)

    def backlight_off(self):
        self.set_rgb(0, 0, 0)

    def idle_off(self):
        self.clear()
        self.display_off()
        self.backlight_off()
        time.sleep(2.0)
        
    def wake(self):
        self.display_on()
        self.set_rgb(0, 128, 255)
