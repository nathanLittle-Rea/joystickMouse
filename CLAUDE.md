# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **MicroPython hardware project** to replace a traditional computer mouse with a thumb-operated joystick controller. The code runs on a **Raspberry Pi Pico** (RP2040) and emulates a USB HID mouse device.

**Key Technologies:**
- **MicroPython** on Raspberry Pi Pico
- **USB HID** protocol for mouse emulation
- **ADC input** for analog joystick (2-axis)
- **GPIO** for 7 buttons (3 main clicks + 4 arrow keys)

## Hardware Pin Configuration

**Critical: These GPIO assignments are hardcoded in config.py and must match physical wiring:**

```
Joystick (Analog Input):
  GP26 (ADC0) ← X-axis
  GP27 (ADC1) ← Y-axis

Main Click Buttons:
  GP15 ← Left Click
  GP14 ← Right Click
  GP13 ← Middle Click

Arrow Buttons (Precision):
  GP10 ← Up
  GP11 ← Down
  GP12 ← Left
  GP16 ← Right
```

All buttons use `Pin.PULL_DOWN` and connect between GPIO pin and 3.3V.

## Architecture

### Module Structure

The codebase follows a modular design:

```
main.py          → Main loop orchestrates everything
joystick.py      → Read ADC, apply dead zone, return velocity
buttons.py       → Debounce buttons, track state
hid_mouse.py     → USB HID descriptor, send mouse reports
config.py        → All tunable parameters (dead zone, acceleration, etc.)
lib/usb_hid/     → USB HID library (third-party)
```

### Data Flow

```
Hardware → ADC/GPIO → Processing → USB HID → OS
             ↓           ↓           ↓
         joystick.py  config.py  hid_mouse.py
         buttons.py   (dead zone) (mouse reports)
                      (accel curve)
```

### Key Algorithms

**Dead Zone** (prevents drift):
- Raw joystick center ≈ 32768 (16-bit ADC)
- If `abs(value - CENTER) < DEAD_ZONE`, return 0
- Implemented in `config.py::apply_dead_zone()`

**Acceleration Curve** (natural feel):
- Quadratic by default (`exponent=2.0`)
- `velocity = (normalized ** exponent) * sign * MAX_SPEED`
- Small movements = slow/precise, large = fast
- Implemented in `config.py::apply_acceleration()`

**Button Debouncing**:
- Software debounce with configurable delay (default 20ms)
- Tracks last state change time
- Implemented in `buttons.py::Button` class

## Development Workflow

### Upload Code to Pico

**Using Thonny IDE:**
1. Open file in Thonny
2. File > Save as... > Raspberry Pi Pico
3. Run current script (F5)

**Using mpremote (CLI):**
```bash
mpremote cp main.py :
mpremote cp config.py :
mpremote cp joystick.py :
mpremote cp buttons.py :
mpremote cp hid_mouse.py :
mpremote cp -r lib :
```

### Testing

**Test joystick input (no HID):**
```python
from machine import ADC, Pin
x = ADC(Pin(26))
y = ADC(Pin(27))
print(x.read_u16(), y.read_u16())  # Should be ~32768 centered
```

**Test single button:**
```python
from machine import Pin
btn = Pin(15, Pin.IN, Pin.PULL_DOWN)
print(btn.value())  # 1 = pressed, 0 = released
```

**Calibrate center position:**
```python
# Average 100 samples while joystick rests
from machine import ADC, Pin
import time
x_axis = ADC(Pin(26))
samples = [x_axis.read_u16() for _ in range(100)]
center = sum(samples) // len(samples)
print(f"CENTER_X = {center}")  # Update in config.py
```

**Monitor update rate:**
```python
import time
start = time.ticks_us()
# ... main loop iteration ...
fps = 1000000 / (time.ticks_us() - start)
print(f"FPS: {fps}")  # Target: 125Hz
```

### Serial Console Access

**Thonny:** Built-in REPL at bottom of window

**mpremote:**
```bash
mpremote repl  # Enter REPL
# Ctrl+C to interrupt, Ctrl+D to soft reset, Ctrl+X to exit
```

## Configuration Tuning

All tunable parameters are in `config.py`. **Never hardcode values in other modules.**

### Common Adjustments

**Cursor drifts when centered:**
```python
DEAD_ZONE = 3000  # Increase from default 2000
```

**Cursor too fast/slow:**
```python
MAX_SPEED = 80            # Decrease for slower
ACCELERATION_EXPONENT = 2.5  # Increase for gentler curve
```

**Double-clicks instead of single:**
```python
DEBOUNCE_MS = 40  # Increase from default 20
```

**Choppy movement:**
```python
UPDATE_RATE_HZ = 150  # Increase from default 125
```

### Configuration Presets

Three preset configurations are commented out in `config.py`:
- **Precision Mode**: Slow max speed, gentle curve
- **Gaming Mode**: Fast max speed, aggressive curve
- **Comfort Mode**: Balanced (default values)

## Implementation Status

**Completed (Planning Phase):**
- ✅ Documentation (README.md, PROJECT_PLAN.md, SETUP.md)
- ✅ Configuration structure (config.py)
- ✅ Pin assignments defined

**Not Yet Implemented:**
- ❌ `main.py` - main loop
- ❌ `joystick.py` - ADC reading module
- ❌ `buttons.py` - button handling module
- ❌ `hid_mouse.py` - USB HID implementation
- ❌ USB HID library in `lib/`
- ❌ Hardware wiring
- ❌ Testing/calibration

**Follow PROJECT_PLAN.md for implementation order (5 sprints).**

## Important Constraints

### Hardware Limitations

- **ADC Resolution**: 16-bit (0-65535), not perfectly centered at 32768
- **HID Mouse Limits**: Movement delta is -127 to +127 per report
- **Update Rate**: Target 125Hz (USB HID standard), max ~250Hz
- **Button Count**: 7 GPIO pins allocated (expandable up to ~20)

### MicroPython Limitations

- No floating-point in tight loops (use integer math)
- Limited RAM (~264KB)
- No external libraries except what's in `lib/`
- USB HID requires specific library (CircuitPython port or custom)

### USB HID Requirements

- **HID Descriptor** must match report format exactly
- **Report Format**: `[buttons, x_delta, y_delta, wheel, reserved]`
  - Byte 0: Button bits (0=left, 1=right, 2=middle)
  - Byte 1: X movement (-127 to +127)
  - Byte 2: Y movement (-127 to +127)
  - Bytes 3-4: Wheel/reserved (optional)

## Critical Implementation Notes

### When Implementing joystick.py

- **Must** use `ADC(Pin(26))` for X-axis, `ADC(Pin(27))` for Y-axis
- **Must** call `read_u16()` for 16-bit resolution (don't use `read_u12()`)
- **Must** import dead zone functions from `config.py`
- Implement smoothing if `SMOOTHING_FACTOR > 0` in config
- Return velocity in range -32767 to +32767 (raw offset from center)

### When Implementing buttons.py

- **Must** use `Pin(pin_num, Pin.IN, Pin.PULL_DOWN)` for all buttons
- **Must** implement debouncing using `time.ticks_ms()` and `time.ticks_diff()`
- Track both current state and last state change time
- Arrow buttons need repeat functionality (initial delay + repeat rate)
- Main buttons only need debounce (no repeat)

### When Implementing hid_mouse.py

- **Critical**: USB HID library research required (Sprint 2, Story 2.1)
- Potential libraries: CircuitPython `usb_hid`, custom RP2040 implementation
- Must create proper HID mouse descriptor
- Must handle button bit packing: `buttons = (left | right<<1 | middle<<2)`
- Must clamp X/Y to -127 to +127 range before sending

### When Implementing main.py

- **Must** run at UPDATE_RATE_HZ (default 125Hz)
- Loop structure:
  1. Read joystick velocity
  2. Apply acceleration curve
  3. Read button states
  4. Combine into HID report
  5. Send HID report
  6. Sleep for LOOP_DELAY_MS
- Handle arrow buttons separately (override joystick if arrow pressed)
- Optionally print FPS if DEBUG_PERFORMANCE enabled

## Troubleshooting Guide

### Device Not Recognized

1. Verify MicroPython firmware flashed correctly
2. Check USB HID library installed in `lib/`
3. Verify HID descriptor format matches OS expectations
4. Check console for error messages

### Joystick Not Reading

1. Check wiring: VCC=3.3V, GND=GND, VRx=GP26, VRy=GP27
2. Verify ADC pins initialized correctly
3. Test with `ADC(Pin(26)).read_u16()` in REPL
4. Check if joystick module is 3.3V compatible

### Buttons Not Working

1. Verify PULL_DOWN enabled in Pin initialization
2. Check wiring: one pin to GPIO, other to 3.3V
3. Test with `Pin(15, Pin.IN, Pin.PULL_DOWN).value()` in REPL
4. Increase DEBOUNCE_MS if getting spurious clicks

### Performance Issues

1. Profile main loop to find bottlenecks
2. Reduce print statements (they're slow)
3. Use integer math instead of float
4. Consider lookup tables for acceleration curve
5. Check UPDATE_RATE_HZ isn't too high for hardware

## References

**MicroPython:**
- Official docs: https://docs.micropython.org/
- Pico quick ref: https://docs.micropython.org/en/latest/rp2/quickref.html

**USB HID:**
- USB HID spec: https://www.usb.org/hid
- Mouse report format: https://www.usb.org/sites/default/files/hid1_11.pdf

**Hardware:**
- Pico pinout: https://datasheets.raspberrypi.com/pico/Pico-R3-A4-Pinout.pdf
- RP2040 datasheet: https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf
