import DBINTERFACE as DB
import ACCOUNTMANAGER as AM
import json, random, sqlite3
from flask import Flask
from flask import request, render_template, redirect, Response, jsonify, Blueprint,abort

rooms = Blueprint('rooms', __name__, template_folder='templates')

@rooms.route('/rooms/<room>')
def serveroom(room):
    roomrow = DB.query('rooms', args='WHERE floornumber = {fn} AND roomnumber = {rn}'.format(fn = room[:2], rn=room[2:]))
    if len(roomrow) == 1:
        return render_template('room.html', r = DB.genjson('rooms', DB.query('rooms', args='WHERE floornumber = {fn} AND roomnumber = {rn}'.format(fn = room[:2], rn=room[2:]))))
    else:
        return "404"

@rooms.route('/bookroom', methods=['POST'])
def bookroom():
    #room id, token, date
    data = json.loads(request.data)
    floornumber = data['roomid'][:2]
    roomnumber = data['roomid'][2:]
    print(str(data))
    rows = DB.query('bookings', args='WHERE floornumber = {fn} AND roomnumber = {rn} AND date = \"{d}\"'.format(
        fn = floornumber, rn = roomnumber, d = data['date']
    ))
    
    if len(rows) > 0:
        return {'code':'failed', 'message':'Room already booked for that date.'}

    userdata = AM.checktoken(data['token'])
    if userdata[0] == False:
        return {'code':'failed', 'message':'Invalid user token.'}
    try:
        price = DB.query('rooms', columns='price', args='WHERE floornumber = {fn} AND roomnumber = {rn}'.format(
            fn = floornumber, rn = roomnumber
        ))[0][0]
    except IndexError as E:
        return {'code':'failed', 'message': 'No such room exists.'}
    transID = random.randint(100000, 999999)
    bookingID = random.randint(100000, 999999)

    while True:
        try:
            DB.insert('bookings', (str(bookingID), "\'"+str(floornumber)+"\'", "\'"+str(roomnumber)+"\'", "\'"+userdata[2]+"\'", "\'"+data['date']+"\'", "\'"+data['customer_name']+"\'"))
            break
        except sqlite3.InterfaceError as E:
            bookingID = random.randint(100000, 999999)

    while True:
        try:
            DB.insert('transactions', (str(transID), "\'"+userdata[2]+"\'", "\'"+price+"\'", str(bookingID), "\'"+data['customer_name']+"\'"))
            break
        except sqlite3.IntegrityError as E:
            transID = random.randint(100000, 999999)

    return {'code':'success', 'message':'Room booked.', 'bookingID':bookingID, 'transactionID':transID}

#       !!!!!!!!!!
#   TERRIBLE CODE BELOW
#       !!!!!!!!!!
@rooms.route('/getrooms', methods=['POST'])
def searchrooms():
    #this can all be changed to a single test case

    print(json.loads(request.data))
    data = json.loads(request.data)

    if data['all']:
        return DB.genjson('rooms', DB.query('rooms'))

    available = list()   
    
    if data['bed-type']!=None or data['microwave']!=None or data['balcony']!=None or data['ethernet']!=None or data['TV']!=None or data['bed-amount']!=None:    
        feature_args = 'WHERE 1 {be} {mi} {ba} {et} {tv} {be_a}'.format(
            be = 'AND bed =  \''+data['bed-type']+'\'' if data['bed-type'] != 'null' else '', 
            mi = 'AND microwave = \''+str(data['microwave']).lower()+'\'' if data['microwave']!=False else '',
            ba = 'AND balcony = \''+str(data['balcony']).lower()+'\'' if data['balcony']!=False else '',
            et = 'AND ethernet = \''+str(data['ethernet']).lower()+'\'' if data['ethernet']!=False else '',
            tv = 'AND TV = \''+str(data['TV']).lower()+'\'' if data['TV']!=False else '',
            be_a = 'AND bedamount ='+data['bed-amount'] if data['bed-amount']!='null' else ''
        )

        print(feature_args)

        rooms_wf = DB.query('room_info', 'floornumber, roomnumber', feature_args)
        if data['date'] != '':
            for room in rooms_wf:
                if (len(DB.query('bookings', args='WHERE roomnumber={rn} AND floornumber={fn} AND date = \'{d}\''.format(
                        fn = room[0], rn = room[1], d = data['date']
                    ))) == 0):
                    available.append(DB.query('rooms', args='WHERE floornumber = {fn} AND roomnumber = {rn}'.format(fn=room[0], rn=room[1]))[0])

            return DB.genjson('rooms', available)
        else:
            for room in rooms_wf:
                available.append(DB.query('rooms', args='WHERE floornumber = {fn} AND roomnumber = {rn}'.format(fn=room[0], rn=room[1]))[0])

            return DB.genjson('rooms', available)
    elif data['date'] != '':
        rooms = DB.query('rooms')
        for room in rooms:
            if (len(DB.query('bookings', args='WHERE roomnumber={rn} AND floornumber={fn} AND date = \'{d}\''.format(
                    fn = room[0], rn = room[1], d = data['date']
                ))) == 0):
                available.append(room)
        return DB.genjson('rooms', available)
    else:
        return DB.genjson('rooms', DB.query('rooms'))


    #select * from rooms where room not in (select * from bookings where room/floor and 
    #   date)
@rooms.route('/getroom', methods=['POST'])
def getroom():
    data = json.loads(request.data)
    print(data)
    roomrow = DB.query('rooms', args='WHERE floornumber = {fn} AND roomnumber = {rn}'.format(
        fn = data['roomid'][:2], rn = data['roomid'][2:], 
    ))
    if len(roomrow) < 1:
        return {'code':'failed', 'message': 'No such room exists.'}

    roomfeatures = DB.query('room_info', args='WHERE floornumber = {fn} AND roomnumber = {rn}'.format(
        fn = data['roomid'][:2], rn = data['roomid'][2:], 
    ))
    return str({**json.loads(DB.genjson('rooms', roomrow))[0], **json.loads(DB.genjson('room_info', roomfeatures))[0]}).replace('\'', '"')

#WIP
@rooms.route('/admin_createroom', methods=['POST'])   
def createroom():
    data = json.loads(request.data)
    if AM.checktoken(json.loads(request.data)['token'])[1] != 'admin':
        return {'code':'failed', 'message':'Privilege level not high enough.'}
    print(str(data))
    if len(DB.query('rooms', args='WHERE floornumber = {fn} AND roomnumber = {rn}'
        .format(fn = data['update']['floornumber'], rn = data['update']['roomnumber']))) > 0:
            return {'code':'failed', 'message':'Room already exists.'}

    DB.insert('rooms', (data['update']['floornumber'], data['update']['roomnumber'],
                        "\'"+data['update']['isVaccant']+"\'","\'"+data['update']['isReady']+"\'",
                        "\'"+data['update']['description']+"\'","\'"+data['update']['price']+"\'"))

    DB.insert('room_info', (data['update']['floornumber'], data['update']['roomnumber'],
                        "\'"+data['update']['bed']+"\'","\'"+data['update']['microwave']+"\'",
                        "\'"+data['update']['balcony']+"\'","\'"+data['update']['ethernet']+"\'",
                        "\'"+data['update']['TV']+"\'",data['update']['bedamount']))

    return {'code':'success', 'message':'Room added to DB.'}
    

#WIP
@rooms.route('/admin_editroom', methods=['POST'])   
def editroom():
    data = json.loads(request.data)
    if AM.checktoken(json.loads(request.data)['token'])[1] != 'admin':
        return {'code':'failed', 'message':'Privilege level not high enough.'}

    if len(DB.query('rooms', args='WHERE floornumber = {fn} AND roomnumber = {rn}'
        .format(fn = data['update']['floornumber'], rn = data['update']['roomnumber']))) < 1:
            return {'code':'failed', 'message':'No such room exists.'}


    DB.update('rooms', 
        'SET isVaccant = \'{isVaccant}\', isReady = \'{isReady}\', description = \'{description}\', price = \'{price}\' WHERE floornumber = {fn} AND roomnumber = {rn}'
        .format(isVaccant = data['update']['isVaccant'], isReady = data['update']['isReady'],
        description = data['update']['description'], price = data['update']['price'],
        fn = data['update']['floornumber'], rn = data['update']['roomnumber']))

    DB.update('room_info', 
        'SET bed = \'{bed}\', microwave =\'{microwave}\', balcony=\'{balcony}\', ethernet=\'{ethernet}\', TV=\'{TV}\', bedamount={bedamount} WHERE floornumber = {fn} AND roomnumber = {rn}'
        .format(bed = data['update']['bed'], microwave = data['update']['microwave'], balcony = data['update']['balcony'],
        ethernet = data['update']['ethernet'], TV=data['update']['TV'], bedamount=data['update']['bedamount'],
        fn = data['update']['floornumber'], rn=data['update']['roomnumber']))
    return {'code': 'success', 'message':'Update saved.'}
    
    

