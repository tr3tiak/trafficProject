import json

def add_bandwidth_field(filename):
    """Добавляет поле 'bandwidth' со значением 0 к каждому элементу в JSON-файле.

    Args:
        filename (str): Имя JSON-файла.
    """

    with open(filename, 'r') as f:
        data = json.load(f)

    for item in data['elements']:
        item["bandwidth"] = 350
        item["flow"] = {
            "8:00": 120,
            "18:00": 150
        } 

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)  # indent=4 для форматирования вывода

add_bandwidth_field('ways.json') 