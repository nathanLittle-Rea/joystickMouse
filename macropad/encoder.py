"""
Rotary encoder reader (EC11 or compatible).
Detects CW/CCW rotation and button press.
"""
from machine import Pin
import time
import config

_clk = Pin(config.ENC_CLK, Pin.IN, Pin.PULL_UP)
_dt  = Pin(config.ENC_DT,  Pin.IN, Pin.PULL_UP)
_sw  = Pin(config.ENC_SW,  Pin.IN, Pin.PULL_UP)  # active LOW

_last_clk = _clk.value()
_sw_state = True   # released
_sw_last_change = 0

# Pending events
_delta = 0   # +1 CW, -1 CCW per tick
_btn_pressed = False


def update():
    """Call each loop iteration. Accumulates rotation and button events."""
    global _last_clk, _sw_state, _sw_last_change, _delta, _btn_pressed

    clk = _clk.value()
    dt  = _dt.value()

    if clk != _last_clk:
        _last_clk = clk
        if clk == 0:  # falling edge
            if dt == 1:
                _delta += 1   # CW
            else:
                _delta -= 1   # CCW

    now = time.ticks_ms()
    sw_raw = bool(_sw.value())  # active LOW → False = pressed
    if sw_raw != _sw_state:
        if time.ticks_diff(now, _sw_last_change) >= config.DEBOUNCE_MS:
            _sw_state = sw_raw
            _sw_last_change = now
            if not sw_raw:  # falling edge = press
                _btn_pressed = True


def consume():
    """
    Returns (delta, btn_pressed) and resets pending state.
    delta: integer, positive=CW, negative=CCW
    """
    global _delta, _btn_pressed
    d = _delta
    b = _btn_pressed
    _delta = 0
    _btn_pressed = False
    return d, b
