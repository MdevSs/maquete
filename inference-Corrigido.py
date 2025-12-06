# ...existing code...
import os
import cv2
import requests
import numpy as np
from ultralytics import YOLO
import time
import serial
import torch
from ultralytics.nn.tasks import DetectionModel

# ==== CONFIGURAÇÕES ====
BACKEND_URL = "http://10.0.1.236:8000/decide/"
#BACKEND_URL = "http://127.0.0.1:8000/decide/"
# ESPs (aceita 1 ou 2)
ESP_URL = ["http://10.0.1.189:8080/shot.jpg", "http://10.0.1.223:8080//shot.jpg"]
#MODEL_PATH = r"c:\github\IA-ESP32-CAM\models\best.pt"
MODEL_PATH = r"/home/raspberry/Desktop/maquete/models/best.onnx"
# Quantos segundos esperar antes de fazer nova requisição ao backend (cooldown entre POSTS)
BACKEND_COOLDOWN = 5

# Parâmetros de inferência (ajuste conforme desempenho)
MODEL_IMGSZ = 320
MODEL_CONF = 0.25

def run_capture_inference():
    car_regressive = False
    last_time_regressive = 0.0  # usado pela lógica regressive
    sec_limit = 0               # primeiro envio imediato, depois setado para 10s após primeiro POST
    torch.serialization.add_safe_globals([DetectionModel])

    # Carrega modelo (ajuste device se necessário: device='cpu' ou device='cuda:0')
    model = YOLO(MODEL_PATH)
    try:
        model.overrides = {"imgsz": MODEL_IMGSZ, "conf": MODEL_CONF}
    except Exception:
        pass

    # Conecta Arduino (se disponível)
    try:
        arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        print("Arduino conectado")
        time.sleep(2)
    except Exception:
        print("Erro ao conectar no Arduino")
        arduino = None

    last_sent_command = None
    last_backend_call = 0.0

    session = requests.Session()
    exit_requested = False

    while not exit_requested:
        try:
            now = time.time()

            car_counts = []
            annotated_frames = []

            # Captura + inferência para cada ESP configurada
            for i, url in enumerate(ESP_URL):
                try:
                    response = session.get(url, timeout=3)
                except Exception as e:
                    print(f"Erro ao capturar da câmera {i}: {e}")
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

                # Otimização: redimensiona antes da inferência
                inference_frame = cv2.resize(frame, (MODEL_IMGSZ, MODEL_IMGSZ))
                # Executa inferência (passa imgsz explicitamente)
                try:
                    results = model(inference_frame, imgsz=MODEL_IMGSZ, conf=MODEL_CONF)
                except Exception as e:
                    print(f"Erro na inferência câmera {i}: {e}")
                    car_counts.append(0)
                    annotated_frames.append(None)
                    continue

                boxes = results[0].boxes if hasattr(results[0], "boxes") else []
                car_count = len(boxes)
                car_counts.append(car_count)

                print(f"Câmera {i}: {car_count} carros")

                # Plot apenas para exibição (pode ser pesado; manter somente para debug)
                try:
                    annotated = results[0].plot() if hasattr(results[0], "plot") else inference_frame
                    annotated_frames.append(annotated)
                except Exception:
                    annotated_frames.append(inference_frame)

            # Só prossegue com POST se tiver ao menos 2 leituras quando esperado; aceita 1 câmera também
            if len(car_counts) >= 2:
                # Lógica de requisição: respeita sec_limit (regressive) e BACKEND_COOLDOWN
                if (not car_regressive) and (now - last_time_regressive >= sec_limit) and (now - last_backend_call >= BACKEND_COOLDOWN):
                    payload = {"car_count1": int(car_counts[0]), "car_count2": int(car_counts[1])}
                    print("Enviando payload:", payload)
                    try:
                        req = session.post(BACKEND_URL, json=payload, timeout=5)
                        command = req.text.strip().replace('"', '')
                        print(f"[BACKEND] recebido: {command}")

                        # se retorno válido, atualiza estados e envia ao Arduino se conectado
                        if command:
                            # enviar apenas se arduino conectado
                            if arduino:
                                try:
                                    # evita enviar repetido se for igual ao último (opcional)
                                    if command != last_sent_command:
                                        arduino.write((command + "\n").encode())
                                        print(f"[ARDUINO] enviado: {command}")
                                except Exception as e:
                                    print("Erro ao escrever no Arduino:", e)

                            last_sent_command = command
                            last_backend_call = now
                            car_regressive = True
                            # após primeiro envio, queremos que o sec_limit seja 10 (comportamento desejado)
                            if sec_limit == 0:
                                sec_limit = 10
                            # atualiza last_time_regressive apenas quando a requisição foi realmente enviada/com sucesso
                            last_time_regressive = now
                    except Exception as e:
                        print("Erro backend:", e)

            # Atualiza car_regressive para false quando não houver carros no semáforo verde
            if last_sent_command:
                try:
                    # assume formato contendo "G" ou "R" indicando qual semáforo está verde
                    if "G" in last_sent_command:
                        # se semáforo 1 verde e não há carros na câmera 0
                        if car_counts and car_counts[0] == 0:
                            car_regressive = False
                    else:
                        # presume semáforo 2 verde
                        if car_counts and len(car_counts) > 1 and car_counts[1] == 0:
                            car_regressive = False
                except Exception:
                    pass

            # Exibição das janelas e checagem para sair
            for i, frame in enumerate(annotated_frames):
                if frame is not None:
                    resized = cv2.resize(frame, (640, 480))
                    cv2.imshow(f"ESP32 CAM {i}", resized)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                exit_requested = True

            # pequeno sleep para evitar uso 100% CPU (ajuste se necessário)
            time.sleep(0.01)

        except Exception as e:
            print("Erro geral:", e)
            time.sleep(0.5)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_capture_inference()