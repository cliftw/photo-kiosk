# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      tests/test_lcd_tiny.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Minimal LCD hardware smoke test.
# =============================================================================
import time
from smbus2 import SMBus

LCD_ADDR = 0x3e
RGB_ADDR = 0x62

bus = SMBus(1)

def cmd(x):
    bus.write_byte_data(LCD_ADDR, 0x80, x)

def data(x):
    bus.write_byte_data(LCD_ADDR, 0x40, x)

def set_rgb(r, g, b):
    bus.write_byte_data(RGB_ADDR, 0x00, 0x00)
    bus.write_byte_data(RGB_ADDR, 0x01, 0x00)
    bus.write_byte_data(RGB_ADDR, 0x08, 0xaa)
    bus.write_byte_data(RGB_ADDR, 0x04, r)
    bus.write_byte_data(RGB_ADDR, 0x03, g)
    bus.write_byte_data(RGB_ADDR, 0x02, b)

time.sleep(0.05)
cmd(0x38)
cmd(0x39)
cmd(0x14)
cmd(0x70)
cmd(0x56)
cmd(0x6c)
time.sleep(0.2)
cmd(0x38)
cmd(0x0c)
cmd(0x01)
time.sleep(0.002)

set_rgb(0, 128, 255)

for ch in "Hello Wayne":
    data(ord(ch))

cmd(0xc0)

for ch in "LCD Works":
    data(ord(ch))

time.sleep(10)
bus.close()
