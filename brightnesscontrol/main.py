import os
import time
from datetime import datetime
from astral import LocationInfo
from astral.sun import sun

# Configuración de la pantalla Waveshare DSI (ruta 10-0045)
BRIGHTNESS_PATH = "/sys/class/backlight/10-0045/brightness"

# Definimos Barcelona para el cálculo de horas de sol reales
city = LocationInfo("Barcelona", "Spain", "Europe/Madrid", 41.3851, 2.1734)

def set_screen_brightness(percentage):
    """Ajusta el brillo de la pantalla de 0 a 100% (mapeado a 0-255)"""
    try:
        percentage = max(0, min(100, percentage))
        value = int((percentage / 100.0) * 255)
        
        with open(BRIGHTNESS_PATH, "w") as f:
            f.write(str(value))
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Brillo físico cambiado al: {percentage}% ({value})")
    except Exception as e:
        print(f"Error al escribir en el hardware de la pantalla: {e}")

def main():
    print("Iniciando servicio independiente de brillo automático...")
    while True:
        try:
            ahora = datetime.now(city.tzinfo)
            s = sun(city.observer, date=ahora.date(), tzinfo=city.tzinfo)
            
            amanecer = s['dawn']
            anochecer = s['dusk']
            
            if ahora < amanecer or ahora > anochecer:
                # 🌙 MODO NOCHE
                set_screen_brightness(15) 
            else:
                # ☀️ MODO DÍA
                set_screen_brightness(100)
                
        except Exception as e:
            print(f"Error en el cálculo solar: {e}")
            
        # Duerme 10 minutos (300 segundos) antes de volver a chequear
        time.sleep(600)

if __name__ == '__main__':
    main()