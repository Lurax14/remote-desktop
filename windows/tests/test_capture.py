# windows/tests/test_capture.py
import pytest
import pytest_asyncio
import numpy as np

from capture import ScreenCaptureTrack


@pytest_asyncio.fixture
async def track():
    t = ScreenCaptureTrack()
    try:
        yield t
    finally:
        t.stop()


@pytest.mark.asyncio
async def test_frame_has_correct_shape(track):
    """Frame capturado deve ser array numpy com 3 canais e dimensões positivas."""
    frame = await track.recv()
    img = frame.to_ndarray(format='bgr24')
    assert img.ndim == 3
    assert img.shape[2] == 3
    assert img.shape[0] > 0 and img.shape[1] > 0


@pytest.mark.asyncio
async def test_frame_dtype_is_uint8(track):
    frame = await track.recv()
    img = frame.to_ndarray(format='bgr24')
    assert img.dtype == np.uint8


@pytest.mark.asyncio
async def test_pts_monotonicity(track):
    """PTS deve aumentar estritamente entre frames consecutivos."""
    frame1 = await track.recv()
    frame2 = await track.recv()
    assert frame2.pts > frame1.pts
