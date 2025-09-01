import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    r = client.get('/')
    assert r.status_code == 200

def test_video_feed():
    r = client.get('/api/video_feed', stream=True)
    assert r.status_code == 200
    # Should return multipart stream
    assert 'multipart' in r.headers.get('content-type', '')