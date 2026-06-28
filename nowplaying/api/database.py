import json
import os
from datetime import datetime, timezone

DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "current_track.json"))
MARGEN_MINUTOS = 2

def save_current_track(track_data):
    """Guarda la canción junto con la hora actual en formato ISO"""
    # Añadimos la hora actual en la que se registra el evento
    track_data["timestamp"] = datetime.now(timezone.utc).isoformat()
    
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(track_data, f, indent=4, ensure_ascii=False)

def get_current_track():
    """Lee la canción actual y aplica el margen de 2 minutos si no se detecta nada"""
    estado_vacio = {
        "success": False,
        "title": "Ninguna canción",
        "artist": "Esperando música...",
        "album_art": None,
        "timestamp": None
    }

    if not os.path.exists(DB_FILE):
        return estado_vacio

    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Si la última lectura de Shazam fue exitosa, la mostramos siempre
    if data.get("success") is True:
        return data

    # Si la última lectura fue un fallo ("success": False), comprobamos cuándo ocurrió
    # por si tenemos que mantener la canción anterior en la pantalla
    last_time_str = data.get("timestamp")
    if not last_time_str:
        return estado_vacio

    # Calculamos la diferencia de tiempo
    last_time = datetime.fromisoformat(last_time_str)
    ahora = datetime.now(timezone.utc)
    diferencia = (ahora - last_time).total_seconds() / 60

    # Si han pasado más de 2 minutos desde el último registro de "no detectado",
    # entonces ya mostramos el estado vacío oficialmente
    if diferencia > MARGEN_MINUTOS:
        return estado_vacio
        
    return data
