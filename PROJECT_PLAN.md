# Joystick Mouse - Project Plan

## Sprint Overview

| Sprint | Focus | Duration | Stories |
|--------|-------|----------|---------|
| Sprint 1 | Foundation & Input | 2-3 days | 3 stories |
| Sprint 2 | USB HID Emulation | 2-3 days | 3 stories |
| Sprint 3 | Click Functionality | 1-2 days | 1 story |
| Sprint 4 | Precision Control | 1-2 days | 1 story |
| Sprint 5 | Polish & Tuning | 2-3 days | 1 story |

**Total Estimated Time**: 8-13 days (working part-time)

---

## SPRINT 1: Foundation & Basic Input

**Goal**: Read joystick input and handle dead zones

### Story 1.1: Development Environment Setup
**Priority**: CRITICAL
**Story Points**: 2
**Assignee**: Developer

**User Story**:
*As a developer, I need to set up my development environment so that I can write and test MicroPython code on the Pico.*

**Acceptance Criteria**:
- [ ] MicroPython firmware successfully flashed to Pico
- [ ] Thonny IDE installed and configured
- [ ] Can upload and run "Hello World" blink script
- [ ] Serial console shows print statements
- [ ] Pico reconnects properly after code upload

**Tasks**:
1. Download MicroPython UF2 from official site
2. Flash firmware using BOOTSEL method
3. Install Thonny IDE
4. Configure Thonny for Pico (select interpreter)
5. Write LED blink test (GP25 onboard LED)
6. Verify serial console output
7. Test code persistence across reboots

**Verification**:
```python
# test_blink.py
from machine import Pin
import time

led = Pin(25, Pin.OUT)
for i in range(10):
    led.toggle()
    print(f"Blink {i}")
    time.sleep(0.5)
```

**Definition of Done**:
- LED blinks 10 times
- Console shows "Blink 0" through "Blink 9"
- Code runs automatically on power-up

---

### Story 1.2: Joystick Input Reading
**Priority**: HIGH
**Story Points**: 3
**Assignee**: Developer

**User Story**:
*As a user, I want the system to read my joystick movements so that I can eventually control the cursor.*

**Acceptance Criteria**:
- [ ] X-axis values range from ~0 to ~65535
- [ ] Y-axis values range from ~0 to ~65535
- [ ] Centered position reads approximately 32768 on both axes
- [ ] Values update at minimum 60Hz
- [ ] No missing samples or glitches

**Wiring**:
- Joystick VCC → Pico 3.3V (Pin 36)
- Joystick GND → Pico GND (Pin 38)
- Joystick VRx → Pico GP26/ADC0 (Pin 31)
- Joystick VRy → Pico GP27/ADC1 (Pin 32)

**Tasks**:
1. Wire joystick module to Pico
2. Create `joystick.py` module
3. Initialize ADC pins (GP26, GP27)
4. Implement `read_raw()` function
5. Add timestamp tracking for update rate
6. Test full range of motion
7. Document center position values

**Code Template**:
```python
# joystick.py
from machine import ADC, Pin
import time

class Joystick:
    def __init__(self, x_pin=26, y_pin=27):
        self.x_axis = ADC(Pin(x_pin))
        self.y_axis = ADC(Pin(y_pin))

    def read_raw(self):
        """Returns (x, y) raw ADC values 0-65535"""
        x = self.x_axis.read_u16()
        y = self.y_axis.read_u16()
        return (x, y)

# Test
joy = Joystick()
while True:
    x, y = joy.read_raw()
    print(f"X: {x:5d}  Y: {y:5d}")
    time.sleep(0.016)  # ~60Hz
```

**Definition of Done**:
- Console shows live X/Y values
- Values respond to joystick movement in all directions
- Update rate measured at 60Hz or higher

---

### Story 1.3: Dead Zone Implementation
**Priority**: HIGH
**Story Points**: 2
**Assignee**: Developer

**User Story**:
*As a user, I want the cursor to remain stationary when I'm not touching the joystick, preventing unwanted drift.*

**Acceptance Criteria**:
- [ ] Centered joystick outputs (0, 0) velocity
- [ ] Small movements within dead zone are ignored
- [ ] Movement outside dead zone is smooth (no sudden jumps)
- [ ] Dead zone is configurable
- [ ] Works for all joystick types (slight variance in center point)

**Tasks**:
1. Measure center point value (let joystick rest, average 100 samples)
2. Define dead zone threshold (start with ±2000)
3. Implement `apply_dead_zone()` function
4. Implement `get_velocity()` function
5. Test with various dead zone sizes
6. Add to `config.py` as tunable parameter

**Algorithm**:
```python
# config.py
CENTER_X = 32768  # Calibrated center
CENTER_Y = 32768
DEAD_ZONE = 2000  # Adjust based on joystick

# joystick.py
def apply_dead_zone(value, center, dead_zone):
    """
    Returns offset from center, or 0 if within dead zone
    """
    offset = value - center
    if abs(offset) < dead_zone:
        return 0
    return offset

def get_velocity(self):
    """Returns (vx, vy) velocity values"""
    x_raw, y_raw = self.read_raw()
    vx = apply_dead_zone(x_raw, CENTER_X, DEAD_ZONE)
    vy = apply_dead_zone(y_raw, CENTER_Y, DEAD_ZONE)
    return (vx, vy)
```

**Testing**:
- Let joystick rest: Should output (0, 0)
- Barely move joystick: Should output (0, 0)
- Move just outside dead zone: Should output small non-zero values
- Move to extremes: Should output large values

**Definition of Done**:
- No output when joystick is centered
- Smooth transition at dead zone boundary
- Configuration parameter works correctly

---

## SPRINT 2: USB HID Mouse Emulation

**Goal**: Get computer to recognize Pico as mouse and send cursor movements

### Story 2.1: HID Device Recognition
**Priority**: CRITICAL
**Story Points**: 5
**Assignee**: Developer

**User Story**:
*As a user, I want my computer to recognize the Pico as a USB mouse so that it can control my cursor without drivers.*

**Acceptance Criteria**:
- [ ] Device Manager (Windows) / System Info (Mac) shows "HID Mouse"
- [ ] No driver installation required
- [ ] Device persists across reconnects
- [ ] OS mouse cursor responds to device (even if movement is wrong)

**Research Required**:
- MicroPython USB HID libraries
- USB HID descriptor format
- Mouse report descriptor structure

**Potential Libraries**:
1. **CircuitPython `usb_hid`** (may need porting)
2. **Custom implementation** using `machine.USB_HID`
3. **Community libraries** (check GitHub)

**Tasks**:
1. Research available MicroPython HID libraries
2. Download/install chosen library
3. Study HID mouse descriptor specification
4. Create `hid_mouse.py` module
5. Define USB HID mouse descriptor
6. Initialize HID device
7. Test OS recognition

**HID Mouse Descriptor Structure**:
```python
# Typical HID mouse report (5 bytes)
# Byte 0: Button states (bit 0=left, bit 1=right, bit 2=middle)
# Byte 1: X movement (-127 to +127)
# Byte 2: Y movement (-127 to +127)
# Byte 3: Wheel (optional)
# Byte 4: Reserved
```

**Verification Commands**:
```bash
# Windows
devcon find usb*  # Look for HID Mouse

# Mac
system_profiler SPUSBDataType  # Look for HID device

# Linux
lsusb
dmesg | grep -i hid
```

**Definition of Done**:
- OS recognizes device as HID mouse
- Device appears in system device list
- No errors in device manager

---

### Story 2.2: Basic Cursor Movement
**Priority**: HIGH
**Story Points**: 3
**Assignee**: Developer

**User Story**:
*As a user, I want to move the cursor with the joystick so that I can navigate my screen.*

**Acceptance Criteria**:
- [ ] Cursor moves up when joystick pushed up
- [ ] Cursor moves down when joystick pushed down
- [ ] Cursor moves left when joystick pushed left
- [ ] Cursor moves right when joystick pushed right
- [ ] Diagonal movements work correctly
- [ ] Movement is smooth (no stuttering)

**Tasks**:
1. Implement `send_report()` function in `hid_mouse.py`
2. Map joystick velocity to HID mouse coordinates
3. Scale velocity to -127 to +127 range
4. Create main loop at 100Hz minimum
5. Test directional accuracy
6. Fix axis inversions if needed

**Coordinate Mapping**:
```python
def joystick_to_mouse_velocity(vx, vy):
    """
    Convert joystick velocity to HID mouse delta
    Input: vx, vy in range -32768 to +32767
    Output: mouse_x, mouse_y in range -127 to +127
    """
    # Simple linear scaling
    MAX_JOY_DEFLECTION = 32767
    MAX_MOUSE_SPEED = 127

    mouse_x = int((vx / MAX_JOY_DEFLECTION) * MAX_MOUSE_SPEED)
    mouse_y = int((vy / MAX_JOY_DEFLECTION) * MAX_MOUSE_SPEED)

    # Clamp to valid range
    mouse_x = max(-127, min(127, mouse_x))
    mouse_y = max(-127, min(127, mouse_y))

    return mouse_x, mouse_y
```

**Main Loop Structure**:
```python
# main.py
import time
from joystick import Joystick
from hid_mouse import HIDMouse

joy = Joystick()
mouse = HIDMouse()

while True:
    vx, vy = joy.get_velocity()
    mx, my = joystick_to_mouse_velocity(vx, vy)
    mouse.move(mx, my)
    time.sleep(0.008)  # ~125Hz
```

**Definition of Done**:
- Cursor moves in correct direction
- All 8 directions work (including diagonals)
- Movement is fluid at 100Hz+

---

### Story 2.3: Movement Acceleration
**Priority**: MEDIUM
**Story Points**: 3
**Assignee**: Developer

**User Story**:
*As a user, I want precise control for small joystick movements and fast cursor travel for large movements, creating a natural feel.*

**Acceptance Criteria**:
- [ ] Small joystick deflection = slow, precise cursor movement
- [ ] Large joystick deflection = fast cursor movement
- [ ] Acceleration curve feels natural (not linear)
- [ ] Can still hit all screen edges
- [ ] Configuration allows tuning

**Acceleration Curves to Test**:

1. **Quadratic** (recommended starting point):
```python
velocity = (deflection ** 2) * sign(deflection) * MAX_SPEED
```

2. **Exponential**:
```python
velocity = (e ** abs(deflection) - 1) * sign(deflection) * MAX_SPEED
```

3. **Custom piecewise**:
```python
if abs(deflection) < 0.3:
    velocity = deflection * SLOW_SPEED
elif abs(deflection) < 0.7:
    velocity = deflection * MEDIUM_SPEED
else:
    velocity = deflection * FAST_SPEED
```

**Tasks**:
1. Add `ACCELERATION_CURVE` to `config.py`
2. Implement acceleration function
3. Test quadratic curve
4. Compare to linear movement
5. Allow curve exponent to be configurable
6. Test with real usage (web browsing)

**Implementation**:
```python
# config.py
MAX_SPEED = 127
ACCELERATION_EXPONENT = 2.0  # 1.0 = linear, 2.0 = quadratic

def apply_acceleration(velocity, max_velocity=32767):
    """Apply acceleration curve to velocity"""
    normalized = velocity / max_velocity  # -1.0 to 1.0
    sign = 1 if normalized >= 0 else -1
    accelerated = (abs(normalized) ** ACCELERATION_EXPONENT) * sign
    return int(accelerated * MAX_SPEED)
```

**Testing**:
- Barely move joystick → cursor should move very slowly
- Half deflection → medium speed
- Full deflection → maximum speed
- Feel should be smooth, predictable

**Definition of Done**:
- Acceleration curve implemented
- Configurable via `config.py`
- Feels natural in testing

---

## SPRINT 3: Click Functionality

### Story 3.1: Mouse Button Implementation
**Priority**: HIGH
**Story Points**: 3
**Assignee**: Developer

**User Story**:
*As a user, I want to perform left-click, right-click, and middle-click actions so that I can interact with UI elements.*

**Acceptance Criteria**:
- [ ] Button 1 triggers left-click
- [ ] Button 2 triggers right-click
- [ ] Button 3 triggers middle-click
- [ ] Click-and-drag works
- [ ] Double-click works
- [ ] No false/duplicate clicks

**Wiring**:
```
Button 1 (Left)   → GP15 + 3.3V
Button 2 (Right)  → GP14 + 3.3V
Button 3 (Middle) → GP13 + 3.3V
All commons       → GND
```

**Tasks**:
1. Wire 3 buttons to GPIO pins
2. Create `buttons.py` module
3. Configure GPIO pins as INPUT with PULL_DOWN
4. Implement basic button reading
5. Add debouncing (20ms delay)
6. Integrate with HID mouse reports
7. Test click, double-click, drag operations

**Button Class**:
```python
# buttons.py
from machine import Pin
import time

class Button:
    def __init__(self, pin_num, debounce_ms=20):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_DOWN)
        self.debounce_ms = debounce_ms
        self.last_state = 0
        self.last_time = 0

    def is_pressed(self):
        """Returns True if button is currently pressed (debounced)"""
        current_state = self.pin.value()
        current_time = time.ticks_ms()

        if current_state != self.last_state:
            if time.ticks_diff(current_time, self.last_time) > self.debounce_ms:
                self.last_state = current_state
                self.last_time = current_time
                return current_state == 1
        return False

    def value(self):
        """Returns current button state"""
        return self.pin.value()

# Usage
left_btn = Button(15)
right_btn = Button(14)
middle_btn = Button(13)
```

**HID Integration**:
```python
# Update HID report to include button states
def send_report(x, y, buttons):
    """
    buttons: bit 0 = left, bit 1 = right, bit 2 = middle
    """
    report = bytes([buttons, x & 0xFF, y & 0xFF, 0, 0])
    hid.send(report)

# Main loop
buttons = 0
if left_btn.value():
    buttons |= 0b001
if right_btn.value():
    buttons |= 0b010
if middle_btn.value():
    buttons |= 0b100

mouse.move(mx, my, buttons)
```

**Test Cases**:
- [ ] Single left-click on desktop icon
- [ ] Double-click to open file
- [ ] Right-click to open context menu
- [ ] Middle-click to paste (Linux) or open link in new tab
- [ ] Click and drag to select text
- [ ] Click and drag to move window

**Definition of Done**:
- All 3 buttons work reliably
- Drag operations work smoothly
- No missed or duplicate clicks

---

## SPRINT 4: Precision Control

### Story 4.1: Arrow Button Precision Movement
**Priority**: MEDIUM
**Story Points**: 2
**Assignee**: Developer

**User Story**:
*As a user, I want arrow buttons for pixel-perfect cursor positioning so that I can click tiny UI elements accurately.*

**Acceptance Criteria**:
- [ ] Each arrow button press moves cursor exactly 1 pixel
- [ ] Holding arrow button repeats movement
- [ ] Works independently of joystick movement
- [ ] No interference between arrow and joystick input

**Wiring**:
```
Arrow Up     → GP10 + 3.3V
Arrow Down   → GP11 + 3.3V
Arrow Left   → GP12 + 3.3V
Arrow Right  → GP16 + 3.3V
```

**Tasks**:
1. Wire 4 arrow buttons
2. Create `ArrowButton` class with repeat functionality
3. Implement 1-pixel movement
4. Add repeat delay (initial: 300ms, repeat: 100ms)
5. Test precision tasks

**Arrow Button with Repeat**:
```python
class ArrowButton:
    def __init__(self, pin_num, initial_delay=300, repeat_delay=100):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_DOWN)
        self.initial_delay = initial_delay
        self.repeat_delay = repeat_delay
        self.pressed_time = 0
        self.last_repeat = 0
        self.is_held = False

    def get_movement(self):
        """Returns True if movement should occur"""
        current_time = time.ticks_ms()
        is_pressed = self.pin.value()

        if is_pressed:
            if not self.is_held:
                # First press
                self.is_held = True
                self.pressed_time = current_time
                self.last_repeat = current_time
                return True
            else:
                # Held down
                elapsed = time.ticks_diff(current_time, self.pressed_time)
                if elapsed > self.initial_delay:
                    # Check repeat interval
                    if time.ticks_diff(current_time, self.last_repeat) > self.repeat_delay:
                        self.last_repeat = current_time
                        return True
        else:
            self.is_held = False

        return False

# Usage
arrow_up = ArrowButton(10)
arrow_down = ArrowButton(11)
arrow_left = ArrowButton(12)
arrow_right = ArrowButton(16)

# In main loop
dx, dy = 0, 0
if arrow_up.get_movement():
    dy = -1
if arrow_down.get_movement():
    dy = 1
if arrow_left.get_movement():
    dx = -1
if arrow_right.get_movement():
    dx = 1

if dx != 0 or dy != 0:
    mouse.move(dx, dy, buttons)
```

**Test Tasks**:
- [ ] Click tiny "X" close button on dialog
- [ ] Select single character in text editor
- [ ] Position cursor on specific pixel in image editor
- [ ] Navigate dropdown menu items

**Definition of Done**:
- Arrow buttons move exactly 1 pixel
- Repeat functionality works smoothly
- Useful for precision tasks

---

## SPRINT 5: Polish & Tuning

### Story 5.1: System Optimization & Tuning
**Priority**: HIGH
**Story Points**: 5
**Assignee**: Developer

**User Story**:
*As a user, I want the joystick mouse to feel natural and responsive so that I can use it comfortably for extended periods.*

**Acceptance Criteria**:
- [ ] Update rate ≥ 125Hz
- [ ] Comfortable for 15+ minutes continuous use
- [ ] Natural acceleration feel
- [ ] No fatigue or frustration
- [ ] Works well for web browsing, coding, general UI

**Tasks**:

#### 5.1.1: Performance Benchmarking
```python
# Add performance monitoring
import time

frame_times = []
start = time.ticks_ms()

# In main loop
loop_start = time.ticks_ms()
# ... do work ...
loop_end = time.ticks_ms()
frame_times.append(time.ticks_diff(loop_end, loop_start))

# Report every second
if time.ticks_diff(loop_end, start) > 1000:
    avg_time = sum(frame_times) / len(frame_times)
    fps = 1000 / avg_time if avg_time > 0 else 0
    print(f"Update rate: {fps:.1f} Hz")
    frame_times = []
    start = loop_end
```

**Target**: ≥ 125Hz (8ms per frame)

#### 5.1.2: Parameter Tuning Matrix

| Parameter | Default | Test Range | Optimal |
|-----------|---------|------------|---------|
| DEAD_ZONE | 2000 | 1000-4000 | TBD |
| MAX_SPEED | 127 | 50-127 | TBD |
| ACCELERATION_EXPONENT | 2.0 | 1.5-3.0 | TBD |
| DEBOUNCE_MS | 20 | 10-50 | TBD |
| UPDATE_RATE_HZ | 125 | 100-250 | TBD |
| ARROW_REPEAT_INITIAL | 300 | 200-500 | TBD |
| ARROW_REPEAT_RATE | 100 | 50-150 | TBD |

**Tuning Process**:
1. Start with defaults
2. Change one parameter at a time
3. Test for 5 minutes
4. Record subjective feel (1-10 rating)
5. Keep or revert change
6. Repeat

#### 5.1.3: Real-World Usage Tests

**Test 1: Web Browsing** (15 minutes)
- [ ] Navigate to website
- [ ] Click links (various sizes)
- [ ] Scroll with joystick (if implemented)
- [ ] Fill out form with precise clicking
- [ ] Rate comfort: ___/10

**Test 2: Text Editing** (10 minutes)
- [ ] Open text editor
- [ ] Select text with click-drag
- [ ] Position cursor precisely between characters
- [ ] Use arrow buttons for fine positioning
- [ ] Rate comfort: ___/10

**Test 3: General UI Work** (10 minutes)
- [ ] Open/close windows
- [ ] Drag windows around screen
- [ ] Click small buttons (window controls)
- [ ] Navigate nested menus
- [ ] Rate comfort: ___/10

#### 5.1.4: Code Optimization

**Profile main loop**:
- Identify slowest operations
- Optimize ADC reads (cache if needed)
- Reduce allocations
- Use integer math where possible

**Example optimizations**:
```python
# BEFORE (slow)
velocity = float(deflection) ** 2.0 * float(sign) * MAX_SPEED

# AFTER (fast)
# Pre-calculate lookup table for acceleration
ACCEL_TABLE = [int((i/100)**2 * MAX_SPEED) for i in range(101)]

def fast_acceleration(deflection):
    normalized = min(100, abs(deflection) // 327)  # 0-100
    return ACCEL_TABLE[normalized] * (1 if deflection >= 0 else -1)
```

**Definition of Done**:
- Update rate ≥ 125Hz consistently
- All parameters tuned and documented
- Passed all real-world usage tests with ≥7/10 comfort
- Code optimized for performance

---

## Backlog: Future Enhancements

### Feature: Scroll Wheel Emulation
**Priority**: LOW
**Story Points**: 2

**User Story**: *As a user, I want to scroll web pages and documents using the joystick.*

**Implementation**: Shift button + Y-axis = scroll wheel

---

### Feature: Multi-Profile Support
**Priority**: LOW
**Story Points**: 3

**User Story**: *As a user, I want to switch between sensitivity profiles for different tasks.*

**Implementation**: Profile button cycles through: Slow (precision), Medium (general), Fast (gaming)

---

### Feature: Wireless Operation
**Priority**: MEDIUM
**Story Points**: 8

**User Story**: *As a user, I want to use the joystick mouse wirelessly.*

**Hardware**: Upgrade to Pico W, add battery & charging

---

### Feature: Configuration UI
**Priority**: LOW
**Story Points**: 5

**User Story**: *As a user, I want to tune parameters without editing code.*

**Implementation**: Web interface or serial configuration tool

---

## Definition of Ready (Story)
- [ ] User story clearly defined
- [ ] Acceptance criteria written
- [ ] Technical approach discussed
- [ ] Dependencies identified
- [ ] Story points estimated

## Definition of Done (Story)
- [ ] All acceptance criteria met
- [ ] Code written and tested
- [ ] Hardware wired and verified
- [ ] No regression of previous features
- [ ] Code commented and readable
- [ ] Story reviewed and accepted

## Velocity Tracking

| Sprint | Planned Points | Completed Points | Notes |
|--------|---------------|------------------|-------|
| Sprint 1 | 7 | | |
| Sprint 2 | 11 | | |
| Sprint 3 | 3 | | |
| Sprint 4 | 2 | | |
| Sprint 5 | 5 | | |
| **Total** | **28** | | |

---

**Last Updated**: 2026-03-06
**Project Status**: Planning Complete, Ready to Start Sprint 1
