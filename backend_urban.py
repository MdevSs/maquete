# backend_urbanflow.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple
import time
import threading

app = FastAPI(title="UrbanFlow Backend")

class Count(BaseModel):
    car_count1: int;
    car_count2: int

@app.post("/decide/")
async def create_item(count: Count):
    if(count.car_count1 > 0 and count.car_count2 > 0):
        # sec = 3+(count.car_count*2)
        command = "1G"
    else:
        # sec = 4+(count.car_count2*2)
        command = "1R"
    print(command)
    return command

# Run with:
# uvicorn backend_urbanflow:app --host 0.0.0.0 --port 8000
