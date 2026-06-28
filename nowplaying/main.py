import asyncio
import time
import requests
from datetime import datetime, timezone
import os
import json

# Importamos las funciones que ya programamos y funcionan
from core.recorder import record_audio
from core.shazam_client import recognize_song

API_URL = "http://127.0.0.1:8000/update-track"
DB_FILE = "current_track.json" # Archivo donde la API lee el estado
MARGEN_MINUTOS = 0.5
RECORD_DEVICE = 1  # Tu micrófono USB

def obtener_ultimo_estado_guardado():
    """Lee el archivo JSON directamente para saber qué había antes"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

async def loop_reconocimiento():
    print("🚀 Automatizador de 'Now Playing' iniciado...")
    WAV_FILE = "live_sample.wav"
    
    while True:
        # 1. Grabar fragmento de 5 segundos
        record_audio(duration=5, device_id=RECORD_DEVICE, output_filename=WAV_FILE)
        
        # 2. Intentar reconocer con Shazam
        result = await recognize_song(WAV_FILE)
        
        if result:
            ahora = datetime.now(timezone.utc)
            
            if result["success"]:
                # ¡Hay música! Actualizamos la API inmediatamente
                print(f"📢 Actualizando API: {result['title']} - {result['artist']}")
                try:
                    requests.post(API_URL, json=result)
                except requests.exceptions.ConnectionError:
                    print("❌ Error: No se pudo conectar con la API (¿está encendida?)")
            
            else:
                # Shazam no ha detectado nada en esta ronda. Aplicamos tu lógica de cortesía:
                ultimo_estado = obtener_ultimo_estado_guardado()
                
                if ultimo_estado and ultimo_estado.get("success") is True:
                    # Había una canción sonando antes. Comprobamos cuánto hace
                    last_time_str = ultimo_estado.get("timestamp")
                    if last_time_str:
                        last_time = datetime.fromisoformat(last_time_str)
                        diferencia_minutos = (ahora - last_time).total_seconds() / 60
                        
                        if diferencia_minutos <= MARGEN_MINUTOS:
                            # Estamos dentro de los 2 minutos, mantenemos la canción anterior silenciosamente
                            restante = int((MARGEN_MINUTOS - diferencia_minutos) * 60)
                            print(f"⏳ Silencio/No detectado. Manteniendo canción anterior por cortesía ({restante}s restantes).")
                            # No enviamos nada a la API para no machacar el estado válido
                            await asyncio.sleep(10)
                            continue
                
                # Si no había canción anterior, o si ya pasaron los 2 minutos, enviamos el estado vacío
                print("🍂 Margen de cortesía superado o sin historial. Limpiando pantalla...")
                try:
                    requests.post(API_URL, json=result)
                except requests.exceptions.ConnectionError:
                    pass

        # Espera de 10 segundos antes de volver a activar el micrófono
        print("💤 Esperando 7 segundos para el siguiente ciclo...\n")
        await asyncio.sleep(7)

if __name__ == "__main__":
    try:
        asyncio.run(loop_reconocimiento())
    except KeyboardInterrupt:
        print("\n🛑 Automatizador detenido por el usuario.")
