# windows/capture.py
import asyncio
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
        self._pts_lock = asyncio.Lock()
        # aiortc RTP convention: 90 kHz clock
        self.time_base = fractions.Fraction(1, 90000)

    async def recv(self) -> VideoFrame:
        frame_data = None
        while frame_data is None:
            if self.readyState != "live":
                break
            frame_data = self._camera.get_latest_frame()
            if frame_data is None:
                await asyncio.sleep(1 / self._fps)

        video_frame = VideoFrame.from_ndarray(frame_data, format='bgr24')
        async with self._pts_lock:
            video_frame.pts = self._pts
            self._pts += int(90000 / self._fps)
        video_frame.time_base = self.time_base
        return video_frame

    def stop(self):
        try:
            self._camera.stop()
        except Exception:
            pass
        super().stop()
