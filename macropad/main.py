"""
Macropad main loop
"""
import time
import config
import matrix
import encoder
import display
import hid_keyboard

current_layer = 0
prev_matrix   = [False] * 16

display.update(current_layer)


def handle_action(action_tuple):
    kind, data = action_tuple

    if kind == 'key':
        hid_keyboard.tap(0, data)

    elif kind == 'combo':
        mod = data[0]
        keys = data[1:]
        hid_keyboard.tap(mod, keys)

    elif kind == 'macro':
        hid_keyboard.type_string(data)

    elif kind == 'media':
        hid_keyboard.media(data)

    elif kind == 'layer':
        global current_layer
        current_layer = data % config.NUM_LAYERS
        display.update(current_layer)

    # 'none' → do nothing


def handle_encoder(delta, btn):
    global current_layer

    if btn:
        current_layer = (current_layer + 1) % config.NUM_LAYERS
        display.update(current_layer)
        display.show_message(config.LAYER_NAMES[current_layer], "")
        time.sleep_ms(400)
        display.update(current_layer)
        return

    if delta > 0:
        action = config.ENCODER_CW[current_layer]
    elif delta < 0:
        action = config.ENCODER_CCW[current_layer]
    else:
        return

    # Encoder actions are media strings or special combos
    if action in ('vol_up', 'vol_down', 'mute', 'play', 'next', 'prev', 'stop'):
        hid_keyboard.media(action)
    elif action == 'combo_next_line':
        hid_keyboard.tap(0x01, [0x28])   # Ctrl+Enter (new line below in VSCode)
    elif action == 'combo_prev_line':
        hid_keyboard.tap(0x01|0x02, [0x28])
    elif action == 'numpad_plus':
        hid_keyboard.tap(0, [0x57])
    elif action == 'numpad_minus':
        hid_keyboard.tap(0, [0x56])


while True:
    encoder.update()
    delta, btn = encoder.consume()
    if delta or btn:
        handle_encoder(delta, btn)

    curr_matrix = matrix.scan()
    pressed, released = matrix.get_events(prev_matrix, curr_matrix)

    for idx in pressed:
        action = config.LAYERS[current_layer][idx]
        display.show_keypress(current_layer, idx)
        handle_action(action)

    if released:
        hid_keyboard.key_up()
        display.update(current_layer)

    prev_matrix = curr_matrix
    time.sleep_ms(5)
