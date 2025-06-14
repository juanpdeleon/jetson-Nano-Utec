# -*- coding: utf-8 -*-
import torch
import time
import csv
import os
from datetime import datetime
from glob import glob
from jtop import jtop


# === CONFIGURACIÓN ===
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, "video_metrics_summary.csv")
FRAMES_POR_VIDEO = 100

# === MODELO DE EJEMPLO ===
model = torch.nn.Identity().to(DEVICE)
model.eval()

# === HEADERS DEL CSV ===
headers = [
    "timestamp", "video_file", "frames_simulados", "duracion_s", "fps_promedio",
    "mem_allocated_MB", "mem_reserved_MB" , "Volt","Curr","power"
]

def power_jetson():

	with jtop() as jetson:
		if not jetson.ok():
			raise RuntimeError("No se pudo conectar con jtop")
		power_data = jetson.power['tot']
		voltaje = power_data['volt']
		corriente = power_data['curr']
		potencia = power_data['power']
            
		return(voltaje,corriente,potencia)
       
            
# Crear CSV si no existe
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as f:
        csv.writer(f).writerow(headers)

# === PROCESAR VIDEOS ===
video_files = sorted(glob(os.path.join(SCRIPT_DIR, "*.mp4")))
print(f"🎞 Se encontraron {len(video_files)} videos.")



for video_path in video_files:
    video_name = os.path.basename(video_path)
    print(f"\n▶️ Procesando: {video_name}")
    print("🕒 Inicio:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    video_start = time.time()

    for _ in range(FRAMES_POR_VIDEO):
        dummy_input = torch.randn(1, 3, 224, 224).to(DEVICE)
        torch.cuda.synchronize()
        with torch.no_grad():
            _ = model(dummy_input)
        torch.cuda.synchronize()

    video_end = time.time()
    duracion = video_end - video_start
    fps_promedio = FRAMES_POR_VIDEO / duracion if duracion > 0 else 0.0
    mem_alloc = torch.cuda.memory_allocated(0) / 1024**2
    mem_reserved = torch.cuda.memory_reserved(0) / 1024**2

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Escribir CSV
    medidas = power_jetson()
    v, i, p = medidas
    with open(CSV_FILE, mode='a', newline='') as f:
        csv.writer(f).writerow([
            timestamp, video_name, FRAMES_POR_VIDEO, round(duracion, 3),
            round(fps_promedio, 2), round(mem_alloc, 2), round(mem_reserved, 2,),v,i,p
        ])

    print(f"✅ {video_name} procesado. Duración: {duracion:.2f}s | FPS: {fps_promedio:.1f}")

print("\n📁 Resultado guardado en:", CSV_FILE)

