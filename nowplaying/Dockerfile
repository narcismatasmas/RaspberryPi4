FROM python:3.11-slim

# Instalar dependencias de audio del sistema y compiladores necesarios
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar el archivo de requerimientos e instalar librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Evitar que los prints de Python se queden en el limbo de la caché
ENV PYTHONUNBUFFERED=1

# Copiar el resto del código del proyecto
COPY . .

# ¡ESTO ES LO QUE FALTA! 
# Darle permiso de ejecución al script antes de usarlo
RUN chmod +x entrypoint.sh

# Asegurar que los logs salgan a la consola (importante en Docker)
ENV PYTHONUNBUFFERED=1

# Exponer el puerto en el que corre tu API (asumo que es el 5000, si es otro cámbialo)
EXPOSE 8000

# Ejecutar el script principal
CMD ["./entrypoint.sh"]
