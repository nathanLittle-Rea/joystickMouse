"""
Button handling module - debounce and state tracking for all buttons
"""
from machine import Pin
import time
import config


class Button:
    """Debounced button with optional repeat support."""

    def __init__(self, pin_num, repeat=False):
        self._pin = Pin(pin_num, Pin.IN, Pin.PULL_DOWN)
        self._repeat = repeat
        self._state = False
        self._last_change_ms = 0
        self._repeat_started = False
        self._last_repeat_ms = 0

    def update(self):
        """
        Call each loop iteration. Returns True if button triggered this tick
        (pressed edge, or repeat event if repeat=True).
        """
        now = time.ticks_ms()
        raw = bool(self._pin.value())

        if raw != self._state:
            if time.ticks_diff(now, self._last_change_ms) >= config.DEBOUNCE_MS:
                self._state = raw
                self._last_change_ms = now
                if raw:
                    self._repeat_started = False
                    return True  # rising edge
        elif self._state and self._repeat:
            if not self._repeat_started:
                if time.ticks_diff(now, self._last_change_ms) >= config.ARROW_REPEAT_INITIAL_DELAY:
                    self._repeat_started = True
                    self._last_repeat_ms = now
                    return True
            else:
                if time.ticks_diff(now, self._last_repeat_ms) >= config.ARROW_REPEAT_RATE:
                    self._last_repeat_ms = now
                    return True

        return False

    @property
    def pressed(self):
        return self._state


# Main click buttons (no repeat)
left   = Button(config.BUTTON_LEFT)
right  = Button(config.BUTTON_RIGHT)
middle = Button(config.BUTTON_MIDDLE)

# Arrow buttons (with repeat)
arrow_up    = Button(config.BUTTON_ARROW_UP,    repeat=True)
arrow_down  = Button(config.BUTTON_ARROW_DOWN,  repeat=True)
arrow_left  = Button(config.BUTTON_ARROW_LEFT,  repeat=True)
arrow_right = Button(config.BUTTON_ARROW_RIGHT, repeat=True)

ALL_BUTTONS = [left, right, middle, arrow_up, arrow_down, arrow_left, arrow_right]


def update_all():
    """Update all buttons. Returns dict of triggered events."""
    return {
        'left':        left.update(),
        'right':       right.update(),
        'middle':      middle.update(),
        'arrow_up':    arrow_up.update(),
        'arrow_down':  arrow_down.update(),
        'arrow_left':  arrow_left.update(),
        'arrow_right': arrow_right.update(),
    }


def get_click_byte():
    """Return HID button byte: bit0=left, bit1=right, bit2=middle."""
    return (left.pressed | (right.pressed << 1) | (middle.pressed << 2))
