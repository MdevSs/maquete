import os
import cv2
import requests
import numpy as np
from ultralytics import YOLO
import time
import serial

def run_capture_inference(
    url="http://10.77.201.240/capture", 
    model_paths=None
):
    sleep = 0
    BACKEND_URL = "http://127.0.0.1:8000/decide/"
    if model_paths is None:
        model_paths = [
            r"c:\github\IA-ESP32-CAM\models\best.pt",  # modelo 1
            # r"c:\github\IA-ESP32-CAM\models\best.pt",  # modelo 2
        ]
    
    models = []
    for path in model_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Modelo não encontrado em: {path}")
        models.append(YOLO(path))

    arduino = 0
    try:
        arduino = serial.Serial('COM7', 9600)
        print("Arduino conectado");
    except:
        pass

    while True:
        try:
            # requisita uma imagem
            resp = requests.get(url, timeout=50)
            img_array = np.frombuffer(resp.content, np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if frame is None:
                print("Falha ao decodificar frame")
                continue

            annotated_frame = frame.copy()

            # roda inferência em cada modelo
            for model in models:
                results = model(frame)
                annotated_frame = results[0].plot()  # só chama o plot
                # print(results[0].boxes)

                # if(results[0].boxes>1):
                if(len(results[0].boxes)>0):
                    car_count = len(results[0].boxes)
                    print(car_count)
                    payload = {
                        "car_count": car_count
                    }
                    req = 0
                    try:

                        req = requests.post(f"{BACKEND_URL}", json=payload, timeout=5)

                    except Exception as e:

                        print("erro papai:", e)

                    print("requisição feita")
                    print(req.status_code)
                    print(req.text)
                    dado = dado = req.text.strip()  
                    dado = dado.replace('"', '')          # remove aspas
                    sleep_raw = dado.replace("1G", "")    # remove prefixo
                    sleep_int = int(sleep_raw)            # agora dá certo
                    arduino.write(dado.encode())
                    print(sleep_int)
                #   requisição para o backend

            # mostra na tela
            cv2.imshow("Inferência ESP32-CAM (/capture)", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        except Exception as e:
            print("Erro ao capturar imagem:", e)
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_capture_inference()