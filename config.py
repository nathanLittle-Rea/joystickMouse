"""
Configuration file for Joystick Mouse
Adjust these parameters to tune the feel and responsiveness
"""

# ============================================================================
# JOYSTICK CALIBRATION
# ============================================================================

# Center position (neutral joystick position)
# Measure these values by running joystick_test.py and letting joystick rest
# Default: 32768 for 16-bit ADC (range 0-65535)
CENTER_X = 32768
CENTER_Y = 32768

# Dead zone radius - prevents drift when joystick is centered
# Increase if cursor drifts when you're not touching the joystick
# Decrease for more sensitive response (but may cause drift)
# Recommended range: 1500-4000
DEAD_ZONE = 2000

# Invert axes if movement direction is wrong
# True = inverted, False = normal
INVERT_X = False
INVERT_Y = False

# ============================================================================
# CURSOR MOVEMENT & ACCELERATION
# ============================================================================

# Maximum cursor speed (HID mouse limit is 127)
# Lower = slower max speed, Higher = faster max speed
# Recommended range: 80-127
MAX_SPEED = 127

# Acceleration curve exponent
# 1.0 = Linear (proportional)
# 2.0 = Quadratic (gentle at first, fast at extremes) - RECOMMENDED
# 3.0 = Cubic (very gentle, then very fast)
# Higher values = more precision at small movements, more speed at large movements
ACCELERATION_EXPONENT = 2.0

# Minimum speed threshold
# Below this velocity, cursor won't move (prevents tiny jitters)
# Set to 0 to disable
MIN_SPEED_THRESHOLD = 0

# ============================================================================
# BUTTON CONFIGURATION
# ============================================================================

# Button GPIO pins
BUTTON_LEFT = 15      # Left mouse click
BUTTON_RIGHT = 14     # Right mouse click
BUTTON_MIDDLE = 13    # Middle mouse click

# Arrow button GPIO pins (for precision movement)
BUTTON_ARROW_UP = 10
BUTTON_ARROW_DOWN = 11
BUTTON_ARROW_LEFT = 12
BUTTON_ARROW_RIGHT = 16

# Button debounce time in milliseconds
# Increase if you get double-clicks from single press
# Decrease for faster response (but may cause bounce)
# Recommended range: 15-50ms
DEBOUNCE_MS = 20

# ============================================================================
# ARROW BUTTON PRECISION CONTROL
# ============================================================================

# Pixels to move per arrow button press
ARROW_PIXELS_PER_PRESS = 1

# Initial delay before repeat starts (milliseconds)
# How long you must hold arrow button before it starts repeating
ARROW_REPEAT_INITIAL_DELAY = 300

# Repeat rate once repeating starts (milliseconds)
# Lower = faster repeat, Higher = slower repeat
ARROW_REPEAT_RATE = 100

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

# Main loop update rate in Hz
# Higher = smoother cursor movement, more CPU usage
# Lower = less smooth, less CPU usage
# Recommended: 100-200Hz
# USB HID standard: 125Hz
UPDATE_RATE_HZ = 125

# Calculate loop delay from update rate
LOOP_DELAY_MS = int(1000 / UPDATE_RATE_HZ)

# Enable performance monitoring (prints FPS to console)
# Useful for tuning, but disable for production
DEBUG_PERFORMANCE = False

# Print interval for debug output (seconds)
DEBUG_PRINT_INTERVAL = 1.0

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# Joystick ADC resolution (don't change unless you know what you're doing)
ADC_MAX = 65535  # 16-bit ADC
ADC_MIN = 0

# Maximum deflection from center for scaling calculations
# This is the maximum useful deflection (center +/- this value)
MAX_DEFLECTION = 32767

# Smoothing factor for joystick input (0.0 = no smoothing, 1.0 = max smoothing)
# Higher values = smoother but more latency
# Set to 0.0 to disable (recommended for gaming/precision)
# Set to 0.1-0.3 for smoother feel (recommended for general use)
SMOOTHING_FACTOR = 0.0

# ============================================================================
# PRESETS (Uncomment to use)
# ============================================================================

# # PRESET: Precision Mode (slow and precise)
# MAX_SPEED = 60
# ACCELERATION_EXPONENT = 2.5
# DEAD_ZONE = 1500

# # PRESET: Gaming Mode (fast and responsive)
# MAX_SPEED = 127
# ACCELERATION_EXPONENT = 1.5
# DEAD_ZONE = 1000

# # PRESET: Comfortable Mode (balanced)
# MAX_SPEED = 100
# ACCELERATION_EXPONENT = 2.0
# DEAD_ZONE = 2000

# ============================================================================
# FEATURE FLAGS
# ============================================================================

# Enable scroll wheel emulation (not implemented yet)
ENABLE_SCROLL = False

# Scroll modifier button (hold this button + move Y-axis to scroll)
BUTTON_SCROLL_MODIFIER = None  # Set to GPIO pin number when implemented

# Enable multiple sensitivity profiles (not implemented yet)
ENABLE_PROFILES = False

# Profile switch button (cycles through profiles)
BUTTON_PROFILE_SWITCH = None  # Set to GPIO pin number when implemented

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def apply_dead_zone(value, center, dead_zone):
    """
    Apply dead zone to raw ADC value
    Returns offset from center, or 0 if within dead zone
    """
    offset = value - center
    if abs(offset) < dead_zone:
        return 0
    return offset


def apply_acceleration(velocity, max_velocity, exponent, max_speed):
    """
    Apply acceleration curve to velocity
    Input: velocity in range -max_velocity to +max_velocity
    Output: accelerated velocity in range -max_speed to +max_speed
    """
    if velocity == 0:
        return 0

    # Normalize to -1.0 to 1.0
    normalized = velocity / max_velocity

    # Apply acceleration curve (preserve sign)
    sign = 1 if normalized >= 0 else -1
    accelerated = (abs(normalized) ** exponent) * sign

    # Scale to output range
    output = int(accelerated * max_speed)

    # Clamp to valid range
    return max(-max_speed, min(max_speed, output))


def clamp(value, min_val, max_val):
    """Clamp value to range"""
    return max(min_val, min(max_val, value))


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_config():
    """
    Validate configuration parameters
    Returns True if valid, prints warnings otherwise
    """
    valid = True

    if DEAD_ZONE < 0 or DEAD_ZONE > 10000:
        print("WARNING: DEAD_ZONE should be 0-10000")
        valid = False

    if MAX_SPEED < 1 or MAX_SPEED > 127:
        print("WARNING: MAX_SPEED must be 1-127 (HID limit)")
        valid = False

    if ACCELERATION_EXPONENT < 1.0 or ACCELERATION_EXPONENT > 5.0:
        print("WARNING: ACCELERATION_EXPONENT should be 1.0-5.0")
        valid = False

    if UPDATE_RATE_HZ < 10 or UPDATE_RATE_HZ > 1000:
        print("WARNING: UPDATE_RATE_HZ should be 10-1000")
        valid = False

    if DEBOUNCE_MS < 0 or DEBOUNCE_MS > 100:
        print("WARNING: DEBOUNCE_MS should be 0-100")
        valid = False

    if SMOOTHING_FACTOR < 0.0 or SMOOTHING_FACTOR > 1.0:
        print("WARNING: SMOOTHING_FACTOR should be 0.0-1.0")
        valid = False

    return valid


# Run validation on import
if __name__ == "__main__":
    if validate_config():
        print("Configuration valid!")
    else:
        print("Configuration has warnings, please review")
