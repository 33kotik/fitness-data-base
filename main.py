import pandas as pd
import numpy as np
import random
import scipy
from collections import deque
import re
import mysql.connector
from mysql.connector import Error
import PySimpleGUI as sg
import datetime
import time

layout = [
    [sg.Button('sign gum membership')],
    [sg.Button('Make sales and attendance report')
     ],
    # [sg.Button('Make forecast of the hall is workload'),
    #  ],
    [sg.Button('edit time interval')
     ],
    [sg.Button('return membership(')
     ],

    # [sg.popup_get_date(9,1,2020)
    # ],
    [sg.Cancel()]
]

sg.theme('Dark Blue9')
window = sg.Window('fitness base', layout, size=(1500, 200))


# сделано
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


# сделано
def timing_table():
    query = "select   ti.id,t.kind,h.hall,k.name,ti.capacity,t.capacity from timing ti join type t on t.id = ti.type_id join kvants k on ti.kvant_id = k.id join halls h on h.id = ti.hall_id"
    try:
        cursor.execute(query)
        data = pd.DataFrame(cursor.fetchall())
        data.columns = ["id", "kind", "hall", "kvant", "capacity", "max capacity"]
    except Error as e:
        print(f"The error '{e}' occurred")
    return data


# сделано
def update_capacity(id, delta=1):
    type_id = find(table='timing', table_header='id', item=id, ret='type_id')[0][0]
    max_capacity = find(table='type', table_header='id', item=type_id, ret='capacity')[0][0]

    now_capacity = find(table='timing', table_header='id', item=id, ret='capacity')[0][0]
    # print(max_capacity,now_capacity)
    if now_capacity >= max_capacity:
        error("the timing is full")
    else:
        query = "UPDATE timing t SET t.capacity = t.capacity+{delta} WHERE t.id={id};".format(id=id, delta=delta)
        try:
            cursor.execute(query)
        except Error as e:
            print(f"The error '{e}' occurred")
    return


# сделано
def error(text):
    layout = [
        [sg.Text(text),
         ],
        [sg.Cancel()],
    ]
    window = sg.Window('error', layout)
    while True:
        event, values = window.read()
        if event == 'Cancel' or event == None:
            window.close()
            break
    return


myre = r'\W+'


# сделано
def sign():
    layout = [
        [sg.Button('sign gum membership'), sg.Button('print timings'),
         sg.Radio('first subscription', "RADIO1", default=True),
         sg.Radio('repeat subscription', "RADIO1"),
         ],
        [sg.Text('repeat subscription: phone, period, timing id'),
         sg.InputText('89021111111,  year, 1', size=(100, 10))
         ],
        [sg.Text('first time customer enter :name, gender, phone period, type, `time_of_day` ,hall'),
         sg.InputText('Misha, male, 89081231212 day 2', size=(100, 10))
         ],

        [sg.Output(size=(150, 30))],
        [sg.Cancel()],
    ]
    window = sg.Window('fitness base', layout, size=(1500, 500))

    # 89824366463 2020 year gum evening
    while True:
        event, values = window.read()
        # print(event)
        # print(values)
        if event == 'print timings':
            print(timing_table())
        if event == 'sign gum membership':
            request = re.split(myre, values[2])
            if (values[1] == False):
                request = re.split(myre, values[3])
                query = r"insert into clients (name,gender,phone) values ('{name1}','{gendr}',{phone})". \
                    format(name1=request[0], gendr=request[1], phone=request[2])
                request = request[2:]
                # print(request)
                # print(query)
                try:
                    cursor.execute(query)
                except Error as e:
                    error(f"The error '{e}' occurred")
                    break
            # print(request)
            # for i, k in enumerate(request):
            # print(i, k)

            time_id = find(table='times_multiple', table_header='period', item=request[1])[0][0]
            # print(time_id)
            try:
                client_id = find(table='clients', table_header='phone', item=request[0])[0][0]
            except:
                error("wrong number")
                break
            # print(client_id)
            date_in = datetime.date.today()
            timing_id = request[2]
            update_capacity(timing_id)
            timing_id = find(table='timing', table_header='id', item=request[2])[0][0]
            date_out = date_in + datetime.timedelta(
                days=find(ret='days', table='times_multiple', table_header='period', item=request[1])[0][0])
            # print(date_out)
            cost = (find(ret='days', table='times_multiple', table_header='period', item=request[1])[0][0] *
                    (find(ret='multiple_bay', table='times_multiple', table_header='period', item=request[1])[0][0]))
            # print(cost)
            query = "insert into content (client_id,time_id,timing_id,date_in,date_out,cost) values ({client_id}, {time_id} ,{timing_id},'{date_in}','{date_out}',{cost})". \
                format(client_id=client_id, time_id=time_id, timing_id=timing_id, date_in=date_in,
                       date_out=date_out, cost=cost)
            # print(query)

            try:
                cursor.execute(query)
            except Error as e:
                error(f"The error '{e}' occurred")
                break
            print("pay", cost, "dollars")
        if event == 'Cancel' or event == None:
            break
    window.close()
    connection.commit()


# сделано
def find(table, table_header, item, ret='id'):
    result = None
    query = "SELECT c.{ret} FROM {table} c WHERE c.{table_header}='{item}'".format(ret=ret, table=table,
                                                                                   table_header=table_header, item=item)
    # print(query)
    try:
        cursor.execute(query)
        # result = pd.DataFrame(cursor.fetchall())
        result = list(cursor.fetchall())
        return result
    except Error as e:
        error(f"The error '{e}' occurred")


def report():
    sizein = (20, 10)
    layout = [
        [sg.Button('make report')
         ],
        # [sg.Text('sales and attendance report from'), sg.In(key='C1', enable_events=True, visible=True),
        #  sg.CalendarButton('from', target='C1', ), sg.Text('before')
        #     , sg.In(key='C2', enable_events=True, visible=True),
        #  sg.CalendarButton('before', target='C2', ),
        #  ],
        [sg.Text('sales and attendance report for'), sg.InputText("2020"), sg.Text('year')
         ],
        [sg.Output(size=(150, 30))
         ],
        [sg.Cancel()]
    ]
    window = sg.Window('fitness base', layout, size=(1500, 500))
    # 89824366463 2020 year gum evening
    while True:
        event, values = window.read()
        year = values[0];
        if event == 'Cancel' or event == None:
            break
        if event == 'C1':
            date1 = (values['C1']).split()[0]
        if event == 'C2':
            date2 = (values['C2']).split()[0]
        if event == 'make report':
            print("month         profit         col")

            query = "select  e.name,  IFNULL(c.sum1,0),IFNULL(c.count1,0) from empty_month e left outer join " \
                    "(select month(c.date_in)  as month1,   sum(c.cost) as sum1, count(c.cost) as count1 from content c where year(date_in)= {year} group by month(date_in)) c on e.month = c.month1;".format(
                year=year)
            result = None
            try:
                cursor.execute(query)
                result = cursor.fetchall()
            except Error as e:
                print(f"The error '{e}' occurred")
            month = pd.DataFrame(data=result)
            # print("month",month)
            query = "select   IFNULL(c.sum1,0),IFNULL(c.count1,0) from empty_quarter e left outer join " \
                    "(select quarter(c.date_in)  as month1,   sum(c.cost) as sum1, count(c.cost) as count1 from content c where year(date_in)={year} group by quarter(date_in)) c on e.quarter = c.month1;".format(
                year=year)
            result = None
            try:
                cursor.execute(query)
                result = cursor.fetchall()
            except Error as e:
                print(f"The error '{e}' occurred")
            quarter = pd.DataFrame(data=result)
            # prinet another example of showing CSV data in Tablet("quar", quarter)
            for i in range(1, 13):
                print('         '.join(map(str, (month.iloc[i - 1].to_numpy()))))
                if i % 3 == 0:
                    print('             ', '          '.join(map(str, ((quarter.iloc[i // 3 - 1]).to_numpy()))))
            print("_____________________________________")

    window.close()


def forecast():
    sizein = (20, 10)
    layout = [
        [sg.Button('make forecast')
         ],
        [sg.Text('date'), sg.In(key='C1', enable_events=True, visible=True),
         sg.CalendarButton('from', target='C1', ), sg.Text('kvant'),
         sg.InputText()
         ],
        # [sg.Output(size=(1000, 50))],
        [sg.Cancel()]
    ]
    window = sg.Window('fitness base', layout, size=(1500, 500))
    # 89824366463 2020 year gum evening
    while True:
        event, values = window.read()
        if event == 'Cancel' or event == None:
            break
        date1 = values['C1'].split()[0]
        kvant = values[0]
        print(values)
        print(date1)
        if event == 'make forecast':
            query = ' select c.cost from content c where c.date_in>={d1} join `time interval` ti on `ti`.id = ct.interval_id'.format(
                d1=date1, )
            ######################################################this query don't work
            print(query)
            result = None
            try:
                cursor.execute(query)
                result = cursor.fetchall()
            except Error as e:
                error(f"The error '{e}' occurred")
                break
            print(result)
            ans = 0
            for i in result:
                ans += i
            print('sum', ans)
    window.close()


def edit():
    layout = [
        # [sg.Button('edit', sg.InputText('name'), sg.InputText('time'))
        #  ],
        [sg.Button('add cvant'), sg.InputText('name'), ],
        [sg.Button('add section'), sg.InputText('type hall cvant'), ],
        # [sg.Button('Delete'), sg.InputText('name'), sg.InputText('time')
        #  ],
        # [sg.Text('intervals:'), sg.Table(values=list(timing_table().values), key='tab')
        #  ],
        [sg.Button('Show timetable'), sg.Button('Show cvants')
         ],

        [sg.Output(size=(150, 30))],
        [sg.Cancel()]
    ]
    window = sg.Window('fitness base', layout, size=(1500, 500))
    # 89824366463 2020 year gum evening

    while True:
        # print(timing_table())
        event, values = window.read()
        if event == 'Cancel' or event == None:
            break
        # print(values)
        if event == 'Show timetable':
            print(timing_table())
        if event == 'Show cvants':
            query = "SELECT c.name FROM kvants c"
            result = None
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute(query)
                result = list(cursor.fetchall())
            except Error as e:
                error(f"The error '{e}' occurred")
                break
            for i in result:
                print(i[0])
        if event == 'add cvant':
            name = values[0]
            query = "insert into `kvants` ( name) values ('{name}') ".format(
                name=name)
            cursor = connection.cursor()
            result = None
            try:
                cursor.execute(query)
            except Error as e:
                error(f"The error '{e}' occurred")
                break

            ans = 0
        if event == 'add section':
            sec = values[1].split()
            print(sec)
            try:
                type_id = find(table='type', table_header='kind', item=sec[0])[0][0]
            except:
                error(f"type is not found")
                break
            # print(time_id)
            try:
                hall_id = find(table='halls', table_header='hall', item=sec[1])[0][0]
            except:
                error(f"hall is not found")
                break
            # print(client_id)
            try:
                kvant_id = find(table='kvants', table_header='name', item=sec[2])[0][0]
            except:
                error(f"cvant is not found")
                break
            query = "insert  into timing (type_id, hall_id, kvant_id) values  ({type_id}, {hall_id}, {kvant_id})".format(
                type_id=type_id, hall_id=hall_id, kvant_id=kvant_id)
            cursor = connection.cursor()
            result = None
            print(query)
            try:
                cursor.execute(query)
            except Error as e:
                error(f"The error '{e}' occurred")
                break

            ans = 0
        # if event == 'edit':

    window.close()


def ret():
    layout = [
        [sg.Button('return'), sg.Text('phone, time ,timing id'), sg.InputText('89081231212,  day, 1'), ],
        [sg.Button('print timings')],
        [sg.Output(size=(150, 30))],
        [sg.Cancel()]
    ]
    window = sg.Window('fitness base', layout, size=(1500, 500))
    # 89824366463 2020 year gum evening

    while True:
        # print(timing_table())
        event, values = window.read()
        if event == 'Cancel' or event == None:
            break
        if event == 'print timings':
            print(timing_table())

        if event == 'return':
            request = re.split(myre, values[0])
            time_id = find(table='times_multiple', table_header='period', item=request[1])[0][0]
            # print(time_id)
            client_id = find(table='clients', table_header='phone', item=request[0])[0][0]
            # print(client_id)

            timing_id = request[2]
            update_capacity(timing_id, -1)
            # timing_id = find(table='timing', table_header='id', item=request[2])[0][0]
            # print(timing_id)
            cost = (find(ret='days', table='times_multiple', table_header='period', item=request[1])[0][0] *
                    (find(ret='multiple_return', table='times_multiple', table_header='period', item=request[1])[0][0]))
            try:
                content_id = find_id(client_id, timing_id)[0][0]
            except:
                error("перед нами жулик")
                break
            # print(cost()
            query = "UPDATE content c SET c.activated = 0 WHERE c.id={content_id};".format(content_id=content_id)
            # print(query)
            try:
                cursor.execute(query)
            except Error as e:
                error(f"The error '{e}' occurred")
                break
            query = "insert into content (client_id,time_id,timing_id,date_in,date_out,cost,activated) values ({client_id}, {time_id} ,{timing_id},'{date_out}','{date_out}',{cost},0);". \
                format(client_id=client_id, time_id=time_id, timing_id=timing_id,
                       date_out=datetime.date.today(), cost=cost)
            # print(query)
            try:
                cursor.execute(query)
            except Error as e:
                error(f"The error '{e}' occurred")
                break

            print("return", -cost, "dollars")
    window.close()


def find_id(client, timing, ret='id'):
    result = None
    query = "SELECT c.{ret} FROM content c  WHERE c.client_id={client_id} and c.timing_id={timing_id} and c.activated=1;".format(
        client_id=client, timing_id=timing, ret=ret)
    # print(query)
    try:
        cursor.execute(query)
        # result = pd.DataFrame(cursor.fetchall())
        result = list(cursor.fetchall())
        return result
    except Error as e:
        error(f"The error '{e}' occurred")


def chek():
    data = find("content", "date_out", str(datetime.date.today()), "*")
    # print(data)
    for i in data:
        if i[7] == 1:
            update_capacity(i[3], -1)
            query = "UPDATE content c SET c.activated = 0 WHERE c.id={content_id};".format(content_id=i[0])
            # print(query)
            try:
                cursor.execute(query)
            except Error as e:
                error(f"The error '{e}' occurred")


connection = create_connection("localhost", "root", "P@$$w0rd", "fitness")
cursor = connection.cursor(buffered=True)
print(datetime.date.today())


def test_gen(name, col):
    for i in range(col):
        query = "insert into  {name}  ( info) values ({a});".format(name=name, a=col)
        # print(query)
        try:
            cursor.execute(query)
        except Error as e:
            error(f"The error '{e}' occurred")
            break
def test_sel(name, col):
    query = "select t.info from {name} t where t.info={col}".format(name=name, col=col/2 + 100)
    start_time = time.time()
    cursor.execute(query)
    print("%s " % (time.time() - start_time))

def test_sel1(name, col):
    query = "select t.id from {name} t where t.id={col}".format(name=name, col=col  + 100)
    start_time = time.time()
    cursor.execute(query)
    print("%s " % (time.time() - start_time))


# Поиск по маске
def test_sel2(name, col):
    start_time = time.time()
    query = "select t.id from {name} t where t.info like 			'{col}'".format(name=name, col="10%")
    start_time = time.time()
    cursor.execute(query)

    print("%s " % (time.time() - start_time))


# Добавление записи
def test_add(name, col):
    start_time = time.time()
    query = "insert into {name} (info) values ({col});".format(name=name, col=col / 2 + 100)
    start_time = time.time()
    cursor.execute(query)
    print("%s " % (time.time() - start_time))


# Добавление группы записей
def test_add2(name, col):
    start_time = time.time()

    query = "insert into {name} (info) values (100),(101),(100),({col}),({col}),({col}),({col}),({col}),({col}),({col});".format(
            name=name, col=col / 2 +100 )
    start_time = time.time()
    cursor.execute(query)
    print("%s " % (time.time() - start_time))


# Изменение записи
def test_up(name, col):
    start_time = time.time()

    query = "update {name} t set info=5 where t.id={col} ;".format(name=name, col=col  + 100)
    start_time = time.time()
    cursor.execute(query)
    print("%s " % (time.time() - start_time))
def test_up2(name, col):
    start_time = time.time()

    query = "update {name} t set info=5 where t.info={col} ;".format(name=name, col=col / 2 + 100)
    start_time = time.time()
    cursor.execute(query)
    print("%s " % (time.time() - start_time))


# Удаление записи
def test_del(name, col):

    query = "delete from {name} t  where t.info={a} ;".format(name=name, a=col-500)
    start_time = time.time()
    cursor.execute(query)
    print("%s " % (time.time() - start_time))
def test_del2(name, col):

    query = "delete from {name} t  where t.id={a} ;".format(name=name, a=col+200)
    start_time = time.time()
    cursor.execute(query)
    print("%s " % (time.time() - start_time))
def test_del3(name, col):

    query = "delete from {name} t  where t.id>{col} and t.id<({col}+102) ;".format(name=name,col=col+102)
    start_time = time.time()
    cursor.execute(query)
    print("%s " % (time.time() - start_time))
def test_sel222(name, col):
    start_time = time.time()
    # query = "delete from {name} t  WHERE info IN ({a})  ;".format(name=name,a=str(', '.join(list(str(i).split(",")))))

    # print(query)
    # cursor.execute(query)
    print("%s " % (time.time() - start_time))


# 0.0005216598510742188
# 0.0003788471221923828
# 0.0003418922424316406
# Движок InnoDB не поддерживает уменьшение размеров файлов БД — это принципиальное ограничение.
# Единственный способ уменьшить размер БД — сделать дамп, переинициализировать хранилище, восстановить из дампа.
if __name__ == '__main__':

    # 46.146.232.210
    # P0$t9re$

    # connection.commit()
    last_chek = 0
    while True:
        ww = ['test1000', 'test10000', 'test100000']
        www = [1000, 10000, 100000]
        # test_gen('second100000',100000)
        # connection.commit()
        print("поиск по не ключевому ")
        for i in range(3):
            test_sel(ww[i], www[i])
        print ("поиск по ключевому ")
        for i in range(3):
            test_sel1(ww[i], www[i])
        print ("поиск по маске ")
        for i in range(3):
            test_sel2(ww[i], www[i])
        print("добавленеие одной записи ")
        for i in range(3):
            test_add(ww[i], www[i])
        print("добавленеие 10 записей ")
        for i in range(3):
            test_add2(ww[i], www[i])
        print("изменение одной записи по ключевому ")
        for i in range(3):
            test_up(ww[i], www[i])
        print("изменение одной записи не по ключевому ")
        for i in range(3):
            test_up2(ww[i], www[i])
        print("удаление по не ключевому")
        for i in range(3):
            test_del(ww[i], www[i])
        print("удаление по  ключевому")
        for i in range(3):
            test_del2(ww[i], www[i])
        print("удаление по  ключевому группы")
        for i in range(3):
            test_del3(ww[i], www[i])
        # connection.commit()
        event, values = window.read()
        if (datetime.date.today() != last_chek):
            chek()
            print("chek")
            last_chek = datetime.date.today()
        if event == 'Cancel' or event == None:
            break
        # if values[0] == True:
        #     def_text='name, age, gender,date, period, type, time of day'
        if event == 'sign gum membership':
            sign()
        if event == 'Make sales and attendance report':
            report()
        if event == 'Make forecast of the hall is workload':
            forecast()
        if event == 'edit time interval':
            edit()
        if event == 'return membership(':
            ret()

        # print(values)
        # print(event)
        connection.commit()
window.close()
