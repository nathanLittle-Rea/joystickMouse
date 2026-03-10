"""
4x4 key matrix scanner with debounce.
Rows are driven HIGH one at a time; columns are read with pull-down.
A diode (cathode toward row) on each switch prevents ghosting.
"""
from machine import Pin
import time
import config

_rows = [Pin(p, Pin.OUT, value=0) for p in config.ROW_PINS]
_cols = [Pin(p, Pin.IN, Pin.PULL_DOWN) for p in config.COL_PINS]

# Debounce state: raw and confirmed
_raw      = [False] * 16
_state    = [False] * 16
_last_ms  = [0] * 16


def scan():
    """
    Scan the matrix. Returns list of 16 bools (True = pressed).
    Updates internal debounce state.
    """
    now = time.ticks_ms()

    for r, row_pin in enumerate(_rows):
        row_pin.value(1)
        for c, col_pin in enumerate(_cols):
            idx = r * 4 + c
            raw = bool(col_pin.value())
            if raw != _raw[idx]:
                _raw[idx] = raw
                _last_ms[idx] = now
            elif time.ticks_diff(now, _last_ms[idx]) >= config.DEBOUNCE_MS:
                _state[idx] = raw
        row_pin.value(0)

    return list(_state)


def get_events(prev, curr):
    """
    Compare previous and current state lists.
    Returns (pressed_indices, released_indices).
    """
    pressed  = [i for i in range(16) if curr[i] and not prev[i]]
    released = [i for i in range(16) if not curr[i] and prev[i]]
    return pressed, released
