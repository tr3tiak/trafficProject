# app/main.py
from fastapi import FastAPI, Request
from databases import Database
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse
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

@app.get("{file_name}")
async def get_file(file_name: str):
    file_path = os.path.join("css", file_name)

    if file_name.endswith(".css"):
        with open(file_path, "r") as file:
            content = file.read()
        return PlainTextResponse(content=content)
    else:
        return {"error": "Invalid file extension"}


@app.get("{file_name}")
async def get_file(file_name: str):
    file_path = os.path.join("scripts", file_name)

    if file_name.endswith(".js"):
        with open(file_path, "r") as file:
            data = file.read()
        return HTMLResponse(content=data)
    else:
        return {"error": "Invalid file extension"}
 

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

@app.post("/update-ways/")
async def upd_ways(request: Request):
    resp = []
    try:
        item_data = await request.json()
        item_data = jsonable_encoder(item_data)
        for ways in item_data['elements']:
            id = ways["id"]
            bandwidth = ways["bandwidth"]
            flow_list = ways["flow"]
                    
            query_ways = f"""
INSERT INTO ways (id, bandwidth)
VALUES (:id, :bandwidth),
ON CONFLICT (id)
DO UPDATE SET 
    bandwidth = EXCLUDED.bandwidth
"""
            query_flow = f"""
INSERT INTO flow_ways (ways_id, time, flow)
VALUES (:id, :time, :flow),
ON CONFLICT (ways_id, time)
DO UPDATE SET 
    flow = EXCLUDED.flow
"""
            try:
                async with database.transaction():
                    await database.execute(query_ways, values = {"id": int(id), "bandwidth": bandwidth})
                    for time_str, flow in flow_list.items():
                        time_obj = datetime.strptime(time_str, '%H:%M').time() 
                        await database.execute(query_flow, values = {"id": int(id), "time": time_obj, "flow": flow})
                    resp.append({"id": id, "status": "success"})  # Добавить информацию об успешном обновлении
            except Exception as e:
                print(f"Ошибка: {e}")
                resp.append({"id": id, "status": "error", "message": str(e)}) # Добавить информацию об ошибке

        return {"status": "ok", "data": resp}  # Возвращаем JSON-ответ с результатами
    except:
        return {"status": "error", "message": "Invalid JSON format"}  # Возвращаем JSON-ответ об ошибке

@app.post("/update-metro/")
async def upd_metro(request: Request):
    resp = []
    try:
        item_data = await request.json()
        item_data = jsonable_encoder(item_data)
        for metro in item_data['elements']:
            id = metro["id"]
            bandwidth = metro["bandwidth"]
            flow_list = metro["flow"]
                    
            query_metro = f"""
INSERT INTO metro (id, bandwidth)
VALUES (:id, :bandwith),
ON CONFLICT (id)
DO UPDATE SET 
    bandwidth = EXCLUDED.bandwidth
"""
            query_flow = f"""
INSERT INTO flow_metro (metro_id, time, flow)
VALUES (:id, :time, :flow),
ON CONFLICT (metro_id, time)
DO UPDATE SET 
    flow = EXCLUDED.flow
"""
            try:
                async with database.transaction():
                    await database.execute(query_metro, values = {"id": int(id), "bandwidth": bandwidth})
                    for time_str, flow in flow_list.items():
                        time_obj = datetime.strptime(time_str, '%H:%M').time() 
                        await database.execute(query_flow, values = {"id": int(id), "time": time_obj, "flow": flow})
                    resp.append({"id": id, "status": "success"})  # Добавить информацию об успешном обновлении
            except Exception as e:
                print(f"Ошибка: {e}")
                resp.append({"id": id, "status": "error", "message": str(e)}) # Добавить информацию об ошибке

        return {"status": "ok", "data": resp}  # Возвращаем JSON-ответ с результатами
    except:
        return {"status": "error", "message": "Invalid JSON format"}  # Возвращаем JSON-ответ об ошибке