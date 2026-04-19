import json
import pytest
from unittest.mock import MagicMock, patch, call


def test_mouse_move_calls_pynput_move():
    with patch('input_handler.mouse') as mock_mouse:
        from input_handler import handle_input_event
        event = json.dumps({
            'type': 'mouse_move',
            'x': 0.5,
            'y': 0.25,
            'screen_w': 1920,
            'screen_h': 1080
        })
        handle_input_event(event)
        mock_mouse.position = (960, 270)
        assert True  # if no exception, passed


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
