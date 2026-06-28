import sounddevice as sd
from scipy.io import wavfile
import os

def record_audio(duration=7, sample_rate=44100, device_id=None, output_filename="sample.wav"):
    print(f"🎤 Grabando {duration} segundos de audio...")
    try:
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16',
            device=device_id
        )

        sd.wait()
        print("✅ Grabación finalizada.")

        wavfile.write(output_filename, sample_rate, recording)
        print(f"💾 Archivo guardado como: {output_filename}")
        return os.path.abspath(output_filename)

    except Exception as e:
        print(f"❌ Error al grabar: {e}")
        return None


# Bloque de prueba: se ejecuta solo si lanzas este script directamente
if __name__ == "__main__":
    # Cambiado a 1 según tu configuración de micro
    RECORD_DEVICE = 1

    print("--- Test de Grabación ---")
    record_audio(duration=5, device_id=RECORD_DEVICE, output_filename="test_micro.wav")
