import asyncio
import requests
from core.recorder import record_audio
from core.shazam_client import recognize_song

DEVICE_ID = "RaspberryBCN" 

API_URL = f"http://127.0.0.1:8000/update-track?device_id={DEVICE_ID}"
RECORD_DEVICE = 1  # Tu micrófono USB

async def loop_reconocimiento():
    print("🚀 Automatizador de 'Now Playing' iniciado...")
    WAV_FILE = "live_sample.wav"
    
    while True:
        # 1. Grabar fragmento
        record_audio(duration=5, device_id=RECORD_DEVICE, output_filename=WAV_FILE)
        
        # 2. Intentar reconocer con Shazam
        result = await recognize_song(WAV_FILE)
        
        if result:
            # 3. Enviar TODO a la API (ella decidirá qué hacer con el margen)
            try:
                requests.post(API_URL, json=result)
                if result.get("success"):
                    print(f"📢 Detectado y enviado: {result.get('title')} - {result.get('artist')}")
                else:
                    print("🍂 No hay música. Notificando a la API...")
            except requests.exceptions.ConnectionError:
                print("❌ Error: No se pudo conectar con la API (¿está encendida?)")

        # Espera antes del siguiente ciclo
        print("💤 Esperando 7 segundos...\n")
        await asyncio.sleep(7)

if __name__ == "__main__":
    try:
        asyncio.run(loop_reconocimiento())
    except KeyboardInterrupt:
        print("\n🛑 Automatizador detenido por el usuario.")