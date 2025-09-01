from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pathlib import Path
import numpy as np, cv2, os, asyncio
from ..services.vision import VisionPipeline
from ..services.rl_agent import RLAgent
from ..services.pid import PID
from ..services.sensor_fusion import ComplementaryFusion
from ..services.ros_bridge import RosBridge

router = APIRouter()

vision = VisionPipeline()
agent = RLAgent()
pid_roll = PID(kp=0.9, ki=0.02, kd=0.15, clamp=(-1.0,1.0))
pid_pitch = PID(kp=0.9, ki=0.02, kd=0.15, clamp=(-1.0,1.0))
fusion = ComplementaryFusion(alpha=0.96)
ros = RosBridge()

MODEL_DIR = Path(__file__).resolve().parents[2] / 'models'
MODEL_DIR.mkdir(exist_ok=True)

@router.post('/process_frame')
async def process_frame(file: UploadFile = File(...)):
    if file.content_type not in ['image/jpeg','image/png']:
        raise HTTPException(status_code=415, detail='Only JPEG/PNG supported')
    data = np.frombuffer(await file.read(), dtype=np.uint8)
    frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail='Invalid image data')

    obs = vision.detect_obstacles(frame)
    state = vision.estimate_state(frame)
    imu = {'roll': state.get('roll',0.0), 'pitch': state.get('pitch',0.0)}
    fused = fusion.update(imu=imu, gps=None, baro=None)
    action = agent.act(obs, state)
    return {'obstacles': obs, 'state': state, 'fused': fused, 'action': action}

@router.post('/upload_model')
async def upload_model(file: UploadFile = File(...)):
    # save the model to models/ and attempt to load
    if not file.filename:
        raise HTTPException(status_code=400, detail='No file')
    dest = MODEL_DIR / file.filename
    content = await file.read()
    dest.write_bytes(content)
    ok, msg = agent.load(str(dest))
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {'ok': True, 'detail': msg, 'path': str(dest)}

@router.post('/set_mode')
async def set_mode(mode: str):
    if mode not in {'manual','rl','pid'}:
        raise HTTPException(status_code=400, detail='Invalid mode')
    agent.set_mode(mode)
    return {'ok': True, 'mode': agent.mode}

@router.get('/video_feed')
def video_feed():
    # MJPEG streaming response: try to open webcam (0) else simulated frames
    def gen():
        cap = None
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise RuntimeError('No webcam')
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                _, jpg = cv2.imencode('.jpg', frame)
                chunk = jpg.tobytes()
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + chunk + b'\r\n')
        except Exception:
            # Simulated frames
            import numpy as np, cv2, time
            w,h = 640,480
            i = 0
            while True:
                img = (np.ones((h,w,3), dtype=np.uint8)*30)
                cv2.putText(img, f"Simulated Frame {i}", (20,50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (200,200,255), 2)
                _, jpg = cv2.imencode('.jpg', img)
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpg.tobytes() + b'\r\n')
                i += 1
                time.sleep(0.1)
        finally:
            if cap is not None:
                cap.release()

    return StreamingResponse(gen(), media_type='multipart/x-mixed-replace; boundary=frame')

@router.post('/ros/subscribe')
async def ros_subscribe(topic: str):
    ok, msg = ros.subscribe(topic)
    return {'ok': ok, 'detail': msg}

@router.post('/ros/unsubscribe')
async def ros_unsubscribe(topic: str):
    ok, msg = ros.unsubscribe(topic)
    return {'ok': ok, 'detail': msg}