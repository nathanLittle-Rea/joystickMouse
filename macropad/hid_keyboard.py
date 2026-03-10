"""
USB HID keyboard + media keys via machine.USBDevice (MicroPython >= 1.23).
Supports: standard keys, modifier combos, media/consumer keys.
"""
import machine
import struct
import time

# ---------------------------------------------------------------------------
# HID Report Descriptors
# ---------------------------------------------------------------------------

# Keyboard: 8-byte report
#   [modifier, reserved, key1, key2, key3, key4, key5, key6]
_KBD_DESCRIPTOR = bytes([
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x06,        # Usage (Keyboard)
    0xA1, 0x01,        # Collection (Application)
    # Report ID 1 - Keyboard
    0x85, 0x01,
    # Modifier byte
    0x05, 0x07,        #   Usage Page (Key Codes)
    0x19, 0xE0,        #   Usage Minimum (224) - Left Ctrl
    0x29, 0xE7,        #   Usage Maximum (231) - Right GUI
    0x15, 0x00,        #   Logical Minimum (0)
    0x25, 0x01,        #   Logical Maximum (1)
    0x75, 0x01,        #   Report Size (1)
    0x95, 0x08,        #   Report Count (8)
    0x81, 0x02,        #   Input (Data, Variable, Absolute)
    # Reserved byte
    0x95, 0x01,        #   Report Count (1)
    0x75, 0x08,        #   Report Size (8)
    0x81, 0x03,        #   Input (Constant)
    # Key array (6 keys)
    0x95, 0x06,        #   Report Count (6)
    0x75, 0x08,        #   Report Size (8)
    0x15, 0x00,        #   Logical Minimum (0)
    0x25, 0x65,        #   Logical Maximum (101)
    0x05, 0x07,        #   Usage Page (Key Codes)
    0x19, 0x00,        #   Usage Minimum (0)
    0x29, 0x65,        #   Usage Maximum (101)
    0x81, 0x00,        #   Input (Data, Array)
    0xC0,              # End Collection

    # Report ID 2 - Consumer (media keys)
    0x05, 0x0C,        # Usage Page (Consumer)
    0x09, 0x01,        # Usage (Consumer Control)
    0xA1, 0x01,        # Collection (Application)
    0x85, 0x02,        #   Report ID (2)
    0x15, 0x00,        #   Logical Minimum (0)
    0x25, 0x01,        #   Logical Maximum (1)
    0x75, 0x01,        #   Report Size (1)
    0x95, 0x08,        #   Report Count (8)
    0x09, 0xB5,        #   Usage (Scan Next Track)
    0x09, 0xB6,        #   Usage (Scan Prev Track)
    0x09, 0xB7,        #   Usage (Stop)
    0x09, 0xCD,        #   Usage (Play/Pause)
    0x09, 0xE2,        #   Usage (Mute)
    0x09, 0xE9,        #   Usage (Volume Up)
    0x09, 0xEA,        #   Usage (Volume Down)
    0x09, 0xB8,        #   Usage (Eject)
    0x81, 0x02,        #   Input (Data, Variable, Absolute)
    0xC0,              # End Collection
])

_CFG_DESC_LEN = 9 + 9 + 9 + 7  # config + interface + HID + endpoint
_HID_DESC_LEN = len(_KBD_DESCRIPTOR)

_USB_DEV_DESC = bytes([
    0x12, 0x01, 0x00, 0x02,  # bLength, bDescriptorType, bcdUSB
    0x00, 0x00, 0x00, 0x40,  # class, subclass, protocol, maxpacket
    0xC0, 0x16, 0xDC, 0x05,  # VID, PID
    0x01, 0x00,              # bcdDevice
    0x01, 0x02, 0x00,        # iManufacturer, iProduct, iSerial
    0x01,                    # bNumConfigurations
])

_USB_CFG_DESC = bytes([
    # Configuration
    0x09, 0x02, _CFG_DESC_LEN, 0x00,
    0x01, 0x01, 0x00, 0xA0, 0x32,
    # Interface
    0x09, 0x04, 0x00, 0x00, 0x01,
    0x03, 0x01, 0x01, 0x00,   # HID, Boot, Keyboard
    # HID descriptor
    0x09, 0x21, 0x11, 0x01, 0x00, 0x01, 0x22,
    _HID_DESC_LEN & 0xFF, (_HID_DESC_LEN >> 8) & 0xFF,
    # Endpoint IN1, Interrupt, 8 bytes, 10ms
    0x07, 0x05, 0x81, 0x03, 0x08, 0x00, 0x0A,
])

# Media key bit positions in report ID 2
_MEDIA_BITS = {
    'next':     0x01,
    'prev':     0x02,
    'stop':     0x04,
    'play':     0x08,
    'mute':     0x10,
    'vol_up':   0x20,
    'vol_down': 0x40,
    'eject':    0x80,
}


def _control_xfer_cb(stage, request):
    if stage == 1:
        bmRequestType, bRequest, wValue = struct.unpack_from('<BBH', request)
        if bmRequestType == 0x81 and bRequest == 0x06 and (wValue >> 8) == 0x22:
            return _KBD_DESCRIPTOR
    return False


_usb = machine.USBDevice()
_usb.builtin_driver = machine.USBDevice.BUILTIN_NONE
_usb.config(
    desc_dev=_USB_DEV_DESC,
    desc_cfg=_USB_CFG_DESC,
    desc_strs=(b'', b'MacroPad', b'Pico MacroPad'),
    control_xfer_cb=_control_xfer_cb,
)
_usb.active(1)
time.sleep_ms(500)

# Report buffers
_kbd_report   = bytearray(9)   # report_id + modifier + reserved + 6 keys
_kbd_report[0] = 0x01
_media_report = bytearray(2)   # report_id + bits
_media_report[0] = 0x02


def _send_kbd():
    _usb.submit_xfer(0x81, _kbd_report)

def _send_media():
    _usb.submit_xfer(0x81, _media_report)


def key_down(modifier, keycodes):
    """Press keys: modifier byte + list of up to 6 keycodes."""
    _kbd_report[1] = modifier & 0xFF
    for i, kc in enumerate(keycodes[:6]):
        _kbd_report[3 + i] = kc
    _send_kbd()


def key_up():
    """Release all keys."""
    for i in range(8):
        _kbd_report[i + 1] = 0
    _send_kbd()


def tap(modifier, keycodes):
    """Press and release."""
    key_down(modifier, keycodes)
    time.sleep_ms(20)
    key_up()
    time.sleep_ms(20)


def type_string(s):
    """Type a string character by character (ASCII printable only)."""
    # Simple ASCII -> HID keycode table (lowercase a-z, 0-9, space, enter)
    for ch in s:
        o = ord(ch)
        mod = 0
        if 0x61 <= o <= 0x7A:          # a-z
            kc = o - 0x61 + 0x04
        elif 0x41 <= o <= 0x5A:        # A-Z (shift)
            kc = o - 0x41 + 0x04
            mod = 0x02
        elif 0x31 <= o <= 0x39:        # 1-9
            kc = o - 0x31 + 0x1E
        elif o == 0x30:                # 0
            kc = 0x27
        elif o == 0x20:                # space
            kc = 0x2C
        elif o == 0x0A or o == 0x0D:   # newline
            kc = 0x28
        elif o == 0x09:                # tab
            kc = 0x2B
        else:
            continue
        tap(mod, [kc])


def media(action):
    """Send a media key event."""
    bit = _MEDIA_BITS.get(action, 0)
    if not bit:
        return
    _media_report[1] = bit
    _send_media()
    time.sleep_ms(20)
    _media_report[1] = 0
    _send_media()
    time.sleep_ms(20)
