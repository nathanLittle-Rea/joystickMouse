"""
USB HID mouse using machine.USBDevice (MicroPython >= 1.23, rp2 port).
"""
import machine
import struct
import time

# HID mouse report descriptor
_MOUSE_DESCRIPTOR = bytes([
    0x05, 0x01,  # Usage Page (Generic Desktop)
    0x09, 0x02,  # Usage (Mouse)
    0xA1, 0x01,  # Collection (Application)
    0x09, 0x01,  #   Usage (Pointer)
    0xA1, 0x00,  #   Collection (Physical)
    0x05, 0x09,  #     Usage Page (Button)
    0x19, 0x01,  #     Usage Minimum (1)
    0x29, 0x03,  #     Usage Maximum (3)
    0x15, 0x00,  #     Logical Minimum (0)
    0x25, 0x01,  #     Logical Maximum (1)
    0x95, 0x03,  #     Report Count (3)
    0x75, 0x01,  #     Report Size (1)
    0x81, 0x02,  #     Input (Data, Variable, Absolute)
    0x95, 0x01,  #     Report Count (1)
    0x75, 0x05,  #     Report Size (5)
    0x81, 0x03,  #     Input (Constant) - padding
    0x05, 0x01,  #     Usage Page (Generic Desktop)
    0x09, 0x30,  #     Usage (X)
    0x09, 0x31,  #     Usage (Y)
    0x15, 0x81,  #     Logical Minimum (-127)
    0x25, 0x7F,  #     Logical Maximum (127)
    0x75, 0x08,  #     Report Size (8)
    0x95, 0x02,  #     Report Count (2)
    0x81, 0x06,  #     Input (Data, Variable, Relative)
    0xC0,        #   End Collection
    0xC0,        # End Collection
])

# Full USB descriptor set
_USB_DESC = (
    # Device descriptor
    bytes([
        0x12, 0x01,        # bLength, bDescriptorType (Device)
        0x00, 0x02,        # bcdUSB 2.0
        0x00, 0x00, 0x00,  # bDeviceClass, SubClass, Protocol (defined by interface)
        0x40,              # bMaxPacketSize0 (64)
        0xC0, 0x16,        # idVendor (0x16C0 - VOTI)
        0xDC, 0x05,        # idProduct (0x05DC)
        0x00, 0x01,        # bcdDevice
        0x01,              # iManufacturer
        0x02,              # iProduct
        0x00,              # iSerialNumber
        0x01,              # bNumConfigurations
    ]),
    # Configuration descriptor (config + interface + HID + endpoint)
    bytes([
        # Configuration
        0x09, 0x02,        # bLength, bDescriptorType (Configuration)
        0x22, 0x00,        # wTotalLength (9+9+9+7 = 34)
        0x01,              # bNumInterfaces
        0x01,              # bConfigurationValue
        0x00,              # iConfiguration
        0xA0,              # bmAttributes (bus powered, remote wakeup)
        0x32,              # bMaxPower (100mA)
        # Interface
        0x09, 0x04,        # bLength, bDescriptorType (Interface)
        0x00,              # bInterfaceNumber
        0x00,              # bAlternateSetting
        0x01,              # bNumEndpoints
        0x03,              # bInterfaceClass (HID)
        0x01,              # bInterfaceSubClass (Boot)
        0x02,              # bInterfaceProtocol (Mouse)
        0x00,              # iInterface
        # HID descriptor
        0x09, 0x21,        # bLength, bDescriptorType (HID)
        0x11, 0x01,        # bcdHID 1.11
        0x00,              # bCountryCode
        0x01,              # bNumDescriptors
        0x22,              # bDescriptorType (Report)
        len(_MOUSE_DESCRIPTOR), 0x00,  # wDescriptorLength
        # Endpoint
        0x07, 0x05,        # bLength, bDescriptorType (Endpoint)
        0x81,              # bEndpointAddress (IN, EP1)
        0x03,              # bmAttributes (Interrupt)
        0x08, 0x00,        # wMaxPacketSize (8)
        0x0A,              # bInterval (10ms polling)
    ]),
)

_report = bytearray(3)  # [buttons, x, y]

def _control_xfer_cb(stage, request):
    # stage 1 = SETUP
    if stage == 1:
        bmRequestType, bRequest, wValue, wIndex, wLength = struct.unpack('<BBHHH', request)
        # GET_DESCRIPTOR for HID Report (0x22)
        if bmRequestType == 0x81 and bRequest == 0x06 and (wValue >> 8) == 0x22:
            return _MOUSE_DESCRIPTOR
    return False

_usb = machine.USBDevice()
_usb.builtin_driver = machine.USBDevice.BUILTIN_NONE
_usb.config(
    desc_dev=_USB_DESC[0],
    desc_cfg=_USB_DESC[1],
    desc_strs=(b'', b'JoystickMouse', b'Joystick Mouse'),
    control_xfer_cb=_control_xfer_cb,
)
_usb.active(1)

# Give host time to enumerate
time.sleep_ms(500)


def move(buttons, dx, dy):
    """Send a mouse HID report. buttons=bitmask, dx/dy=-127..127."""
    dx = max(-127, min(127, dx))
    dy = max(-127, min(127, dy))
    _report[0] = buttons & 0x07
    _report[1] = dx & 0xFF
    _report[2] = dy & 0xFF
    _usb.submit_xfer(0x81, _report)
