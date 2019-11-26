import DBINTERFACE as DB
import ACCOUNTMANAGER as AM
import sqlite3
import json
from datetime import datetime  
from flask import Flask
from flask import request, render_template, redirect, Response, jsonify, Blueprint

user = Blueprint('user', __name__, template_folder='templates')

@user.route('/getreciept', methods = ['POST'])
def getreciept():
    # returns code, message, reciept

    data = json.loads(request.data)
    account = AM.checktoken(data['token'])
    #does account exist
    if account[0] == False:
        return {'code': 'failed', 'message': 'Not logged in.', 'reciept': None}

    booking = DB.query('bookings', args='WHERE bookingID = {bi}'.format(bi = data['bookingID']))
    transaction = DB.query('transactions', args='WHERE bookingID = {bi}'.format(bi = data['bookingID'])) 

    #does the booking exist
    if len(booking) != 1:
        return {'code': 'failed', 'message': 'No such booking exists.', 'reciept': None}

    #is this the correct account
    if booking[0][3] != account[2]:
        return {'code': 'failed', 'message': 'Incorrect account.', 'reciept': None}

    return {'code': 'success', 'message': '', 'reciept': json.loads(str({**json.loads(DB.genjson('bookings', booking))[0], **json.loads(DB.genjson('transactions', transaction))[0]}).replace('\'', '"'))}
    
@user.route('/getbookings', methods = ['POST'])
def getbookings():
    #returns list of bookings

    data = json.loads(request.data)
    account = AM.checktoken(data['token'])
    #does account exist
    if account[0] == False:
        return {'code': 'failed', 'message': 'Not logged in.', 'bookings': None}

    return {'code': 'success', 'message': '', 'bookings': 
        json.loads(DB.genjson('bookings', DB.query('bookings', args='WHERE username = \'{u}\''
            .format(u = account[2]))))
            }

@user.route('/cancelbooking', methods = ['POST'])
def cancelBooking():

    data = json.loads(request.data)
    account = AM.checktoken(data['token'])
    #does account exist
    if account[0] == False:
        return {'code': 'failed', 'message': 'Not logged in.'}

    booking = DB.query('bookings', args="WHERE username = \'{u}\' AND bookingID = {bi}".format(u = account[2], bi = data['bookingID']))
    if len(booking) < 1:
        return {'code': 'failed', 'message': 'No such booking exists.'}

    bookingDate = datetime.strptime(booking[0][4], '%Y-%m-%d')

    print(bookingDate)
    print(datetime.now())

    if datetime.now() >= bookingDate:
        return {'code': 'failed', 'message': 'This date of this booking has already passed.'}

    DB.delete('bookings', 'bookingID = {bi}'.format(bi = data['bookingID']))
    DB.delete('transactions', 'bookingID = {bi}'.format(bi = data['bookingID']))

    return {'code': 'success', 'message': 'Booking has been cancelled.'}