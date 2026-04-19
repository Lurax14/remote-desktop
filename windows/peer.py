# windows/peer.py
import asyncio
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
from capture import ScreenCaptureTrack
from input_handler import handle_input_event

STUN = RTCIceServer(urls='stun:stun.l.google.com:19302')
TURN = RTCIceServer(
    urls='turn:openrelay.metered.ca:80',
    username='openrelayproject',
    credential='openrelayproject'
)

class RemoteDesktopPeer:
    def __init__(self, signaling_url: str, room_id: str):
        self._url = signaling_url
        self._room = room_id
        self._sio = socketio.AsyncClient()
        self._pc: RTCPeerConnection | None = None
        self._track = ScreenCaptureTrack()

    async def connect(self):
        self._pc = RTCPeerConnection(
            configuration=RTCConfiguration(iceServers=[STUN, TURN])
        )
        self._pc.addTrack(self._track)

        channel = self._pc.createDataChannel('input')

        @channel.on('message')
        def on_message(msg):
            handle_input_event(msg)

        @self._sio.on('peer-ready')
        async def on_peer_ready():
            offer = await self._pc.createOffer()
            await self._pc.setLocalDescription(offer)
            await self._sio.emit('offer', {
                'roomId': self._room,
                'sdp': {'type': offer.type, 'sdp': offer.sdp}
            })

        @self._sio.on('answer')
        async def on_answer(sdp):
            desc = RTCSessionDescription(sdp=sdp['sdp'], type=sdp['type'])
            await self._pc.setRemoteDescription(desc)

        @self._sio.on('ice-candidate')
        async def on_ice(candidate):
            if candidate:
                from aiortc import RTCIceCandidate
                await self._pc.addIceCandidate(RTCIceCandidate(
                    sdpMid=candidate.get('sdpMid'),
                    sdpMLineIndex=candidate.get('sdpMLineIndex'),
                    candidate=candidate.get('candidate', '')
                ))

        @self._pc.on('icecandidate')
        async def on_local_ice(candidate):
            if candidate:
                await self._sio.emit('ice-candidate', {
                    'roomId': self._room,
                    'candidate': {
                        'candidate': candidate.candidate,
                        'sdpMid': candidate.sdpMid,
                        'sdpMLineIndex': candidate.sdpMLineIndex
                    }
                })

        await self._sio.connect(self._url)
        await self._sio.emit('join', self._room)
        await self._sio.wait()

    async def close(self):
        if self._pc:
            self._track.stop()
            await self._pc.close()
        await self._sio.disconnect()
