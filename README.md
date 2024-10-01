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
В проекте уже добавлены файлы metro.json и ways.json, которые содержат информацию о дорогах и метро в области, указанной в техническом задании



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