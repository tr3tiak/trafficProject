import json
import psycopg2

# Загружаем данные из JSON файла
with open('ways.json', 'r') as f:
  data = json.load(f)

# Выбираем все id из объектов типа 'way'
ways_ids = [ways['id'] for ways in data['elements']]




# Параметры подключения к PostgreSQL
host = "localhost"
database = "mydb"
user = "user"
password = "DP5vR23y"

# SQL-запрос для добавления строки
sql_ways = """
INSERT INTO ways (id, bandwidth)
VALUES (%s, %s),
ON CONFLICT (id)
DO UPDATE SET 
    bandwidth = EXCLUDED.bandwidth
"""
sql_flow = """
INSERT INTO flow_ways (ways_id, time, flow)
VALUES (%s, %s, %s),
ON CONFLICT (ways_id, time)
DO UPDATE SET 
    flow = EXCLUDED.flow
"""

try:
    conn = psycopg2.connect(host=host, database=database, user=user, password=password, port = 5432)

# Создание курсора
    cur = conn.cursor()

# Добавление строк без транзакции
    for ways in data['elements']:
        id = ways["id"]
        bandwidth = ways["bandwidth"]
        flow_list = ways["flow"]

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
