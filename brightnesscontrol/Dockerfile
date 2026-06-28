# Usamos una imagen ligera de Python oficial para la arquitectura de la Pi
FROM python:3.11-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

RUN pip install --no-cache-dir astral

ENV PYTHONUNBUFFERED=1

# Copiamos tu script de brillo dentro del contenedor
COPY main.py .

# Comando para arrancar tu script
CMD ["python", "main.py"]
