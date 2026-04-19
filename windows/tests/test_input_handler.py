import json
import pytest
from unittest.mock import MagicMock, patch, call, PropertyMock


def test_mouse_move_calls_pynput_move():
    with patch('input_handler.mouse') as mock_mouse:
        position_mock = PropertyMock()
        type(mock_mouse).position = position_mock
        from input_handler import handle_input_event
        event = json.dumps({
            'type': 'mouse_move',
            'x': 0.5,
            'y': 0.25,
            'screen_w': 1920,
            'screen_h': 1080
        })
        handle_input_event(event)
        # PropertyMock records setter calls as positional args on the mock itself
        position_mock.assert_called_once_with((960, 270))


def test_mouse_click_calls_press_and_release():
    with patch('input_handler.mouse') as mock_mouse:
        from input_handler import handle_input_event
        event = json.dumps({'type': 'mouse_click', 'button': 'left'})
        handle_input_event(event)
        mock_mouse.press.assert_called_once()
        mock_mouse.release.assert_called_once()


def test_key_type_calls_keyboard():
    with patch('input_handler.keyboard') as mock_keyboard:
        from input_handler import handle_input_event
        event = json.dumps({'type': 'key_type', 'text': 'a'})
        handle_input_event(event)
        mock_keyboard.type.assert_called_once_with('a')


def test_unknown_event_does_not_raise():
    from input_handler import handle_input_event
    handle_input_event(json.dumps({'type': 'unknown_xyz'}))


def test_key_press_special_key():
    """key_press with a known pynput Key enum name (e.g. 'ctrl') must call keyboard.press with the Key object."""
    with patch('input_handler.keyboard') as mock_keyboard:
        from input_handler import handle_input_event
        from pynput.keyboard import Key
        event = json.dumps({'type': 'key_press', 'key': 'ctrl'})
        handle_input_event(event)
        mock_keyboard.press.assert_called_once_with(Key.ctrl)


def test_key_press_unknown_key_does_not_raise():
    """key_press with a multi-char unknown key name must not raise and must not call keyboard.press."""
    with patch('input_handler.keyboard') as mock_keyboard:
        from input_handler import handle_input_event
        event = json.dumps({'type': 'key_press', 'key': 'unknown_special'})
        handle_input_event(event)
        mock_keyboard.press.assert_not_called()
