#!/bin/bash
cd /home/nmatas/nowplaying
# Arrancamos la API en segundo plano
./venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 &
# Esperamos 3 segundos a que la API esté lista
sleep 3
# Arrancamos el bucle del micrófono
./venv/bin/python3 main.py
