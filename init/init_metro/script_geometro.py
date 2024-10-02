import requests
import json
import psycopg2

def find_nearest_railway_station_or_halt(coordinates):
    try:
        # Extract the coordinates from GeoJSON
        
        lon, lat = coordinates

        # Overpass query to find the nearest railway station or halt
        overpass_query = f"""
        [out:json];
        (
          node(around:100,{lat},{lon})["railway"="station"];
          node(around:100,{lat},{lon})["railway"="halt"];
        );
        out body;
        """

        response = requests.post('https://overpass-api.de/api/interpreter', data=overpass_query)
        response.raise_for_status()
        data = response.json()

        # Find the nearest node by calculating distance (already sorted by Overpass API with "around")
        if len(data['elements']) == 0:
            return None, "No railway station or halt found"

        nearest_node = data['elements'][0]

        return nearest_node['id'], "Success"

    except Exception as e:
        return None, f"Error: {str(e)}"



# Загружаем данные из JSON файла
with open('my_geojson.json', 'r') as f:
  data = json.load(f)





# Параметры подключения к PostgreSQL
host = "localhost"
database = "mydb"
user = "user"
password = "DP5vR23y"

# SQL-запрос для добавления строки
# SQL-запрос для добавления строки
sql_metro = """
INSERT INTO metro (id, bandwidth)
VALUES (%s, %s)
ON CONFLICT (id)
DO UPDATE SET 
    bandwidth = EXCLUDED.bandwidth
"""
sql_flow = """
INSERT INTO flow_metro (metro_id, time, flow)
VALUES (%s, %s, %s)
ON CONFLICT (metro_id, time)
DO UPDATE SET 
    flow = EXCLUDED.flow
"""

try:
    conn = psycopg2.connect(host=host, database=database, user=user, password=password, port = 5432)

# Создание курсора
    cur = conn.cursor()

# Добавление строк без транзакции
    for metro in data['features']:
        
        id, error = find_nearest_railway_station_or_halt(metro["geometry"]["coordinates"])
        bandwidth = metro["properties"]["bandwidth"]
        flow_list = metro["properties"]["flow"]
        try:
            # Выполнение SQL-запроса
            cur.execute(sql_metro, (id, bandwidth))
            for time, flow in flow_list.items():
                cur.execute(sql_flow, (id, time, flow))
            # Сохранение изменений сразу после каждой строки
            conn.commit()
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            # Откат изменений, если произошла ошибка
            conn.rollback()

    # Закрытие курсора и соединения
    cur.close()
    conn.close()

except (Exception, psycopg2.Error) as error:
    print("Ошибка при добавлении данных:", error)
