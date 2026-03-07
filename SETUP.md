# Setup Guide - Joystick Mouse

Complete step-by-step instructions to get your joystick mouse up and running.

## Prerequisites

### Hardware Checklist
- [ ] Raspberry Pi Pico (or Pico W)
- [ ] Analog 2-axis joystick module
- [ ] 7x tactile push buttons (3x 12mm + 4x 6mm recommended)
- [ ] Breadboard (half or full size)
- [ ] Jumper wires (male-to-male and male-to-female)
- [ ] Micro USB cable (data capable, not just charging)
- [ ] Computer with USB port

### Software Checklist
- [ ] Python 3.7+ installed on your computer
- [ ] Internet connection for downloads

---

## Step 1: Flash MicroPython Firmware

### 1.1 Download MicroPython UF2
1. Visit https://micropython.org/download/rp2-pico/
2. Download latest **stable** release (file ending in `.uf2`)
3. Save to your Downloads folder

### 1.2 Enter BOOTSEL Mode
1. **Unplug** the Pico from USB
2. **Hold down** the white BOOTSEL button on the Pico
3. While holding BOOTSEL, **plug in** the USB cable
4. **Release** BOOTSEL button after 1 second
5. Pico should appear as USB drive named "RPI-RP2"

**Troubleshooting**:
- If no drive appears, try a different USB cable (must support data)
- Some cables are charge-only and won't work
- Try a different USB port

### 1.3 Flash Firmware
1. **Drag and drop** the `.uf2` file onto the RPI-RP2 drive
2. The Pico will flash green LED briefly
3. Drive will disappear automatically (this is normal!)
4. **MicroPython is now installed**

**Verify**:
```bash
# The Pico should now appear as a serial device:
# Windows: COM port in Device Manager
# Mac: /dev/cu.usbmodem*
# Linux: /dev/ttyACM0
```

---

## Step 2: Install Development Tools

Choose **Option A** (recommended for beginners) or **Option B** (for advanced users).

### Option A: Thonny IDE (Recommended)

#### 2.1 Install Thonny
**Windows**:
1. Download from https://thonny.org
2. Run installer
3. Follow installation wizard

**Mac**:
```bash
brew install --cask thonny
# Or download DMG from https://thonny.org
```

**Linux**:
```bash
sudo apt install thonny
# Or: pip3 install thonny
```

#### 2.2 Configure Thonny for Pico
1. Open Thonny
2. Go to **Tools > Options > Interpreter**
3. Select **MicroPython (Raspberry Pi Pico)**
4. Select correct port:
   - Windows: `COM3` (or similar)
   - Mac: `/dev/cu.usbmodem...`
   - Linux: `/dev/ttyACM0`
5. Click **OK**

#### 2.3 Test Connection
1. In Thonny's Shell pane (bottom), you should see:
```
MicroPython v1.xx on 2024-xx-xx; Raspberry Pi Pico with RP2040
Type "help()" for more information.
>>>
```

2. Type: `print("Hello, Pico!")`
3. Press Enter
4. You should see: `Hello, Pico!`

**Success!** You can now write code for the Pico.

---

### Option B: Command Line Tools (Advanced)

#### 2.1 Install mpremote
```bash
pip3 install mpremote
```

#### 2.2 Test Connection
```bash
mpremote connect list
# Should show: /dev/cu.usbmodem... (or COM port on Windows)

mpremote repl
# Should enter Python REPL
# Type: print("Hello!")
# Press Ctrl+X to exit
```

---

## Step 3: Test LED Blink (Verify Setup)

### 3.1 Create Blink Script

In Thonny, create new file with this code:

```python
# blink_test.py
from machine import Pin
import time

led = Pin(25, Pin.OUT)  # Onboard LED is GP25

print("Blinking LED 10 times...")
for i in range(10):
    led.toggle()
    print(f"Blink {i+1}")
    time.sleep(0.5)

print("Test complete!")
```

### 3.2 Run Script
**Thonny**:
1. Click **File > Save as...**
2. Choose **Raspberry Pi Pico**
3. Save as `blink_test.py`
4. Click **Run** (green play button)

**mpremote**:
```bash
mpremote run blink_test.py
```

### 3.3 Expected Result
- Onboard LED should blink 10 times
- Console shows "Blink 1" through "Blink 10"
- If this works, **your setup is correct!**

---

## Step 4: Wire the Joystick

### 4.1 Joystick Module Pinout

Most joystick modules have 5 pins:
```
   ┌─────────────┐
   │   Joystick  │
   │             │
   │      ●      │  ● = thumb position
   │             │
   └─┬─┬─┬─┬─┬──┘
     │ │ │ │ │
     │ │ │ │ └─ SW  (button, optional)
     │ │ │ └─── VRy (Y-axis output)
     │ │ └───── VRx (X-axis output)
     │ └─────── +5V or VCC (power)
     └───────── GND (ground)
```

**IMPORTANT**: Some modules are labeled +5V but work fine on 3.3V.

### 4.2 Wiring Instructions

| Joystick Pin | Wire Color | Pico Pin | Pico Pin # |
|--------------|------------|----------|------------|
| GND | Black | GND | 38 (any GND) |
| VCC/+5V | Red | 3.3V | 36 |
| VRx | Yellow | GP26 (ADC0) | 31 |
| VRy | Green | GP27 (ADC1) | 32 |
| SW | Blue (optional) | GP22 | 29 |

**Visual Diagram**:
```
Joystick Module          Raspberry Pi Pico
┌─────────────┐          ┌──────────────────┐
│   GND ●─────┼─────────→│ GND (Pin 38)     │
│   VCC ●─────┼─────────→│ 3.3V (Pin 36)    │
│   VRx ●─────┼─────────→│ GP26 (Pin 31)    │
│   VRy ●─────┼─────────→│ GP27 (Pin 32)    │
│   SW  ●─────┼─────────→│ GP22 (Pin 29)    │
└─────────────┘          └──────────────────┘
```

### 4.3 Double-Check Connections
- [ ] Power and ground not reversed (will damage components!)
- [ ] No loose wires
- [ ] Breadboard connections firm
- [ ] VRx goes to GP26, VRy goes to GP27 (correct axes)

---

## Step 5: Test Joystick Input

### 5.1 Create Test Script

```python
# joystick_test.py
from machine import ADC, Pin
import time

# Initialize ADC pins for X and Y axes
x_axis = ADC(Pin(26))
y_axis = ADC(Pin(27))

print("Joystick Test - Move joystick around")
print("Press Ctrl+C to stop")
print()

try:
    while True:
        x_value = x_axis.read_u16()
        y_value = y_axis.read_u16()

        # Create simple bar graph
        x_bar = "#" * (x_value // 3000)
        y_bar = "#" * (y_value // 3000)

        print(f"X: {x_value:5d} [{x_bar:<22}]  Y: {y_value:5d} [{y_bar:<22}]", end='\r')

        time.sleep(0.05)  # 20Hz update

except KeyboardInterrupt:
    print("\nTest stopped")
```

### 5.2 Run Test
1. Upload and run `joystick_test.py`
2. Move joystick in all directions
3. Observe changing values

### 5.3 Expected Values

| Joystick Position | X Value | Y Value |
|-------------------|---------|---------|
| Center (resting) | ~32768 | ~32768 |
| Full Left | ~0 | ~32768 |
| Full Right | ~65535 | ~32768 |
| Full Up | ~32768 | ~0 |
| Full Down | ~32768 | ~65535 |
| Top-Left Corner | ~0 | ~0 |
| Bottom-Right | ~65535 | ~65535 |

**Troubleshooting**:
- **No values change**: Check wiring, especially VRx/VRy connections
- **Only one axis works**: Check other axis wiring
- **Values reversed**: This is fine, we'll fix in code
- **Center not ~32768**: Record actual center value for calibration

### 5.4 Calibration Notes
Record your joystick's actual center position:

```
Center X: _______ (should be ~32768)
Center Y: _______ (should be ~32768)

Note: Use these values in config.py
```

---

## Step 6: Wire the Buttons

### 6.1 Button Wiring Scheme

Each button connects between a GPIO pin and 3.3V:

```
    3.3V (Pin 36)
       │
       ├──[Button 1]──→ GP15 (Left Click)
       ├──[Button 2]──→ GP14 (Right Click)
       ├──[Button 3]──→ GP13 (Middle Click)
       ├──[Button 4]──→ GP10 (Arrow Up)
       ├──[Button 5]──→ GP11 (Arrow Down)
       ├──[Button 6]──→ GP12 (Arrow Left)
       └──[Button 7]──→ GP16 (Arrow Right)

(Pico internal pull-down resistors prevent floating pins)
```

### 6.2 Complete Button Pinout Table

| Button Function | GPIO Pin | Physical Pin | Wire to 3.3V |
|----------------|----------|--------------|--------------|
| Left Click | GP15 | 20 | Pin 36 |
| Right Click | GP14 | 19 | Pin 36 |
| Middle Click | GP13 | 17 | Pin 36 |
| Arrow Up | GP10 | 14 | Pin 36 |
| Arrow Down | GP11 | 15 | Pin 36 |
| Arrow Left | GP12 | 16 | Pin 36 |
| Arrow Right | GP16 | 21 | Pin 36 |

**Breadboard Layout Tip**:
- Connect all button "top" pins to 3.3V power rail
- Connect button "bottom" pins to respective GPIO pins
- Keeps wiring organized

### 6.3 Test Buttons

```python
# button_test.py
from machine import Pin
import time

# Define buttons
buttons = {
    'Left': Pin(15, Pin.IN, Pin.PULL_DOWN),
    'Right': Pin(14, Pin.IN, Pin.PULL_DOWN),
    'Middle': Pin(13, Pin.IN, Pin.PULL_DOWN),
    'Up': Pin(10, Pin.IN, Pin.PULL_DOWN),
    'Down': Pin(11, Pin.IN, Pin.PULL_DOWN),
    'Left_Arrow': Pin(12, Pin.IN, Pin.PULL_DOWN),
    'Right_Arrow': Pin(16, Pin.IN, Pin.PULL_DOWN),
}

print("Button Test - Press each button")
print("Press Ctrl+C to stop\n")

last_states = {name: 0 for name in buttons}

try:
    while True:
        for name, pin in buttons.items():
            state = pin.value()
            if state != last_states[name]:
                if state == 1:
                    print(f"{name} button PRESSED")
                else:
                    print(f"{name} button RELEASED")
                last_states[name] = state

        time.sleep(0.01)  # 100Hz polling

except KeyboardInterrupt:
    print("\nTest stopped")
```

### 6.4 Verify All Buttons
- [ ] Left click button works
- [ ] Right click button works
- [ ] Middle click button works
- [ ] Arrow Up works
- [ ] Arrow Down works
- [ ] Arrow Left works
- [ ] Arrow Right works

---

## Step 7: Install Project Code

### 7.1 Clone/Download Project Files

**Option A: Git**
```bash
git clone [repository-url]
cd joystickMouse
```

**Option B: Manual Download**
Download these files from the repository:
- `main.py`
- `config.py`
- `joystick.py`
- `buttons.py`
- `hid_mouse.py`
- `lib/` (USB HID library)

### 7.2 Upload to Pico

**Using Thonny**:
1. Open each `.py` file in Thonny
2. Click **File > Save as...**
3. Choose **Raspberry Pi Pico**
4. Save with same filename

**Using mpremote**:
```bash
mpremote cp main.py :
mpremote cp config.py :
mpremote cp joystick.py :
mpremote cp buttons.py :
mpremote cp hid_mouse.py :
mpremote cp -r lib :
```

### 7.3 Verify Files on Pico

**Thonny**: View > Files, check Pico files

**mpremote**:
```bash
mpremote ls
# Should show: main.py, config.py, joystick.py, etc.
```

---

## Step 8: Configure Settings

### 8.1 Edit config.py

Open `config.py` and adjust for your hardware:

```python
# Joystick calibration
CENTER_X = 32768  # Your measured center X
CENTER_Y = 32768  # Your measured center Y
DEAD_ZONE = 2000  # Adjust if drift occurs

# Sensitivity
MAX_SPEED = 127  # Maximum cursor speed
ACCELERATION_EXPONENT = 2.0  # 1.0=linear, 2.0=quadratic

# Button settings
DEBOUNCE_MS = 20  # Increase if getting double-clicks

# Performance
UPDATE_RATE_HZ = 125  # Polling frequency
```

### 8.2 Calibration Tips

**If cursor drifts when centered**:
- Increase `DEAD_ZONE` to 3000 or 4000

**If cursor too fast**:
- Decrease `MAX_SPEED` to 80-100

**If cursor too slow**:
- Increase `MAX_SPEED` to 127 (max)
- Decrease `ACCELERATION_EXPONENT` to 1.5

**If acceleration feels weird**:
- Try `ACCELERATION_EXPONENT = 1.5` (gentler)
- Try `ACCELERATION_EXPONENT = 2.5` (more aggressive)

---

## Step 9: First Run

### 9.1 Start the Program

**Thonny**:
1. Open `main.py`
2. Click **Run**
3. Watch console for status messages

**mpremote**:
```bash
mpremote run main.py
```

### 9.2 Expected Console Output

```
Joystick Mouse v1.0
Initializing joystick...
Initializing buttons...
Initializing USB HID...
Ready! Update rate: 125Hz
```

### 9.3 Check OS Recognition

**Windows**:
1. Open Device Manager
2. Expand "Human Interface Devices"
3. Look for "HID-compliant mouse"

**Mac**:
```bash
system_profiler SPUSBDataType | grep -A 10 Mouse
```

**Linux**:
```bash
lsusb | grep -i hid
dmesg | tail | grep -i mouse
```

### 9.4 Test Cursor Movement
1. Move joystick slowly → cursor should move
2. Center joystick → cursor should stop
3. Press left button → should click
4. Press arrow buttons → precise movement

**Success!** Your joystick mouse is working!

---

## Step 10: Make it Permanent

### 10.1 Auto-Run on Boot

Rename `main.py` to `main.py` on the Pico (it already is!)

MicroPython automatically runs `main.py` on boot.

### 10.2 Test Boot Behavior
1. Unplug Pico
2. Plug back in
3. Wait 2-3 seconds
4. Cursor should respond to joystick
5. No computer interaction needed!

---

## Troubleshooting Guide

### Issue: Pico Not Recognized

**Symptoms**: No serial port appears

**Solutions**:
- Try different USB cable (must support data, not just charging)
- Try different USB port
- Re-flash MicroPython firmware
- Check Device Manager (Windows) for unknown devices

---

### Issue: Joystick Values Not Changing

**Symptoms**: Test shows constant values

**Solutions**:
- Check wiring: VRx to GP26, VRy to GP27
- Verify 3.3V and GND connections
- Try different jumper wires (could be broken)
- Test joystick with multimeter (should show 0-3.3V on outputs)

---

### Issue: Cursor Drifts When Centered

**Symptoms**: Cursor slowly moves on its own

**Solutions**:
- Increase `DEAD_ZONE` in config.py to 3000
- Calibrate `CENTER_X` and `CENTER_Y` using test script
- Some cheap joysticks have larger drift (consider upgrading)

---

### Issue: Buttons Don't Work

**Symptoms**: Button test shows no response

**Solutions**:
- Check button wiring (one pin to GPIO, other to 3.3V)
- Verify pull-down resistors enabled in code (`Pin.PULL_DOWN`)
- Test button with multimeter (should show continuity when pressed)
- Try different GPIO pins

---

### Issue: Computer Doesn't Recognize as Mouse

**Symptoms**: No HID device appears in OS

**Solutions**:
- Check USB HID library is installed in `lib/` folder
- Verify MicroPython firmware is latest version
- Review `hid_mouse.py` for errors
- Check console for error messages

---

### Issue: Cursor Movement Choppy

**Symptoms**: Cursor stutters or updates slowly

**Solutions**:
- Increase `UPDATE_RATE_HZ` in config.py
- Optimize main loop (reduce print statements)
- Check CPU usage (may be maxing out)

---

### Issue: Double-Clicks Instead of Single

**Symptoms**: One button press = two clicks

**Solutions**:
- Increase `DEBOUNCE_MS` to 30-50ms
- Check for loose button connections
- Use better quality buttons

---

## Next Steps

Now that your joystick mouse is working:

1. **Tune parameters** in `config.py` for your preference
2. **Real-world test** for 15+ minutes of use
3. **Design enclosure** for permanent build
4. **Explore enhancements** from backlog (scroll, profiles, etc.)

## Need Help?

- Check `README.md` for architecture details
- Review `PROJECT_PLAN.md` for implementation guide
- Search forums: https://forum.micropython.org/
- Raspberry Pi Pico community: https://forums.raspberrypi.com/

---

**Congratulations! You've built a custom joystick mouse!**
