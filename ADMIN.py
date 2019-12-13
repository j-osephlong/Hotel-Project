import DBINTERFACE as DB
import ACCOUNTMANAGER as AM
import sqlite3
import json
from flask import Flask
from flask import request, render_template, redirect, Response, jsonify, Blueprint

admin = Blueprint('admin', __name__, template_folder='templates')

@admin.route("/approveuser", methods=['POST'])
def approveuser():
    data = json.loads(request.data)
    username = data['username']
    if (AM.checktoken(data['token'])[1] == 'admin'):
        row = DB.query('accountrequests', args='WHERE username = \'{u}\''.format(u = username))
        DB.delete('accountrequests', args='username = \'{u}\''.format(u = username))
        DB.insert('users', ('\''+row[0][0]+'\'', '\''+row[0][1]+'\'', '\''+row[0][2]+'\'', '\'user\'', '\'false\'', '(SELECT datetime())'))
        return {'code': 'success'}
    return {'code': 'failed'}

@admin.route("/banuser", methods=['POST'])
def banuser():
    data = json.loads(request.data)
    if (AM.checktoken(data['token'])[1] == 'admin'):
        if DB.query('users', 'banned', 'WHERE username = \'{u}\''.format(u = data['username']))[0][0] == 'false':
            DB.update('users', 'SET banned = \'true\' WHERE username = \'{u}\''.format(u = data['username']))
        else:
            DB.update('users', 'SET banned = \'false\' WHERE username = \'{u}\''.format(u = data['username']))
            
        return {'code': 'success'}
    return {'code': 'failed'}

@admin.route("/admin_deleteroom", methods=['POST'])
def deleteRoom():
    data = json.loads(request.data)
    account = AM.checktoken(data['token'])

    if account[1] != 'admin':
        return {'code' : 'failed', 'message' : 'TYou do not have high enough privilege to do that.'}

    DB.delete('rooms', 'floornumber = {fn} AND roomnumber = {rn}'.format(fn = data['roomid'][:2], rn = data['roomid'][2:]))
    DB.delete('room_info', 'floornumber = {fn} AND roomnumber = {rn}'.format(fn = data['roomid'][:2], rn = data['roomid'][2:]))
    return {'code' : 'success', 'message' : 'Room deleted.'}


@admin.route("/setuserpriv", methods=['POST'])
def setuserpriv():
    data = json.loads(request.data)
    if (AM.checktoken(data['token'])[1] == 'admin'):
        try:
            DB.update('users', 'SET privilege = \'{p}\' WHERE username = \'{u}\''.format(u = data['username'], p = data['priv']))
        except sqlite3.IntegrityError as e:
            return {'code': 'failed', 'message':'Incorrect privilege level.'}
        return {'code': 'success', 'message':'Done.'}
    return {'code': 'failed', 'message':'You do not have high enough privilege to do that.'}

@admin.route("/adminfill", methods = ['POST'])
def filladmin():
    tokendata = AM.checktoken(json.loads(request.data)['token'])
    if tokendata[0] and tokendata[1] == 'admin':
        return render_template("admin.html")
    else:
        return "Your account, or lack there of, does not have the privilege level to view this page."

@admin.route('/admin_logs', methods=['POST'])
def getlog():
    if AM.checktoken(json.loads(request.data)['token'])[1] == 'admin':
        return json.dumps(DB.genjson('dblog', DB.query('dblog',args='ORDER BY time DESC')))

@admin.route('/admin_accountrequests', methods=['POST'])
def getaccountrequests():
    if AM.checktoken(json.loads(request.data)['token'])[1] == 'admin':
        return json.dumps(DB.genjson('accountrequests', DB.query('accountrequests')))

@admin.route('/admin_getusers', methods=['POST'])
def getusers():
    if AM.checktoken(json.loads(request.data)['token'])[1] == 'admin':
        return json.dumps(DB.genjson('users', DB.query('users'), exceptfor=('hashpass', 'salt')))

@admin.route('/admin_getrooms', methods=['POST'])
def getrooms():
    if AM.checktoken(json.loads(request.data)['token'])[1] == 'admin':
        return json.dumps(DB.genjson('rooms', DB.query('rooms')))
