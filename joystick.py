"""
Joystick module - reads ADC inputs and returns processed velocity
"""
from machine import ADC, Pin
import config

x_axis = ADC(Pin(26))
y_axis = ADC(Pin(27))

_smooth_x = 0
_smooth_y = 0


def read():
    """
    Read joystick and return (vx, vy) velocity tuple.
    Values are in range -MAX_DEFLECTION to +MAX_DEFLECTION after dead zone,
    ready for acceleration curve processing.
    """
    global _smooth_x, _smooth_y

    raw_x = x_axis.read_u16()
    raw_y = y_axis.read_u16()

    vx = config.apply_dead_zone(raw_x, config.CENTER_X, config.DEAD_ZONE)
    vy = config.apply_dead_zone(raw_y, config.CENTER_Y, config.DEAD_ZONE)

    if config.INVERT_X:
        vx = -vx
    if config.INVERT_Y:
        vy = -vy

    if config.SMOOTHING_FACTOR > 0.0:
        f = config.SMOOTHING_FACTOR
        _smooth_x = int(_smooth_x * f + vx * (1.0 - f))
        _smooth_y = int(_smooth_y * f + vy * (1.0 - f))
        vx = _smooth_x
        vy = _smooth_y

    return vx, vy


def get_mouse_delta():
    """
    Read joystick and return (dx, dy) ready to send in HID report (-127 to 127).
    """
    vx, vy = read()
    dx = config.apply_acceleration(vx, config.MAX_DEFLECTION, config.ACCELERATION_EXPONENT, config.MAX_SPEED)
    dy = config.apply_acceleration(vy, config.MAX_DEFLECTION, config.ACCELERATION_EXPONENT, config.MAX_SPEED)
    return dx, dy
