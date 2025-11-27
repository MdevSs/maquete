import os
import cv2
import requests
import numpy as np
from ultralytics import YOLO
import time
import serial
import torch
from ultralytics.nn.tasks import DetectionModel

# ==== CONFIGURAÃ‡Ã•ES ====
BACKEND_URL = "http://10.0.1.236:8000/decide/"
#BACKEND_URL = "http://127.0.0.1:8000/decide/"
#ESP_URL = ["http://10.0.2.119/capture", "http://10.0.2.152:8080//shot.jpg"]
ESP_URL = ["http://10.0.1.189:8080/shot.jpg", "http://10.0.1.223:8080//shot.jpg"]
#MODEL_PATH = r"c:\github\IA-ESP32-CAM\models\best.pt"
MODEL_PATH = r"/home/raspberry/Desktop/maquete/models/best.onnx"
# Quantos segundos esperar antes de fazer nova requisiÃ§Ã£o ao backend
BACKEND_COOLDOWN = 5  


def run_capture_inference():
    car_regressive=False
    last_time_regressive=0
    sec_limit=0
    torch.serialization.add_safe_globals([DetectionModel])
    # Carrega modelo
    model = YOLO(MODEL_PATH)

    # Conecta Arduino
    try:
        arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        print("Arduino conectado")
        time.sleep(2)
    except:
        print("Erro ao conectar no Arduino")
        arduino = None

    last_sent_command = None
    last_backend_call = 0

    session = requests.Session()
    while True:
        try:
            car_counts = []
            annotated_frames = []


            for i, url in enumerate(ESP_URL):

                # CAPTURA DA ESP32
                try:
                    # response = requests.get(url, timeout=5)
                    response = session.get(url, timeout=3)
                except Exception as e:
                    
                    print(f"Erro ao capturar da cÃ¢mera {i}\nErro: {e}")
                    car_counts.append(0)
                    annotated_frames.append(None)
                    continue

                img_array = np.frombuffer(response.content, np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                if frame is None:
                    print(f"Frame invÃ¡lido da cÃ¢mera {i}")
                    car_counts.append(0)
                    annotated_frames.append(None)
                    continue

                # INFERÃŠNCIA
                #frame = cv2.resize(frame, (160, 160))
                results = model(frame)
                boxes = results[0].boxes
                car_count = len(boxes)
                car_counts.append(car_count)

                print(f"CÃ¢mera {i}: {car_count} carros")

                annotated_frame = results[0].plot()
                annotated_frames.append(annotated_frame)

            # --------- LÃ“GICA DE REQUISIÃ‡ÃƒO ----------
            now = time.time()


            
            if(car_regressive == False and now - last_time_regressive >= sec_limit):
                if now - last_backend_call >= BACKEND_COOLDOWN:

                    payload = {"car_count1": car_counts[0], "car_count2": car_counts[1]}
                    print(payload)
                    try:
                        req = requests.post(BACKEND_URL, json=payload, timeout=5)
                        command = req.text.strip().replace('"', '')  # ex: 1G15
                        #last_sent_command = command
                        car_regressive = True
                        if(sec_limit == 0):
                            sec_limit = 10
                        print(f"[BACKEND] recebido: {command}")

                        # sÃ³ envia ao Arduino se mudou
                        #if arduino and command != last_sent_command:
                        arduino.write((command + "\n").encode())
                        print(f"[ARDUINO] enviado: {command}")
                        last_sent_command = command

                        last_backend_call = now
                    except Exception as e:
                        print("Erro backend:", e)
                    # MOSTRA JANELA PARA DEBUG
                    # MOSTRA JANELAS PARA DEBUG
                    

                last_time_regressive = now
            for i, frame in enumerate(annotated_frames):
                if frame is not None:
                    resized = cv2.resize(frame, (640, 480))
                    cv2.imshow(f"ESP32 CAM {i}", resized)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                if("G" in last_sent_command):
                    if(car_counts[0] == 0):
                        car_regressive = False
                        print(car_regressive)
                else:
                    if(car_counts[1] == 0): 
                        car_regressive = False
                        print(car_regressive)
                        
                # sec_limit-=1
                #print(sec_limit) 


        except Exception as e:
            print("Erro geral:", e)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_capture_inference()

# uvicorn backend_urban:app --host 0.0.0.0 --port 8000
# uvicorn backend_urban:app --host 127.0.0.1 --port 8000
