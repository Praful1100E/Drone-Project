from fastapi import FastAPI, Request, UploadFile, File, Form, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routers import api, stream

app = FastAPI(title="Autonomous Drone Navigation - Web v2")
app.include_router(api.router, prefix="/api", tags=["api"])
app.include_router(stream.router, tags=["stream"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})