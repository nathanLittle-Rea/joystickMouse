# Quick Reference - Joystick Mouse

Fast lookup for pinouts, commands, and common issues.

## Pin Assignments

### Joystick
```
GP26 (ADC0) ← X-axis
GP27 (ADC1) ← Y-axis
3.3V        ← VCC
GND         ← GND
```

### Main Buttons
```
GP15 ← Left Click
GP14 ← Right Click
GP13 ← Middle Click
```

### Arrow Buttons
```
GP10 ← Up
GP11 ← Down
GP12 ← Left
GP16 ← Right
```

All buttons: One pin to GPIO, other pin to 3.3V

## Quick Commands

### Flash MicroPython
```bash
# 1. Hold BOOTSEL, plug USB, release
# 2. Drag .uf2 file to RPI-RP2 drive
```

### Upload Code (mpremote)
```bash
mpremote cp main.py :
mpremote cp config.py :
mpremote cp joystick.py :
mpremote cp buttons.py :
mpremote cp hid_mouse.py :
```

### Serial Console
```bash
mpremote repl
# or use Thonny's built-in console
```

### Run Tests
```bash
mpremote run joystick_test.py
mpremote run button_test.py
```

## Expected Values

### Joystick ADC Readings
| Position | X Value | Y Value |
|----------|---------|---------|
| Center | ~32768 | ~32768 |
| Left | ~0 | ~32768 |
| Right | ~65535 | ~32768 |
| Up | ~32768 | ~0 |
| Down | ~32768 | ~65535 |

### Performance Targets
- **Update Rate**: ≥125 Hz
- **Latency**: <8 ms per frame
- **Dead Zone**: 1500-4000 units

## Configuration Presets

### Precision Mode (slow & accurate)
```python
MAX_SPEED = 60
ACCELERATION_EXPONENT = 2.5
DEAD_ZONE = 1500
```

### Gaming Mode (fast & responsive)
```python
MAX_SPEED = 127
ACCELERATION_EXPONENT = 1.5
DEAD_ZONE = 1000
```

### Comfort Mode (balanced)
```python
MAX_SPEED = 100
ACCELERATION_EXPONENT = 2.0
DEAD_ZONE = 2000
```

## Troubleshooting Quick Fixes

### Cursor drifts when centered
```python
# In config.py
DEAD_ZONE = 3000  # Increase
```

### Cursor too fast
```python
MAX_SPEED = 80  # Decrease
```

### Cursor too slow
```python
MAX_SPEED = 127  # Increase
ACCELERATION_EXPONENT = 1.5  # Decrease
```

### Double-clicks instead of single
```python
DEBOUNCE_MS = 40  # Increase
```

### Choppy movement
```python
UPDATE_RATE_HZ = 150  # Increase
```

### Wrong direction
```python
INVERT_X = True  # Flip axis
INVERT_Y = True  # Flip axis
```

## Useful Test Snippets

### Test Joystick Raw Values
```python
from machine import ADC, Pin
x = ADC(Pin(26))
y = ADC(Pin(27))
print(x.read_u16(), y.read_u16())
```

### Test Single Button
```python
from machine import Pin
btn = Pin(15, Pin.IN, Pin.PULL_DOWN)
print(btn.value())  # 1 = pressed, 0 = not pressed
```

### Measure Update Rate
```python
import time
start = time.ticks_us()
# ... your loop code ...
end = time.ticks_us()
fps = 1000000 / (end - start)
print(f"FPS: {fps}")
```

### Calibrate Center Position
```python
from machine import ADC, Pin
import time

x_axis = ADC(Pin(26))
y_axis = ADC(Pin(27))

samples_x = []
samples_y = []

print("Let joystick rest, sampling...")
for i in range(100):
    samples_x.append(x_axis.read_u16())
    samples_y.append(y_axis.read_u16())
    time.sleep(0.01)

center_x = sum(samples_x) // len(samples_x)
center_y = sum(samples_y) // len(samples_y)

print(f"CENTER_X = {center_x}")
print(f"CENTER_Y = {center_y}")
```

## File Structure
```
joystickMouse/
├── README.md           # Full project documentation
├── PROJECT_PLAN.md     # Scrum board & detailed plan
├── SETUP.md           # Step-by-step setup guide
├── QUICKREF.md        # This file
├── config.py          # Configuration parameters
├── main.py            # Main program loop
├── joystick.py        # Joystick input handling
├── buttons.py         # Button debouncing & state
├── hid_mouse.py       # USB HID mouse emulation
└── lib/
    └── usb_hid/       # USB HID library
```

## Key Config Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DEAD_ZONE` | 2000 | Prevent drift |
| `MAX_SPEED` | 127 | Max cursor velocity |
| `ACCELERATION_EXPONENT` | 2.0 | Curve steepness |
| `DEBOUNCE_MS` | 20 | Button debounce |
| `UPDATE_RATE_HZ` | 125 | Loop frequency |

## Hardware Checklist

- [ ] Raspberry Pi Pico
- [ ] Analog joystick module (2-axis)
- [ ] 7x tactile buttons
- [ ] Breadboard
- [ ] Jumper wires (M-M, M-F)
- [ ] Micro USB cable (data capable)

## Software Checklist

- [ ] MicroPython firmware flashed
- [ ] Thonny IDE installed (or mpremote)
- [ ] USB HID library uploaded
- [ ] All .py files on Pico
- [ ] config.py customized

## Test Checklist

- [ ] LED blink test passes
- [ ] Joystick reads 0-65535 on both axes
- [ ] All 7 buttons register press/release
- [ ] OS recognizes HID mouse device
- [ ] Cursor moves in all 8 directions
- [ ] No drift when centered
- [ ] All click types work
- [ ] Arrow buttons move 1 pixel

## Common Error Messages

### `ImportError: no module named 'usb_hid'`
**Fix**: Upload USB HID library to `lib/` folder

### `OSError: [Errno 19] ENODEV`
**Fix**: Check USB connection, try different cable

### `ValueError: pin already in use`
**Fix**: Reset Pico (unplug/replug), check for GPIO conflicts

### `AttributeError: 'Pin' object has no attribute 'read_u16'`
**Fix**: Use ADC, not Pin: `ADC(Pin(26)).read_u16()`

## Useful Links

- MicroPython Docs: https://docs.micropython.org/
- Pico Pinout: https://datasheets.raspberrypi.com/pico/Pico-R3-A4-Pinout.pdf
- USB HID Spec: https://www.usb.org/hid
- Forum: https://forum.micropython.org/

## Emergency Reset

**Soft Reset**: Press Ctrl+C in REPL, then Ctrl+D

**Hard Reset**: Unplug USB, replug

**Factory Reset**: Re-flash MicroPython firmware

## Performance Monitoring

Add to main loop:
```python
import time

frame_count = 0
start_time = time.ticks_ms()

while True:
    # ... your code ...

    frame_count += 1
    if frame_count >= 125:
        elapsed = time.ticks_diff(time.ticks_ms(), start_time)
        fps = (frame_count * 1000) / elapsed
        print(f"FPS: {fps:.1f}")
        frame_count = 0
        start_time = time.ticks_ms()
```

---

**TIP**: Keep this file open while building/debugging!
