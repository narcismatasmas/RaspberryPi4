import json
import sqlite3
import os
from datetime import datetime, timezone
from contextlib import contextmanager

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "nowplaying.db"))
MARGEN_MINUTOS = 1

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    """Crea las tablas si no existen. Llamar una vez al arrancar la API."""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                album_art TEXT,
                detected_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS current_state (
                device_id TEXT PRIMARY KEY,
                success INTEGER NOT NULL,
                title TEXT,
                artist TEXT,
                album_art TEXT,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_device ON tracks(device_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_detected_at ON tracks(detected_at)")


# ==========================================
# GESTIÓN DE LA CANCIÓN ACTUAL
# ==========================================

def save_current_track(track_data, device_id="default"):
    now = datetime.now(timezone.utc).isoformat()


    with get_conn() as conn:
        if track_data.get("success") is True:
            conn.execute("""
                INSERT INTO current_state (device_id, success, title, artist, album_art, updated_at)
                VALUES (?, 1, ?, ?, ?, ?)
                ON CONFLICT(device_id) DO UPDATE SET
                    success=1, title=excluded.title, artist=excluded.artist,
                    album_art=excluded.album_art, updated_at=excluded.updated_at
            """, (device_id, track_data.get("title"), track_data.get("artist"),
                  track_data.get("album_art"), now))

            _add_to_history(conn, device_id, track_data, now)
            return

        row = conn.execute(
            "SELECT * FROM current_state WHERE device_id = ?", (device_id,)
        ).fetchone()

        if row is None:
            conn.execute("""
                INSERT INTO current_state (device_id, success, title, artist, album_art, updated_at)
                VALUES (?, 0, ?, ?, ?, ?)
            """, (device_id, track_data.get("title"), track_data.get("artist"),
                  track_data.get("album_art"), now))
            return

        if row["success"] == 0:
            return  # ya estaba marcado como "nada sonando"

        last_time = datetime.fromisoformat(row["updated_at"])
        diferencia = (datetime.now(timezone.utc) - last_time).total_seconds() / 60

        if diferencia > MARGEN_MINUTOS:
            conn.execute("""
                UPDATE current_state
                SET success=0, title=?, artist=?, album_art=?, updated_at=?
                WHERE device_id=?
            """, (track_data.get("title"), track_data.get("artist"),
                  track_data.get("album_art"), now, device_id))




def get_current_track(device_id="default"):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM current_state WHERE device_id = ?", (device_id,)
        ).fetchone()

    if row is None:
        return {
            "success": False,
            "title": "Ninguna canción",
            "artist": "Esperando música...",
            "album_art": None,
            "timestamp": None,
        }

    return {
            "success": bool(row["success"]),
            "title": row["title"],
            "artist": row["artist"],
            "album_art": row["album_art"],
            "timestamp": row["updated_at"],    
        }


# ==========================================
# 🆕 GESTIÓN DEL HISTORIAL
# ==========================================


def _add_to_history(conn, device_id, track_data, timestamp):
    """Evita duplicar si es la misma canción que la última registrada para ese dispositivo."""
    last = conn.execute("""
        SELECT title, artist FROM tracks
        WHERE device_id = ? ORDER BY id DESC LIMIT 1
    """, (device_id,)).fetchone()

    if last and last["title"] == track_data.get("title") and last["artist"] == track_data.get("artist"):
        return

    conn.execute("""
        INSERT INTO tracks (device_id, title, artist, album_art, detected_at)
        VALUES (?, ?, ?, ?, ?)
    """, (device_id, track_data.get("title"), track_data.get("artist"),
          track_data.get("album_art"), timestamp))


def get_history(device_id=None, since=None, until=None, limit=50, offset=0):
    """
    Filtros pensados para la futura app:
    - device_id: filtrar por dispositivo
    - since / until: timestamps ISO, para rango de fechas
    - limit / offset: paginación
    """
    query = "SELECT * FROM tracks WHERE 1=1"
    params = []
    if device_id:
        query += " AND device_id = ?"
        params.append(device_id)
    if since:
        query += " AND detected_at >= ?"
        params.append(since)
    if until:
        query += " AND detected_at <= ?"
        params.append(until)

    query += " ORDER BY detected_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()

    return [dict(r) for r in rows]