import json
import os
from datetime import datetime, timezone

DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "current_track.json"))
DB_HISTORY_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "history.json"))
MARGEN_MINUTOS = 1

# ==========================================
# GESTIÓN DE LA CANCIÓN ACTUAL
# ==========================================

def save_current_track(track_data):
    """Guarda la canción o el fallo. Si es un éxito, lo añade al historial."""
    track_data["timestamp"] = datetime.now(timezone.utc).isoformat()
    

    if track_data.get("success") is True:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(track_data, f, indent=4, ensure_ascii=False)
        add_to_history(track_data)
        return

    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(track_data, f, indent=4, ensure_ascii=False)
        return

    # Leemos la última canción registrada
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data_actual = json.load(f)

    # Si lo que hay guardado ya era un fallo, no hacemos nada
    if data_actual.get("success") is False:
        return

    # Si hay una canción real en el JSON, medimos cuánto tiempo lleva sonando
    last_time_str = data_actual.get("timestamp")
    if last_time_str:
        last_time = datetime.fromisoformat(last_time_str)
        ahora = datetime.now(timezone.utc)
        diferencia = (ahora - last_time).total_seconds() / 60

        # Solo marcamos como Unknown si ha pasado el tiempo de gracia
        if diferencia > MARGEN_MINUTOS:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(track_data, f, indent=4, ensure_ascii=False)





def get_current_track():
    """Lee la canción actual y aplica el margen si no se detecta nada"""
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


    return data

# ==========================================
# 🆕 GESTIÓN DEL HISTORIAL (Últimas 10)
# ==========================================

def get_history():
    """Devuelve la lista del historial. Crea el archivo si no existe."""
    if not os.path.exists(DB_HISTORY_FILE):
        with open(DB_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
        
    with open(DB_HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def add_to_history(track_data):
    """Añade la canción al historial sin duplicar la última y manteniendo máximo 10."""
    history = get_history()
    
    # Comprobar que no sea exactamente la misma que la última añadida
    if len(history) > 0:
        last_track = history[0]
        if last_track.get("title") == track_data.get("title") and last_track.get("artist") == track_data.get("artist"):
            return # Es la misma, no la duplicamos
            
    # Preparamos los datos limpios para el historial
    historial_entry = {
        "title": track_data.get("title"),
        "artist": track_data.get("artist"),
        "album_art": track_data.get("album_art"),
        "timestamp": track_data.get("timestamp")
    }
    
    # Insertar al principio de la lista
    history.insert(0, historial_entry)
    
    # Recortar a las últimas 10
    history = history[:10]
    
    # Guardar en el archivo JSON
    with open(DB_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)