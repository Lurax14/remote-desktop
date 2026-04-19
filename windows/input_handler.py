import json
import screeninfo
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController

mouse = MouseController()
keyboard = KeyboardController()

_BUTTON_MAP = {
    'left': Button.left,
    'right': Button.right,
    'middle': Button.middle,
}


def _get_screen_size() -> tuple[int, int]:
    monitor = screeninfo.get_monitors()[0]
    return monitor.width, monitor.height


def handle_input_event(raw: str) -> None:
    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        return

    kind = event.get('type')

    if kind == 'mouse_move':
        sw = event.get('screen_w') or _get_screen_size()[0]
        sh = event.get('screen_h') or _get_screen_size()[1]
        x = int(event['x'] * sw)
        y = int(event['y'] * sh)
        mouse.position = (x, y)

    elif kind == 'mouse_click':
        btn = _BUTTON_MAP.get(event.get('button', 'left'), Button.left)
        mouse.press(btn)
        mouse.release(btn)

    elif kind == 'mouse_scroll':
        mouse.scroll(event.get('dx', 0), event.get('dy', 0))

    elif kind == 'key_type':
        keyboard.type(event.get('text', ''))

    elif kind == 'key_press':
        keyboard.press(event.get('key', ''))

    elif kind == 'key_release':
        keyboard.release(event.get('key', ''))
