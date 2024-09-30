import json
import psycopg2

# Загружаем данные из JSON файла
with open('metros.json', 'r') as f:
  data = json.load(f)

# Выбираем все id из объектов типа 'way'
metro_ids = [metro['id'] for metro in data['elements']]




# Параметры подключения к PostgreSQL
host = "localhost"
database = "mydb"
user = "user"
password = "DP5vR23y"

# SQL-запрос для добавления строки
sql_metro = """
INSERT INTO metro (id, name, bandwidth)
VALUES (%s, %s, %s)
ON CONFLICT (id)
DO UPDATE SET 
    bandwidth = EXCLUDED.bandwidth
"""

sql_flow =  """
DO $$
BEGIN
    -- Проверяем, существует ли запись
    IF EXISTS (SELECT 1 FROM flow_metro WHERE metro_id = %s AND time = %s) THEN
        -- Если существует, обновляем запись
        UPDATE flow_metro
        SET flow = %s  -- Укажите значение для обновления
        WHERE metro_id = %s AND time = %s;
    ELSE
        -- Если не существует, вставляем новую запись
        INSERT INTO flow_metro (metro_id, time, flow)
        VALUES (%s, %s, %s);  -- Укажите значения для time и flow
    END IF;
END $$;
"""

try:
    conn = psycopg2.connect(host=host, database=database, user=user, password=password, port = 5432)

# Создание курсора
    cur = conn.cursor()

# Добавление строк без транзакции
    for metro in data['elements']:
        id = metro["id"]
        bandwidth = metro["bandwidth"]
        name = metro["tags"]["name"]
        flow_list = metro["flow"]
        print(flow_list)
        try:
            # Выполнение SQL-запроса
            cur.execute(sql_metro, (id, name, bandwidth))
            for time, flow in flow_list.items():
                cur.execute(sql_flow, (id, time, flow, id, time, id, time, flow))
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
