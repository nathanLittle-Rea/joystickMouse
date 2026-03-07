# Joystick Mouse Replacement System

A hardware project to replace a traditional computer mouse with a thumb-operated joystick controller featuring clickable buttons and precision arrow controls.

## Project Overview

Traditional mice are limiting. This project creates a custom USB HID mouse using:
- **Thumb-controlled analog joystick** for cursor movement with acceleration
- **3 main buttons** for left-click, right-click, and middle-click
- **4 arrow buttons** for pixel-perfect precision movement
- **MicroPython** running on Raspberry Pi Pico
- **USB HID** protocol for plug-and-play compatibility

## Hardware Requirements

### Core Components
| Component | Specification | Purpose |
|-----------|---------------|---------|
| Raspberry Pi Pico | RP2040, 3.3V logic | Main microcontroller with USB HID support |
| Analog Joystick Module | 2-axis, 0-3.3V output | Thumb-controlled cursor movement |
| Tactile Buttons (3x) | 12mm momentary switches | Main mouse buttons |
| Tactile Buttons (4x) | 6mm momentary switches | Arrow keys for precision |
| Micro USB Cable | Data + Power | Connect Pico to computer |
| Breadboard | Half or full size | Prototyping |
| Jumper Wires | M-M and M-F | Connections |

### Optional Components
- 10kΩ resistors (if buttons lack pull-downs)
- Perfboard or custom PCB (permanent build)
- 3D printed enclosure
- Status LED

## Why Raspberry Pi Pico?

- **Native USB HID support** in MicroPython (critical for this project)
- Dual-core 133MHz RP2040 processor
- 26 GPIO pins, 3 ADC channels
- Well-documented, affordable (~$4)
- Better suited than ESP32 for USB HID (ESP32 classic requires USB-serial chip)

## Pin Assignments

```
Raspberry Pi Pico Pinout:
┌─────────────────────────────┐
│  GP26 (ADC0) ← Joystick X   │
│  GP27 (ADC1) ← Joystick Y   │
│  GND         ← Joystick GND │
│  3.3V        ← Joystick VCC │
│                              │
│  GP15        ← Button 1 (Left Click)   │
│  GP14        ← Button 2 (Right Click)  │
│  GP13        ← Button 3 (Middle Click) │
│                              │
│  GP10        ← Arrow Up      │
│  GP11        ← Arrow Down    │
│  GP12        ← Arrow Left    │
│  GP16        ← Arrow Right   │
│                              │
│  GND         ← All Button Commons │
└─────────────────────────────┘

All buttons use internal pull-down resistors
Button press = HIGH (3.3V)
```

## Wiring Diagram

### Joystick Module
```
Joystick        Pico
────────        ────
VCC     ───→    3.3V (Pin 36)
GND     ───→    GND (Pin 38)
VRx     ───→    GP26/ADC0 (Pin 31)
VRy     ───→    GP27/ADC1 (Pin 32)
SW      ───→    (optional - joystick click button)
```

### Buttons (with internal pull-down)
```
Button          Pico
──────          ────
Left Click
  Pin 1  ───→   GP15 (Pin 20)
  Pin 2  ───→   3.3V (Pin 36)

Right Click
  Pin 1  ───→   GP14 (Pin 19)
  Pin 2  ───→   3.3V

Middle Click
  Pin 1  ───→   GP13 (Pin 17)
  Pin 2  ───→   3.3V

Arrow Buttons (same pattern)
  Up     ───→   GP10
  Down   ───→   GP11
  Left   ───→   GP12
  Right  ───→   GP16
```

## Development Plan - Scrum Board

### SPRINT 1: Foundation & Basic Input

#### Story 1: Development Environment Setup
**Goal**: Can write and run MicroPython code on Pico

**Tasks**:
- [ ] Flash MicroPython firmware to Raspberry Pi Pico
- [ ] Install Thonny IDE
- [ ] Write and run blink test
- [ ] Verify serial console communication

**Acceptance Criteria**: LED blinks, serial console shows output

---

#### Story 2: Joystick Input Reading
**Goal**: Console shows X/Y values when joystick moved

**Tasks**:
- [ ] Wire joystick to Pico ADC pins
- [ ] Write script to read ADC values (0-65535 range)
- [ ] Print X/Y values to console at 60Hz
- [ ] Verify full range of motion

**Acceptance Criteria**: Moving joystick shows changing values in console

---

#### Story 3: Dead Zone Implementation
**Goal**: No cursor drift when joystick is centered

**Tasks**:
- [ ] Calculate center point (~32768 for 16-bit ADC)
- [ ] Implement dead zone (±2000 units from center)
- [ ] Test centered joystick outputs (0, 0)

**Acceptance Criteria**: Centered joystick produces zero velocity output

---

### SPRINT 2: USB HID Mouse Emulation

#### Story 4: HID Device Recognition
**Goal**: Computer recognizes Pico as USB mouse

**Tasks**:
- [ ] Research MicroPython USB HID libraries
- [ ] Install USB HID library for Pico
- [ ] Create USB HID mouse descriptor
- [ ] Test device recognition in OS

**Acceptance Criteria**: Device Manager/System shows Pico as HID mouse

---

#### Story 5: Cursor Movement
**Goal**: Cursor moves in all directions smoothly

**Tasks**:
- [ ] Map joystick deflection to X/Y velocity (-127 to +127)
- [ ] Send HID mouse movement reports
- [ ] Test diagonal movement accuracy
- [ ] Implement 100Hz+ update loop

**Acceptance Criteria**: Cursor moves smoothly in response to joystick

---

#### Story 6: Movement Acceleration
**Goal**: Small deflections = slow, large deflections = fast

**Tasks**:
- [ ] Implement linear velocity mapping
- [ ] Add quadratic/exponential acceleration curve
- [ ] Define max cursor speed
- [ ] Test and tune acceleration feel

**Acceptance Criteria**: Natural feeling acceleration curve

---

### SPRINT 3: Click Functionality

#### Story 7: Mouse Button Clicks
**Goal**: Can left-click, right-click, middle-click

**Tasks**:
- [ ] Wire 3 buttons to GPIO pins
- [ ] Configure GPIO as INPUT with pull-down
- [ ] Implement software debouncing (20ms)
- [ ] Send HID button press/release events
- [ ] Test click-and-drag

**Acceptance Criteria**: All click types work reliably, can drag objects

---

### SPRINT 4: Precision Control

#### Story 8: Arrow Button Precision
**Goal**: Pixel-perfect cursor positioning

**Tasks**:
- [ ] Wire 4 arrow buttons to GPIO
- [ ] Implement button scanning
- [ ] Send 1-pixel HID movement on press
- [ ] Add repeat functionality (hold = continuous)
- [ ] Test precision tasks

**Acceptance Criteria**: Each arrow press moves exactly 1 pixel

---

### SPRINT 5: Polish & Tuning

#### Story 9: Response Tuning
**Goal**: Natural, comfortable feel for extended use

**Tasks**:
- [ ] Benchmark update rate (target 125Hz+)
- [ ] Tune dead zone size
- [ ] Tune max speed multiplier
- [ ] Tune acceleration curve parameters
- [ ] Real-world usage test (15+ minutes)

**Acceptance Criteria**: Comfortable for web browsing, coding, UI work

---

## Software Architecture

### Core Components

```
joystick_mouse/
├── main.py              # Entry point, main loop
├── hid_mouse.py         # USB HID mouse implementation
├── joystick.py          # Joystick reading & dead zone
├── buttons.py           # Button debouncing & scanning
├── config.py            # Tunable parameters
└── lib/
    └── usb_hid/         # USB HID library
```

### Key Algorithms

#### Dead Zone Calculation
```python
# Center position (neutral)
CENTER = 32768
DEAD_ZONE = 2000

def apply_dead_zone(raw_value):
    offset = raw_value - CENTER
    if abs(offset) < DEAD_ZONE:
        return 0
    return offset
```

#### Acceleration Curve
```python
# Quadratic acceleration for natural feel
def calculate_velocity(deflection, max_deflection=30000):
    normalized = deflection / max_deflection  # -1.0 to 1.0
    accelerated = normalized ** 2 * sign(normalized)
    return int(accelerated * MAX_SPEED)
```

#### Button Debouncing
```python
# Software debounce prevents false clicks
DEBOUNCE_MS = 20
last_press_time = 0

def is_button_pressed(pin):
    if pin.value() and (time_ms() - last_press_time) > DEBOUNCE_MS:
        last_press_time = time_ms()
        return True
    return False
```

## Configuration Parameters

These values in `config.py` can be tuned for feel:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DEAD_ZONE` | 2000 | Joystick center tolerance (prevent drift) |
| `MAX_SPEED` | 127 | Maximum cursor velocity (HID limit) |
| `ACCELERATION_CURVE` | 2.0 | Exponent for acceleration (2.0 = quadratic) |
| `UPDATE_RATE_HZ` | 125 | Mouse update frequency |
| `DEBOUNCE_MS` | 20 | Button debounce time |
| `ARROW_SPEED` | 1 | Pixels per arrow button press |
| `ARROW_REPEAT_MS` | 100 | Repeat rate when holding arrow |

## Setup Instructions

### 1. Flash MicroPython Firmware

1. Download latest MicroPython UF2 for Pico: https://micropython.org/download/rp2-pico/
2. Hold BOOTSEL button on Pico while plugging in USB
3. Pico appears as USB drive
4. Drag UF2 file to drive
5. Pico reboots with MicroPython

### 2. Install Development Tools

**Option A: Thonny (Recommended for beginners)**
```bash
# Download from https://thonny.org
# Select "MicroPython (Raspberry Pi Pico)" interpreter
```

**Option B: Command line tools**
```bash
pip install mpremote
mpremote connect list
```

### 3. Upload Code

Using Thonny:
1. Open main.py
2. Click "Run > Run current script"
3. Select "Raspberry Pi Pico" as target

Using mpremote:
```bash
mpremote cp main.py :
mpremote cp hid_mouse.py :
mpremote cp joystick.py :
mpremote cp buttons.py :
mpremote cp config.py :
```

### 4. Test Basic Functionality

```python
# Test joystick reading
from machine import ADC
x_axis = ADC(26)
y_axis = ADC(27)
print(x_axis.read_u16(), y_axis.read_u16())
```

## Testing Checklist

### Hardware Tests
- [ ] Joystick X-axis reads 0-65535 across full range
- [ ] Joystick Y-axis reads 0-65535 across full range
- [ ] Centered joystick reads ~32768 on both axes
- [ ] All 7 buttons register press/release
- [ ] No shorts or loose connections

### Software Tests
- [ ] Dead zone prevents drift when centered
- [ ] Cursor moves in all 8 directions (N, NE, E, SE, S, SW, W, NW)
- [ ] Acceleration feels natural
- [ ] Left click works (single, double)
- [ ] Right click opens context menus
- [ ] Middle click works (paste, scroll)
- [ ] Arrow buttons move exactly 1 pixel
- [ ] No missed clicks (debouncing works)
- [ ] Update rate > 100Hz (smooth motion)

### Real-World Tests
- [ ] Web browsing for 15 minutes
- [ ] Text editing with precision selection
- [ ] Clicking small UI elements (close buttons, links)
- [ ] Drag-and-drop operations
- [ ] Gaming (if applicable)

## Troubleshooting

### Cursor Drifts When Joystick Centered
- **Cause**: Dead zone too small or joystick not centered at 32768
- **Fix**: Increase `DEAD_ZONE` value or calibrate center point

### Cursor Movement Too Slow/Fast
- **Cause**: Incorrect `MAX_SPEED` or acceleration curve
- **Fix**: Adjust `MAX_SPEED` and `ACCELERATION_CURVE` in config

### Buttons Register Multiple Clicks
- **Cause**: Insufficient debouncing
- **Fix**: Increase `DEBOUNCE_MS` to 30-50ms

### OS Doesn't Recognize Device
- **Cause**: USB HID descriptor issue
- **Fix**: Check HID library installation, verify Pico firmware

### Choppy Cursor Movement
- **Cause**: Update rate too low
- **Fix**: Optimize main loop, reduce processing, increase `UPDATE_RATE_HZ`

## Future Enhancements (Backlog)

### Planned Features
- [ ] **Scroll wheel emulation**: Shift + joystick Y-axis = scroll
- [ ] **Multiple sensitivity profiles**: Button to switch slow/medium/fast modes
- [ ] **Programmable macros**: Assign complex actions to buttons
- [ ] **LED status indicators**: Show current mode/profile
- [ ] **Configuration UI**: Web interface for tuning parameters
- [ ] **Auto-calibration**: Automatic dead zone and center detection

### Advanced Features
- [ ] **Bluetooth wireless**: Use Pico W for wireless operation
- [ ] **Battery powered**: LiPo battery + charging circuit
- [ ] **Gesture controls**: Joystick patterns trigger actions
- [ ] **Multi-device switching**: KVM-like functionality
- [ ] **Haptic feedback**: Vibration motor for clicks
- [ ] **OLED display**: Show current settings/status

### Hardware Improvements
- [ ] **Ergonomic enclosure**: 3D printed case with thumb rest
- [ ] **Hall effect joystick**: No mechanical wear, longer life
- [ ] **Mechanical key switches**: Better tactile feedback for buttons
- [ ] **Modular design**: Hot-swappable joystick modules

## References & Resources

### MicroPython Documentation
- Official MicroPython docs: https://docs.micropython.org/
- Pico-specific: https://docs.micropython.org/en/latest/rp2/quickref.html

### USB HID Resources
- USB HID spec: https://www.usb.org/hid
- CircuitPython HID library (reference): https://github.com/adafruit/Adafruit_CircuitPython_HID
- Pico USB HID examples: https://github.com/raspberrypi/pico-examples

### Hardware Datasheets
- RP2040 datasheet: https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf
- Pico pinout: https://datasheets.raspberrypi.com/pico/Pico-R3-A4-Pinout.pdf

### Community
- Raspberry Pi forums: https://forums.raspberrypi.com/
- MicroPython forum: https://forum.micropython.org/

## License

Open source - build, modify, share freely!

## Contributing

Improvements welcome! Areas of interest:
- Better acceleration algorithms
- Ergonomic enclosure designs
- Alternative input methods
- Performance optimizations

---

**Built by hackers, for hackers. Because a mouse is just not good enough.**
