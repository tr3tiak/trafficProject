import psycopg2
import requests
from shapely.geometry import LineString
from shapely.ops import transform
from functools import partial
import pyproj
import json

with open('my_geojson.json', 'r') as f:
    data = json.load(f)

# Function to calculate the similarity between two LineStrings using Hausdorff distance
def calculate_similarity(geojson_line, overpass_line):
    # Convert the Overpass geometry to a Shapely LineString
    overpass_coords = [(point['lon'], point['lat']) for point in overpass_line]
    overpass_line_string = LineString(overpass_coords)

    # Calculate the Hausdorff distance between the two geometries
    hausdorff_distance = geojson_line.hausdorff_distance(overpass_line_string)
    
    # Normalize the distance to a similarity score (the smaller the distance, the higher the similarity)
    similarity_score = 1 / (1 + hausdorff_distance)  # A higher score means more similar
    return similarity_score



# Main function to find the most similar highway based on the GeoJSON input
def find_most_similar_highway(coordinates):
    try:
        geojson_line = LineString(coordinates)
        centroid = geojson_line.centroid
        lon, lat = centroid.x, centroid.y
        #rint(lon, lat)
        # Overpass query to find nearby highways, excluding specific types
        overpass_query= f"""
    [out:json];
    way(around:100,{lat},{lon})["highway"]["highway"!="footway"]["highway"!="cycleway"]["highway"!="path"]["highway"!="steps"]["highway"!="service"]["highway"!="construction"];
    out geom;
    """


        response = requests.post('https://overpass-api.de/api/interpreter', data=overpass_query)
        response.raise_for_status()
        data = response.json()

        if len(data['elements']) == 0:
            return None, "No highways found in the area"

        # Iterate over the results and calculate similarity with the GeoJSON line
        best_similarity = -1
        best_way = None
        for element in data['elements']:
            if 'geometry' in element:
                similarity = calculate_similarity(geojson_line, element['geometry'])
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_way = element

        # Return the most similar way
        return best_way['id'], "Success"

    except Exception as e:
        return None, f"Error: {str(e)}"
    




# Параметры подключения к PostgreSQL
host = "localhost"
database = "mydb"
user = "user"
password = "DP5vR23y"

# SQL-запрос для добавления строки
sql_ways = """
INSERT INTO ways (id, bandwidth)
VALUES (%s, %s)
ON CONFLICT (id)
DO UPDATE SET 
    bandwidth = EXCLUDED.bandwidth
"""
sql_flow = """
INSERT INTO flow_ways (ways_id, time, flow)
VALUES (%s, %s, %s)
ON CONFLICT (ways_id, time)
DO UPDATE SET 
    flow = EXCLUDED.flow
"""

try:
    conn = psycopg2.connect(host=host, database=database, user=user, password=password, port = 5432)

# Создание курсора
    cur = conn.cursor()

# Добавление строк без транзакции
    for ways in data['features']:
        id, error = find_most_similar_highway(ways["geometry"]["coordinates"])
        print(id)
        bandwidth = ways["properties"]["bandwidth"]
        flow_list = ways["properties"]["flow"]

        try:
            # Выполнение SQL-запроса
            cur.execute(sql_ways, (id, bandwidth))
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
