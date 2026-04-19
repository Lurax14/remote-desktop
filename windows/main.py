# windows/main.py
import asyncio
import sys
from peer import RemoteDesktopPeer

SIGNALING_URL = 'https://remote-desktop-vf65.onrender.com'
ROOM_ID = 'meu-desktop'

async def main():
    peer = RemoteDesktopPeer(SIGNALING_URL, ROOM_ID)
    print(f'[RD] Conectando ao servidor de sinalização: {SIGNALING_URL}')
    print(f'[RD] Sala: {ROOM_ID}')
    print('[RD] Aguardando cliente Android conectar...')
    try:
        await peer.connect()
    finally:
        await peer.close()

if __name__ == '__main__':
    asyncio.run(main())
