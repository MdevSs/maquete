import os
import cv2
import requests
import numpy as np
from ultralytics import YOLO
import time
import serial

# ==== CONFIGURAÇÕES ====
BACKEND_URL = "http://127.0.0.1:8000/decide/"
ESP_URL = ["http://10.0.2.119/capture", "http://10.0.2.152:8080//shot.jpg"]
MODEL_PATH = r"c:\github\IA-ESP32-CAM\models\best.pt"

# Quantos segundos esperar antes de fazer nova requisição ao backend
BACKEND_COOLDOWN = 5  


def run_capture_inference():

    # Carrega modelo
    model = YOLO(MODEL_PATH)

    # Conecta Arduino
    try:
        arduino = serial.Serial('COM5', 9600, timeout=1)
        print("Arduino conectado")
        time.sleep(2)
    except:
        print("Erro ao conectar no Arduino")
        arduino = None

    last_sent_command = None
    last_backend_call = 0

    while True:
        try:
            car_counts = []
            annotated_frames = []

            session = requests.Session()

            for i, url in enumerate(ESP_URL):

                # CAPTURA DA ESP32
                try:
                    # response = requests.get(url, timeout=5)
                    response = session.get(url, timeout=3)
                except:
                    print(f"Erro ao capturar da câmera {i}")
                    car_counts.append(0)
                    annotated_frames.append(None)
                    continue

                img_array = np.frombuffer(response.content, np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                if frame is None:
                    print(f"Frame inválido da câmera {i}")
                    car_counts.append(0)
                    annotated_frames.append(None)
                    continue

                # INFERÊNCIA
                frame = cv2.resize(frame, (160, 160))
                results = model(frame)
                boxes = results[0].boxes
                car_count = len(boxes)
                car_counts.append(car_count)

                print(f"Câmera {i}: {car_count} carros")

                annotated_frame = results[0].plot()
                annotated_frames.append(annotated_frame)

            # --------- LÓGICA DE REQUISIÇÃO ----------
            now = time.time()
    
            # if car_count > 0

            # só chama o backend a cada X segundos
            # if now - last_backend_call >= BACKEND_COOLDOWN:

            #     payload = {"car_count": car_count}
            #     try:
            #         req = requests.post(BACKEND_URL, json=payload, timeout=5)
            #         command = req.text.strip().replace('"', '')  # ex: 1G15

            #         print(f"[BACKEND] recebido: {command}")

            #         # só envia ao Arduino se mudou
            #         if arduino and command != last_sent_command:
            #             arduino.write((command + "\n").encode())
            #             print(f"[ARDUINO] enviado: {command}")
            #             last_sent_command = command

            #         last_backend_call = now

            #     except Exception as e:
            #         print("Erro backend:", e)

            # MOSTRA JANELA PARA DEBUG
            # MOSTRA JANELAS PARA DEBUG
            for i, frame in enumerate(annotated_frames):
                if frame is not None:
                    resized = cv2.resize(frame, (640, 480))
                    cv2.imshow(f"ESP32 CAM {i}", resized)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break


        except Exception as e:
            print("Erro geral:", e)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_capture_inference()
