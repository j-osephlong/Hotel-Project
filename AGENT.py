import DBINTERFACE as DB
import ACCOUNTMANAGER as AM
import sqlite3
import json
from flask import Flask
from flask import request, render_template, redirect, Response, jsonify, Blueprint

agent = Blueprint('agent', __name__, template_folder='templates')

@agent.route('/addclient', methods=['POST'])
def addClient():
    # returns code

    data = json.loads(request.data)
    account = AM.checktoken(data['token'])

    if account[1] != 'agent':
        return {'code' : 'failed', 'message' : 'This is not an agent account.'}

    try:
        DB.insert('agent_clients', ('\''+account[2]+'\'', '\''+data['client_name']+'\'', '\''+data['client_email']+'\''))
        return {'code' : 'success', 'message' : 'Client added.'}
    except sqlite3.IntegrityError as E:
        return {'code' : 'failed', 'message' : 'Client already exists.'}

@agent.route('/removeclient', methods=['POST'])
def removeClient():
    # returns code

    data = json.loads(request.data)
    account = AM.checktoken(data['token'])

    print(str(data))

    if account[1] != 'agent':
        return {'code' : 'failed', 'message' : 'This is not an agent account.'}

    if len(DB.query('agent_clients', args= "WHERE username = \'{u}\' AND client_email = \'{e}\'"
        .format(u = account[2], e = data['client_email']))) != 1:
        return {'code' : 'failed', 'message' : 'Not your client.'}

    DB.delete('agent_clients', 'client_email = \'{e}\''.format(e = data['client_email']))
    return {'code' : 'success', 'message' : 'Client removed.'}

@agent.route('/getclients', methods=['POST'])
def getClients():
    # returns code

    data = json.loads(request.data)
    account = AM.checktoken(data['token'])

    if account[1] != 'agent':
        return {'code' : 'failed', 'message' : 'This is not an agent account.', 'clients':None}

    return {'code' : 'success', 'message': '', 'clients': 
        json.loads(DB.genjson('agent_clients', DB.query('agent_clients', args='WHERE username = \'{u}\''
        .format(u = account[2]))))}