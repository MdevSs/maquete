import requests
import time

BACKEND_URL = "http://127.0.0.1:8000/decide/"

last_command=""
car_regressive=False
last_time_regressive=0
sec_limit=0
count1=0
count2=0
while True:
    count1 = input("carros no 1ª semaforo: ")
    count2 = input("carros no 2ª semaforo: ")
    now = time.time()
    print(now)
    if(car_regressive == False and now - last_time_regressive >= sec_limit):
        if(sec_limit == 0):
            sec_limit = 10

        print(last_time_regressive)
        last_time_regressive = now
        print(last_time_regressive)
        payload = {"car_count1": count1, "car_count2": count2}
        try:
            req = requests.post(BACKEND_URL, json=payload, timeout=5)
        except Exception as e:
            print("Erro: ", e)

        command = req.text.strip().replace('"', '')  # ex: 1G15
        last_command=command
        print(f"[BACKEND] recebido: {command}")
        car_regressive = True
        print(car_regressive)
        print("Redefinido: ", str(car_regressive))
    else:
        if("G" in last_command):
            if(count1 == "0"):
                car_regressive = False
                print(car_regressive)
        else:
            if(count2 == "0"): 
                car_regressive = False
                print(car_regressive)
        # sec_limit-=1
        print(sec_limit)  

    

# 1ª Pega quantidade de carros
# 2ª envia para o backend
# 3ª backend retorna qual semaforo fechar
# 4ª Limita a requisição até a quantidade de carros for = 0