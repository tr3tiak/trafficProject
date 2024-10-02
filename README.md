# trafficProject

### Запуск проекта

1. Запуск через Docker Compose:
  - Перейдите в корневой каталог проекта.
  - Запустите команду: docker-compose up —build

2. Инициализация базы данных:
  - После запуска приложения необходимо добавить данные из JSON-файлов в базу данных.
  - Карта метро:
   - Перейдите в папку init/init_metro.
   - Запустите скрипт: python script_metro.py 
   - Этот скрипт считывает данные из metro.json и добавляет их в базу данных.
  - Карта дорог:
   - Перейдите в папку init/init_ways.
   - Запустите скрипт: python script_ways.py
   - Этот скрипт считывает данные из ways.json и добавляет их в базу данных.


### Формат данных

Данные о карте метро и карте дорог хранятся в JSON-файлах с одинаковой структурой.  Идентификаторы  (id)  в  файлах  соответствуют  идентификаторам  объектов  в  базе  данных  OpenStreetMap.org.
В проекте уже добавлены файлы metro.json и ways.json, которые содержат информацию о дорогах и метро в области, указанной в техническом задании. Также предусмотрена возможность загрузки данных через GEOJson. Для этого предусмотрены скрипты script_geoways.py и script_geometro.py в папке init_ways и init_metro соответственно. Пример формата представлен в виде файла my_geojson.json в тех же папках. 



metro.json (ways.json)

json
{
 "elements": [
  {
   "id": 1, 
   "bandwidth": 1000, 
   "flow": {
    "8:00": 200,
    "18:00": 400
   }
  },
  {
   "id": 2, 
   "bandwidth": 500, 
   "flow": {
    "8:00": 150
   }
  }
 ]
}

Описание полей:

- id: Идентификатор дороги (для ways.json) или линии метро (для metro.json).
- bandwidth: Пропускная способность дороги (только для ways.json).
- flow: Словарь, содержащий значения потока транспорта для разных временных интервалов. 
 - Ключ: Время в формате "HH:MM" (например, "8:00", "18:00").
 - Значение: Значение потока транспорта для заданного времени

## Документация API

### 1. Получение данных о метро

Адрес:  https://api.example.com/metro

Метод:  POST

Заголовки:

* Content-Type: application/json

Тело запроса (JSON):{
  "id": [
    "26999673"
  ],
  "time": "8:00"
}
Тело ответа (JSON):{
    "metro_ids": [
        {
            "id": 26999673,
            "bandwidth": 499.0,
            "time": "8:00",
            "flow": 139.0
        }
    ]
}
Описание:  Возвращает данные о метро для заданных ID в указанное время.

### 2. Получение данных о дорогах

Адрес:  https://api.example.com/ways

Метод:  POST

Заголовки:

* Content-Type: application/json

Тело запроса (JSON):{
{
  "id": [
    "10266552"
  ],
  "time": "8:00"
}

}
Тело ответа (JSON):{
    "ways_ids": [
        {
            "id": 10266552,
            "bandwidth": 499.0,
            "time": "8:00",
            "flow": 139.0
        }
    ]
}
Описание:  Возвращает данные о дорогах для заданных ID в указанное время.

### 3. Обновление данных о дорогах

Адрес:  https://api.example.com/update-ways

Метод:  POST

Заголовки:

* Content-Type: application/json

Тело запроса (JSON):{
  "elements": [
    {"id":"264555729",
    "bandwidth":500,
    "flow":{"8:00":150}
    }]}
Тело ответа (JSON):{
    "status": "ok",
    "data": [
        {
            "id": "264555729",
            "status": "success"
        }
    ]
}
Описание: Обновляет данные о пропускной способности и потоке для указанных путей.

### 4. Обновление данных о метро

Адрес:  https://api.example.com/update-metro

Метод:  POST

Заголовки:

* Content-Type: application/json

Тело запроса (JSON):{
    "elements": [
        {
            "id": 26999673,
            "bandwidth": 499,
            "flow": {
                "8:00": 139
            }
        }
    ]
}
Тело ответа (JSON):{
    "status": "ok",
    "data": [
        {
            "id": 26999673,
            "status": "success"
        }
    ]
}
Описание: Обновляет данные о пропускной способности и потоке для указанных ID метро.


### Алгоритмы и расчеты

1.  Распределение потока по метро и дорогам:

*   Определение путей:  API  использует сервис  OSRM  (Open Source Routing Machine) для расчета маршрутов до центра. Для расчета маршрутов до области используется алгоритм, по которому выбирается вектор противоположный по направлению вектору, направленному в центр, и строится маршрут до ближайшей точки в области по направлению выбранного вектора. API  берет несколько путей с разными параметрами для получения более точных данных.
*   Распределение потока:  Поток распределяется между метро пропорционально их текущей загрузке.  API  использует данные о пропускной способности и потоке каждого метро, чтобы рассчитать, насколько каждое метро загружено. Между дорожными путями поток распределяется равномерно.


2.  Круги на карте:

*   Радиусы:  Круги на карте представляют радиус, в котором происходит расчет потока для каждого метро и дорог.  Радиус задается пользователем.
*   Цель:  API  использует радиусы для определения области, в которой находится поток, который  влияет на загрузку дорог и метро.  
