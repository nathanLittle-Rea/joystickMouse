"""
Main loop for Joystick Mouse
Runs at UPDATE_RATE_HZ, reads joystick + buttons and sends HID reports
"""
import time
import config
import joystick
import buttons
import hid_mouse

config.validate_config()

if config.DEBUG_PERFORMANCE:
    _perf_last = time.ticks_ms()
    _perf_frames = 0

while True:
    loop_start = time.ticks_ms()

    # --- Update button states ---
    events = buttons.update_all()

    # --- Build movement delta ---
    dx, dy = joystick.get_mouse_delta()

    # Arrow buttons override joystick movement
    if events['arrow_up']:
        dy = -config.ARROW_PIXELS_PER_PRESS
        dx = 0
    elif events['arrow_down']:
        dy = config.ARROW_PIXELS_PER_PRESS
        dx = 0
    elif events['arrow_left']:
        dx = -config.ARROW_PIXELS_PER_PRESS
        dy = 0
    elif events['arrow_right']:
        dx = config.ARROW_PIXELS_PER_PRESS
        dy = 0

    # --- Build HID button byte ---
    btn_byte = buttons.get_click_byte()

    # --- Send HID report ---
    hid_mouse.move(btn_byte, dx, dy)

    # --- Performance debug ---
    if config.DEBUG_PERFORMANCE:
        _perf_frames += 1
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, _perf_last)
        if elapsed >= int(config.DEBUG_PRINT_INTERVAL * 1000):
            fps = _perf_frames * 1000 // elapsed
            print("FPS:", fps)
            _perf_frames = 0
            _perf_last = now

    # --- Rate limiting ---
    elapsed = time.ticks_diff(time.ticks_ms(), loop_start)
    remaining = config.LOOP_DELAY_MS - elapsed
    if remaining > 0:
        time.sleep_ms(remaining)
