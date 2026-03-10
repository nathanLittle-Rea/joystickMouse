"""
OLED display driver for macropad.
Shows current layer name and 4-key labels for the top row.
Uses the ssd1306 library already present on the Pico.
"""
from machine import I2C, Pin
import config

# Import ssd1306 from root (already on device)
import sys
sys.path.insert(0, '/')
import ssd1306

_i2c = I2C(0, sda=Pin(config.I2C_SDA), scl=Pin(config.I2C_SCL), freq=400_000)
_oled = ssd1306.SSD1306_I2C(128, 64, _i2c, addr=config.I2C_ADDR)

_current_layer = -1  # force first draw


def _draw(layer):
    _oled.fill(0)

    # Layer name bar at top
    name = config.LAYER_NAMES[layer]
    _oled.fill_rect(0, 0, 128, 12, 1)
    _oled.text(name, (128 - len(name) * 8) // 2, 2, 0)

    # Show 4 rows x 4 cols of key labels (4 chars each, 8px font = 32px wide per key)
    labels = config.KEY_LABELS[layer]
    for row in range(4):
        for col in range(4):
            idx = row * 4 + col
            label = labels[idx][:4].ljust(4)
            x = col * 32
            y = 14 + row * 12
            _oled.text(label, x, y, 1)

    _oled.show()


def update(layer):
    global _current_layer
    if layer != _current_layer:
        _current_layer = layer
        _draw(layer)


def show_keypress(layer, key_idx):
    """Briefly highlight which key was pressed."""
    row = key_idx // 4
    col = key_idx % 4
    x = col * 32
    y = 14 + row * 12
    _oled.fill_rect(x, y, 32, 12, 1)
    label = config.KEY_LABELS[layer][key_idx][:4].ljust(4)
    _oled.text(label, x, y, 0)
    _oled.show()


def show_message(line1, line2=""):
    """Show a temporary message (caller responsible for restoring)."""
    _oled.fill(0)
    _oled.text(line1, 0, 20, 1)
    if line2:
        _oled.text(line2, 0, 36, 1)
    _oled.show()
