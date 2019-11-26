import sqlite3
import json

def initdb():
    sql_create_log =                """ CREATE TABLE IF NOT EXISTS dblog (
                                            command text NOT NULL,
                                            type text NOT NULL,
                                            time text NOT NULL
                                        ); """

    sql_create_users =              """ CREATE TABLE IF NOT EXISTS users (
                                            username text NOT NULL PRIMARY KEY,
                                            hashpass text NOT NULL,
                                            salt text NOT NULL,
                                            privilege text NOT NULL 
                                                check (privilege in (\'user\', \'agent\', \'admin\')),
                                            banned text NOT NULL
                                                check (banned in (\'true\', \'false\')),
                                            time text NOT NULL
                                        ); """

    sql_create_logintokens =        """ CREATE TABLE IF NOT EXISTS logintokens (
                                            username text NOT NULL,
                                            spice text NOT NULL,
                                            time text NOT NULL,
                                            PRIMARY KEY(username, spice)
                                        ); """ #primary key should be token, username foreign to users

    sql_create_accountrequests =    """ CREATE TABLE IF NOT EXISTS accountrequests (
                                            username text NOT NULL,
                                            hashpass text NOT NULL,
                                            spice text NOT NULL,
                                            time text NOT NULL,
                                            PRIMARY KEY(username, spice)
                                        ); """ 

    sql_create_rooms =              """ CREATE TABLE IF NOT EXISTS rooms (
                                            floornumber number NOT NULL,
                                            roomnumber number NOT NULL,
                                            isVaccant text NOT NULL
                                                check (isVaccant in (\'true\', \'false\')),
                                            isReady text NOT NULL
                                                check (isReady in (\'true\', \'false\')),
                                            description text NOT NULL,
                                            price text NOT NULL,
                                            PRIMARY KEY(floornumber, roomnumber)
                                        ); """

    sql_create_room_info =          """ CREATE TABLE IF NOT EXISTS room_info (
                                            floornumber number NOT NULL,
                                            roomnumber number NOT NULL,
                                            bed text NOT NULL
                                                check (bed in (\'single\', \'twin\', \'queen\', \'king\', \'double\')),
                                            microwave text NOT NULL
                                                check (microwave in (\'true\', \'false\')),
                                            balcony text NOT NULL
                                                check (balcony in (\'true\', \'false\')),
                                            ethernet text NOT NULL
                                                check (ethernet in (\'true\', \'false\')),
                                            TV text NOT NULL
                                                check (TV in (\'true\', \'false\')),
                                            bedamount number NOT NULL,
                                            PRIMARY KEY(floornumber, roomnumber)
                                        ); """

    sql_create_bookings =           """ CREATE TABLE IF NOT EXISTS bookings (
                                            bookingID number NOT NULL PRIMARY KEY,
                                            floornumber number NOT NULL,
                                            roomnumber number NOT NULL,
                                            username text NOT NULL,
                                            date text NOT NULL,
                                            customer_name text NOT NULL
                                        ); """

    sql_create_transactions =       """ CREATE TABLE IF NOT EXISTS transactions (
                                            transID number NOT NULL PRIMARY KEY,
                                            username text NOT NULL,
                                            price text NOT NULL,
                                            bookingID number NOT NULL,
                                            customer_name text NOT NULL
                                        ); """

    sql_create_agent_clients =      """ CREATE TABLE IF NOT EXISTS agent_clients (
                                            username text NOT NULL,
                                            client_name text NOT NULL,
                                            client_email text NOT NULL PRIMARY KEY
                                        ); """

    dbconn = sqlite3.connect("user.db")
    cursor = dbconn.cursor()
    cursor.execute(sql_create_users)
    cursor.execute(sql_create_logintokens)
    cursor.execute(sql_create_log)
    cursor.execute(sql_create_accountrequests)
    cursor.execute(sql_create_rooms)
    cursor.execute(sql_create_room_info)
    cursor.execute(sql_create_bookings)
    cursor.execute(sql_create_transactions)
    cursor.execute(sql_create_agent_clients)
    dbconn.close()

def insert(table, values):
    vals = ''
    for value in values:
        vals+=value+','
    vals = vals[:-1]

    sql_insert= """INSERT INTO {t} VALUES({v});""".format(t=table, v=vals)
    sql_log = """ INSERT INTO dblog VALUES (\'{c}\', \'insert\', (SELECT datetime())); """.format(c = table + ", " + vals.replace("\'", ""))
    print(sql_log)
    dbconn = sqlite3.connect("user.db")
    cursor = dbconn.cursor()
    cursor.execute(sql_insert)
    cursor.execute(sql_log)
    dbconn.commit()
    dbconn.close()

def query(table, columns='*', args=''):
    sql_query= """SELECT {c} FROM {t} {a};""".format(c=columns, t=table, a=args)  
    dbconn = sqlite3.connect("user.db")
    cursor = dbconn.cursor()
    cursor.execute(sql_query)
    result = cursor.fetchall()
    dbconn.close()

    return result

def delete(table, args):
    sql_query= """DELETE FROM {t} WHERE {a};""".format(t = table, a = args)
    sql_log = """ INSERT INTO dblog VALUES (\'{c}\', \'delete\', (SELECT datetime())); """.format(c = table + ", " + args.replace("\'", ""))
    dbconn = sqlite3.connect("user.db")
    cursor = dbconn.cursor()
    cursor.execute(sql_query)
    cursor.execute(sql_log)
    dbconn.commit()
    dbconn.close()

def update(table, args):
    sql_query= """UPDATE {t} {a};""".format(t = table, a = args)
    sql_log = """ INSERT INTO dblog VALUES (\'{c}\', \'update\', (SELECT datetime())); """.format(c = table + ", " + args.replace("\'", ""))
    dbconn = sqlite3.connect("user.db")
    cursor = dbconn.cursor()
    cursor.execute(sql_query)
    cursor.execute(sql_log)
    dbconn.commit()
    dbconn.close()
    
def genjson(table, query, exceptfor=()):
    dbconn = sqlite3.connect("user.db")
    cursor = dbconn.cursor()
    column_info = cursor.execute("""PRAGMA table_info({t})""".format(t = table)).fetchall()

    jsonstr = ""
    for i in range(len(query)):
        jsonatt = ["\"{c}\" : \"{v}\",".format(c = cname[1], v = cvalue) for cname, cvalue in zip(column_info, query[i]) if cname[1] not in exceptfor]
        jsonrow = ""
        for entry in jsonatt:
            jsonrow+=entry
        jsonrow="{"+jsonrow[:-1]+"},"
        jsonstr+=jsonrow
    jsonstr = "["+jsonstr[:-1]+"]"
    return jsonstr