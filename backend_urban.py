# backend_urbanflow.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collections import defaultdict, deque
from typing import Literal
import time
import threading

app = FastAPI(title="UrbanFlow Backend")



class Count(BaseModel):
    car_count1: int;
    car_count2: int

class Command(BaseModel):
    last_command: Literal["1R", "1G"];

@app.post("/invert/")
def inert_command(cmd: Command):
    res = "1G" if cmd == "1R" else "1R";
    print(f"INVERT: {res}")
    return res

@app.post("/decide/")
async def create_item(count: Count):
    sem1 = count.car_count1
    sem2 = count.car_count2
    command = ""
    if(sem1 != 0 or sem2 != 0):
        # sec = 3+(count.car_count*2)
        if(sem1 > sem2):
            command = "1G"
        else:
            command = "1R"

    
    print(command)
    return command

# Run with:
# uvicorn backend_urban:app --host 127.0.0.1 --port 8000
# uvicorn backend_urban:app --host 0.0.0.0 --port 8000
