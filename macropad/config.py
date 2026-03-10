"""
Macropad configuration - pins, layers, macros
All tunable parameters live here.
"""

# ============================================================================
# GPIO PINS
# ============================================================================

# 4x4 key matrix
# Rows: driven HIGH one at a time (output)
# Cols: read (input with pull-down)
ROW_PINS = [0, 1, 2, 3]     # GP0-GP3
COL_PINS = [4, 5, 6, 7]     # GP4-GP7

# Rotary encoder
ENC_CLK = 10   # GP10
ENC_DT  = 11   # GP11
ENC_SW  = 12   # GP12 (push button)

# OLED I2C
I2C_SDA = 16   # GP16
I2C_SCL = 17   # GP17
I2C_ADDR = 0x3C

# ============================================================================
# DEBOUNCE
# ============================================================================
DEBOUNCE_MS = 20
ENCODER_DEBOUNCE_MS = 5

# ============================================================================
# LAYERS
# ============================================================================
LAYER_NAMES = ["General", "Media", "VSCode", "Numpad"]
NUM_LAYERS = len(LAYER_NAMES)

# ============================================================================
# KEY LAYOUT (4x4 = 16 keys, row-major)
# Each entry is one of:
#   ('key',   keycodes)       - send HID keycode(s), e.g. ('key', [0x04]) for 'a'
#   ('macro', string)         - type a string
#   ('combo', [mod, keycode]) - modifier+key, e.g. Ctrl+C
#   ('media', action)         - media key: 'vol_up','vol_down','mute','play','next','prev'
#   ('layer', n)              - switch to layer n
#   ('none',  None)           - no action
#
# HID keycodes: https://usb.org/sites/default/files/hut1_21.pdf page 53+
# Common: 0x28=Enter, 0x2A=Backspace, 0x2B=Tab, 0x4F-0x58=F1-F10
#         0x29=Escape, 0x4C=Delete, 0x52=Up 0x51=Down 0x50=Left 0x4F=Right
# Modifiers: CTRL=0x01, SHIFT=0x02, ALT=0x04, GUI=0x08

LAYERS = [
    # --- Layer 0: General ---
    [
        ('combo', [0x01, 0x06]),   # Ctrl+C  (Copy)
        ('combo', [0x01, 0x19]),   # Ctrl+V  (Paste)
        ('combo', [0x01, 0x1C]),   # Ctrl+Y  (Redo)
        ('combo', [0x01, 0x1D]),   # Ctrl+Z  (Undo)

        ('combo', [0x01, 0x04]),   # Ctrl+A  (Select All)
        ('combo', [0x01, 0x21]),   # Ctrl+X  (Cut)
        ('combo', [0x01, 0x13]),   # Ctrl+P  (Print)
        ('combo', [0x01, 0x16]),   # Ctrl+S  (Save)

        ('combo', [0x01, 0x14]),   # Ctrl+Q  (Quit)
        ('combo', [0x01, 0x17]),   # Ctrl+T  (New Tab)
        ('combo', [0x01, 0x11]),   # Ctrl+N  (New)
        ('combo', [0x01, 0x08]),   # Ctrl+E  (unused/search)

        ('key',   [0x29]),         # Escape
        ('key',   [0x28]),         # Enter
        ('key',   [0x2A]),         # Backspace
        ('key',   [0x4C]),         # Delete
    ],

    # --- Layer 1: Media ---
    [
        ('media', 'prev'),
        ('media', 'play'),
        ('media', 'next'),
        ('media', 'stop'),

        ('media', 'vol_down'),
        ('media', 'mute'),
        ('media', 'vol_up'),
        ('none',  None),

        ('combo', [0x08, 0x04]),   # Win+A (Action Center)
        ('combo', [0x08, 0x1D]),   # Win+D (Show Desktop)
        ('combo', [0x08, 0x05]),   # Win+E (Explorer)
        ('combo', [0x08, 0x15]),   # Win+R (Run)

        ('combo', [0x08, 0x06]),   # Win+C (Cortana)
        ('combo', [0x08, 0x27]),   # Win+0 (jump list)
        ('combo', [0x01|0x02, 0x29]), # Ctrl+Shift+Esc (Task Manager)
        ('none',  None),
    ],

    # --- Layer 2: VSCode ---
    [
        ('combo', [0x01, 0x10]),   # Ctrl+M  (Toggle minimap / misc)
        ('combo', [0x01, 0x2B]),   # Ctrl+Tab (next tab)
        ('combo', [0x01|0x02, 0x2B]), # Ctrl+Shift+Tab (prev tab)
        ('combo', [0x01, 0x35]),   # Ctrl+` (terminal)

        ('key',   [0x3A]),         # F1 (command palette shortcut)
        ('combo', [0x01, 0x36]),   # Ctrl+F2 (select all occurrences)
        ('key',   [0x3C]),         # F3 (find next)
        ('combo', [0x02, 0x3C]),   # Shift+F3 (find prev)

        ('combo', [0x01, 0x2F]),   # Ctrl+/ (comment line)
        ('combo', [0x01|0x02, 0x0B]), # Ctrl+Shift+H (replace in files)
        ('combo', [0x01, 0x0B]),   # Ctrl+H (replace)
        ('combo', [0x01, 0x0F]),   # Ctrl+L (select line)

        ('combo', [0x01, 0x37]),   # Ctrl+F5 (run without debug)
        ('key',   [0x40]),         # F7 (build)
        ('combo', [0x01, 0x0C]),   # Ctrl+I (format/suggest)
        ('combo', [0x01, 0x16]),   # Ctrl+S (save)
    ],

    # --- Layer 3: Numpad ---
    [
        ('key',   [0x5F]),  # Numpad 7
        ('key',   [0x60]),  # Numpad 8
        ('key',   [0x61]),  # Numpad 9
        ('key',   [0x56]),  # Numpad -

        ('key',   [0x5C]),  # Numpad 4
        ('key',   [0x5D]),  # Numpad 5
        ('key',   [0x5E]),  # Numpad 6
        ('key',   [0x57]),  # Numpad +

        ('key',   [0x59]),  # Numpad 1
        ('key',   [0x5A]),  # Numpad 2
        ('key',   [0x5B]),  # Numpad 3
        ('key',   [0x58]),  # Numpad Enter

        ('key',   [0x62]),  # Numpad 0
        ('key',   [0x62]),  # Numpad 0
        ('key',   [0x63]),  # Numpad .
        ('key',   [0x55]),  # Numpad *
    ],
]

# Key labels shown on OLED (4 chars max per key, row-major per layer)
KEY_LABELS = [
    ["Copy", "Pste", "Redo", "Undo",
     "SelA", "Cut ", "Prnt", "Save",
     "Quit", "NTab", "New ", "Srch",
     "Esc ", "Entr", "Bksp", "Del "],

    ["Prev", "Play", "Next", "Stop",
     "VolD", "Mute", "VolU", "    ",
     "WinA", "WinD", "WinE", "WinR",
     "WinC", "Win0", "TskM", "    "],

    ["Mmap", "NxTb", "PvTb", "Term",
     "F1  ", "SelO", "Find", "PFnd",
     "Cmnt", "RepF", "Repl", "SelL",
     "Run ", "F7  ", "Sust", "Save"],

    ["7   ", "8   ", "9   ", "-   ",
     "4   ", "5   ", "6   ", "+   ",
     "1   ", "2   ", "3   ", "Entr",
     "0   ", "0   ", ".   ", "*   "],
]

# ============================================================================
# ENCODER ACTIONS PER LAYER
# ============================================================================
# clockwise / counter-clockwise
ENCODER_CW  = ['vol_up',  'next', 'combo_next_line', 'numpad_plus']
ENCODER_CCW = ['vol_down','prev', 'combo_prev_line', 'numpad_minus']
# Encoder press cycles to next layer
