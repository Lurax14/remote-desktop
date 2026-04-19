import json
import screeninfo
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key

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


def _parse_key(key_name: str):
    """Try to map to pynput Key enum, fall back to raw char, or None if unhandleable."""
    try:
        return Key[key_name]
    except KeyError:
        return key_name if len(key_name) == 1 else None


def handle_input_event(raw: str) -> None:
    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        return

    kind = event.get('type')

    if kind == 'mouse_move':
        sw = event.get('screen_w')
        sh = event.get('screen_h')
        if sw is None or sh is None:
            sw, sh = _get_screen_size()
        try:
            x = int(float(event['x']) * sw)
            y = int(float(event['y']) * sh)
        except (KeyError, TypeError, ValueError):
            return
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
        k = _parse_key(event.get('key', ''))
        if k is not None:
            keyboard.press(k)

    elif kind == 'key_release':
        k = _parse_key(event.get('key', ''))
        if k is not None:
            keyboard.release(k)
