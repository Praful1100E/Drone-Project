# Autonomous Drone Navigation - Web (v2)

Enhancements in v2:
- Model upload UI + backend saving to `models/` and auto-loading into the RL agent.
- Live MJPEG video stream at `/video_feed` (uses the system webcam if available; else simulated frames).
- Tailwind CDN frontend with model upload, live video, telemetry, and model status.
- ROS subscription management endpoints to subscribe/unsubscribe to topics and forward messages to WebSocket clients.
- Everything is modular so you can replace simulated parts with real hardware and ROS topics.

Run:
1) pip install -r requirements.txt
2) uvicorn app.main:app --reload
3) Open http://127.0.0.1:8000