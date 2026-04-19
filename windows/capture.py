# windows/capture.py
import asyncio
import time
import numpy as np
import dxcam
from av import VideoFrame
from aiortc import VideoStreamTrack
import fractions

class ScreenCaptureTrack(VideoStreamTrack):
    kind = 'video'

    def __init__(self, fps: int = 30):
        super().__init__()
        self._fps = fps
        self._camera = dxcam.create(output_color='BGR')
        self._camera.start(target_fps=fps)
        self._pts = 0

    async def recv(self) -> VideoFrame:
        frame_data = None
        while frame_data is None:
            frame_data = self._camera.get_latest_frame()
            if frame_data is None:
                await asyncio.sleep(1 / self._fps)

        video_frame = VideoFrame.from_ndarray(frame_data, format='bgr24')
        video_frame.pts = self._pts
        video_frame.time_base = fractions.Fraction(1, self._fps)
        self._pts += 1
        return video_frame

    def stop(self):
        self._camera.stop()
        super().stop()
