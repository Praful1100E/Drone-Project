import asyncio, time, random, json
from fastapi import APIRouter, WebSocket
from ..services.ros_bridge import RosBridge

router = APIRouter()
ros = RosBridge()

clients = set()

@router.websocket('/ws/telemetry')
async def telemetry(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            # Try to pull last ros message if available
            ros_msg = ros.get_last_msg()
            if ros_msg is not None:
                payload = {'ts': time.time(), 'ros': ros_msg}
            else:
                payload = {
                    'ts': time.time(),
                    'pose': {'x': random.uniform(-5,5), 'y': random.uniform(-5,5), 'z': random.uniform(0,10)},
                    'attitude': {'roll': random.uniform(-10,10), 'pitch': random.uniform(-10,10), 'yaw': random.uniform(-180,180)},
                    'battery': random.uniform(11.0, 12.6),
                    'mode': 'rl',
                }
            await ws.send_text(json.dumps(payload))
            await asyncio.sleep(0.5)
    except Exception:
        pass
    finally:
        clients.discard(ws)