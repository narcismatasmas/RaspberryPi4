import asyncio
from shazamio import Shazam
import os

async def recognize_song(file_path):
    """
    Lee un archivo de audio local como bytes puros y lo envía a Shazam.
    """
    if not os.path.exists(file_path):
        print(f"❌ El archivo {file_path} no existe.")
        return None

    print("🔍 Enviando archivo binario directo a Shazam...")
    shazam = Shazam()
    
    try:
        # Leemos el archivo en modo binario directo
        with open(file_path, 'rb') as f:
            file_bytes = f.read()

        # Enviamos los bytes directamente
        out = await shazam.recognize(file_bytes)
        
        if not out.get('matches'):
            print("❓ Canción no identificada por ShazamIO.")
            return {
                "success": False,
                "title": "Unknown",
                "artist": "Unknown",
                "album_art": None
            }
            
        track = out['track']
        title = track.get('title', 'Título desconocido')
        artist = track.get('subtitle', 'Artista desconocido')
        
        album_art = None
        images = track.get('images')
        if images:
            album_art = images.get('coverart')

        print(f"🎵 ¡Identificada con éxito! {title} - {artist}")
        
        return {
            "success": True,
            "title": title,
            "artist": artist,
            "album_art": album_art
        }

    except Exception as e:
        print(f"❌ Error durante el reconocimiento: {e}")
        return None

if __name__ == "__main__":
    print("--- Test de Reconocimiento Binario ---")
    TEST_FILE = "test_micro.wav"
    result = asyncio.run(recognize_song(TEST_FILE))
    print("\nResultado:")
    print(result)
