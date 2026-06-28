from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.database import get_current_track, save_current_track
import os

app = FastAPI(title="Now Playing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conseguimos la ruta absoluta de la raíz del proyecto (nowplaying/)
# Como este archivo está en nowplaying/api/main.py, el padre de su carpeta es la raíz.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Montamos los archivos estáticos y las plantillas asegurando que las carpetas existen
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# --- RUTA PARA MOSTRAR LA WEB ---
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """Sirve la página web principal del Dashboard"""
    return templates.TemplateResponse(request=request, name="index.html", context={})

# --- RUTAS DE DATOS ---
@app.get("/now-playing")
def now_playing():
    return get_current_track()

@app.post("/update-track")
def update_track(track: dict):
    save_current_track(track)
    return {"status": "success", "updated_at": track.get("timestamp")}
