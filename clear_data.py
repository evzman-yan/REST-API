import sqlite3
from sqlite3 import Error


def connect(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        print('Failed')
    return connection


def SET(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

query1 = 'DROP TABLE assign_order;'
query2 = 'CREATE TABLE "assign_order" (\
    courier_id INTEGER,\
	order_id INTEGER,\
	assign_time VARCHAR,\
	region INTEGER,\
	FOREIGN KEY (courier_id) REFERENCES couriers(courier_id)\
	FOREIGN KEY(order_id) REFERENCES orders(order_id))'
query3 = 'DROP TABLE courier_time;'
query4 = '\
CREATE TABLE "courier_time" (\
	courier_id INTEGER,\
	region INTEGER UNIQUE,\
	amount INTEGER,\
	duration INTEGER NOT NULL\
)'
query5 = 'DROP TABLE couriers;'
query6 = '\
CREATE TABLE "couriers" (\
    courier_id INTEGER PRIMARY KEY,\
    courier_type VARCHAR(4),\
    regions INTEGER [],\
    working_hours VARCHAR [],\
	rating FLOAT,\
	earnings FLOAT\
)'
query7 = 'DROP TABLE orders;'
query8 = '\
CREATE TABLE "orders" (\
    order_id INTEGER PRIMARY KEY,\
    weight FLOAT,\
    region INTEGER,\
    delivery_hours VARCHAR ARRAY\
)'

dataB = connect('DataBase')
SET(dataB, query1)
SET(dataB, query2)
SET(dataB, query3)
SET(dataB, query4)
SET(dataB, query5)
SET(dataB, query6)
SET(dataB, query7)
SET(dataB, query8)
dataB.close()
