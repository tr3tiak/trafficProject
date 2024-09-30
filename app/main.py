# app/main.py
from fastapi import FastAPI, Request
from databases import Database
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from datetime import datetime
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
"*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешенные домены
    allow_credentials=True,  # Разрешить отправку куки
    allow_methods=["*"],  # Разрешить все HTTP методы: GET, POST, PUT и т.д.
    allow_headers=["*"],  # Разрешить все заголовки
)

# Получаем URL для подключения к базе данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Инициализируем подключение к базе данных
database = Database(DATABASE_URL)

@app.on_event("startup")
async def startup():
    # Подключаемся к базе данных при старте приложения
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    # Отключаемся от базы данных при остановке приложения
    await database.disconnect()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    file_path = os.path.join("static", "index.html")
    with open(file_path, "r") as file:
        content = file.read()
    return HTMLResponse(content=content)

 

@app.post("/metro/")
async def ret_metro(request: Request):
    resp = []
    try:
        item_data = await request.json()
        item_data = jsonable_encoder(item_data)
        time_str = item_data.get("time")
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        all_ids = item_data.get("id", [])
        
        
        query_metro = "SELECT id, name, bandwidth FROM metro WHERE id =:id"
        query_flow = "SELECT metro_id, time, flow FROM flow_metro WHERE metro_id =:id AND time =:time" 
        for id in all_ids:
            try:
                row_metro = await database.fetch_one(query_metro, values = {"id": int(id)})
                row_flow = await database.fetch_one(query_flow, values = {"id": int(id), "time": time_obj})
                data = {
                    "id": row_metro["id"],
                    "name": row_metro["name"],
                    "bandwidth": row_metro["bandwidth"],
                    "time": time_str,
                    "flow": row_flow["flow"]
                }
                resp.append(data)
            except Exception as e:
                print(f"Ошибка: {e}")
    except:
        print("json not formatted") 
    return {"metro_ids": resp}

@app.post("/ways/")
async def ret_ways(request: Request):
    resp = []
    try:
        item_data = await request.json()
        item_data = jsonable_encoder(item_data)
        time_str = item_data.get("time")
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        all_ids = item_data.get("id", [])
        
        
        query_ways = "SELECT id, bandwidth FROM ways WHERE id =:id"
        query_flow = "SELECT ways_id, time, flow FROM flow_ways WHERE ways_id =:id AND time =:time" 
        for id in all_ids:
            try:
                row_ways = await database.fetch_one(query_ways, values = {"id": int(id)})
                row_flow = await database.fetch_one(query_flow, values = {"id": int(id), "time": time_obj})
                data = {
                    "id": row_ways["id"],
                    "bandwidth": row_ways["bandwidth"],
                    "time": time_str,
                    "flow": row_flow["flow"]
                }
                resp.append(data)
            except Exception as e:
                print(f"Ошибка: {e}")
    except:
        print("json not formatted") 
    return {"ways_ids": resp}