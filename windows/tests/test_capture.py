# windows/tests/test_capture.py
import pytest
import asyncio
import numpy as np

@pytest.mark.asyncio
async def test_frame_has_correct_shape():
    """Frame capturado deve ser array numpy com 3 canais e dimensões positivas."""
    from capture import ScreenCaptureTrack
    track = ScreenCaptureTrack()
    frame = await track.recv()
    img = frame.to_ndarray(format='bgr24')
    assert img.ndim == 3
    assert img.shape[2] == 3
    assert img.shape[0] > 0 and img.shape[1] > 0

@pytest.mark.asyncio
async def test_frame_dtype_is_uint8():
    from capture import ScreenCaptureTrack
    track = ScreenCaptureTrack()
    frame = await track.recv()
    img = frame.to_ndarray(format='bgr24')
    assert img.dtype == np.uint8
