#### REST-API
```
REST API for Yandex Academy backend school
Данный проект является REST-сервисом написанным на Python, который умеет обрабатывать URL запросы:
/POST/couriers - добавить курьеров
/POST/orders - добавить заказы
/PATCH/couriers/courier_id - изменить параметры для курьера(courier_id)
/POST/orders/assign({courier_id})- назначить заказы(которые он может выполнить) для курьера(courier_id)
/POST/orders/complete({courier_id, order_id, complete_time}) - завершить заказ(order_id) для курьера(courier_id)
/GET/couriers/courier_id - получить данные о курьере(courier_id)
```

#### Установка:
```
Запустить виртуальную машину
Заустить сервер:
$ python3 RESTapi/main.py

Для отчистки базы данных:
$ python3 RESTapi/clear_data.py
```



