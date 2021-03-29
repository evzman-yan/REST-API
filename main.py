from flask import Flask, jsonify, abort
import sqlite3
from sqlite3 import Error
from flask import make_response, request
from datetime import datetime


app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'description': 'Not found'}), 404)


# Подключиться к базе данных
def connect(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        print('Failed')
    return connection


# Выполнить запрос в базе данных
def SET(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


# Выполнить запрос и получить данные
def GET(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
        return []


# Превратить лист в строку
def list_to_str(value) -> str:
    s = '\'{'
    n = len(value)
    for i in range(n):
        if i != 0:
            s += ','
        s += str(value[i])
    s += '}\''
    return s


# Превратить строку в лист
def str_to_list(value) -> list:
    res = []
    value = value[1: len(value) - 1]
    if value.count(','):
        res = list(map(int, value.split(',')))
    else:
        res = [int(value)]
    return res


# превратить значение в строку
def value_to_str(value) -> str:
    s = '\"' + str(value) + '\"'
    return s


# для времени вида 2021/01/25T09:13:45Z
def str_to_time(value) -> list:
    time = value.split('T')[1]
    time = time[: len(time) - 1]
    h, m, s = map(int, time.split(':'))
    return [h, m, s]


# для промежутков времени ("18:05-22:45")
def str_to_hours(value) -> list:
    res = []
    value = value[1: len(value) - 1]
    if value.count(','):
        res = value.split(',')
    else:
        res = [value]
    return res


# Получить данные из запроса
def get_data_request():
    if not request.json:
        return (False, [])
    data = request.json
    return (True, data)


# Получить данные из базы данных о курьере(courier_id)
def select_courier(courier_id):
    dataB = connect('DataBase')
    query = 'SELECT * FROM couriers WHERE courier_id == ' + str(courier_id) + ';'
    courier = GET(dataB, query)
    dataB.close()
    if len(courier) == 0:
        abort(404, 'Not found')
    courier = courier[0]
    if len(courier) != 6:
        abort(404)
    result = {
        'courier_id': courier[0],
        'courier_type': courier[1],
        'regions': str_to_list(courier[2]),
        'working_hours': courier[3]
    }

    if courier[4] != -1:
        result['rating'] = courier[4]
        result['earnings'] = courier[5]
    return result


# ===================  /POST/couriers/courier_id ==================
@app.route('/couriers/<int:courier_id>', methods=['GET'])
def get_courier_by_id(courier_id):
    courier = select_courier(courier_id)
    return jsonify(courier), 200


# ===================  /POST/couriers ==================
@app.route('/couriers', methods=['POST'])
def create_couriers():
    info = get_data_request()
    if not info[0] or not 'data' in info[1]:
        abort(400)
    couriers = info[1]['data']
    n = len(couriers)
    bad_data = {'couriers': []}
    for i in range(n):
        d = couriers[i]
        if not 'courier_type' in d \
                or 'regions' not in d or not 'working_hours' in d:
            bad_data['couriers'].append({"id": d['courier_id']})
    if len(bad_data['couriers']) > 0:
        abort(400, bad_data)
    dataB = connect('DataBase')
    data = {'couriers': []}
    for i in range(n):
        d = couriers[i]
        data['couriers'].append({"id": d['courier_id']})
        query = 'INSERT INTO couriers VALUES (' + str(d['courier_id']) + ',' \
                + value_to_str(d['courier_type']) + ',' \
                + list_to_str(d['regions']) + ',' \
                + list_to_str(d['working_hours']) + ',' \
                + str(-1) + ',' + str(0) + ');'
        SET(dataB, query)
    dataB.close()
    return jsonify(data), 201


# ===================  /POST/orders ==================
@app.route('/orders', methods=['POST'])
def create_orders():
    info = get_data_request()
    if not info[0] or not 'data' in info[1]:
        abort(400)
    orders = info[1]['data']
    bad_data = {'orders': []}
    n = len(orders)
    for i in range(n):
        d = orders[i]
        print(d)
        if not 'weight' in d \
                or 'region' not in d or not 'delivery_hours' in d:
            bad_data['orders'].append({"id": d['order_id']})
    if len(bad_data['orders']) > 0:
        abort(400, bad_data)
    dataB = connect('DataBase')
    data = {'orders': []}
    for i in range(n):
        d = orders[i]
        data['orders'].append({"id": d['order_id']})
        query = 'INSERT INTO orders VALUES (' + str(d['order_id']) + ',' \
                + value_to_str(d['weight']) + ',' \
                + str(d['region']) + ',' \
                + list_to_str(d['delivery_hours']) + ');'
        SET(dataB, query)
    dataB.close()
    return jsonify(data), 201


# ===================  /PATCH/couriers ==================
@app.route('/couriers/<int:courier_id>', methods=['PATCH'])
def patch_courier_by_id(courier_id):
    new_data = request.json
    current_data = select_courier(courier_id)
    dataB = connect('DataBase')
    used = False
    if 'regions' in new_data:
        query = 'UPDATE couriers SET regions=' + list_to_str(new_data['regions']) + \
                ' WHERE courier_id=' + str(current_data['courier_id']) + ';'
        SET(dataB, query)
        used = True
    if 'courier_type' in new_data:
        query = 'UPDATE couriers SET courier_type=' + value_to_str(new_data['courier_type']) + \
                ' WHERE courier_id=' + str(current_data['courier_id']) + ';'
        SET(dataB, query)
        used = True
    if 'working_hours' in new_data:
        query = 'UPDATE couriers SET working_hours=' + list_to_str(new_data['working_hours']) + \
                ' WHERE courier_id=' + str(current_data['courier_id']) + ';'
        SET(dataB, query)
        used = True
    if not used:
        abort(400)
    return jsonify(select_courier(courier_id)), 200


# Получить информацию о всех заказах
def get_orders():
    query = 'SELECT * FROM orders'
    dataB = connect('DataBase')
    data = GET(dataB, query)
    dataB.close()
    result = []
    for order in data:
        d = dict()
        d['order_id'] = order[0]
        d['weight'] = order[1]
        d['region'] = order[2]
        d['delivery_hours'] = order[3]
        result.append(d)
    return result


# Пересекается ли time1(working_hours) и time1(delivery_hours) по времени
def has_intersection_of_time(time1: str, time2: str) -> bool:
    l1, r1 = time1.split('-')
    l2, r2 = time2.split('-')
    l1 = list(map(int, l1.split(':')))
    r1 = list(map(int, r1.split(':')))
    l2 = list(map(int, l2.split(':')))
    r2 = list(map(int, r2.split(':')))

    if l2[0] > r1[0] or (l2[0] == r1[0] and l2[1] > r1[1]):
        return False
    if l1[0] > r2[0] or (l1[0] == r2[0] and l1[1] > r2[1]):
        return False
    print('INTERSECT = True')
    return True


# Может ли курьер(courier) взять заказ(order)
def is_suitable(courier, order):
    c_type = courier['courier_type']
    weight = order['weight']
    # 10 15 50
    if c_type == 'foot':
        if weight > 10:
            return False
    elif c_type == 'bike':
        if weight > 15:
            return False
    else:
        if weight > 50:
            return False
    region = int(order['region'])
    if courier['regions'].count(region) == 0:
        return False
    wh = str_to_hours(courier['working_hours'])  # working_hours list
    dh = str_to_hours(order['delivery_hours'])  # delivery_hours list
    intersect = False
    for working_hours in wh:
        for delivery_hours in dh:
            res = has_intersection_of_time(working_hours, delivery_hours)
            intersect = intersect or res
    return intersect


# ===================  /POST/orders/assign ==================
@app.route('/orders/assign', methods=['POST'])
def assign_orders():
    if not request.json or not 'courier_id' in request.json:
        abort(400)
    courier_id = request.json['courier_id']
    courier = select_courier(courier_id)
    orders = get_orders()
    result = {"orders": []}
    regions_by_id = dict()
    for order in orders:
        regions_by_id[order['order_id']] = order['region']
        if is_suitable(courier, order):
            result['orders'].append({"id": order['order_id']})
    if len(result['orders']) == 0:
        return jsonify([])
    now = datetime.now()
    date_string = now.strftime("%Y/%m/%dT%H:%M:%SZ")
    result['assign_time'] = date_string
    for info in result['orders']:
        dataB = connect('DataBase')
        query = 'INSERT INTO assign_order VALUES (' + str(courier_id) + ', ' + str(info['id']) + \
                ', ' + value_to_str(date_string) + ', ' + str(regions_by_id[info['id']]) + ');'
        SET(dataB, query)
        query = "DELETE FROM orders WHERE order_id=" + str(info['id'])
        SET(dataB, query)
        dataB.close()
    return jsonify(result), 200


# Проверить есть ли назначенный заказ(order_id) для курьера(сourier_id)
# если есть вернуть время назначения и регион заказа и закрыть его, иначе (-1, -1)
def check_in_assign_orders(courier_id, order_id):
    dataB = connect('DataBase')
    query = 'SELECT * FROM assign_order WHERE order_id = ' + str(order_id) + \
            ' AND courier_id = ' + str(courier_id) + ';'
    data = GET(dataB, query)
    if len(data) == 0:
        dataB.close()
        return -1, -1
    query = 'DELETE FROM assign_order WHERE courier_id = ' + str(courier_id) + \
            ' AND order_id = ' + str(order_id) + ';'
    SET(dataB, query)
    dataB.close()
    return data[0][2], data[0][3]


# Обновить среднее время доставки(+ duration) в регионе(region) для курьера(courier_id)
def update_courier_delivery_duration(courier_id, region, duration):
    dataB = connect('DataBase')
    query = "SELECT * FROM courier_time WHERE courier_id = " + str(courier_id) + \
            ' AND region = ' + str(region) + ';'
    data = GET(dataB, query)
    if len(data) == 0:
        query1 = 'INSERT INTO courier_time VALUES(' + str(courier_id) + ', ' + \
                 str(region) + ', ' + str(1) + ', ' + str(duration) + ');'
        SET(dataB, query1)
        return
    data = GET(dataB, query)[0]
    amount = data[2]
    old_duration = data[3]
    new_duration = (old_duration * amount + duration) // (amount + 1)
    amount += 1
    query = 'UPDATE courier_time SET amount = ' + str(amount) + ', duration = ' + \
            str(new_duration) + ' WHERE courier_id = ' + str(courier_id) + ' AND region = ' + \
            str(region) + ';'
    SET(dataB, query)


# Получить минимальное время среди средних значений времени доставки по регионам
def get_min_duration(courier_id):
    res = 10 ** 9
    dataB = connect('DataBase')
    query = 'SELECT * FROM courier_time WHERE courier_id = ' + str(courier_id) + ';'
    data = GET(dataB, query)
    for region in data:
        res = min(res, int(region[3]))
    dataB.close()
    return res


# Обновить рейтинг и заработок для курьера(courier_id)
def update_couriers_params(rating, earnings, courier_id):
    dataB = connect('DataBase')
    query = 'UPDATE couriers SET rating = ' + str(rating) + ', earnings = ' + str(earnings) + \
            ' WHERE courier_id = ' + str(courier_id) + ';'
    SET(dataB, query)
    dataB.close()


# ===================  /POST/orders/complete ==================
@app.route('/orders/complete', methods=['POST'])
def complete_orders():
    data = request.json
    print('DATA', data)
    if not data:
        abort(400)
    print(data)
    courier_id = data['courier_id']
    order_id = data['order_id']
    comlete_time = data['complete_time']
    start_time, region = check_in_assign_orders(courier_id, order_id)
    if start_time == -1:
        abort(400)
    start_time = str_to_time(start_time)
    end_time = str_to_time(comlete_time)
    total_time = (end_time[0] - start_time[0]) * 3600
    total_time += (end_time[1] - start_time[1]) * 60
    total_time += (end_time[2] - start_time[2])
    update_courier_delivery_duration(courier_id, region, total_time)
    t = get_min_duration(courier_id)
    rating = (3600 - t) / 3600
    rating *= 5
    courier = select_courier(courier_id)
    coef = 0
    if courier['courier_type'] == 'foot':
        coef = 2
    elif courier['courier_type'] == 'bike':
        coef = 5
    else:
        coef = 9
    earnings = 0
    if 'earnings' in courier:
        earnings += courier['earnings']
    earnings += coef * 500
    update_couriers_params(rating, earnings, courier_id)
    return jsonify({"order_id": order_id}), 200


# Запуск сервера
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
